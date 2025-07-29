# 🤖 ACOLYTE - Prompt para IAs Colaborativas

> **IMPORTANTE**: Este documento es SOLO para IAs durante desarrollo. Proyecto ubicado en `C:/Users/bextia/Desktop/acolyte-project/` (CASA) o `C:/Users/fix.workshop/Desktop/acolyte-project/` (TIENDA).

> **⚠️ CAMBIO DE NOMBRE**: El paquete se publica como `acolytes` (con 's') en PyPI, pero el proyecto y comandos siguen siendo ACOLYTE.

## 🚀 Quick Start para IAs

**Stack**: FastAPI + Ollama + Weaviate + SQLite  
**Ubicación**: `/Desktop/acolyte-project/`  
**Paquete PyPI**: `acolytes` (versión 0.1.9)  
**Tests**: 93% cobertura, SIEMPRE hacer tests  
**Filosofía**: Sistema LOCAL mono-usuario (simplicidad > complejidad)

```bash
# Comandos de desarrollo
poetry run pytest tests/              # Correr tests
poetry run ruff check .               # Linting
poetry run black .                    # Formateo
poetry run mypy src/acolyte --strict  # Type checking
poetry run uvicorn acolyte.api.main:app --reload  # Iniciar API desarrollo (no implementado)
```

## 📦 Instalación y CLI

### Instalación via pip

ACOLYTE ahora se instala como paquete Python estándar:

```bash
# Desde PyPI (recomendado)
pip install acolytes

# Modo desarrollo
pip install -e .

# Con dependencias de desarrollo
pip install -e ".[dev]"
```

**Nota importante**: El paquete se llama `acolytes` (con 's') en PyPI porque `acolyte` ya estaba ocupado. Sin embargo, los comandos CLI siguen siendo `acolyte` (sin 's').

**Nota**: La instalación descarga ~2GB (incluye PyTorch y modelos). Tiempo estimado: 2-5 minutos.

### Arquitectura del CLI

**Entry point**: `acolyte.cli:main` (directo, sin wrapper)

```toml
# pyproject.toml
[project.scripts]
acolyte = "acolyte.cli:main"
```

### Comandos del CLI

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `acolyte init` | Inicializa ACOLYTE en un proyecto | `acolyte init` |
| `acolyte install` | Configura servicios Docker y BD | `acolyte install` |
| `acolyte start` | Inicia servicios con health checks | `acolyte start` |
| `acolyte stop` | Detiene todos los servicios | `acolyte stop` |
| `acolyte status` | Muestra estado de servicios | `acolyte status` |
| `acolyte index` | Indexa archivos del proyecto | `acolyte index` |
| `acolyte logs` | Muestra logs (Docker o debug.log) | `acolyte logs -f` |
| `acolyte doctor` | Diagnostica problemas comunes | `acolyte doctor` |
| `acolyte reset` | Resetea instalación del proyecto | `acolyte reset --force` |
| `acolyte projects` | Lista todos los proyectos | `acolyte projects` |

### Flujo de instalación completo

1. **pip install** → Instala paquete + dependencias + crea comando `acolyte`
2. **PostInstallCommand** → Crea `~/.acolyte/` + verifica PATH
3. **acolyte init** → Valida proyecto + instala git hooks + crea `.acolyte.project`
4. **acolyte install** → Detecta hardware + configura + genera Docker + inicializa BD
5. **acolyte start** → Levanta servicios + health checks automáticos
6. **acolyte index** → Indexa código del proyecto

### Health Checks (ServiceHealthChecker)

Los comandos ahora esperan automáticamente a que los servicios estén listos:
- Weaviate: `http://localhost:{port}/v1/.well-known/ready`
- Backend: `http://localhost:{port}/api/health`
- Timeout configurable (default: 120s)
- Progreso visual con Rich

### Estructura de archivos post-instalación

```
~/.acolyte/                          # Directorio global
├── .initialized                     # Marca primera ejecución
├── projects/
│   └── {project_id}/               # Por proyecto (hash de 12 chars)
│       ├── .acolyte                # Configuración YAML
│       ├── data/
│       │   ├── acolyte.db          # SQLite
│       │   ├── dreams/             # Análisis Dream
│       │   └── logs/               # Logs
│       └── infra/
│           ├── docker-compose.yml   # Servicios
│           └── Modelfile           # Config Ollama
└── models/                         # Modelos compartidos

{proyecto}/.acolyte.project         # Link al ID del proyecto
{proyecto}/.git/hooks/              # Git hooks instalados
```

### Diagnóstico de problemas

**Comando doctor** verifica:
- PATH del sistema
- Docker instalado y funcionando
- Git disponible
- Permisos de directorios
- Servicios corriendo
- Conectividad a puertos

### Variables de entorno

- `ACOLYTE_DEV`: Usa ~/.acolyte-dev en lugar de ~/.acolyte
- `ACOLYTE_DEBUG`: Muestra stack traces completos
- `ACOLYTE_NO_EMOJI`: Desactiva emojis en output (Windows)
- `ACOLYTE_USE_TESTPYPI`: Genera Dockerfile para TestPyPI (usado durante `acolyte install`)

### ⚠️ Notas importantes para IAs

1. **NO usar el antiguo wrapper** - `bin/acolyte_wrapper.py` ya no existe
2. **CLI está en** `src/acolyte/cli.py` directamente
3. **Health checks son automáticos** - No asumir que servicios están listos inmediatamente
4. **PATH se verifica** durante instalación con instrucciones claras
5. **Reset disponible** para limpiar instalaciones corruptas

## 👤 Contexto del Proyecto

- **Desarrollador único**: Soy Bex no soy programador, trabajo exclusivamente con IAs colaborativas
- **Metodología**: Todo el código es generado por IAs siguiendo estas instrucciones
- **Sin fechas ni histórico**: La documentación mantiene solo el estado actual
- **Proyecto 100% funcional**: 3500 tests implementados, 93% cobertura
- **Stack probado**: Todas las decisiones técnicas han sido validadas, pero no probadas.
- **Idioma**: Siempre hablo a Bex en español, pero el código es en inglés.

## 📋 Resumen Ejecutivo

**ACOLYTE** es un asistente de programación 100% local ejecutado con Ollama (modelo `acolyte:latest` basado en Qwen-2.5-Coder). Diseñado para un único usuario y proyecto, con memoria infinita y API compatible con OpenAI.

### 🏠 Filosofía de Diseño - Sistema LOCAL Mono-Usuario

**ACOLYTE es un sistema PRIVADO que corre en localhost para UN SOLO USUARIO**. Esta decisión fundamental define todos los patrones:

| Aspecto              | Decisión        | Razón                                 |
| -------------------- | --------------- | ------------------------------------- |
| Arquitectura         | Monolito simple | Un usuario no necesita microservicios |
| Autenticación        | Ninguna         | Usuario ya autenticado en su OS       |
| Rate Limiting        | Ninguno         | Uso ilimitado para el dueño           |
| Estado Global        | Permitido       | Sin concurrencia = sin problemas      |
| Singletons           | Recomendados    | Simples y eficientes                  |
| Dependency Injection | No usar         | Complejidad innecesaria               |

**NUNCA** evalúes el código con mentalidad enterprise/SaaS. Es un asistente personal.

### 🎯 Qué es ACOLYTE

- 🧠 **Recuerda Todo**: Memoria infinita entre sesiones - nunca te repitas
- 🔍 **Conoce Tu Código**: Indexa y entiende toda la estructura del proyecto
- 🚀 **Contexto Inteligente**: Usa búsqueda híbrida (70% semántica + 30% léxica)
- 💤 **Análisis Dream**: Modo de análisis profundo que encuentra bugs y oportunidades
- 🔒 **100% Privado**: Corre completamente en tu máquina
- ⚡ **Rápido y Eficiente**: Optimizado para modelos 3B-7B

## ✅ Estado Actual: 100% Funcional

**Módulos Completados**: Core, API, Services (5/5), Models, Embeddings, Semantic, RAG, Dream

**Cobertura de Tests**: 93% (3500 tests)

- Objetivo: ≥90% todos los archivos
- Tests completos implementados para todos los 31 lenguajes
- Ver `/tests/rag/chunking/` para todos los archivos de test
- Cada lenguaje tiene su archivo `test_[language]_chunker_complete.py`

**Pendientes**:

- ❌ Documentación de Usuario (0%)
- ❌ Tests integración E2E (0%)
- ❌ Integración IDE (pendiente Cline vs Continue.dev)

## ⚠️ ACLARACIÓN CRÍTICA: IndexingService

**IndexingService está en `/services/indexing_service.py`**, NO en `/rag/indexing/`. El módulo `/rag/indexing/` NO EXISTE y NO VA A EXISTIR NUNCA.

## 🏠 Paradigma Mono-Usuario Local

### ✅ Lo que es CORRECTO en ACOLYTE (aunque serían anti-patterns en la nube)

#### Variables Globales y Singletons

```python
# ✅ CORRECTO EN ACOLYTE
from acolyte.core.logging import logger  # Singleton global
event_bus = EventBus()  # Instancia global
_dream_orchestrator = None  # Estado global

# Un único usuario = no hay race conditions
# No hay concurrencia real entre usuarios
# Los singletons son eficientes y simples
```

#### Estado Global en Servicios

```python
# ✅ CORRECTO EN ACOLYTE
class ChatService:
    def __init__(self):
        self._active_session_id = None  # Estado de instancia
        self._active_task = None        # Compartido entre métodos
        self.weaviate_client = client   # Cliente reutilizado
```

#### No usar Dependency Injection de FastAPI

```python
# ✅ CORRECTO EN ACOLYTE - Crear servicios directamente
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    service = ChatService()  # Creación directa, no DI
    return await service.process(request)

# DI es para testing y multi-tenancy
# Un usuario no necesita aislar dependencias
# Simplicidad > Complejidad innecesaria
```

#### Sin Autenticación

```python
# ✅ CORRECTO EN ACOLYTE - Sin auth, solo localhost
app = FastAPI(
    title="ACOLYTE API",
    # NO auth middleware
    # NO API keys
    # Solo escucha en 127.0.0.1
)
```

### 🎯 Simplificaciones Apropiadas

Como sistema mono-usuario local, ACOLYTE simplifica muchos aspectos que serían complejos en un SaaS:

1. **Sin Rate Limiting**: Un usuario no se ataca a sí mismo
2. **Sin Caching Distribuido**: Todo en memoria local
3. **Sin Health Checks Complejos**: Simple endpoint /health
4. **Sin Métricas de APM**: Logging local es suficiente
5. **Sin Circuit Breakers**: Reintentos simples con backoff
6. **Sin Message Queues**: asyncio.Queue local es suficiente

(Ver sección "Filosofía de Diseño" para más detalles)

### 📌 Patrones que SÍ Necesitan Documentación

#### FastAPI Lifespan (Mejor Práctica Objetiva)

```python
# ✅ CORRECTO - Usar lifespan en lugar de deprecated on_event
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("ACOLYTE API starting up")
    yield
    # Shutdown
    logger.info("ACOLYTE API shutting down")

app = FastAPI(lifespan=lifespan)

# ❌ INCORRECTO - Deprecated
@app.on_event("startup")  # NO usar
@app.on_event("shutdown") # NO usar
```

#### Header None Handling (Bug Real de FastAPI)

```python
# ✅ CORRECTO - FastAPI pasa Header(None) que es truthy
async def endpoint(
    x_request_id: Optional[str] = Header(None)
):
    # Header(None) es un objeto, no None!
    request_id = x_request_id if x_request_id is not None else generate_id()

# ❌ INCORRECTO
request_id = x_request_id or generate_id()  # Header(None) es truthy!
```

#### WebSocket Event Queues

```python
# ✅ CORRECTO - Patrón para WebSocket + eventos
event_queue: asyncio.Queue[ProgressEvent] = asyncio.Queue()

# Task para procesar eventos
async def process_events():
    while True:
        event = await event_queue.get()
        await manager.send_event(event)

# Publicar eventos
await event_queue.put(ProgressEvent(...))
```

#### Path Validation (Seguridad Local También Importa)

```python
# ✅ CORRECTO - Validar paths incluso en local
try:
    safe_path = file_path.relative_to(project_root)
except ValueError:
    raise SecurityError("Path traversal attempt detected")

# Nunca confiar en paths del usuario, incluso siendo el único
```

### 💡 Filosofía de Diseño

> "La mejor arquitectura es la más simple que resuelve el problema"

ACOLYTE abraza la simplicidad del contexto mono-usuario:

- Menos capas de abstracción
- Menos puntos de fallo
- Menos latencia
- Más fácil de depurar
- Más fácil de entender

**Recuerda**: No estamos construyendo el próximo Twitter. Estamos construyendo el mejor asistente local posible.

## 🏗️ Stack Tecnológico

| Componente    | Tecnología    | Configuración              |
| ------------- | ------------- | -------------------------- |
| **Gestión**   | Poetry        | `pyproject.toml`           |
| **Backend**   | FastAPI       | Solo localhost (127.0.0.1) |
| **Modelo**    | Ollama        | `acolyte:latest`           |
| **Vector DB** | Weaviate      | Puerto 8080                |
| **Storage**   | SQLite        | Thread-safe con locks      |
| **Testing**   | pytest        | Cobertura ≥90%             |
| **Linting**   | Black + Ruff  | `line-length=100`          |
| **Tipos**     | mypy --strict | Sin warnings               |
| **Logs**      | loguru        | Asíncrono, sin emojis      |
| **Parsing**   | tree-sitter   | AST real para 25 lenguajes |
| **Models**    | Pydantic v2   | `^2.6.0` (NO v1)           |
| **Mocking**   | unittest.mock | NO patch sys.modules       |

### 🔥 Tree-sitter para Chunking

**IMPORTANTE**: ACOLYTE usa tree-sitter (el mismo parser de GitHub) para chunking inteligente:

- **Un solo paquete**: `tree-sitter-languages` incluye 30+ lenguajes pre-compilados
- **AST real**: No regex frágil, parsing profesional
- **Fácil de extender**: Agregar un lenguaje es crear una clase de ~50 líneas

**31 lenguajes soportados**:

**Tree-sitter (25)**: Python, TypeScript, Java, Go, Rust, C, C++, Ruby, PHP, Kotlin, SQL, R, Lua, Bash, Perl, Dockerfile, Makefile, Elisp, HTML, CSS, JSON, YAML, TOML, Markdown

**Pattern matching (5)**: C#, Swift, XML, VimScript, INI (cuando no hay gramática tree-sitter)

**DefaultChunker**: Fallback inteligente con detección heurística

```toml
# pyproject.toml
[tool.poetry.dependencies]
tree-sitter = "^0.20.4"
tree-sitter-languages = "^1.10.2"  # TODOS los lenguajes pre-compilados
```

## 🎯 Tabla de Decisiones Críticas

| Decisión         | Elección                    | Razón                                   |
| ---------------- | --------------------------- | --------------------------------------- |
| Base de datos    | SQLite + Weaviate           | Simplicidad local, arquitectura probada |
| Resúmenes        | vs conversaciones completas | 90% reducción de almacenamiento         |
| Chunking         | Tree-sitter (AST real)      | NO regex, precisión profesional         |
| Búsqueda         | Híbrida 70/30               | Balance semántica/léxica                |
| Git              | Reactivo con GitPython      | NO shell, NO fetch automático           |
| IDs              | hex32 sin guiones           | `generate_id()` unificado               |
| Dream            | Análisis técnico real       | NO antropomorfización                   |
| Errores          | Jerarquía en core           | `core/exceptions.py` centralizado       |
| MetricsCollector | Sin namespace               | Diseño intencional                      |
| 18 ChunkTypes    | Precisión máxima            | Búsqueda específica                     |

[Ver `docs/AUDIT_DECISIONS.md` para las 40 decisiones completas]

## 🎯 Arquitectura Simplificada

```
Usuario → API (localhost) → Services → RAG/Semantic → Ollama
              ↓                ↓
         WebSocket        SQLite + Weaviate

         GitService → EventBus → ReindexService
```

### Flujo Principal

1. **API** recibe request → valida y enruta
2. **ChatService** orquesta el procesamiento
3. **RAG** busca código relevante (70% semántico + 30% léxico)
4. **Semantic** construye prompts y resume
5. **Ollama** genera respuesta con `acolyte:latest`
6. **SQLite** guarda resúmenes (~90% reducción)
7. **Weaviate** indexa para búsqueda futura
8. **ReindexService** mantiene índice actualizado automáticamente

## 📁 Estructura de Módulos

```
src/acolyte/
├── api/         # HTTP endpoints (OpenAI compatible)
├── core/        # Infraestructura base
├── services/    # Lógica de negocio (6 servicios)
├── models/      # Esquemas Pydantic
├── embeddings/  # Vectorización con UniXcoder
├── semantic/    # Procesamiento NLP
├── rag/         # Búsqueda y recuperación
└── dream/       # Optimización profunda (DeepDream)
```

## 🔧 Configuración Principal (.acolyte)

```yaml
version: "1.0"
project:
  name: mi-proyecto
  path: .

model:
  name: qwen2.5-coder:3b # Base para acolyte:latest
  version_activa: "3b" # Versión actual en uso (3b|7b|14b|32b)
  context_size: 32768 # Límite TOTAL del modelo (32k para 3b)

# Dream System
dream:
  fatigue_threshold: 7.5
  emergency_threshold: 9.5
  cycle_duration_minutes: 5
  dream_folder_name: ".acolyte-dreams"

ports:
  weaviate: 8080
  ollama: 11434
  backend: 8000
# Ver examples/.acolyte.example para configuración completa
```

## ⚠️ GOTCHAS CRÍTICOS

| Problema                   | Incorrecto ❌                        | Correcto ✅                                                | Razón                           |
| -------------------------- | ------------------------------------ | ---------------------------------------------------------- | ------------------------------- |
| **FastAPI Header(None)**   | `x_id or generate_id()`              | `x_id if x_id is not None else generate_id()`              | Header(None) es truthy!         |
| **HybridSearch mal uso**   | Buscar conversaciones                | Solo para chunks de código                                 | Conversaciones usan SQL         |
| **MetricsCollector**       | `MetricsCollector(namespace="x")`    | `MetricsCollector()` + prefijos                            | No tiene parámetro namespace    |
| **Tests modifican código** | Cambiar código para tests            | Corregir los tests                                         | Tests pueden estar mal escritos |
| **Pydantic v1 métodos**    | `.parse_obj()`, `.json()`, `.dict()` | `.model_validate()`, `.model_dump_json()`, `.model_dump()` | Usando v2                       |
| **Patch sys.modules**      | `patch.dict('sys.modules', {...})`   | Patch en punto de uso                                      | Afecta todos los imports        |

## 📜 Reglas para IAs Colaborativas

### 1. Archivos y Testing

- Scripts de prueba en raíz con prefijo `claude_`
- NO borrar sin copia previa
- TODO código debe pasar: Black + Ruff + mypy + pytest
- Tests unitarios para TODA funcionalidad nueva
- Cobertura mínima: 90% en todos los archivos
- **ACTUALIZAR CHANGELOG después de cada cambio en el código**

### 2. Seguridad y Calidad

- Solo localhost (127.0.0.1)
- Validación con pathlib (NO path traversal)
- Git con GitPython (NO comandos shell)
- Logging asíncrono (latencia = 0)

### 3. Principio LOCAL Primero

- **NO añadir autenticación**: El usuario ya está autenticado en su OS
- **NO añadir rate limiting**: Un usuario puede usar su sistema ilimitadamente
- **NO over-engineering**: Si funciona para un usuario, está bien
- **SÍ a singletons**: Son seguros y simples para mono-usuario
- **SÍ a estado global**: Sin concurrencia = sin problemas
- **SÍ a strings simples**: No todo necesita ser un Enum

### 4. Convenciones

- Imports absolutos: `from acolyte.core.logging import logger`
- Conventional Commits: `feat:`, `fix:`, `docs:`, etc.
- Docstrings Google-style
- NO crear archivos sin preguntar
- **IMPORTANTE**: Actualizar SIEMPRE el archivo CHANGELOG cuando se hagan cambios en el código

### 4. Manejo de Funcionalidades No Implementadas

- Si una funcionalidad está marcada como PENDIENTE (❌) o parcial (🚧), informar al usuario del estado actual
- NO intentar usar funcionalidades al 0% salvo petición explícita de implementarlas
- Para funcionalidades parciales, usar solo las partes completadas (✅)

### 5. Marcadores de Código (TODO Tree Extension)

El usuario utiliza la extensión "Todo Tree" que escanea estos marcadores. **USAR SIEMPRE** este formato:

```python
# TODO: Descripción de lo que falta implementar
# FIXME: Bug o problema que necesita arreglo urgente
# HACK: Solución temporal que necesita refactoring
# NOTE: Información importante para otros desarrolladores
# REVIEW: Código que necesita revisión antes de producción
# OPTIMIZE: Código funcional pero puede mejorarse
```

**IMPORTANTE para CHANGELOG**: Cuando agregues TODOs al archivo CHANGELOG, SIEMPRE usa `# TODO` (con #) para que la extensión Todo Tree los detecte:

```
2025-07-03 15:02:00 +0200 - # TODO(cli): Show Docker build progress in real-time during 'acolyte start'
```

### 6. LECCIÓN CRÍTICA: Nunca modificar código fuente para hacer pasar tests

**PROBLEMA DOCUMENTADO**: Los tests pueden estar mal escritos y esperar comportamientos incorrectos.

**SOLUCIÓN INCORRECTA**: Modificar el código fuente para satisfacer tests mal escritos.

**SOLUCIÓN CORRECTA**:

- Si un test falla, primero verificar si el test está mal escrito
- Corregir los TESTS, no el código fuente
- El código fuente define el comportamiento correcto, no los tests

**Ejemplo real del proyecto**:

```python
# Test mal escrito esperaba:
MetricsCollector(namespace="semantic")  # NO existe este parámetro

# Corrección: cambiar el TEST a:
metrics = MetricsCollector()
metrics.increment("semantic.task_detector.count")
```

**REGLA DE ORO**: Si un test falla, primero verifica si el test está mal escrito antes de modificar código funcional.

### 7. Política de Comentarios en Código

**TODOS los comentarios deben estar en INGLÉS**. Al encontrar comentarios en español, cambiarlos a inglés.

**MANTENER solo estos comentarios**:

- Marcadores TODO/FIXME/HACK/NOTE/REVIEW/OPTIMIZE
- Lógica compleja no obvia
- Advertencias críticas de seguridad o bugs conocidos
- Valores mágicos que necesitan explicación

**ELIMINAR estos comentarios**:

- Descripciones obvias ("Initialize logger", "Return result")
- Documentación de arquitectura (mover a docs/ARCHITECTURE.md)
- Historia o decisiones pasadas (mover a docs/ARCHITECTURE.md)
- TODOs obsoletos o completados
- Explicaciones largas de diseño (mover a docs/)

### 8. Actualización del CHANGELOG - OBLIGATORIO

**SIEMPRE actualizar el archivo CHANGELOG después de hacer cambios en el código**:

1. **Formato del CHANGELOG**:
   ```
   # Changelog
   Todas las modificaciones siguen el formato [Keep a Changelog](https://keepachangelog.com) y versionado [SemVer](https://semver.org).
   
   ## [Unreleased]
   ### Added
   - Nueva funcionalidad o feature.
   ### Changed
   - Cambios en funcionalidades existentes.
   ### Deprecated
   - Funcionalidades marcadas para eliminación futura.
   ### Removed
   - Funcionalidades eliminadas.
   ### Fixed
   - Errores y bugs corregidos.
   ### Security
   - Mejoras de seguridad o vulnerabilidades solucionadas.
   
   ## [1.0.0] - 2025-07-03
   ### Added
   - Soporte inicial para memoria persistente en SQLite.
   - API REST `/v1/context/flush` para reiniciar contexto.
   ### Fixed
   - Error al cargar configuración cuando faltaba `docker-compose.yml`.
   ```

2. **Categorías de cambios**:
   - `Added`: Nueva funcionalidad o feature
   - `Changed`: Cambios en funcionalidades existentes
   - `Deprecated`: Funcionalidades marcadas para eliminación futura
   - `Removed`: Funcionalidades eliminadas  
   - `Fixed`: Errores y bugs corregidos
   - `Security`: Mejoras de seguridad o vulnerabilidades solucionadas

3. **Cuándo actualizar**:
   - Después de CUALQUIER cambio en archivos `.py`
   - Al modificar configuraciones importantes
   - Al actualizar documentación técnica
   - NO para cambios menores de formato o typos

4. **Ejemplo**:
   ```
   ## [Unreleased]
   ### Added
   - Nueva funcionalidad de validación en el CLI.
   - Soporte para GPU NVIDIA en Docker.
   
   ### Fixed
   - Corregido error 404 en endpoint `/api/index`.
   - Solucionado problema de permisos en directorio `/data/logs`.
   ```

## 🚀 Características Clave

### Sistema de Memoria

- **SQLite**: Resúmenes inteligentes (NO conversaciones completas)
- **Weaviate**: Vectores 768-dim con UniXcoder
- **Búsqueda asociativa**: Encuentra contextos relacionados automáticamente
- **Persistencia dual**: Metadatos + embeddings

### Sistema Dream (DeepDream)

- **Análisis profundo**: Como "Deep Search" pero para tu código
- **Fatiga inteligente**: Detecta cuando necesita optimización usando métricas Git
- **5 tipos de análisis**: Bugs, seguridad, performance, arquitectura, patrones
- **NeuralGraph integrado**: Analiza dependencias y predice impacto de cambios
- **Ventana deslizante**: Para modelos 32k mantiene contexto entre ciclos
- **Siempre pide permiso**: Nunca se activa automáticamente
- **Sugiere solo cuando**: Fatiga alta + usuario trabajando con código + >2h desde último análisis

### Gestión de Tokens

- **context_size = límite TOTAL** (no por mensaje)
- **NUNCA usar tiktoken**: Sistema 100% local, no dependencias de OpenAI
- **Token counting**: Usar el contador interno basado en el modelo local
- **Distribución dinámica**:
  - Generación de código: 75% respuesta / 25% contexto
  - Preguntas simples: 20% respuesta / 80% contexto
  - Por defecto: 10% respuesta / 90% contexto

### Sistema de IDs Unificado

- **Formato único**: hex32 via `generate_id()`
- **Importar siempre**: `from acolyte.core.id_generator import generate_id`
- **Compatible**: Python + SQLite + Weaviate

### Cache Coordinado

- **EventBus**: Sistema pub/sub para invalidación
- **Flujo**: Git detecta cambios → Publica evento → Services invalidan cache
- **TTL**: 5 minutos para objetos pesados (repo Git)

## 📊 Decisiones Arquitectónicas Principales

1. **Resúmenes vs Conversaciones**: SQLite guarda resúmenes (~90% reducción)
2. **Sin autenticación**: Sistema mono-usuario local
3. **Sin rate limiting**: Uso ilimitado
4. **Git reactivo**: NO fetch automático, solo reacciona a cambios del usuario
5. **Jerarquía clara**: Task > Session > Message
6. **Dream es técnico**: Optimizador real, no antropomorfización
7. **18 ChunkTypes**: Precisión en búsqueda de código
8. **Errores consolidados**: Todo en `core/exceptions.py`
9. **🔥 Tree-sitter para chunking**: AST real para TODOS los lenguajes, NO regex. El chunking inteligente ES la ventaja competitiva de ACOLYTE

[Ver AUDIT_DECISIONS.md para las 40 decisiones completas]

## 🔄 Estado de Implementación Detallado

### ✅ Completado (100% funcional)

- **API OpenAI-compatible**: `/v1/chat/completions`, `/v1/embeddings`, `/v1/models`
- **ConversationService**: Persistencia dual, búsqueda SQL directa
- **TaskService**: Jerarquía completa, decisiones técnicas
- **ChatService**: Orquestación con retry logic, distribución dinámica de tokens, integración Dream
- **GitService**: Operaciones reactivas, cache TTL, notificaciones
- **IndexingService**: Pipeline completo de indexación automática
- **ReindexService**: Sistema dedicado de re-indexación automática con cola y deduplicación
- **HybridSearch (RAG)**: 70% semántica + 30% léxica con re-ranking
- **CompressionService (RAG)**: <50ms latencia, 60-80% ahorro en queries
- **ChunkingService (RAG)**: 31 lenguajes con tree-sitter + pattern matching
- **EnrichmentService**: Metadata Git completa con todas las métricas
- **Sistema EventBus**: WebSocket progress con pub/sub
- **Embeddings**: UniXcoder 768 dims, cache persistente
- **Semantic**: 6 módulos (Summarizer, PromptBuilder, TaskDetector, etc.)
- **Dream System**: Análisis profundo completamente operativo

### Estado Actual de Módulos

- **Core**: Excelente cobertura (mayoría al 100%)
- **Models**: 100% cobertura en TODOS los archivos
- **Embeddings**: Muy buena cobertura (mayoría >95%)
- **API**: Excelente cobertura (mayoría >90%)
- **Services**: Excelente cobertura (todos >90%)
- **Semantic**: Excelente cobertura (mayoría >95%)
- **Dream**: Excelente cobertura (todos >95%)
- **RAG**: Buena cobertura general
  - Retrieval: Excelente (mayoría >90%)
  - Compression: Muy buena (mayoría >90%)
  - Collections: Excelente (mayoría >90%)
  - Enrichment: Buena (>85%)
  - Graph: Excelente (mayoría >95%)
  - Chunking: Base excelente, lenguajes mixto pero mejorado

### Detalles Técnicos de Chunkers

#### Metadata Completa Implementada (27/31)

Todos estos chunkers extraen Y asignan metadata específica del lenguaje:

- **Python**: is_async, decorators, type_hints, complexity, patterns
- **Ruby**: visibility, is_singleton, has_yield, attr_accessors
- **Java**: annotations, implements, extends, generics, throws
- **TypeScript**: React/Angular/Vue patterns, JSDoc, decorators
- **Go**: goroutines, channels, defer count, struct tags
- **Rust**: lifetimes, generics, is_unsafe, attributes
- **SQL**: statement_type, dependencies, security (injection)
- **XML**: namespaces, Maven dependencies, security patterns
- Y 19 más con metadata completa...

#### Limitaciones de Cobertura

**Ruby (77%) y R (75%)** tienen cobertura máxima alcanzable:

- Naturaleza dinámica de los lenguajes
- Limitaciones de tree-sitter para ciertos patrones
- No intentar aumentar más su cobertura

#### Estado de Tests

**Tests completos implementados para los 31 lenguajes**:

- Ver `/tests/rag/chunking/` para todos los archivos de test
- Cada lenguaje tiene su archivo `test_[language]_chunker_complete.py`
- Cobertura general del módulo RAG/chunking: >90%

## 🎉 Sistema Funcional Completo

ACOLYTE está completamente implementado y operativo. Solo quedan tareas de mejora y documentación.

## 💡 Tips para IAs Colaborativas

### Carga Selectiva de Documentación

Cada módulo tiene documentación fragmentada en `docs/`:

- `README.md` - Índice general
- `ARCHITECTURE.md` - Diseño y decisiones
- `STATUS.md` - Estado actual
- `REFERENCE.md` - API completa
- `WORKFLOWS.md` - Flujos y ejemplos
- `INTEGRATION.md` - Dependencias

**Ejemplo**: Para trabajar con Dream:

```
Dame README.md de dream          # Ver overview del módulo
Dame orchestrator.py de dream    # Ver implementación principal
Dame WORKFLOWS.md de api         # Ver cómo se conecta con API
```

### Antes de Implementar

1. Verificar en STATUS.md si ya existe
2. Revisar INTEGRATION.md para dependencias
3. Consultar WORKFLOWS.md para flujos similares

### Al Generar Código

1. Usar `generate_id()` para TODOS los IDs
2. Importar errores desde Core: `from acolyte.core.exceptions import ...`
3. Composición sobre herencia para métricas
4. Cache consistente: max_size=1000, ttl=3600
5. Comentarios SIEMPRE en inglés

## 🔧 Patrones de Implementación

### Logging - Usar logger Global

**Importar logger global, NO crear instancias de AsyncLogger**:

```python
# ✅ CORRECTO - Patrón usado en TODO el proyecto
from acolyte.core.logging import logger

class MyService:
    def __init__(self):
        logger.info("MyService initialized")

    async def process(self):
        logger.info("Processing started", item_count=10)
        try:
            # ...
        except Exception as e:
            logger.error("Processing failed", error=str(e))

# ❌ INCORRECTO - NO crear instancias de AsyncLogger
self.logger = AsyncLogger("my_service")  # NO hacer esto
```

**Características del logging**:

- Singleton global ya configurado
- Sin emojis, formato plano
- Latencia cero (QueueHandler)
- Enmascarar datos sensibles automáticamente
- Include stack trace con `logger.error("msg", error=str(e))`

**Performance logging**:

```python
from acolyte.core.logging import PerformanceLogger

perf_logger = PerformanceLogger()

# Usar con context manager
with perf_logger.measure("database_query", query=sql):
    result = await db.execute(sql)
# Automáticamente registra duración en ms
```

### Testing - Patrones y Convenciones

**Estructura de tests**:

```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestMyService:
    """Agrupar tests por clase."""

    @pytest.fixture
    async def service(self):
        """Fixture con todas las dependencias mockeadas."""
        with patch('acolyte.services.my_service.HeavyDependency'):
            service = MyService()
            service.dep = AsyncMock()  # Mock explícito
            yield service
```

**Mocking de dependencias pesadas**:

```python
# Evitar imports de torch, weaviate, etc en tests
# Ver sección Testing para detalles
```

**Markers especiales**:

```python
@pytest.mark.requires_internet  # Tests que necesitan conexión
@pytest.mark.slow              # Tests >10 segundos
@pytest.mark.ml                # Tests que requieren modelos ML
```

**AsyncMock vs Mock**:

- `AsyncMock` para métodos async
- `Mock` para métodos síncronos
- `MagicMock` cuando necesitas magic methods

### Testing - NO usar sys.modules

**❌ INCORRECTO - Pattern encontrado en algunos tests**:

```python
# NO hacer esto - modifica el comportamiento global de imports
@pytest.fixture(autouse=True)
def mock_weaviate_globally():
    with patch.dict('sys.modules', {'weaviate': MagicMock()}):
        yield
```

**✅ CORRECTO - Mockear en el punto de uso**:

```python
# Opción 1: Patch donde se importa
with patch('acolyte.services.chat_service.weaviate'):
    service = ChatService()

# Opción 2: Inyectar dependencias
def __init__(self, weaviate_client=None):
    self.client = weaviate_client or self._create_client()

# Opción 3: Patch múltiples imports
with (
    patch('acolyte.services.chat_service.OllamaClient'),
    patch('acolyte.services.chat_service.ConversationService'),
    patch('acolyte.services.chat_service.HybridSearch')
):
    service = ChatService()
```

**Razón**: `patch.dict('sys.modules')` afecta TODOS los imports en el proceso de test, causando efectos secundarios impredecibles.

### Testing - Uso de unittest.mock

**Imports estándar**:

```python
from unittest.mock import Mock, AsyncMock, patch, MagicMock
```

**AsyncMock para métodos async**:

```python
# Para métodos async
service.process = AsyncMock(return_value={"status": "ok"})
await service.process()  # Debe ser awaited

# Para async context managers
async_cm = AsyncMock()
async_cm.__aenter__.return_value = mock_response
async_cm.__aexit__.return_value = None
mock_session.post.return_value = async_cm
```

**Mock fixtures con cleanup**:

```python
@pytest.fixture
async def service():
    """Service con todas las dependencias mockeadas."""
    with patch('acolyte.services.my_service.HeavyDependency'):
        service = MyService()
        service.dep = AsyncMock()
        yield service
        # Cleanup automático al salir del fixture
```

**Verificación de llamadas**:

```python
# Verificar que se llamó
mock.assert_called_once()
mock.assert_called_once_with(arg1="value", arg2=42)

# Verificar múltiples llamadas
assert mock.call_count == 3
calls = [call("first"), call("second"), call("third")]
mock.assert_has_calls(calls, any_order=True)

# Para AsyncMock
mock.assert_awaited_once()
mock.assert_awaited_with("expected", "args")
```

### Pydantic v2 - Patrones Correctos

**ConfigDict en lugar de Config class**:

```python
# ✅ CORRECTO - Pydantic v2
from pydantic import BaseModel, Field, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid",
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v),
        }
    )

# ❌ INCORRECTO - Pydantic v1
class MyModel(BaseModel):
    class Config:
        validate_assignment = True  # NO usar
```

**Validación y serialización**:

```python
# ✅ CORRECTO - v2
data = {"name": "test", "age": 30}
model = MyModel.model_validate(data)  # De dict a modelo
json_str = model.model_dump_json()    # A JSON string
dict_data = model.model_dump()         # A dict

# Con exclusión
dict_data = model.model_dump(exclude={"internal_field"})

# ❌ INCORRECTO - v1
model = MyModel.parse_obj(data)       # NO existe en v2
json_str = model.json()               # NO existe en v2
dict_data = model.dict()              # NO existe en v2
```

**Field con default_factory**:

```python
# ✅ CORRECTO
from pydantic import Field

class MyModel(BaseModel):
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = Field(default_factory=list)

# ❌ INCORRECTO
tags: List[str] = []  # Mutable default compartido!
```

### Type Stubs (.pyi) - Cuándo y Cómo

**Cuándo crear stubs**:

1. Módulos con lógica compleja donde los tipos ayudan al IDE
2. APIs públicas que otros módulos importan
3. Cuando mypy no puede inferir tipos correctamente

**Formato correcto**:

```python
# archivo: models/base.pyi
from datetime import datetime
from typing import Optional, Protocol, runtime_checkable
from pydantic import BaseModel, Field

class TimestampMixin(BaseModel):
    created_at: datetime = Field(...)
    updated_at: Optional[datetime] = Field(default=None)

    def touch(self) -> None: ...

@runtime_checkable
class Identifiable(Protocol):
    @property
    def primary_key(self) -> str: ...
    @property
    def primary_key_field(self) -> str: ...

def get_model_primary_key(model: Identifiable) -> str: ...
```

**Reglas para stubs**:

- Solo firmas de tipos, sin implementación
- Usar `...` para cuerpos de funciones
- Sin docstrings ni comentarios
- Incluir decoradores importantes (@property, @runtime_checkable)
- Mantener sincronizado con el .py

### Async/Await - Patrones Correctos

**Context managers async**:

```python
# Definir
class AsyncResource:
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

# Usar
async with AsyncResource() as resource:
    await resource.process()
```

**Concurrencia con asyncio.gather**:

```python
# Ejecutar múltiples operaciones en paralelo
results = await asyncio.gather(
    self.analyze_bugs(code),
    self.analyze_security(code),
    self.analyze_performance(code),
    return_exceptions=True  # No fallar si una falla
)

# Manejar excepciones individuales
for i, result in enumerate(results):
    if isinstance(result, Exception):
        logger.error(f"Analysis {i} failed", error=str(result))
```

**Timeouts y cancelación**:

```python
try:
    async with asyncio.timeout(30):  # Python 3.11+
        result = await long_operation()
except asyncio.TimeoutError:
    logger.warning("Operation timed out")

# Para Python < 3.11
try:
    result = await asyncio.wait_for(long_operation(), timeout=30)
except asyncio.TimeoutError:
    pass
```

### Dependency Injection

**Constructor injection**:

```python
class ChatService:
    def __init__(
        self,
        context_size: int = 4096,
        conversation_service: Optional[ConversationService] = None,
        task_service: Optional[TaskService] = None,
        ollama_client: Optional[OllamaClient] = None
    ):
        # Usar inyectadas o crear defaults
        self.conversation_service = conversation_service or ConversationService()
        self.task_service = task_service or TaskService()
        self.ollama = ollama_client or OllamaClient()
```

**Factory pattern para dependencias opcionales**:

```python
def _create_weaviate_client(self) -> Optional[WeaviateClient]:
    """Crear cliente solo si Weaviate está disponible."""
    try:
        import weaviate
        client = weaviate.Client(f"http://localhost:{self.port}")
        if client.is_ready():
            return client
    except Exception as e:
        logger.warning("Weaviate not available", error=str(e))
    return None
```

### Configuration Pattern

**NO usar pydantic-settings, usar clase custom**:

```python
# ✅ CORRECTO - Patrón usado en el proyecto
from acolyte.core.secure_config import Settings

config = Settings()  # Singleton
value = config.get("model.name", "default")
required = config.require("project.name")  # Lanza excepción si no existe

# ❌ INCORRECTO - No usar pydantic BaseSettings
from pydantic_settings import BaseSettings
class Settings(BaseSettings):  # NO hacer esto
    model_config = SettingsConfigDict(env_prefix="ACOLYTE_")
```

### Error Handling - Jerarquía y Uso

**Jerarquía de excepciones**:

```python
AcolyteError (base)
├── ValidationError      # Datos inválidos del usuario
├── ConfigurationError   # Configuración incorrecta
├── NotFoundError       # Recurso no encontrado
├── DatabaseError       # Errores de BD
│   └── is_retryable() -> bool
└── ExternalServiceError # Servicios externos (Ollama, Weaviate)
    └── is_retryable() -> bool
```

**Uso con sugerencias**:

```python
try:
    result = await db.execute(query)
except DatabaseError as e:
    if e.is_retryable():
        # Reintentar con backoff
        await asyncio.sleep(2 ** attempt)
        return await retry()

    # Agregar contexto útil
    e.add_suggestion("Verificar que .acolyte.db existe")
    e.add_suggestion("Comprobar permisos de escritura")
    raise
```

**Logging de errores**:

```python
try:
    await risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        operation="risky_operation",
        error=str(e),
        error_type=type(e).__name__,
        traceback=traceback.format_exc()
    )
    raise  # Re-raise después de loggear
```

### Manejo de IDs

**SIEMPRE usar generate_id()**:

```python
from acolyte.core.id_generator import generate_id

# CORRECTO
new_id = generate_id()  # hex32 sin guiones

# INCORRECTO
import uuid
new_id = str(uuid.uuid4())  # NO usar
```

## 🎯 Métricas de Calidad (Gatekeepers)

- ✅ 100% tests passing
- ✅ 0 Ruff warnings
- ✅ Coverage ≥ 90%
- ✅ p95 latency ≤ 5s
- ✅ 0 duplicados en Weaviate
- ✅ Logging latency = 0

## 📝 TODOs Consolidados

### Críticos para Producción

1. **Documentación de Usuario** (0% completada)

   - Guía de instalación detallada
   - Tutoriales paso a paso
   - Ejemplos de uso de Dream
   - API reference completa
   - Videos demostrativos

2. **Tests de Integración End-to-End** (0% implementados)

   - Flujo completo de indexación
   - Conversación multi-sesión
   - Activación y ciclo Dream
   - Integración con Git hooks

3. **Integración con IDEs** (Pendiente decisión)
   - Evaluar Cline vs Continue.dev
   - Implementar protocolo LSP básico
   - Plugin para VS Code
   - Soporte para comandos inline

### Mejoras Futuras

4. **Helpers de datetime centralizados** ✅ **IMPLEMENTADO - Decisión #41**

   - Creado `core/utils/datetime_utils.py` con helpers: `utc_now()`, `utc_now_iso()`, `parse_iso_datetime()`, `format_iso()`
   - **Aplicar durante auditoría**: Migrar cada archivo mientras se revisa
   - Reemplazar `datetime.utcnow()` → `utc_now()`
   - Reemplazar `datetime.utcnow().isoformat()` → `utc_now_iso()`

5. **CLI Commands**

   - `acolyte vacuum` - Limpieza de BD
   - `acolyte stats` - Estadísticas de uso
   - `acolyte export` - Exportar insights

6. **Dashboard Web**
   - Interfaz visual para métricas
   - Visualización del grafo neuronal
   - Historial de análisis Dream

## 🚀 Casos de Uso Comunes

### 1. Entender un Codebase Nuevo

```
Tú: "Dame un overview de la arquitectura de este proyecto"
ACOLYTE: "Este es una aplicación FastAPI con 3 componentes principales:
- Módulo Auth: Autenticación JWT con refresh tokens
- Capa API: Endpoints RESTful con docs OpenAPI automáticos
- Database: PostgreSQL con SQLAlchemy ORM..."
```

### 2. Debugging con Contexto

```
Tú: "Por qué obtengo error 401 al llamar /api/users?"
ACOLYTE: "Mirando tu middleware de auth en auth/middleware.py:45,
la validación del token falla porque... [muestra código relevante]"
```

### 3. Ayuda con Implementación

```
Tú: "Implementa un rate limiter para la API"
ACOLYTE: "Basándome en tu arquitectura actual, aquí está un
rate limiter basado en Redis que se integra con tu middleware..."
[genera código que encaja con TU estilo de proyecto]
```

### 4. Code Review

```
Tú: "Revisa los cambios en mi último commit"
ACOLYTE: "Encontré 3 issues en commit a1b2c3d:
1. Potencial SQL injection en la nueva función de búsqueda
2. Falta manejo de errores en el procesador de pagos
3. El nuevo endpoint de API no tiene autenticación..."
```

## 🛠️ Troubleshooting

### ACOLYTE no arranca

```bash
# Verificar si los servicios están corriendo
acolyte status

# Ver logs detallados
acolyte logs --tail 50

# Reset y reiniciar
acolyte reset
acolyte start
```

### Errores de memoria

- Reducir `batch_size` en configuración
- Usar modelo más pequeño (3B en vez de 7B)
- Aumentar swap del sistema

### Respuestas lentas

- Verificar si Dream está corriendo: `acolyte dream status`
- Verificar que Ollama usa GPU: `ollama list`
- Reducir `max_chunks_in_context` en settings de búsqueda

### Weaviate no conecta

```bash
# Verificar que Weaviate está corriendo
docker ps | grep weaviate

# Reiniciar Weaviate
docker restart weaviate

# Verificar puerto
netstat -an | grep 8080

# Si el puerto está ocupado, cambiar en .acolyte:
# ports:
#   weaviate: 8081
```

### SQLite "database is locked"

- ACOLYTE maneja reintentos automáticos
- Si persiste, cerrar otras aplicaciones que accedan a .acolyte.db
- Último recurso: `acolyte db repair`

### Ollama timeout en respuestas

```bash
# Verificar que Ollama está corriendo
ollama list

# Verificar modelo cargado
ollama ps

# Pre-cargar modelo
ollama run acolyte:latest

# Si falla, verificar VRAM disponible
nvidia-smi  # Para GPUs NVIDIA
```

### Indexación no encuentra archivos

- Verificar `.acolyteignore` no esté excluyendo archivos deseados
- Confirmar extensiones soportadas (ver lista en prompt)
- Verificar permisos de lectura en directorios

### WebSocket se desconecta frecuentemente

- Aumentar `heartbeat_interval` en .acolyte (max 300s)
- Verificar configuración de proxy reverso si aplica
- Deshabilitar suspensión de red en el OS

### Git service errores

```bash
# Verificar que es un repositorio Git válido
git status

# Si no está inicializado
git init

# Si hay problemas de permisos
chmod -R u+rw .git/
```

### Embeddings fallan

- Verificar UniXcoder se descargó correctamente
- Primera ejecución descarga ~350MB, requiere internet
- Cache en `~/.cache/huggingface/`
- Si falla: `rm -rf ~/.cache/huggingface/hub/models--microsoft--unixcoder-base/`

### Dream se activa muy seguido

- Aumentar `fatigue_threshold` en .acolyte (default 7.5, max ~15)
- Verificar que no haya loops de cambios en Git
- Temporalmente deshabilitar: `dream.enabled: false`

### Tests fallan después de actualizar

```bash
# Limpiar caches de Python
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reinstalar dependencias
poetry install --no-cache

# Correr tests con output verbose
poetry run pytest -xvs tests/
```

### Puerto 8000 ocupado

```bash
# Encontrar proceso usando el puerto
lsof -i :8000

# Cambiar puerto en .acolyte:
# ports:
#   backend: 8001
```

---

**Recuerda**: Este es un proyecto LOCAL y PRIVADO. Toda decisión debe optimizar para un único usuario con control total sobre su máquina.

**ACOLYTE está funcionalmente completo. La prioridad ahora es documentación de usuario e integración con IDEs.**

---

> Por favor, cuando generes código:
>
> - Usa Optional en los tipos de los parámetros y retornos si pueden ser None o faltar.
> - No pongas None como valor por defecto si el tipo no lo permite.
> - Inicializa listas y diccionarios vacíos si es necesario.
> - Asegúrate de que los tipos de retorno siempre cumplen con lo que espera el tipado.
> - Haz que el código pase un chequeo de tipado estricto (mypy o pyright).

## ⚠️ Errores Comunes a Evitar

### 1. NO usar HybridSearch para conversaciones

```python
# ❌ INCORRECTO - HybridSearch es SOLO para chunks de código
results = await self.hybrid_search.search(session_id=session)

# ✅ CORRECTO - Usar búsqueda SQL directa
results = await self._search_sessions_sql(query)
```

**HybridSearch es exclusivamente para buscar código en Weaviate, NO conversaciones en SQLite**

### 2. NO modificar código fuente para hacer pasar tests

```python
# Si un test falla esperando MetricsCollector(namespace="semantic")
# NO cambies MetricsCollector para aceptar namespace
# En su lugar, corrige el TEST:

# ❌ MAL - Modificar el código fuente
class MetricsCollector:
    def __init__(self, namespace=None):  # NO hacer esto

# ✅ BIEN - Corregir el test
self.metrics = MetricsCollector()
self.metrics.increment("semantic.task_detector.count")
```

### 3. NO usar print() para debugging

```python
# ❌ INCORRECTO
print(f"DEBUG: Processing {item}")  # Se queda en producción

# ✅ CORRECTO
self.logger.debug("Processing item", item=item)  # Controlado por config
```

### 4. NO hardcodear paths o asumir estructura

```python
# ❌ INCORRECTO
config_path = "/home/user/project/.acolyte"  # Path absoluto
indexing_path = "src/acolyte/rag/indexing/"  # NO EXISTE

# ✅ CORRECTO
config_path = Path(".acolyte")  # Relativo
indexing_service = "src/acolyte/services/indexing_service.py"  # Path real
```

### 5. NO ignorar el tipo de chunker

```python
# ❌ INCORRECTO - Asumir que todos usan tree-sitter
for lang in all_languages:
    chunker.parse_with_tree_sitter()  # Falla en C#, Swift, etc

# ✅ CORRECTO - Verificar capacidades
if hasattr(chunker, '_get_tree_sitter_language'):
    # Es tree-sitter based
else:
    # Es pattern matching based
```

### 6. NO crear archivos sin confirmar

```python
# ❌ INCORRECTO
with open("test_output.py", "w") as f:
    f.write(code)  # Crea archivo sin preguntar

# ✅ CORRECTO
# Primero mostrar el código al usuario
# Preguntar: "¿Deseas que cree el archivo test_output.py?"
# Solo crear si confirma
```

### 7. NO usar patch.dict('sys.modules') en tests

```python
# ❌ INCORRECTO - Encontrado en test_chat_service.py
@pytest.fixture(autouse=True)
def mock_weaviate_globally():
    with patch.dict('sys.modules', {'weaviate': MagicMock()}):
        yield

# ✅ CORRECTO - Mockear donde se usa
with patch('acolyte.services.chat_service.weaviate'):
    service = ChatService()
```

**Problema**: Modifica el comportamiento global de imports afectando otros tests.

### 8. NO usar métodos obsoletos de Pydantic v1

```python
# ❌ INCORRECTO - Pydantic v1
model = MyModel.parse_obj(data)
json_str = model.json()
dict_data = model.dict()

# ✅ CORRECTO - Pydantic v2
model = MyModel.model_validate(data)
json_str = model.model_dump_json()
dict_data = model.model_dump()
```

### 9. NO olvidar actualizar el CHANGELOG

```bash
# ❌ INCORRECTO - Hacer cambios sin documentar
# Modificar archivos .py y no actualizar CHANGELOG

# ✅ CORRECTO - Actualizar CHANGELOG después de cambios
# 1. Hacer los cambios en el código
# 2. Añadir entrada en CHANGELOG con formato:
# YYYY-MM-DD HH:MM:SS +ZONE - tipo(módulo): Descripción
```

**RECORDATORIO**: El CHANGELOG es la historia del proyecto. SIEMPRE debe estar actualizado.

## 🗺️ Arquitectura de Datos - Dónde Están las Piezas

### SQLite - Base de Datos Principal

**Archivos clave**:

- **Core**: `/core/database.py` - DatabaseManager + InsightStore
- **Schemas**: `/core/database_schemas/schemas.sql` - Todas las tablas
- **Archivo BD**: `./data/acolyte.db` (generado en runtime)

**Tablas principales**:

1. `conversations` - Historial de chat
2. `tasks` - Agrupación de sesiones
3. `task_sessions` - Relación many-to-many
4. `technical_decisions` - Decisiones arquitectónicas
5. `dream_state` - Estado del optimizador (singleton)
6. `dream_insights` - Descubrimientos del análisis

**Quién usa SQLite**:

- `/services/conversation_service.py` - Maneja conversations
- `/services/task_service.py` - Maneja tasks, sessions, decisions
- `/dream/` (futuro) - Usará InsightStore para dream_insights

### Weaviate - Base de Datos Vectorial

**Conexión principal**:

```python
# En ChatService (/services/chat_service.py)
import weaviate
self.weaviate_client = weaviate.Client(f"http://localhost:{port}")
```

**Archivos que usan Weaviate directamente**:

1. `/services/chat_service.py` - Inicializa cliente, lo pasa a otros
2. `/rag/retrieval/hybrid_search.py` - Búsqueda semántica y léxica
3. `/rag/collections/manager.py` - Gestión de colecciones
4. `/services/indexing_service.py` - Indexa chunks en Weaviate
5. `/dream/fatigue_monitor.py` (cuando exista) - Análisis de código

**Colección principal**: `CodeChunk`

- Contiene todos los chunks de código indexados
- Embeddings de 768 dimensiones (UniXcoder)
- Metadata: file_path, language, chunk_type, etc.

### Patrón de Acceso a Datos

```python
# SQLite - Via DatabaseManager
from acolyte.core.database import get_db_manager
db = get_db_manager()
result = await db.execute_async(query, params, FetchType.ALL)

# Weaviate - Via cliente directo
self.weaviate_client.query.get("CodeChunk", [...]).with_near_vector(...).do()
```

## ⚙️ Sistema de Configuración

### Archivo .acolyte - Fuente de Verdad

**Ubicación**: `/.acolyte` en la raíz del proyecto

**Ejemplo completo**:

```yaml
version: "1.0"
project:
  name: "mi-proyecto-genial"
  path: "." # SIEMPRE relativo, nunca absoluto

model:
  name: "qwen2.5-coder:3b" # SOLO qwen2.5-coder:* o acolyte:latest
  context_size: 32768

ports:
  weaviate: 8080
  ollama: 11434
  backend: 8000 # API de ACOLYTE

dream:
  fatigue_threshold: 7.5
  emergency_threshold: 9.5
  cycle_duration_minutes: 5

cache:
  max_size: 1000
  ttl_seconds: 3600

rag:
  compression:
    ratio: 0.7
    avg_chunk_tokens: 200
```

### Acceso a Configuración

```python
from acolyte.core.secure_config import Settings

# Singleton - siempre la misma instancia
config = Settings()

# Acceso con dot notation
model_name = config.get("model.name")  # "qwen2.5-coder:3b"
port = config.get("ports.backend", 8000)  # Con default

# Requerir valor (lanza excepción si no existe)
project_name = config.require("project.name")
```

### Validaciones Automáticas

1. **Modelos permitidos**: SOLO `qwen2.5-coder:*` o `acolyte:latest`
2. **Puertos**: Solo localhost, rango 1024-65535
3. **Paths**: Siempre relativos, sin `..` ni paths absolutos
4. **Tipos**: Validación automática de tipos

### Variables de Entorno (Desarrollo)

```bash
# Solo estas 3 se pueden override
ACOLYTE_PORT=8001         # Puerto del backend
ACOLYTE_LOG_LEVEL=DEBUG   # Nivel de logging
ACOLYTE_MODEL=acolyte:latest  # Modelo a usar
```

### Configuración por Módulo

**Services**:

- Todos usan `Settings()` para puertos y timeouts
- ChatService lee `model.*` para Ollama
- IndexingService lee `rag.indexing.*`

**RAG**:

- HybridSearch lee `rag.search.*` para pesos
- Compression lee `rag.compression.*`
- Cache lee `cache.*`

**Dream**:

- Lee `dream.*` para umbrales y duraciones
- FatigueMonitor usa `dream.fatigue_threshold`

## 🔄 Flujo de Trabajo Típico

### 1. Usuario envía mensaje

```python
# API recibe POST /v1/chat/completions
# O WebSocket para streaming
{
  "message": "Implementa autenticación JWT",
  "session_id": "optional-session-id"
}
```

### 2. ChatService orquesta

```python
# ChatService.process_message()
1. Carga contexto previo (ConversationService)
2. Analiza intención (QueryAnalyzer)
3. Detecta si es nueva tarea (TaskDetector)
4. Busca código relevante (HybridSearch)
5. Construye prompt dinámico (PromptBuilder)
6. Genera respuesta (Ollama)
7. Resume conversación (Summarizer)
8. Detecta decisiones (DecisionDetector)
9. Persiste todo (Services)
10. Sugiere Dream si fatiga alta
```

### 3. Flujo de búsqueda RAG

```python
# HybridSearch.search()
1. Busca en cache primero
2. Búsqueda semántica (70%) - Weaviate embeddings
3. Búsqueda léxica (30%) - Weaviate BM25
4. Combina y re-rankea resultados
5. Opcionalmente comprime chunks
6. Cachea resultados
```

### 4. Indexación de código (background)

```python
# IndexingService.index_directory()
1. Escanea archivos del proyecto
2. ChunkerFactory selecciona chunker por lenguaje
3. Divide en chunks semánticos (funciones, clases)
4. Enriquece con metadata Git
5. Genera embeddings (UniXcoder)
6. Guarda en Weaviate
```

### 5. Análisis Dream (cuando se activa)

```python
# DreamOrchestrator.start_analysis()
1. Calcula fatiga del código (cambios, complejidad)
2. Ejecuta 5 analizadores en paralelo
3. Usa NeuralGraph para dependencias
4. Consolida hallazgos
5. Escribe insights a BD y markdown
6. Notifica al usuario
```

### Puntos de Extensión

- **Nuevos chunkers**: Agregar en `/rag/chunking/languages/`
- **Nuevos analizadores**: Agregar en `/dream/analyzers/`
- **Nuevos endpoints**: Agregar en `/api/`
- **Nuevos servicios**: Agregar en `/services/`

## 🔨 Patrones de Implementación Avanzados

Para patrones detallados de implementación, consultar [`docs/PROMPT_PATTERNS.md`](PROMPT_PATTERNS.md):
(ESTE DOCUMENTO ES OBLIGATORIO LEERLO JUNTO A PROMPT, ES UNA EXTENDION DE PROMPT, usar filesystem_read_file inmediatamente )

### 📊 Patrones de Persistencia (Base de Datos)

- DatabaseManager - Gestión de Conexiones SQLite
- Clasificación de Errores SQLite
- Patrón execute_async con FetchType
- Retry Logic para Operaciones de BD
- Transacciones con Context Manager
- InsightStore - Compresión zlib

### 🔍 Patrones de Búsqueda Vectorial (Weaviate)

- HybridSearch - Búsqueda 70/30
- Fuzzy Query Expansion
- Filtros en Weaviate Queries
- Normalización de Scores
- Graph Expansion para Búsqueda

### 🚀 Patrones de Performance (Cache)

- LRU Cache con TTL
- Cache Key Hashing
- Invalidación por Patrón
- Compression con Token Budget
- Batch Processing - 95%+ mejora de rendimiento

### 🔄 Patrones de Serialización

- JSON con datetime ISO
- Arrays JSON en SQLite
- Compresión zlib para BLOBs

### 📁 Patrones de Archivos y I/O

- Path Validation Segura
- Archivos Soportados Pattern

### 📊 Patrones de Métricas y Monitoring

- MetricsCollector sin Namespace
- Performance Logging Pattern

### 🔄 Patrones de Concurrencia

- asyncio.gather con return_exceptions
- Queue Pattern para WebSocket

### 🔌 Patrones de Integración Git

- GitPython Lazy Loading
- Git Diff Parsing

### 🌐 Patrones de Servicios Externos

- Ollama Client con Retry
- Weaviate Health Check
