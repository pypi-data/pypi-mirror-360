# 🚀 Guía de Indexación Paralela - ACOLYTE v0.1.8+

## ¿Qué es la Indexación Paralela?

ACOLYTE ahora puede procesar múltiples archivos simultáneamente usando workers paralelos, mejorando la velocidad de indexación **2-4x** en proyectos grandes.

## 🎯 Cuándo Usar

**USAR cuando**:
- ✅ Tu proyecto tiene **>100 archivos**
- ✅ Tu máquina tiene **≥4 CPU cores**
- ✅ Tienes al menos **8GB RAM disponible**
- ✅ Primera indexación de un proyecto grande

**NO USAR cuando**:
- ❌ Proyecto pequeño (<20 archivos)
- ❌ Máquina con poca RAM (<8GB)
- ❌ Re-indexación incremental
- ❌ Si experimentas problemas de estabilidad

## ⚙️ Configuración

Agrega esto a tu archivo `.acolyte`:

```yaml
indexing:
  # Activar paralelización
  enable_parallel: true
  
  # Número de workers (ajustar según CPU cores)
  concurrent_workers: 4
  
  # Mínimo de archivos para activar paralelización
  min_files_for_parallel: 20
  
  # Archivos procesados por cada worker
  worker_batch_size: 10
  
  # Límite de operaciones GPU simultáneas
  embeddings_semaphore: 2
```

### Configuración Recomendada por Hardware

| CPU Cores | RAM   | Workers | Batch Size | GPU Semaphore |
|-----------|-------|---------|------------|---------------|
| 4         | 8GB   | 2       | 5          | 1             |
| 8         | 16GB  | 4       | 10         | 2             |
| 16+       | 32GB+ | 8       | 20         | 3             |

## 📊 Rendimiento Esperado

| Archivos | Tiempo Secuencial | Tiempo Paralelo (4 workers) | Mejora |
|----------|-------------------|----------------------------|--------|
| 100      | ~2 minutos        | ~40 segundos               | 3x     |
| 500      | ~10 minutos       | ~3 minutos                 | 3.3x   |
| 1000     | ~20 minutos       | ~6 minutos                 | 3.3x   |
| 5000     | ~100 minutos      | ~30 minutos                | 3.3x   |

**Nota**: Los tiempos reales dependen de:
- Velocidad del disco
- Tamaño promedio de archivos
- Complejidad del código
- GPU disponible para embeddings

## 🔍 Monitoreo

Durante la indexación paralela verás logs como:

```
[INFO] Using parallel processing workers=4 files=500
[INFO] Worker 0 started
[INFO] Worker 1 started
[INFO] Worker 2 started
[INFO] Worker 3 started
[INFO] Worker 1 acquired embeddings semaphore
[INFO] Worker 1 generated embeddings count=10
```

## ⚠️ Troubleshooting

### Error: "Out of Memory"
```yaml
# Reducir workers y batch size
indexing:
  concurrent_workers: 2
  worker_batch_size: 5
  embeddings_semaphore: 1
```

### Indexación muy lenta
- Verifica que `enable_parallel: true`
- Aumenta `concurrent_workers` si tienes CPU disponible
- Revisa logs para bottlenecks

### Weaviate errors
- Cada worker usa su propio cliente Weaviate
- Si ves errores de conexión, reduce workers

## 🎮 Comando

La paralelización se activa automáticamente con:
```bash
acolyte index
```

Si está configurada Y hay suficientes archivos (>`min_files_for_parallel`).

## 📈 Métricas

El sistema reporta:
- Archivos procesados por worker
- Tiempo por fase (chunking, embeddings, insertion)
- Errores por worker
- Uso del semáforo GPU

## 🔄 Desactivar Temporalmente

Para forzar modo secuencial sin cambiar config:
```yaml
indexing:
  enable_parallel: false  # Cambiar temporalmente
```

## 💡 Tips de Optimización

1. **CPU-bound**: Si tienes muchos cores, aumenta `concurrent_workers`
2. **GPU-bound**: Si embeddings es lento, reduce `embeddings_semaphore`
3. **Memory-bound**: Reduce `worker_batch_size` y `concurrent_workers`
4. **I/O-bound**: Aumenta `worker_batch_size` para procesar más por batch

## 🐛 Reporte de Problemas

Si encuentras problemas con la paralelización:
1. Desactiva con `enable_parallel: false`
2. Captura logs con `acolyte logs`
3. Incluye tu configuración de hardware
4. Reporta en GitHub Issues

---

**Recuerda**: La paralelización es una optimización. Si funciona bien en modo secuencial, no es obligatorio activarla.
