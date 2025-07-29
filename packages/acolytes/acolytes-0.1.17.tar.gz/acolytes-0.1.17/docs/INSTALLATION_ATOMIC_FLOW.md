# 🚀 INSTALACIÓN COMPLETA DE ACOLYTE - Flujo Atómico

Este documento detalla **paso a paso** el proceso completo de instalación de ACOLYTE desde cero, explicando qué hace cada comando internamente.

## 📋 Pre-requisitos del Sistema

Antes de empezar necesitas:

1. **Python 3.11+** instalado
2. **Docker Desktop** instalado y corriendo
3. **Git** instalado
4. **~16GB RAM** mínimo (para el modelo 3B)

---

## FASE 1: Instalación Global de ACOLYTE

### 1️⃣ **Clonar o Descargar ACOLYTE**

```bash
# Opción A: Desde GitHub (cuando esté publicado)
git clone https://github.com/unmasSk/acolyte.git
cd acolyte

# Opción B: Desde tu carpeta actual (desarrollo)
cd /path/to/acolyte-project
```

### 2️⃣ **Ejecutar el Instalador Global**

```bash
# Windows
.\install.bat

# Linux/Mac
./install.sh
```

#### ¿Qué hace `install.bat` internamente?

1. **Verifica requisitos**:

   ```
   ✓ Python 3.11+ encontrado
   ✓ Git encontrado
   ✓ Docker Desktop corriendo
   ```

2. **Crea estructura global** en `~/.acolyte/`:

   ```
   C:\Users\bextia\.acolyte\
   ├── bin\              # Ejecutable acolyte.bat
   ├── src\              # Código fuente copiado
   └── projects\         # Aquí irán los proyectos
   ```

3. **Instala dependencias Python**:

   - PyYAML y requests globalmente (para git hooks)
   - Poetry si no está instalado
   - Dependencias del proyecto con Poetry

4. **Crea el ejecutable** `acolyte.bat`:

   - Lo pone en `~/.acolyte/bin/`
   - Añade esta carpeta al PATH de Windows

5. **Mensaje final**:
   ```
   ✓ ACOLYTE installed successfully!
   Restart your terminal for PATH changes
   ```

---

## FASE 2: Inicializar un Proyecto

### 3️⃣ **Ir a tu proyecto y ejecutar init**

```bash
# Abrir nueva terminal (para que tome el PATH)
cd C:\Users\<username>\mi-proyecto-web
acolyte init
```

#### ¿Qué hace `acolyte init` internamente?

1. **Valida que es un proyecto**:

   - Busca `.git/`, `package.json`, `pyproject.toml`, etc.
   - Si no encuentra, error: "Not a valid project directory"

2. **Genera Project ID único**:

   ```python
   # Combina: git remote URL + path absoluto
   unique_string = "github.com/user/repo:C:/Users/<username>/mi-proyecto-web"
   project_id = sha256(unique_string)[:12]  # "a1b2c3d4e5f6"
   ```

3. **Muestra el wizard interactivo**:

   ```
   🤖 ACOLYTE Project Initialization
   Project path: C:\Users/<username>/mi-proyecto-web
   Project ID: a1b2c3d4e5f6

   Project name [mi-proyecto-web]: Mi Súper Web
   ```

4. **Configuración de Puertos** (con auto-detección):

   ```
   Configure service ports (press Enter for auto-selection):
   ℹ Found available ports: Weaviate=42080, Ollama=42434, Backend=42000

   Weaviate port [42080]: (Enter)
   Ollama port [42434]: (Enter)
   Backend API port [42000]: (Enter)

   ✓ Selected ports - Weaviate: 42080, Ollama: 42434, Backend: 42000
   ```

   **Si el puerto está ocupado**:

   ```
   Weaviate port [42080]: (Enter)
   ⚠️ Port 42080 is not available, using 42081
   ```

5. **Detección de Hardware**:

   ```
   Scanning hardware...
   ✓ Hardware detected:
   📊 CPU: Intel Core i7-9700K (8 cores)
   💾 RAM: 32 GB
   🎮 GPU: NVIDIA RTX 3080 (10240 MB VRAM)
   💿 Free space: 250 GB
   ```

6. **Selección de Modelo IA**:

   ```
   💡 Available models:
   1) qwen2.5-coder:3b - Small model, 8GB RAM, 32k context (recommended)
   2) qwen2.5-coder:7b - Medium model, 16GB RAM, 32k context
   3) qwen2.5-coder:14b - Large model, 32GB RAM, 32k context

   Select model [1]: 1
   ```

7. **Detección de Lenguajes**:

   ```
   Detecting languages in project...
   Languages detected: python, javascript, typescript

   Configure linters? [Y/n]: n (skip por ahora)
   ```

8. **Configuración de Exclusiones**:

   ```
   Additional folders to exclude? (comma separated): build,dist,coverage
   ```

9. **Crea archivos de configuración**:

   a) **En el proyecto** (solo marca):

   ```yaml
   # C:\Users\bextia\mi-proyecto-web\.acolyte.project
   project_id: a1b2c3d4e5f6
   name: Mi Súper Web
   path: C:\Users/<username>/mi-proyecto-web
   initialized: 2024-01-15T10:30:00
   acolyte_version: 1.0.0
   ```

   b) **En ~/.acolyte/projects/a1b2c3d4e5f6/**:

   ```
   C:\Users\bextia\.acolyte\projects\a1b2c3d4e5f6\
   ├── config.yaml           # Configuración completa
   ├── data\
   │   ├── logs\            # Logs de instalación
   │   └── dreams\          # Futuros análisis
   └── infra\
       ├── docker-compose.yml    # Generado con puertos específicos
       └── Modelfile            # Personalizado para el proyecto
   ```

10. **Contenido de config.yaml**:
    ```yaml
    version: "1.0"
    project:
      id: a1b2c3d4e5f6
      name: Mi Súper Web
      path: C:\Users/<username>/mi-proyecto-web
    hardware:
      cpu_cores: 8
      ram_gb: 32
      gpu:
        type: nvidia
        name: NVIDIA RTX 3080
        vram_mb: 10240
    model:
      name: qwen2.5-coder:3b
      context_size: 32768
      ram_required: 8
    ports:
      weaviate: 42080
      ollama: 42434
      backend: 42000
    docker:
      memory_limit: 16G
      cpu_limit: 4
      gpu_enabled: true
    ```

---

## FASE 3: Instalación de Servicios

### 4️⃣ **Ejecutar install**

```bash
acolyte install
```

#### ¿Qué hace `acolyte install` internamente?

1. **Verifica configuración**:

   ```
   🚀 ACOLYTE Installation
   Project: Mi Súper Web (a1b2c3d4)
   ```

2. **Verifica requisitos** (otra vez):

   - Docker corriendo
   - Puertos disponibles
   - Espacio en disco

3. **Levanta servicios Docker**:

   ```bash
   cd ~/.acolyte/projects/a1b2c3d4e5f6/infra
   docker-compose up -d
   ```

   Esto crea contenedores:

   - `acolyte-weaviate` (base de datos vectorial)
   - `acolyte-ollama` (servidor de IA)
   - `acolyte-backend` (API de ACOLYTE) - _cuando esté implementado_

4. **Espera a que estén listos**:

   ```
   Waiting for Weaviate... ✓ Ready
   Waiting for Ollama... ✓ Ready
   Waiting for Backend... ✓ Ready
   ```

   Internamente hace polling HTTP:

   ```python
   # Weaviate
   GET http://localhost:42080/v1/.well-known/ready

   # Ollama
   GET http://localhost:42434/api/tags

   # Backend
   GET http://localhost:42000/api/health
   ```

5. **Descarga el modelo base**:

   ```bash
   docker exec acolyte-ollama ollama pull qwen2.5-coder:3b
   ```

   Progreso:

   ```
   Downloading model ████████████████ 100%
   💭 Los modelos aprenden patrones, no memorizan código
   ```

6. **Crea modelo personalizado**:

   ```bash
   # Copia el Modelfile al contenedor
   docker cp Modelfile acolyte-ollama:/tmp/Modelfile

   # Crea modelo "acolyte" basado en qwen2.5-coder:3b
   docker exec acolyte-ollama ollama create acolyte -f /tmp/Modelfile
   ```

   El Modelfile contiene:

   ```
   FROM qwen2.5-coder:3b
   SYSTEM """You are ACOLYTE for project Mi Súper Web..."""
   PARAMETER temperature 0.1
   PARAMETER num_ctx 32768
   ```

7. **Inicializa base de datos**:

   - SQLite se crea automáticamente en `data/acolyte.db`
   - Tablas creadas por el backend al primer uso

8. **Indexa el proyecto**:

   ```
   Indexing project files...
   ████████████████ 100%
   💭 El código es poesía con propósito
   ✓ Project indexing completed
   ```

   Internamente:

   ```python
   POST http://localhost:42000/api/index/project
   {
     "force_reindex": true,
     "respect_gitignore": true,
     "respect_acolyteignore": true
   }
   ```

   Esto:

   - Escanea todos los archivos del proyecto
   - Respeta `.gitignore` y `.acolyteignore`
   - Divide el código en chunks semánticos
   - Genera embeddings con UniXcoder
   - Guarda en Weaviate para búsqueda

---

## FASE 4: Uso del Sistema

### 5️⃣ **Iniciar servicios**

```bash
# En cualquier momento futuro
cd C:\Users\<username>\mi-proyecto-web
acolyte start
```

Internamente ejecuta:

```bash
docker-compose -f ~/.acolyte/projects/a1b2c3d4e5f6/infra/docker-compose.yml up -d
```

### 6️⃣ **URLs de servicios**

```
Service URLs:
  Weaviate: http://localhost:42080
  Ollama: http://localhost:42434
  API: http://localhost:42000
  API Docs: http://localhost:42000/api/docs
```

---

## 📁 Estructura Final Completa

### En tu máquina:

```
C:\Users\bextia\
├── .acolyte\                      # Instalación global
│   ├── bin\
│   │   └── acolyte.bat           # Ejecutable
│   ├── src\                      # Código fuente
│   │   └── acolyte\
│   │       ├── api\
│   │       ├── core\
│   │       ├── services\
│   │       ├── models\
│   │       ├── embeddings\
│   │       ├── semantic\
│   │       ├── rag\
│   │       └── dream\
│   └── projects\
│       └── a1b2c3d4e5f6\         # Tu proyecto
│           ├── config.yaml       # Configuración
│           ├── data\
│           │   ├── acolyte.db    # Base de datos SQLite
│           │   ├── dreams\       # Análisis Dream
│           │   ├── logs\         # Logs
│           │   └── embeddings_cache\
│           └── infra\
│               ├── docker-compose.yml
│               └── Modelfile
│
└── mi-proyecto-web\              # Tu proyecto original
    └── .acolyte.project          # Solo este archivo (200 bytes)
```

### En Docker:

```
Contenedores:
- acolyte-weaviate (puerto 42080)
- acolyte-ollama (puerto 42434)
- acolyte-backend (puerto 42000) - cuando esté implementado

Volúmenes:
- weaviate-data
- ollama-models
```

---

## 🔄 Segundo Proyecto (Multi-Proyecto)

Si inicias otro proyecto mientras el primero está corriendo:

1. **Ir al segundo proyecto**:

   ```bash
   cd ~/otro-proyecto
   ```

2. **Inicializar con detección de conflictos**:

   ```bash
   acolyte init
   ```

   El PortManager detecta automáticamente:

   ```
   Configure service ports (press Enter for auto-selection):
   ℹ Found available ports: Weaviate=42081, Ollama=42435, Backend=42001
   ```

3. **Instalar servicios separados**:

   ```bash
   acolyte install
   ```

   Crea NUEVOS contenedores:

   - `acolyte-weaviate-{project_id}`
   - `acolyte-ollama-{project_id}`
   - `acolyte-backend-{project_id}`

4. **Cada proyecto es 100% independiente**:
   - Base de datos separada
   - Configuración única
   - Modelo personalizado
   - Memoria propia

---

## ⚙️ Comandos Disponibles

- `acolyte init` - Configura proyecto
- `acolyte install` - Instala servicios
- `acolyte start` - Inicia servicios
- `acolyte stop` - Detiene servicios
- `acolyte status` - Ver estado
- `acolyte index` - Re-indexar código
- `acolyte projects` - Lista todos los proyectos
- `acolyte clean` - Limpia cache y logs

---

## 🔍 Detalles Técnicos Adicionales

### Project ID Generation

```python
def get_project_id(project_path: Path) -> str:
    git_remote = ""
    if (project_path / ".git").exists():
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True
        )
        if result.returncode == 0:
            git_remote = result.stdout.strip()

    abs_path = str(project_path.resolve())
    unique_string = f"{git_remote}:{abs_path}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:12]
```

### Port Auto-Assignment

```python
class PortManager:
    WEAVIATE_BASE = 42080
    OLLAMA_BASE = 42434
    BACKEND_BASE = 42000

    def find_next_available(self, base_port: int) -> int:
        for offset in range(100):
            port = base_port + offset
            if self.is_port_available(port):
                return port
        raise RuntimeError("No available ports")
```

### Docker Compose Generation

El `docker-compose.yml` se genera dinámicamente con:

- Puertos específicos del proyecto
- Límites de recursos según hardware
- GPU habilitada si se detecta
- Nombres únicos de contenedores

---

Este es el flujo COMPLETO y DETALLADO de instalación de ACOLYTE.
