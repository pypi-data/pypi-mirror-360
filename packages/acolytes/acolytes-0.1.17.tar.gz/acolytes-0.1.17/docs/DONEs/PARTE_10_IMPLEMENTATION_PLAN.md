# 📋 Plan de Implementación - PARTE 10: Paralelización con Workers

## 🎯 Estrategia Final: Híbrido de Opciones A+C

Basado en la investigación y la confirmación externa, la mejor estrategia es:

1. **Worker Pool** (mi Opción A) para el flujo general
2. **Cliente Weaviate por Worker** (Opción C + sugerencia externa) para evitar thread-safety issues
3. **Embeddings compartidos** (con lock si es necesario) para no duplicar modelos en GPU

## 🏗️ Arquitectura Propuesta

```python
class IndexingService:
    def __init__(self):
        # Existing code...
        self.concurrent_workers = self.config.get("indexing.concurrent_workers", 4)
        self.enable_parallel = self.config.get("indexing.enable_parallel", False)
        
        # Worker pool components
        self._worker_pool = None
        self._file_queue: asyncio.Queue = None
        self._weaviate_clients = []  # Pool de clientes
        
    async def _initialize_workers(self):
        """Initialize worker pool and resources."""
        if not self.enable_parallel:
            return
            
        # Create queue
        self._file_queue = asyncio.Queue()
        
        # Create Weaviate client pool (one per worker)
        weaviate_url = f"http://localhost:{self.config.get('ports.weaviate', 8080)}"
        for i in range(self.concurrent_workers):
            client = weaviate.Client(weaviate_url)
            self._weaviate_clients.append(client)
            
        # Start workers
        self._worker_pool = []
        for i in range(self.concurrent_workers):
            worker = asyncio.create_task(self._indexing_worker(i))
            self._worker_pool.append(worker)
```

## 📝 Implementación del Worker

```python
async def _indexing_worker(self, worker_id: int):
    """Worker that processes files from queue."""
    logger.info(f"Indexing worker {worker_id} started")
    
    # Get dedicated Weaviate client for this worker
    weaviate_client = self._weaviate_clients[worker_id]
    
    # Create batch inserter with this client
    batch_inserter = WeaviateBatchInserter(weaviate_client, self.config)
    
    while True:
        try:
            # Get batch of files from queue
            file_batch = await self._file_queue.get()
            
            if file_batch is None:  # Shutdown signal
                break
                
            # Process files
            chunks_created = 0
            embeddings_created = 0
            errors = []
            
            for file_path in file_batch:
                try:
                    # 1. CHUNKING (CPU-bound, safe to parallelize)
                    chunks = await self._chunk_single_file(file_path)
                    
                    # 2. ENRICHMENT (I/O-bound, safe)
                    enriched_tuples = await self._enrich_chunks(chunks)
                    
                    # 3. EMBEDDINGS (GPU-bound, needs care)
                    # Use shared embeddings service with internal locking
                    embeddings = await self._generate_embeddings_safe(
                        [chunk for chunk, _ in enriched_tuples],
                        worker_id
                    )
                    
                    # 4. BATCH INSERT (usando cliente dedicado)
                    weaviate_objects = []
                    vectors = []
                    
                    for i, (chunk, metadata) in enumerate(enriched_tuples):
                        obj = self._prepare_weaviate_object(chunk, metadata)
                        weaviate_objects.append(obj)
                        vectors.append(embeddings[i] if i < len(embeddings) else None)
                    
                    # Insert using worker's dedicated client
                    successful, insert_errors = await batch_inserter.batch_insert(
                        data_objects=weaviate_objects,
                        vectors=vectors,
                        class_name="CodeChunk"
                    )
                    
                    chunks_created += successful
                    errors.extend(insert_errors)
                    
                    logger.debug(
                        f"Worker {worker_id} processed file",
                        file=file_path,
                        chunks=successful
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Worker {worker_id} failed on file",
                        file=file_path,
                        error=str(e)
                    )
                    errors.append({
                        "file": file_path,
                        "error": str(e),
                        "worker_id": worker_id
                    })
            
            # Report results back (implement callback or result queue)
            await self._report_worker_results(
                worker_id,
                chunks_created,
                embeddings_created,
                errors
            )
            
        except Exception as e:
            logger.error(f"Worker {worker_id} crashed", error=str(e))
            # Worker will be restarted by supervisor
```

## 🔐 Embeddings Thread-Safe

```python
async def _generate_embeddings_safe(self, chunks: List[Chunk], worker_id: int):
    """Generate embeddings with thread safety for parallel workers."""
    
    # Option 1: Use semaphore to limit concurrent GPU access
    async with self._embeddings_semaphore:
        return await self._generate_embeddings_batch(chunks)
    
    # Option 2: Queue embeddings requests
    # (if Option 1 causes issues)
```

## 🚀 Flujo de Ejecución Paralelo

```python
async def index_files(self, files: List[str], ...):
    """Main entry point with parallel support."""
    
    if not self.enable_parallel or len(files) < 20:
        # Use existing sequential code for small batches
        return await self._index_files_sequential(files, ...)
    
    # Initialize workers if needed
    if self._worker_pool is None:
        await self._initialize_workers()
    
    # Divide files into chunks for workers
    chunk_size = max(10, len(files) // (self.concurrent_workers * 2))
    file_chunks = [files[i:i+chunk_size] for i in range(0, len(files), chunk_size)]
    
    # Queue all chunks
    for chunk in file_chunks:
        await self._file_queue.put(chunk)
    
    # Wait for completion (with timeout)
    # ...
```

## 📊 Métricas por Worker

```python
# Agregar métricas específicas por worker
self.metrics.increment(f"indexing.worker_{worker_id}.files_processed")
self.metrics.record(f"indexing.worker_{worker_id}.processing_time_ms", elapsed)
self.metrics.gauge(f"indexing.worker_{worker_id}.queue_size", self._file_queue.qsize())
```

## ⚙️ Configuración Recomendada

```yaml
indexing:
  # Feature flags
  enable_parallel: false  # Empezar desactivado
  
  # Worker configuration  
  concurrent_workers: 4   # Número de workers
  
  # Batch sizes
  worker_batch_size: 10   # Archivos por batch de worker
  
  # Safety limits
  max_queue_size: 1000    # Límite de archivos en cola
  worker_timeout: 300     # Timeout por batch (segundos)
  
  # Memory management
  embeddings_semaphore: 2 # Max concurrent embedding operations
```

## 🧪 Plan de Testing

### 1. Test Unitarios
```python
async def test_parallel_indexing_small_batch():
    """Test that parallel mode works with small batches."""
    service = IndexingService()
    service.enable_parallel = True
    service.concurrent_workers = 2
    
    files = ["file1.py", "file2.py", "file3.py", "file4.py"]
    result = await service.index_files(files)
    
    assert result["status"] == "success"
    assert result["files_processed"] == 4
```

### 2. Test de Carga
```python
async def test_parallel_vs_sequential_performance():
    """Compare performance of parallel vs sequential."""
    files = generate_test_files(1000)  # 1000 archivos de prueba
    
    # Sequential
    start = time.time()
    await service_seq.index_files(files)
    seq_time = time.time() - start
    
    # Parallel
    start = time.time()
    await service_par.index_files(files)
    par_time = time.time() - start
    
    # Should be at least 1.5x faster
    assert par_time < seq_time * 0.67
```

### 3. Test de Estabilidad
- Ejecutar con diferentes números de workers
- Simular fallos de workers
- Verificar no hay memory leaks
- Confirmar shutdown graceful

## 🚦 Criterios de Activación

Antes de activar `enable_parallel = true`:

1. ✅ Todos los tests pasan
2. ✅ No memory leaks en 1h de ejecución
3. ✅ Performance mejora >1.5x
4. ✅ Métricas muestran distribución equitativa
5. ✅ No errores de "database locked"
6. ✅ GPU memory estable

## 🎯 Resultado Esperado

Con 4 workers en un proyecto de 1000 archivos:
- **Antes**: ~60 segundos (secuencial)
- **Después**: ~15-20 segundos (4x workers)
- **Bottleneck**: Embeddings generation (GPU)

## ⚠️ Rollback Plan

Si algo sale mal:
```yaml
# En .acolyte config
indexing:
  enable_parallel: false  # Instant rollback
```

El código secuencial existente sigue intacto.