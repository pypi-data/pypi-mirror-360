# 📝 REGISTRO COMPLETO DE DESARROLLO - SISTEMA DE INSTALACIÓN ACOLYTE

Este documento registra TODOS los cambios, archivos creados y decisiones tomadas en el desarrollo del sistema de instalación.

## 🏗️ ARQUITECTURA IMPLEMENTADA

### Sistema de Instalación Global

ACOLYTE se instala globalmente en `~/.acolyte/` y cada proyecto solo tiene un archivo `.acolyte.project`.

```
INSTALACIÓN GLOBAL:
C:\Users\{usuario}\.acolyte\
├── bin\                      # Ejecutables
│   └── acolyte.bat          # Windows wrapper
├── src\                     # Código fuente completo de ACOLYTE
│   └── acolyte\
│       ├── api\
│       ├── core\
│       ├── services\
│       ├── models\
│       ├── embeddings\
│       ├── semantic\
│       ├── rag\
│       └── dream\
├── scripts\                 # Scripts de utilidad
│   └── install\            # Scripts de instalación
└── projects\               # Datos por proyecto
    └── {project_id}\       # Hash único de 12 caracteres
        ├── config.yaml     # Configuración del proyecto
        ├── data\           # Datos del proyecto
        │   ├── acolyte.db  # Base de datos SQLite
        │   ├── dreams\     # Análisis Dream (MOVIDO de .acolyte-dreams)
        │   ├── logs\       # Logs del proyecto
        │   └── embeddings_cache\
        └── infra\          # Infraestructura Docker
            ├── docker-compose.yml
            └── Modelfile

PROYECTO DEL USUARIO:
C:\Users\{usuario}\mi-proyecto\
└── .acolyte.project        # ÚNICO archivo añadido (200 bytes)
```

## 📄 ARCHIVOS CREADOS/MODIFICADOS

### 1. INSTALADORES GLOBALES

**`install.bat`** (Windows)
- Ubicación: Raíz del proyecto
- Función: Instala ACOLYTE en `~/.acolyte/`
- Proceso:
  1. Verifica Python, Git, Docker
  2. Copia todo a `~/.acolyte/`
  3. Instala PyYAML y requests globalmente
  4. Instala Poetry si no existe
  5. Ejecuta `poetry install`
  6. Crea `~/.acolyte/bin/acolyte.bat`
  7. Añade al PATH de Windows

**`install.sh`** (Linux/Mac)
- Ubicación: Raíz del proyecto
- Función: Igual que install.bat pero para Unix
- Diferencias: Usa `~/.local/bin/` para el ejecutable

**`bin/acolyte`** (Unix executable)
- Template para el wrapper Unix
- Se copia a `~/.local/bin/acolyte`

**`bin/acolyte.bat`** (Windows executable)
- Template para el wrapper Windows
- Se modifica durante instalación con rutas correctas

### 2. CLI COMPLETO

**`src/acolyte/cli.py`** - CLI principal (440 líneas)
- Comandos implementados:
  - `init` - Inicializa proyecto
  - `install` - Instala servicios Docker
  - `start` - Inicia servicios
  - `stop` - Detiene servicios
  - `status` - Muestra estado
  - `index` - Indexa archivos
  - `projects` - Lista proyectos
  - `clean` - Limpia cache

- Clase `ProjectManager`:
  - `get_project_id()` - Genera ID único con SHA256 de git remote + path
  - `get_project_dir()` - Retorna `~/.acolyte/projects/{id}/`
  - `is_project_initialized()` - Chequea si existe `.acolyte.project`
  - `load_project_info()` - Carga YAML del proyecto
  - `save_project_info()` - Guarda info del proyecto

### 3. SCRIPTS DE INSTALACIÓN

**`scripts/install/init.py`** (600 líneas)
- Ejecutado por `acolyte init`
- Wizard interactivo que:
  1. Valida que es un proyecto (busca .git, package.json, etc.)
  2. Genera project ID único
  3. Configura puertos con AUTO-DETECCIÓN
  4. Detecta hardware (CPU, RAM, GPU)
  5. Recomienda modelo según recursos
  6. Detecta lenguajes del proyecto
  7. Configura linters (opcional)
  8. Configura exclusiones
  9. Genera `config.yaml`
  10. Genera `docker-compose.yml`
  11. Genera `Modelfile` personalizado

**`scripts/install/install.py`** (500 líneas)
- Ejecutado por `acolyte install`
- Proceso de instalación:
  1. Verifica requisitos
  2. Carga configuración
  3. Inicia Docker services
  4. Espera que estén listos
  5. Descarga modelo Ollama
  6. Crea modelo ACOLYTE personalizado
  7. Indexa proyecto completo

### 4. MÓDULOS COMUNES

**`scripts/install/common/__init__.py`**
- Exporta todas las utilidades

**`scripts/install/common/ui.py`**
- `Colors` - Colores ANSI
- `animate_text()` - Texto animado
- `show_spinner()` - Spinner de carga
- `print_success/error/warning/info()` - Mensajes formateados
- `print_progress_bar()` - Barra de progreso
- `ACOLYTE_LOGO` - Logo ASCII
- `CONSCIOUSNESS_TIPS` - Tips durante instalación

**`scripts/install/common/hardware.py`**
- `SystemDetector` - Detecta OS, CPU, RAM, GPU, disco
- `ModelRecommender` - Recomienda modelo según hardware

**`scripts/install/common/docker.py`**
- `DockerGenerator` - Genera docker-compose.yml personalizado
- `GPUDetector` - Detecta NVIDIA/AMD GPU

**`scripts/install/common/validators.py`**
- `validate_port()` - Valida puerto disponible
- `validate_project_name()` - Valida nombre
- `sanitize_yaml_string()` - Sanitiza para YAML

**`scripts/install/common/port_manager.py`** (NUEVO)
- `PortManager` - Auto-asignación de puertos
- Rangos ACOLYTE:
  - Weaviate: 42080-42179
  - Ollama: 42434-42533
  - Backend: 42000-42099
- `find_available_ports()` - Encuentra 3 puertos libres
- `find_next_available()` - Siguiente puerto libre desde base

### 5. INFRAESTRUCTURA DOCKER

**`infra/docker-compose.yml`**
- Template global con variables de entorno
- Servicios: weaviate, ollama, jaeger (opcional)
- Puertos usando variables: ${WEAVIATE_PORT:-42080}

**`infra/Dockerfile`**
- Para construir el backend (cuando esté listo)
- Python 3.11-slim base
- Usuario non-root `acolyte`

**`infra/Modelfile`**
- Template para personalización
- Se modifica durante init con nombre del proyecto

### 6. CAMBIOS DE CONFIGURACIÓN

**`.acolyte.example`** - MODIFICADO
- Puertos cambiados a rango 42XXX
- dream_folder_name: "dreams" (era ".acolyte-dreams")

**`src/acolyte/dream/insight_writer.py`** - MODIFICADO
- Línea 38-41: Ahora usa `data/dreams/` en lugar de `.acolyte-dreams/`
- Creado método `_sanitize_filename()` para seguridad

**`.gitignore`** - MODIFICADO
- Añadido `/data/dreams/*`
- Añadido `!/data/dreams/.gitkeep`
- Añadido `.acolyte-dreams/` como deprecated

**`pyproject.toml`** - MODIFICADO
- Añadido `[tool.poetry.scripts]` con `acolyte = "acolyte.cli:main"`

### 7. ESTRUCTURA DE DATOS

**`data/`** - Directorio de datos
- `acolyte.db` - Base de datos SQLite (ya existía)
- `dreams/` - NUEVO directorio para análisis Dream
- `dreams/.gitkeep` - Para mantener en git
- `embeddings_cache/` - Cache de embeddings
- `README.md` - Documentación

**`.acolyte-dreams/`** - DEPRECATED
- Creado `README_MOVED.md` indicando mudanza a `data/dreams/`

### 8. PROCESO DE INSTALACIÓN DETALLADO

#### FASE 1: Instalación Global

1. Usuario ejecuta `.\install.bat`
2. Script verifica requisitos
3. Copia todo a `C:\Users\{user}\.acolyte\`
4. Instala dependencias Python
5. Crea ejecutable en PATH
6. Usuario reinicia terminal

#### FASE 2: Inicialización de Proyecto

1. Usuario va a su proyecto: `cd C:\mi-proyecto`
2. Ejecuta: `acolyte init`
3. CLI valida que es proyecto válido
4. Genera project ID: SHA256(git_remote + absolute_path)[:12]
5. Ejecuta `scripts/install/init.py` con variables de entorno:
   - ACOLYTE_PROJECT_ID
   - ACOLYTE_PROJECT_PATH
   - ACOLYTE_GLOBAL_DIR
   - ACOLYTE_PROJECT_NAME
6. Wizard interactivo:
   - Nombre del proyecto
   - Puertos (auto-detectados)
   - Hardware detection
   - Modelo selection
   - Language detection
   - Linter config
   - Exclusions
7. Genera archivos:
   - `.acolyte.project` en proyecto del usuario
   - `config.yaml` en `~/.acolyte/projects/{id}/`
   - `docker-compose.yml` personalizado
   - `Modelfile` personalizado

#### FASE 3: Instalación de Servicios

1. Usuario ejecuta: `acolyte install`
2. CLI carga project info
3. Ejecuta `scripts/install/install.py`
4. Verifica Docker, puertos, etc.
5. Levanta servicios con docker-compose
6. Espera que estén listos (polling HTTP)
7. Descarga modelo base (qwen2.5-coder:3b)
8. Crea modelo personalizado "acolyte"
9. Indexa proyecto completo via API

#### FASE 4: Uso Normal

1. `acolyte start` - Levanta servicios
2. `acolyte stop` - Detiene servicios
3. `acolyte status` - Muestra estado
4. `acolyte index` - Re-indexa cambios

### 9. SISTEMA MULTI-PROYECTO

**Identificación Única**:
```python
def get_project_id(project_path: Path) -> str:
    git_remote = ""
    if (project_path / ".git").exists():
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            git_remote = result.stdout.strip()
    
    abs_path = str(project_path.resolve())
    unique_string = f"{git_remote}:{abs_path}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:12]
```

**Auto-Asignación de Puertos**:
- Primer proyecto: 42080, 42434, 42000
- Segundo proyecto: 42081, 42435, 42001
- Tercer proyecto: 42082, 42436, 42002
- Etc.

**Aislamiento Total**:
- Cada proyecto tiene su propia BD
- Cada proyecto tiene su config
- Cada proyecto tiene sus contenedores Docker
- Modelos Ollama se comparten (volumen global)

### 10. CAMBIOS IMPORTANTES

1. **Puertos por defecto**: 8080→42080, 11434→42434, 8000→42000
2. **Dreams location**: `.acolyte-dreams/` → `data/dreams/`
3. **Instalación global**: Todo va a `~/.acolyte/`
4. **Proyecto limpio**: Solo `.acolyte.project` en el repo
5. **Multi-proyecto**: Soporta N proyectos simultáneos
6. **Auto-puertos**: Detecta conflictos automáticamente

### 11. DOCUMENTACIÓN CREADA

- `docs/INSTALLATION_ATOMIC_FLOW.md` - Flujo detallado paso a paso
- `docs/MULTI_PROJECT_PORTS.md` - Sistema de puertos
- `INSTALLATION_COMPLETE.md` - Resumen de lo implementado
- `TODO_PARA_FUNCIONAR.md` - Lo que faltaba (ya implementado)

### 12. ARCHIVOS A BORRAR (Sugerencia)

- `scripts/INSTALL.md` → deprecated
- `scripts/INSTALL_NEW.md` → redirige a atomic flow
- `.continue/` → no se usa
- `.cursor/` → no se usa
- Varios `.md` de documentación interna antigua

### 13. PROBLEMAS CONOCIDOS

1. **Backend no implementado** - El contenedor backend está comentado en docker-compose
2. **Git hooks** - No están integrados en la instalación
3. **Windows PATH** - Requiere reiniciar terminal
4. **GPU detection** - Solo NVIDIA bien soportado

### 14. DECISIONES TÉCNICAS

1. **¿Por qué ~/.acolyte/?** - Estándar Unix, fácil de encontrar
2. **¿Por qué project ID hash?** - Único incluso si mueves el proyecto
3. **¿Por qué puertos 42XXX?** - Rango poco usado, fácil recordar
4. **¿Por qué Poetry?** - Mejor gestión de dependencias Python
5. **¿Por qué multi-proyecto?** - Cada proyecto necesita su contexto

### 15. FLUJO COMPLETO DE ARCHIVOS

```
DESARROLLO (tu máquina):
acolyte-project/
├── install.bat              # Instalador Windows
├── install.sh              # Instalador Unix
├── src/acolyte/cli.py      # CLI principal
├── scripts/install/        # Scripts de instalación
│   ├── init.py            # Wizard de configuración
│   ├── install.py         # Instalador de servicios
│   └── common/            # Utilidades compartidas
└── infra/                  # Templates Docker

↓ INSTALACIÓN GLOBAL ↓

~/.acolyte/                 # Copia completa
├── bin/acolyte.bat        # Ejecutable
├── src/                   # Todo el código
└── projects/              # Vacío inicialmente

↓ PROYECTO USUARIO ↓

mi-proyecto/
└── .acolyte.project       # ID del proyecto

↓ ACOLYTE INIT ↓

~/.acolyte/projects/{id}/
├── config.yaml            # Configuración específica
├── data/                  # Datos del proyecto
└── infra/                 # Docker del proyecto

↓ ACOLYTE INSTALL ↓

Docker containers:
- acolyte-weaviate
- acolyte-ollama
- acolyte-backend (futuro)

Docker volumes:
- weaviate-data
- ollama-models
```

---

**ESTE ES EL REGISTRO COMPLETO DEL SISTEMA DE INSTALACIÓN IMPLEMENTADO**
