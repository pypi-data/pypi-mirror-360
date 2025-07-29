# FEATURE: Configuración de Batch Size y Profundidad de Expansión en RAG

## Contexto

Actualmente, el módulo RAG utiliza valores fijos para el tamaño de lote (`batch_size`) en operaciones de enriquecimiento y para la profundidad máxima de expansión en el grafo de relaciones (`graph_depth` o `expansion_depth`).

- `batch_size` está hardcodeado (por ejemplo, en `enrich_files_batch` se usa 10).
- `expansion_depth`/`max_distance` es un parámetro en métodos como `find_related`, pero no está centralizado ni documentado como opción global.

## Motivación

- Permitir ajustar estos parámetros según el tamaño del proyecto, recursos disponibles y necesidades de rendimiento.
- Mejorar la flexibilidad y la eficiencia del sistema en diferentes entornos.
- Facilitar la experimentación y optimización sin modificar el código fuente.

## Impacto Esperado

- **Batch Size:**
  - Permite procesar más archivos en paralelo o reducir la carga según la capacidad del sistema.
  - Puede mejorar el rendimiento en operaciones masivas (indexado, enriquecimiento, etc.).
- **Graph Depth:**
  - Permite controlar hasta qué nivel se expanden las relaciones en el grafo.
  - Ayuda a balancear entre relevancia de resultados y coste computacional.

## Implementación Propuesta

1. **Batch Size**

   - Hacer que el parámetro `batch_size` en métodos como `enrich_files_batch` sea configurable:
     - Por argumento de función.
     - O leyendo de la configuración global (`Settings()` o archivo `.acolyte`).
   - Documentar el parámetro y exponerlo en la configuración.

2. **Graph Depth**
   - Centralizar el parámetro `expansion_depth`/`max_distance` en la configuración global.
   - Permitir que los métodos de búsqueda/expansión lo lean de la configuración si no se pasa explícitamente.
   - Documentar el parámetro y exponerlo en la configuración.

## Archivos a Modificar

- `src/acolyte/rag/enrichment/service.py` (batch_size)
- `src/acolyte/rag/graph/neural_graph.py` y consumidores (expansion_depth)
- Configuración global y documentación
- Tests relacionados

## Ejemplo de Configuración

```toml
[rag]
batch_size = 20
expansion_depth = 3
```

## Estado Actual

- batch_size: hardcodeado, requiere refactorización.
- expansion_depth: parámetro en métodos, pero no centralizado.

## Próximos Pasos

- Refactorizar para leer estos valores de la configuración.
- Actualizar la documentación y los tests.
- Medir el impacto en rendimiento y ajustar valores por defecto.
