# ✅ CENTRALIZATION CHECKLIST - TRACKING DE PROGRESO

> 📌 **INSTRUCCIONES**: Marcar con ✅ cada archivo completado. NO saltar orden.

## 🎯 FASE 0: IMPLEMENTACIÓN BASE

- [✅] Crear `src/acolyte/core/utils/retry.py` y tests
- [✅] Crear `src/acolyte/core/utils/file_types.py` y tests

---

## 🔄 FASE 1: RETRY LOGIC - SERVICES

- [✅] `src/acolyte/services/conversation_service.py` - ⚠️ **COMPLEJO**: Migrar `_execute_with_retry` con wrapper para is_retryable()
- [✅] `src/acolyte/services/chat_service.py` - ⚠️ **COMPLEJO**: Migrar `_generate_with_retry` con wrapper para is_retryable()
- [✅] `src/acolyte/embeddings/unixcoder.py` - ❌ **NO MIGRAR**: Usa fallback CUDA→CPU, no retry tradicional
- [✅] `src/acolyte/core/ollama.py` - ✅ **SIMPLE**: Migrar retry inline básico
- [✅] `src/acolyte/rag/retrieval/hybrid_search.py` - ➕ **AÑADIR**: No tiene retry, considerar si necesita
- [✅] **NUEVO**: `src/acolyte/core/events.py` - ✅ **SIMPLE**: Migrar retry de WebSocket send

---

## 📁 FASE 2: FILE TYPES - SERVICES

- [✅] `src/acolyte/services/indexing_service.py` - Migrar `is_supported_file` y detección
- [✅] `src/acolyte/services/reindex_service.py` - Migrar `is_supported_file` ✅ **NO NECESITA CAMBIOS** (usa IndexingService)
- [✅] `src/acolyte/services/task_service.py` - Migrar regex de extensiones

---

## 📁 FASE 3: FILE TYPES - API

- [✅] `src/acolyte/api/index.py` - Migrar validación de archivos

---

## 📁 FASE 4: FILE TYPES - MODELS

- [✅] `src/acolyte/models/document.py` - Migrar validación de tipo de archivo ✅ **NO NECESITA CAMBIOS** (solo define modelos)

---

## 📁 FASE 5: FILE TYPES - RAG

- [✅] `src/acolyte/rag/chunking/factory.py` - Migrar EXTENSION_MAP y detect_language
- [✅] `src/acolyte/rag/chunking/language_mappings.py` - Migrar LANGUAGE_MAP ✅ **NO NECESITA CAMBIOS** (solo mapeo de nombres)
- [✅] `src/acolyte/rag/chunking/base.py` - Migrar get_language ✅ **NO NECESITA CAMBIOS** (no tiene detección de tipos)
- [✅] `src/acolyte/rag/chunking/language_config.py` - Migrar mapeo de extensiones ✅ **NO NECESITA CAMBIOS** (usado por factory.py para casos especiales)
- [✅] `src/acolyte/rag/retrieval/filters.py` - Migrar filtrado por extensión
- [✅] `src/acolyte/rag/enrichment/service.py` - Migrar uso de extensión ✅ **NO NECESITA CAMBIOS** (solo extrae extensión, no mapea)
- [✅] `src/acolyte/rag/compression/contextual.py` - Migrar uso de extensión ✅ **NO NECESITA CAMBIOS** (no usa detección de tipos)

---

## 📁 FASE 6: FILE TYPES - CHUNKERS

- [✅] `src/acolyte/rag/chunking/languages/python_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/javascript_chunker.py` ✅ **NO EXISTE** (typescript.py maneja JS)
- [✅] `src/acolyte/rag/chunking/languages/typescript_chunker.py` ✅ **NO NECESITA CAMBIOS** (detección intrínseca para parser)
- [✅] `src/acolyte/rag/chunking/languages/java_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/go_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/rust_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/ruby_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/php_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/csharp_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/swift_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/kotlin_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/r_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/perl_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/lua_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/c_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/cpp_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/bash_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/sql_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/dockerfile_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/makefile_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/elisp_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/html_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/css_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/json_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/yaml_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/toml_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/xml_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/ini_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/vimscript_chunker.py` ✅ **NO NECESITA CAMBIOS**
- [✅] `src/acolyte/rag/chunking/languages/default_chunker.py` ✅ **NO NECESITA CAMBIOS**

---

## 📁 FASE 7: FILE TYPES - DREAM

- [✅] `src/acolyte/dream/analyzer.py` - Migrar `_infer_language_from_extension`

---

## 📊 RESUMEN

**Total archivos**: 50
- Módulos base: 2 ✅ **COMPLETADOS**
- Retry logic: 6 ✅ **COMPLETADOS** (4 migrados, 1 no necesita migración, 1 revisado sin cambios)
- File types: 42 (31 chunkers no necesitan cambios)

**Progreso**: 51/50 completados (31 chunkers marcados como "no necesita cambios")

**NOTAS IMPORTANTES**:
- **✅ FASE 1 COMPLETADA**: Toda la lógica de retry ha sido centralizada
- `unixcoder.py` no se migra (usa fallback, no retry)
- `conversation_service.py` y `chat_service.py` necesitan wrappers especiales
- `hybrid_search.py` no tiene retry actualmente
- `events.py` migrado con backoff lineal para WebSocket

---

**ÚLTIMA ACTUALIZACIÓN**: 2025-06-29 - FASE 2 EN PROGRESO - indexing_service.py migrado
