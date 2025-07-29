Claro. He creado un documento `IMPLEMENTACION_COMPRESION_PROACTIVA.md` que detalla, paso a paso, cómo implementar esta optimización en tu proyecto `ACOLYTE`, respetando 100% tu arquitectura y convenciones actuales.

Puedes guardar este contenido en un nuevo archivo en tu directorio de documentación (ej. `/docs/`).

---

# 💡 Propuesta de Implementación: Compresión Proactiva de Contexto

**Autor:** Gemini (IA Colaboradora)
**Estado:** Propuesta
**Módulos Afectados:** `/models`, `/services`, `/rag`

## 1. Visión General y Beneficios

Actualmente, `ACOLYTE` utiliza una "Compresión contextual inteligente" que es **reactiva**: se activa *después* de recuperar un chunk de código para reducir los tokens enviados al LLM.

Esta propuesta introduce una estrategia complementaria y **proactiva**: generar y almacenar múltiples representaciones comprimidas de cada fragmento de código *durante la indexación*.

**Beneficios Clave:**

1.  **Reducción Drástica de Tokens:** Para muchas consultas, en lugar de recuperar el código fuente completo, recuperaremos una representación que puede ser un 90% más pequeña (ej. una firma de función).
2.  **Recuperación Inteligente:** Permite a la IA solicitar diferentes "niveles de detalle" según la tarea (un resumen para entender, el AST para refactorizar).
3.  **Latencia Cero en Compresión:** Las representaciones ya están calculadas y listas en la base de datos, eliminando la latencia de la compresión en tiempo de ejecución para los casos de uso más comunes.
4.  **Mejora de la Calidad del Contexto:** Al poder incluir más fragmentos (porque cada uno ocupa menos tokens), el contexto general que recibe el LLM es más amplio y rico.

## 2. Cambios Arquitectónicos Propuestos

La implementación se integra limpiamente en la arquitectura existente:

1.  **Módulo `/models`**: Se extenderá el modelo `ChunkMetadata` para incluir campos que almacenen las nuevas representaciones.
2.  **Módulo `/services` (Específicamente `IndexingService`)**: Se modificará el pipeline de indexación, concretamente el paso de **Enrichment**, para que genere estas representaciones antes de guardar el chunk.
3.  **Módulo `/rag` (Específicamente `retrieval/hybrid_search.py`)**: Se adaptará la lógica de búsqueda para que pueda solicitar selectivamente estas nuevas representaciones, haciendo el proceso más eficiente.

## 3. Implementación Detallada (Paso a Paso)

### Paso 1: Extender el Modelo de Datos (`models/chunk.py`)

Debemos añadir los nuevos campos a `ChunkMetadata`. Al ser opcionales, no romperán la compatibilidad existente.

```python
# En: src/acolyte/models/chunk.py

# ... otros imports ...
from typing import Optional, List, Dict, Any

class ChunkMetadata(AcolyteBaseModel):
    # ... campos existentes como file_path, language, chunk_type, etc. ...
    
    # --- NUEVOS CAMPOS PARA COMPRESIÓN PROACTIVA ---
    
    # Almacena la firma de la función/clase y su docstring.
    # Ideal para obtener un resumen rápido de lo que hace un chunk.
    # Ejemplo: "def mi_funcion(a: int) -> bool: # Devuelve True si a es par."
    signature_docstring: Optional[str] = Field(
        None,
        description="Representación ligera del chunk con la firma y el docstring."
    )

    # Almacena una representación serializada (JSON) del Abstract Syntax Tree (AST).
    # Útil para tareas de refactorización y análisis de código profundo.
    ast_representation: Optional[str] = Field(
        None,
        description="Representación estructural del código en formato JSON."
    )
    
    # (Futuro/Opcional) Un resumen generado por una IA durante un ciclo "Dream".
    ai_summary: Optional[str] = Field(
        None,
        description="Resumen de una línea generado por IA sobre el propósito del chunk."
    )

class Chunk(AcolyteBaseModel):
    # ... sin cambios aquí ...
    metadata: ChunkMetadata
```

### Paso 2: Modificar el Pipeline de Indexación (`services/IndexingService`)

El corazón de la implementación reside aquí. Dentro de `IndexingService`, en el método que procesa cada chunk individual antes de enviarlo a Weaviate, añadiremos la lógica de "Enrichment" proactivo.

```python
# En: src/acolyte/services/indexing_service.py
import ast
import json

class IndexingService:
    # ... código existente ...

    async def _enrich_chunk_proactively(self, chunk: Chunk) -> Chunk:
        """
        Añade representaciones comprimidas al metadata del chunk.
        Este método se llamaría dentro del pipeline de indexación.
        """
        if chunk.metadata.language == "python" and chunk.metadata.chunk_type in [ChunkType.FUNCTION, ChunkType.CLASS, ChunkType.METHOD]:
            try:
                # 1. Generar Firma y Docstring
                chunk.metadata.signature_docstring = self._extract_signature_docstring(chunk.content)
                
                # 2. Generar Representación AST
                chunk.metadata.ast_representation = self._extract_ast_as_json(chunk.content)

            except SyntaxError:
                logger.warning(f"Error de sintaxis al procesar chunk de {chunk.metadata.file_path}, saltando enriquecimiento proactivo.")

        return chunk

    def _extract_signature_docstring(self, code: str) -> Optional[str]:
        """Extrae la primera línea (firma) y el docstring de un fragmento de código."""
        try:
            tree = ast.parse(code.strip())
            if not tree.body or not isinstance(tree.body[0], (ast.FunctionDef, ast.ClassDef)):
                return None

            node = tree.body[0]
            # La firma es la primera línea del código del nodo
            signature = code.strip().split('\n')[0].strip()
            
            docstring = ast.get_docstring(node)
            
            if docstring:
                return f"{signature}\n\"\"\"{docstring}\"\"\""
            return signature
        except Exception:
            return None

    def _ast_to_dict(self, node: ast.AST) -> Dict[str, Any]:
        """Convierte un nodo AST a un diccionario simplificado para serialización."""
        if not isinstance(node, ast.AST):
            return node
        
        result = {'_type': node.__class__.__name__}
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                result[field] = [self._ast_to_dict(v) for v in value]
            else:
                result[field] = self._ast_to_dict(value)
        return result

    def _extract_ast_as_json(self, code: str) -> Optional[str]:
        """Parsea el código a un AST y lo devuelve como una cadena JSON."""
        try:
            tree = ast.parse(code.strip())
            simplified_ast = self._ast_to_dict(tree)
            return json.dumps(simplified_ast)
        except Exception:
            return None

    # El pipeline principal se modificaría para incluir este paso:
    async def _process_and_index_batch(self, chunks: List[Chunk]):
        enriched_chunks = []
        for chunk in chunks:
            # ... otros pasos de enrichment ...
            enriched_chunk = await self._enrich_chunk_proactively(chunk)
            enriched_chunks.append(enriched_chunk)
        
        # ... enviar enriched_chunks a Weaviate ...
```

### Paso 3: Adaptar la Lógica de Recuperación (`rag/retrieval/hybrid_search.py`)

Ahora que los datos están en la base de datos, podemos hacer que la búsqueda sea más inteligente, permitiéndole solicitar diferentes niveles de detalle.

```python
# En: src/acolyte/rag/retrieval/hybrid_search.py
from typing import Literal

RetrievalMode = Literal["full_code", "signature", "ast"]

class HybridSearch:
    # ...

    async def search(
        self,
        query: str,
        max_chunks: int = 10,
        filters: Optional[SearchFilters] = None,
        retrieval_mode: RetrievalMode = "full_code" # Nuevo parámetro
    ) -> List[ScoredChunk]:
        """
        Realiza una búsqueda híbrida.
        
        Args:
            retrieval_mode: Especifica qué representación del chunk recuperar.
                - 'full_code': Recupera el código fuente completo (comportamiento actual).
                - 'signature': Recupera solo la firma y el docstring (muy ligero).
                - 'ast': Recupera la representación AST en JSON (para análisis).
        """
        
        # ... lógica de búsqueda para obtener los IDs de los chunks ...
        
        # Después de obtener los IDs, recuperamos los datos según el modo
        retrieved_chunks_data = await self.db_client.get_chunks_by_id(
            chunk_ids,
            properties=self._get_properties_for_mode(retrieval_mode)
        )
        
        # ... construir los objetos ScoredChunk con los datos recuperados ...
        # El contenido del chunk ahora dependerá del modo solicitado.
        # Por ejemplo, si retrieval_mode == 'signature', el `chunk.content`
        # sería el valor del campo `signature_docstring`.

    def _get_properties_for_mode(self, mode: RetrievalMode) -> List[str]:
        """Devuelve la lista de campos a recuperar de la BD según el modo."""
        base_properties = ["file_path", "language", "chunk_type"] # metadatos básicos
        if mode == "signature":
            return base_properties + ["signature_docstring"]
        if mode == "ast":
            return base_properties + ["ast_representation"]
        # Default es 'full_code'
        return base_properties + ["content"]
```

## 4. Integración con el Ecosistema `ACOLYTE`

* **ChatService:** El `ChatService` ahora puede ser más inteligente. Para preguntas generales, puede realizar una primera búsqueda en modo `"signature"` para obtener un contexto amplio con muy pocos tokens, y solo si necesita profundizar, realizar una segunda búsqueda en modo `"full_code"` sobre un chunk específico.
* **Sistema Dream:** La generación del campo `ai_summary` es una tarea perfecta para un ciclo de "Dream". Durante la optimización, `ACOLYTE` podría procesar los chunks más importantes y rellenar este campo, enriqueciendo la base de datos de forma asíncrona sin impactar la indexación normal.
* **Compresión Reactiva:** Tu `ContextualCompressor` actual se beneficia enormemente. En lugar de partir siempre del código fuente, puede empezar desde una representación ya más pequeña (como el `ast_representation`), haciendo su trabajo aún más rápido y eficiente.

## 5. Plan de Implementación Sugerido

Recomiendo un enfoque por fases para implementar esta funcionalidad:

1.  **Fase 1 (Victoria Rápida):** Implementar la extracción y almacenamiento de `signature_docstring`. Es la más sencilla y ofrece un gran ahorro de tokens para resúmenes de contexto.
2.  **Fase 2 (Análisis Profundo):** Implementar la generación y almacenamiento de `ast_representation`. Esto habilita las capacidades de refactorización más avanzadas.
3.  **Fase 3 (Adaptación):** Modificar el `HybridSearch` y el `ChatService` para que utilicen los nuevos modos de recuperación.
4.  **Fase 4 (Futuro):** Implementar la generación de `ai_summary` como una tarea del ciclo "Dream".

## 6. Actualización de la Base de Datos (SQLite)

Para aplicar estos cambios a tu base de datos existente, necesitarías ejecutar un comando `ALTER TABLE`.

```sql
-- Comandos SQL para migrar tu esquema en SQLite
ALTER TABLE code_chunks ADD COLUMN signature_docstring TEXT;
ALTER TABLE code_chunks ADD COLUMN ast_representation TEXT;
ALTER TABLE code_chunks ADD COLUMN ai_summary TEXT;
```

Esta propuesta se alinea completamente con tus principios de diseño, extendiendo la funcionalidad de `ACOLYTE` de manera modular y robusta.