# 📁 File Type Detection Centralization

## 📋 Problema Actual

La detección de tipos de archivo y mapeo de extensiones está duplicada en:

- `indexing_service.py` - Lista de extensiones soportadas
- `chunking/factory.py` - Mapeo extensión → lenguaje
- `git_service.py` - Filtrado de archivos
- Varios chunkers - Detección de tipo de archivo

Cada lugar tiene listas ligeramente diferentes:
- Algunos soportan `.tsx`, otros no
- Diferentes nombres para el mismo lenguaje
- Sin lugar central para añadir nuevas extensiones

## 🎯 Solución Propuesta

### Ubicación: `src/acolyte/core/utils/file_types.py`

```python
from pathlib import Path
from typing import Set, Dict, Optional
from enum import Enum

class FileCategory(Enum):
    CODE = "code"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    DATA = "data"
    OTHER = "other"

class FileTypeDetector:
    """Centralized file type detection and classification."""
    
    # Master mapping of extensions to languages
    LANGUAGE_MAP: Dict[str, str] = {
        ".py": "python",
        ".js": "javascript", 
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".r": "r",
        ".m": "objective-c",
        ".mm": "objective-cpp",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
    }
    
    # Category mappings
    CATEGORY_MAP: Dict[FileCategory, Set[str]] = {
        FileCategory.CODE: {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
            ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
            ".kt", ".scala", ".r", ".m", ".mm", ".sh", ".bash", ".zsh"
        },
        FileCategory.DOCUMENTATION: {
            ".md", ".rst", ".txt", ".adoc"
        },
        FileCategory.CONFIGURATION: {
            ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", 
            ".env", ".properties", ".xml"
        },
        FileCategory.DATA: {
            ".csv", ".sql"
        }
    }
    
    @classmethod
    def get_language(cls, path: Path) -> str:
        """Get programming language for a file."""
        return cls.LANGUAGE_MAP.get(path.suffix.lower(), "unknown")
    
    @classmethod
    def get_category(cls, path: Path) -> FileCategory:
        """Get category for a file."""
        suffix = path.suffix.lower()
        
        for category, extensions in cls.CATEGORY_MAP.items():
            if suffix in extensions:
                return category
        
        return FileCategory.OTHER
    
    @classmethod
    def is_supported(cls, path: Path) -> bool:
        """Check if file type is supported for indexing."""
        return cls.get_category(path) != FileCategory.OTHER
    
    @classmethod
    def get_all_supported_extensions(cls) -> Set[str]:
        """Get all supported file extensions."""
        all_extensions = set()
        for extensions in cls.CATEGORY_MAP.values():
            all_extensions.update(extensions)
        return all_extensions
```

## 📍 Dónde se usa actualmente

### 1. **indexing_service.py** (~línea 300)
```python
def _is_supported_file(self, path: Path) -> bool:
    # Listas hardcodeadas de extensiones
    code_extensions = {".py", ".js", ".ts", ...}
    doc_extensions = {".md", ".rst", ...}
    # etc.
```

### 2. **chunking/factory.py** (~línea 50)
```python
LANGUAGE_MAPPING = {
    ".py": PythonChunker,
    ".js": JavaScriptChunker,
    # etc.
}
```

### 3. **git_service.py**
```python
# Filtrado de archivos para ignorar binarios
```

### 4. **chunking/language_mappings.py**
```python
# Otro mapeo duplicado de extensiones
```

## 💡 Beneficios

1. **Fuente única de verdad**: Una lista de extensiones soportadas
2. **Fácil añadir soporte**: Nuevo lenguaje = 1 línea en 1 archivo
3. **Categorización consistente**: Mismo comportamiento en todo el sistema
4. **Validación centralizada**: `is_supported()` usado por todos
5. **Preparado para Turso**: Fácil añadir metadata específica

## 🔨 Ejemplos de Migración

### Ejemplo 1: indexing_service.py
```python
# ANTES (~línea 300)
def _is_supported_file(self, path: Path) -> bool:
    code_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
                      ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
                      ".kt", ".scala", ".r", ".m", ".mm", ".sh", ".bash", ".zsh"}
    doc_extensions = {".md", ".rst", ".txt", ".adoc"}
    config_extensions = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", 
                        ".env", ".properties", ".xml"}
    data_extensions = {".csv", ".sql"}
    
    suffix = path.suffix.lower()
    return suffix in (code_extensions | doc_extensions | config_extensions | data_extensions)

# DESPUÉS
from acolyte.core.utils.file_types import FileTypeDetector

def _is_supported_file(self, path: Path) -> bool:
    return FileTypeDetector.is_supported(path)
```

### Ejemplo 2: chunking/factory.py
```python
# ANTES (~línea 50)
LANGUAGE_MAPPING = {
    ".py": PythonChunker,
    ".js": JavaScriptChunker,
    ".ts": TypeScriptChunker,
    ".jsx": JavaScriptChunker,
    ".tsx": TypeScriptChunker,
    # ... 20+ líneas más
}

@classmethod
def get_chunker(cls, file_path: str) -> BaseChunker:
    ext = Path(file_path).suffix.lower()
    chunker_class = cls.LANGUAGE_MAPPING.get(ext, DefaultChunker)
    return chunker_class()

# DESPUÉS
from acolyte.core.utils.file_types import FileTypeDetector

LANGUAGE_TO_CHUNKER = {
    "python": PythonChunker,
    "javascript": JavaScriptChunker,
    "typescript": TypeScriptChunker,
    # ... mapeo por lenguaje, no extensión
}

@classmethod
def get_chunker(cls, file_path: str) -> BaseChunker:
    path = Path(file_path)
    language = FileTypeDetector.get_language(path)
    chunker_class = cls.LANGUAGE_TO_CHUNKER.get(language, DefaultChunker)
    return chunker_class()
```

### Ejemplo 3: task_service.py
```python
# ANTES
file_pattern = r"\b[\w\-\.]+\.(?:py|js|ts|jsx|tsx|java|go|rs|rb|php|swift|kt|scala|r|m|mm|sh|bash|zsh|md|rst|txt|adoc|json|yaml|yml|toml|ini|cfg|env|properties|xml|csv|sql)\b"

# DESPUÉS
from acolyte.core.utils.file_types import FileTypeDetector

# Construir patrón dinámicamente
extensions = FileTypeDetector.get_all_supported_extensions()
extensions_pattern = "|".join(ext[1:] for ext in extensions)  # Quitar el punto
file_pattern = rf"\b[\w\-\.]+\.(?:{extensions_pattern})\b"
```

## 🔍 Patrones Exactos a Buscar

```python
# Patrón 1: Sets/listas de extensiones
code_extensions = {".py", ".js", ...}
supported_extensions = ['.py', '.js', ...]
EXTENSIONS = (".py", ".js", ...)

# Patrón 2: Diccionarios de mapeo
EXTENSION_MAP = {".py": "python", ...}
LANGUAGE_MAP = {".py": PythonChunker, ...}
ext_to_lang = {".py": "python", ...}

# Patrón 3: Métodos de detección
def is_supported_file(path):
def _is_code_file(path):
def detect_language(file_path):
def get_file_type(path):

# Patrón 4: Chequeos de extensión
if path.suffix in supported:
if file_path.endswith('.py'):
if ext.lower() in extensions:
```

## ⚠️ Casos Especiales

### 1. Detección por contenido (shebang)
```python
# Si el código detecta lenguaje por contenido:
if not path.suffix and path.is_file():
    with open(path, 'r') as f:
        first_line = f.readline()
        if first_line.startswith('#!/'):
            if 'python' in first_line:
                return 'python'
            elif 'bash' in first_line:
                return 'bash'

# Mantener esta lógica DESPUÉS de FileTypeDetector:
language = FileTypeDetector.get_language(path)
if language == "unknown" and not path.suffix:
    # Lógica de shebang aquí
```

### 2. Extensiones múltiples para un lenguaje
```python
# Código original puede tener:
if ext in ['.h', '.hpp', '.c', '.cpp', '.cc', '.cxx']:
    return 'cpp'

# FileTypeDetector mapea correctamente:
# .h -> "c"
# .hpp -> "cpp"
# Verificar que el comportamiento sea el esperado
```

### 3. Casos especiales de archivos
```python
# Archivos sin extensión pero con nombres específicos:
if path.name == 'Makefile':
    return 'makefile'
if path.name == 'Dockerfile':
    return 'dockerfile'

# Estos casos pueden necesitar lógica adicional
```

### 4. Validación adicional
```python
# Si el código original tenía validaciones extra:
if path.suffix in supported and path.stat().st_size < MAX_SIZE:
    return True

# Mantener validaciones adicionales:
if FileTypeDetector.is_supported(path) and path.stat().st_size < MAX_SIZE:
    return True
```

## 🎯 Para Turso

Con detección centralizada, será fácil:
- Añadir metadata específica por tipo
- Aplicar diferentes estrategias de indexación
- Generar estadísticas por tipo de archivo