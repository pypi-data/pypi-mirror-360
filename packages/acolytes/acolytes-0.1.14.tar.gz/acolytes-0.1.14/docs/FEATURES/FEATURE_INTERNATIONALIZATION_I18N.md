# 🌍 Internacionalización (i18n) para ACOLYTE

## 📋 ¿Qué es?

La internacionalización (i18n) es el proceso de diseñar software para que pueda adaptarse fácilmente a diferentes idiomas y regiones sin cambios en el código. Para ACOLYTE, significa:

### Elementos a internacionalizar:
1. **Mensajes de error**: "File not found" → "Archivo no encontrado"
2. **Respuestas al usuario**: "Optimization complete" → "Optimización completa"
3. **Logs visibles**: "Processing file..." → "Procesando archivo..."
4. **Interfaz de usuario**: Botones, menús, tooltips del futuro dashboard
5. **Prompts del sistema**: Instrucciones que ACOLYTE da al modelo

### Lo que NO se internacionaliza:
- Comentarios en el código (permanecen en inglés)
- Nombres de variables/funciones
- Logs de debugging para desarrolladores
- Documentación técnica interna

## 🎯 ¿Para qué vale?

### Beneficios directos:

1. **Accesibilidad global**
   - Desarrolladores no angloparlantes pueden usar ACOLYTE
   - Reduce barrera de entrada en mercados internacionales
   - Cumple con requisitos de empresas multilingües

2. **Mejor UX para usuarios locales**
   - Mensajes de error en idioma nativo son más claros
   - Reduce confusión y frustración
   - Aumenta productividad

3. **Preparación para el futuro**
   - Añadir idiomas se vuelve trivial
   - No requiere tocar código fuente
   - Comunidad puede contribuir traducciones

### Casos de uso específicos:

- **Empresa española** usa ACOLYTE: todos los mensajes en español
- **Equipo multicultural**: cada desarrollador ve mensajes en su idioma
- **Documentación localizada**: ejemplos y errores en idioma local
- **Soporte corporativo**: grandes empresas requieren software multilingüe

## 💡 ¿Por qué es óptimo?

### 1. **Momento perfecto para implementar**
- Proyecto aún manejable (~20k líneas)
- Strings identificados durante auditoría
- Antes de que se acumule más deuda técnica
- Dashboard web puede ser multilingüe desde el inicio

### 2. **ROI a largo plazo**
```python
# SIN i18n: Cambiar un mensaje = buscar en todo el código
raise ValueError("Cannot process empty file")

# CON i18n: Cambiar/traducir = editar archivo de traducciones
raise ValueError(tr("errors.empty_file"))
```

### 3. **Separación de concerns**
- Lógica de negocio separada de textos
- Traductores no necesitan ser programadores
- Desarrollo y traducción en paralelo

### 4. **Estándares establecidos**
- Patrones i18n bien documentados
- Herramientas maduras disponibles
- Mejores prácticas conocidas

## 🏗️ ¿Cómo debería ser?

### Arquitectura propuesta:

```
src/acolyte/
├── i18n/
│   ├── __init__.py
│   ├── translator.py      # Core translation logic
│   ├── locales/
│   │   ├── en/           # English (default)
│   │   │   ├── common.json
│   │   │   ├── errors.json
│   │   │   └── services.json
│   │   ├── es/           # Spanish
│   │   │   ├── common.json
│   │   │   ├── errors.json
│   │   │   └── services.json
│   │   └── ...           # Other languages
│   └── utils.py          # Helper functions
```

### 1. **Sistema de traducción** (`translator.py`)

```python
import json
from pathlib import Path
from typing import Dict, Optional, Any
from functools import lru_cache

class Translator:
    """
    Simple but effective translation system for ACOLYTE.
    
    Design principles:
    - Zero dependencies (no babel, gettext, etc.)
    - JSON-based for simplicity
    - Lazy loading of translations
    - Fallback to English
    """
    
    def __init__(self, locale: str = "en"):
        self.locale = locale
        self.fallback_locale = "en"
        self._translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files for current locale."""
        locale_dir = Path(__file__).parent / "locales" / self.locale
        fallback_dir = Path(__file__).parent / "locales" / self.fallback_locale
        
        # Load all JSON files in locale directory
        for json_file in locale_dir.glob("*.json"):
            namespace = json_file.stem
            with open(json_file, "r", encoding="utf-8") as f:
                self._translations[namespace] = json.load(f)
        
        # Load fallback translations
        if self.locale != self.fallback_locale:
            self._fallback_translations = {}
            for json_file in fallback_dir.glob("*.json"):
                namespace = json_file.stem
                with open(json_file, "r", encoding="utf-8") as f:
                    self._fallback_translations[namespace] = json.load(f)
    
    def translate(
        self, 
        key: str, 
        **params: Any
    ) -> str:
        """
        Translate a key with optional parameters.
        
        Args:
            key: Translation key (e.g., "errors.file_not_found")
            **params: Parameters for interpolation
            
        Returns:
            Translated string
        """
        # Split key into namespace and path
        parts = key.split(".")
        if len(parts) < 2:
            return key  # Invalid key format
        
        namespace = parts[0]
        path = ".".join(parts[1:])
        
        # Try to get translation
        translation = self._get_nested_value(
            self._translations.get(namespace, {}),
            path
        )
        
        # Fallback to English if not found
        if translation is None and hasattr(self, '_fallback_translations'):
            translation = self._get_nested_value(
                self._fallback_translations.get(namespace, {}),
                path
            )
        
        # If still not found, return key
        if translation is None:
            return key
        
        # Interpolate parameters
        if params:
            try:
                return translation.format(**params)
            except KeyError:
                # Missing parameter, return translation as-is
                return translation
        
        return translation
    
    def _get_nested_value(self, data: Dict, path: str) -> Optional[str]:
        """Get value from nested dict using dot notation."""
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value if isinstance(value, str) else None

# Global translator instance
_translator: Optional[Translator] = None

def init_translator(locale: str = "en"):
    """Initialize the global translator."""
    global _translator
    _translator = Translator(locale)

def tr(key: str, **params: Any) -> str:
    """
    Convenience function for translation.
    
    Usage:
        tr("errors.file_not_found", filename="test.py")
    """
    if _translator is None:
        init_translator()
    return _translator.translate(key, **params)
```

### 2. **Archivos de traducción**

**`locales/en/errors.json`**:
```json
{
  "file_not_found": "File not found: {filename}",
  "database_locked": "Database is temporarily locked. Please try again.",
  "invalid_configuration": "Invalid configuration in .acolyte file",
  "indexing_failed": "Failed to index {count} files",
  "connection_error": "Cannot connect to {service}",
  "permission_denied": "Permission denied for {path}",
  "empty_file": "Cannot process empty file",
  "file_too_large": "File {filename} is too large ({size_mb}MB, limit: {limit_mb}MB)"
}
```

**`locales/es/errors.json`**:
```json
{
  "file_not_found": "Archivo no encontrado: {filename}",
  "database_locked": "Base de datos temporalmente bloqueada. Por favor, intente de nuevo.",
  "invalid_configuration": "Configuración inválida en archivo .acolyte",
  "indexing_failed": "Fallo al indexar {count} archivos",
  "connection_error": "No se puede conectar a {service}",
  "permission_denied": "Permiso denegado para {path}",
  "empty_file": "No se puede procesar archivo vacío",
  "file_too_large": "El archivo {filename} es demasiado grande ({size_mb}MB, límite: {limit_mb}MB)"
}
```

**`locales/en/services.json`**:
```json
{
  "indexing": {
    "starting": "Starting indexing of {count} files",
    "progress": "Processing: {current}/{total} - {filename}",
    "completed": "Indexing completed: {count} files processed in {duration}s",
    "skipped": "Skipped {count} files (unsupported or ignored)"
  },
  "chat": {
    "new_session": "New conversation started",
    "loading_context": "Loading conversation context...",
    "generating_response": "Generating response...",
    "error_generating": "Failed to generate response. Please try again."
  },
  "dream": {
    "analysis_started": "Deep analysis started",
    "patterns_found": "Found {count} optimization patterns",
    "fatigue_high": "Code fatigue is high ({level}/10). Consider running optimization.",
    "optimization_complete": "Optimization complete. {insights} insights generated."
  }
}
```

### 3. **Integración con código existente**

**ANTES**:
```python
# En conversation_service.py
raise NotFoundError(f"Session {session_id} not found")

# En indexing_service.py
logger.info(f"Starting indexing of {len(files)} files")

# En dream/fatigue_monitor.py
return "Code quality is declining. Optimization recommended."
```

**DESPUÉS**:
```python
# En conversation_service.py
from acolyte.i18n import tr
raise NotFoundError(tr("errors.session_not_found", session_id=session_id))

# En indexing_service.py
logger.info(tr("services.indexing.starting", count=len(files)))

# En dream/fatigue_monitor.py
return tr("services.dream.fatigue_high", level=self.fatigue_level)
```

### 4. **Configuración del idioma**

**En `.acolyte`**:
```yaml
version: "1.0"
project:
  name: "mi-proyecto"
  locale: "es"  # Spanish interface

# O detección automática
# locale: "auto"  # Uses system locale
```

**Detección automática**:
```python
import locale
import os

def detect_user_locale() -> str:
    """Detect user's preferred locale."""
    # 1. Check ACOLYTE_LOCALE env var
    if env_locale := os.getenv("ACOLYTE_LOCALE"):
        return env_locale
    
    # 2. Check .acolyte config
    config = Settings()
    if config_locale := config.get("project.locale"):
        return config_locale
    
    # 3. Use system locale
    system_locale = locale.getdefaultlocale()[0]
    if system_locale:
        # Convert "es_ES" to "es"
        return system_locale.split("_")[0]
    
    # 4. Default to English
    return "en"
```

### 5. **Proceso de traducción**

1. **Extracción de strings**:
```bash
# Script para encontrar strings a traducir
python scripts/extract_i18n_strings.py

# Output: Lista de todos los strings marcados como i18n en la auditoría
```

2. **Generación de archivos base**:
```bash
# Crear estructura de archivos JSON
python scripts/generate_i18n_templates.py
```

3. **Traducción**:
- Contratar traductor profesional O
- Usar comunidad para traducciones O
- Empezar con traducción automática y refinar

4. **Validación**:
```bash
# Verificar que todas las keys existen
python scripts/validate_i18n.py

# Verificar parámetros de interpolación
python scripts/check_i18n_params.py
```

### 6. **Mejores prácticas**

1. **Keys semánticas**:
```python
# MAL
tr("error_1")  # ¿Qué error?

# BIEN
tr("errors.file_not_found")  # Claro y específico
```

2. **Evitar concatenación**:
```python
# MAL
message = tr("processing") + " " + filename

# BIEN
message = tr("messages.processing_file", filename=filename)
```

3. **Pluralización**:
```python
# Soporte básico para plurales
def tr_plural(key: str, count: int, **params) -> str:
    if count == 1:
        return tr(f"{key}_one", count=count, **params)
    else:
        return tr(f"{key}_many", count=count, **params)

# Uso
tr_plural("files_processed", count=5)
# EN: "5 files processed"
# ES: "5 archivos procesados"
```

### 7. **Testing**

```python
# tests/test_i18n.py
def test_translations_complete():
    """Verify all languages have all keys."""
    en_keys = get_all_keys("en")
    
    for locale in ["es", "fr", "de"]:
        locale_keys = get_all_keys(locale)
        missing = en_keys - locale_keys
        assert not missing, f"Missing keys in {locale}: {missing}"

def test_parameter_consistency():
    """Verify parameters match across translations."""
    key = "errors.file_not_found"
    en_params = extract_params(get_translation("en", key))
    es_params = extract_params(get_translation("es", key))
    
    assert en_params == es_params
```

## 📁 Archivos a Internacionalizar

Según la auditoría de alineación, estos son los archivos específicos que requieren i18n:

### 🔴 Prioridad Alta - Mensajes de Usuario Final

#### **API Module** (Mayor impacto en UX)
- `api/__init__.py` - Errores de validación e internos
- `api/dream.py` - Mensajes de advertencia, validación y usuario
- `api/health.py` - **14+ mensajes** de error, sugerencias y advertencias
- `api/index.py` - **10 mensajes** de error/skip
- `api/openai.py` - **17 mensajes** de error para usuarios
- `api/websockets/progress.py` - **8 mensajes** de WebSocket

#### **Services Module** (Lógica de negocio)
- `services/chat_service.py` - Mensajes de error, "New conversation"
- `services/conversation_service.py` - NotFoundError, DatabaseError
- `services/git_service.py` - Notificaciones en español (!)
- `services/indexing_service.py` - Mensajes de error
- `services/task_service.py` - Errores y resumen ejecutivo

#### **Dream Module** (Sistema de optimización)
- `dream/analyzer.py` - "Exploration failed", "Deep analysis failed"
- `dream/fatigue_monitor.py` - Descripciones de FatigueLevel, mensajes de trigger
- `dream/state_manager.py` - 2 mensajes de error

### 🟡 Prioridad Media - Errores y Validaciones

#### **Core Module**
- `core/chunking_config.py` - Mensajes de error de validación
- `core/exceptions.py` - Mensajes de error y sugerencias
- `core/secure_config.py` - Mensajes de error
- `core/token_counter.py` - ValueError, NotImplementedError

#### **Models Module**
- `models/conversation.py` - Errores de validación
- `models/document.py` - Errores de validación
- `models/dream.py` - Mensajes de get_recommendation()

#### **Semantic Module**
- `semantic/decision_detector.py` - "Technical decision marked", etc.
- `semantic/prompt_builder.py` - "CONTEXTO ACTUAL", "Sesión", etc.
- `semantic/summarizer.py` - "provided suggestions", "User:", etc.

### 🟢 Prioridad Baja - Logs y Mensajes Técnicos

#### **RAG Modules**
- `rag/chunking/adaptive.py` - 5 mensajes de log
- `rag/chunking/base.py` - 9 mensajes de log
- `rag/chunking/factory.py` - Error de usuario
- `rag/collections/manager.py` - Mensajes de error
- `rag/enrichment/service.py` - Mensajes de error de usuario
- `rag/graph/pattern_detector.py` - 4 strings de recomendación
- `rag/retrieval/metrics.py` - 6 mensajes de logging

#### **Embeddings Module**
- `embeddings/context.py` - Errores de validación
- `embeddings/unixcoder.py` - Mensajes de error

### 📊 Resumen de Strings a Traducir

| Módulo | Archivos | Strings Estimados | Prioridad |
|--------|----------|-------------------|------------|
| API | 6 | ~60-70 | Alta |
| Services | 5 | ~30-40 | Alta |
| Dream | 3 | ~15-20 | Alta |
| Core | 4 | ~20-25 | Media |
| Models | 3 | ~10-15 | Media |
| Semantic | 3 | ~15-20 | Media |
| RAG | 7 | ~30-35 | Baja |
| Embeddings | 2 | ~5-10 | Baja |
| **TOTAL** | **35** | **~200-250** | - |

### 🔧 Proceso de Implementación por Módulo

1. **Comenzar por API Module**
   - Mayor impacto visible
   - Mensajes más claros y directos
   - ~60-70 strings concentrados

2. **Continuar con Services**
   - Lógica de negocio crítica
   - Mensajes de error importantes
   - Git service ya tiene español (!)

3. **Dream y Core juntos**
   - Sistema central del proyecto
   - Excepciones y configuración

4. **Finalizar con RAG/Embeddings**
   - Principalmente logs técnicos
   - Menor impacto en UX

### 💡 Notas Especiales

- **git_service.py** ya tiene mensajes en español que necesitan moverse a i18n
- **health.py** tiene la mayor concentración de mensajes (14+)
- **openai.py** tiene 17 mensajes de error críticos para compatibilidad
- Muchos archivos RAG solo tienen logs de debug (prioridad baja)

## 🚀 Prioridad y Esfuerzo

**Prioridad**: Media
- No crítico para funcionamiento
- Pero importante para adopción global
- Mejor hacerlo antes de v1.0

**Esfuerzo estimado**:
- Sistema i18n básico: 2 días
- Migrar strings existentes: 3-4 días
- Primera traducción (español): 2 días
- Tests y documentación: 1 día

**Total**: ~1 semana para sistema completo

**ROI**: Alto a largo plazo
- Abre mercados internacionales
- Facilita contribuciones de la comunidad
- Mejora profesionalismo del proyecto