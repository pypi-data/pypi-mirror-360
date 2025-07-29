# 🖥️ Dashboard Web para ACOLYTE

## 📋 ¿Qué es?

El Dashboard Web es una interfaz gráfica de usuario (GUI) que permitirá controlar ACOLYTE desde el navegador en lugar de usar solo comandos o la API. Será una aplicación web que se conecte a los endpoints ya existentes de ACOLYTE.

### Componentes principales:
- **Panel de indexación**: Ver qué archivos están indexados y lanzar nuevas indexaciones
- **Visor de conversaciones**: Historial de chats con ACOLYTE
- **Monitor de Dream**: Estado del optimizador y sus descubrimientos
- **Estadísticas**: Métricas de uso, archivos indexados, lenguajes, etc.

## 🎯 ¿Para qué vale?

### Beneficios inmediatos:
1. **Accesibilidad**: No todos los usuarios son cómodos con línea de comandos
2. **Visualización**: Ver estadísticas y progreso de forma visual
3. **Control fácil**: Botones para operaciones comunes (indexar, limpiar, optimizar)
4. **Monitoreo en tiempo real**: WebSockets ya implementados para actualizaciones en vivo

### Casos de uso específicos:
- **Indexación selectiva**: Marcar qué carpetas/archivos indexar con checkboxes
- **Búsqueda manual**: Probar búsquedas sin hacer preguntas completas
- **Gestión de sesiones**: Ver y continuar conversaciones anteriores
- **Control de Dream**: Activar análisis profundo con un clic

## 💡 ¿Por qué es óptimo?

### 1. **Endpoints ya listos**
```
✅ POST /api/index/project - Indexación completa
✅ POST /api/index/git-changes - Re-indexación incremental
✅ GET /api/stats - Estadísticas del sistema
✅ GET /api/health - Estado de servicios
✅ WS /api/ws/progress/{id} - Progreso en tiempo real
✅ GET /api/dream/status - Estado del optimizador
```

### 2. **Reduce fricción de adopción**
- Usuarios no técnicos pueden usar ACOLYTE
- Onboarding visual más intuitivo
- Feedback inmediato de operaciones

### 3. **Mejora la experiencia de desarrollo**
- Ver qué está indexado sin consultar Weaviate
- Depurar problemas visualmente
- Monitorear performance en tiempo real

### 4. **Consistencia con la filosofía mono-usuario**
- No necesita autenticación (localhost only)
- Puede ser muy simple y directo
- No requiere estado complejo

## 🏗️ ¿Cómo debería ser?

### Arquitectura propuesta:

```
Frontend (SPA)
├── React/Vue/Svelte (o vanilla JS para simplicidad)
├── Tailwind CSS para estilos rápidos
├── WebSocket client para actualizaciones
└── Build estático servido por FastAPI

Backend (Ya existente)
├── FastAPI endpoints
├── WebSocket manager
└── Static file serving
```

### Páginas principales:

#### 1. **Home / Overview**
- Cards con estadísticas generales
- Estado de servicios (Weaviate, Ollama, etc.)
- Accesos rápidos a operaciones comunes

#### 2. **Indexación**
```
┌─────────────────────────────────────┐
│ 📁 Project Files                    │
├─────────────────────────────────────┤
│ □ /src                    (2,341)   │
│   ☑ /src/acolyte         (1,234)   │
│   □ /src/tests             (567)   │
│ □ /docs                     (89)   │
│                                     │
│ [Index Selected] [Clear Index]      │
└─────────────────────────────────────┘
```

#### 3. **Conversaciones**
- Lista de sesiones anteriores
- Preview del último mensaje
- Botón para continuar conversación

#### 4. **Dream Monitor**
```
┌─────────────────────────────────────┐
│ 🧠 Optimization Status              │
├─────────────────────────────────────┤
│ Fatigue Level: ████░░░░ 4.5/10     │
│ Last Analysis: 2 hours ago          │
│ Insights Found: 23                  │
│                                     │
│ [Run Analysis Now]                  │
└─────────────────────────────────────┘
```

### Implementación paso a paso:

#### Fase 1: MVP Básico
1. **Setup inicial**
   - Crear carpeta `/frontend` en el proyecto
   - Configurar FastAPI para servir archivos estáticos
   - HTML + JavaScript vanilla para rapidez

2. **Página de indexación**
   - Árbol de archivos simple
   - Botón de indexar
   - Barra de progreso con WebSocket

3. **Página de estadísticas**
   - Mostrar respuesta de `/api/stats`
   - Gráficos simples con Chart.js

#### Fase 2: Mejoras UX
1. **Framework reactive** (React/Vue)
2. **Diseño responsivo**
3. **Notificaciones toast**
4. **Temas claro/oscuro**

#### Fase 3: Features avanzadas
1. **Editor de configuración** (.acolyte)
2. **Visor de logs** en tiempo real
3. **Terminal integrada** (xterm.js)
4. **Exportación de métricas**

### Código ejemplo para el inicio:

```python
# En api/main.py
from fastapi.staticfiles import StaticFiles

# Servir el dashboard
app.mount("/dashboard", StaticFiles(directory="frontend/dist", html=True), name="dashboard")

# Redirigir root al dashboard
@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")
```

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>ACOLYTE Dashboard</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-gray-100">
    <div class="container mx-auto p-8">
        <h1 class="text-4xl font-bold mb-8">🤖 ACOLYTE Control Panel</h1>
        
        <!-- Stats Cards -->
        <div hx-get="/api/stats" 
             hx-trigger="load, every 30s"
             hx-target="#stats">
            <div id="stats">Loading...</div>
        </div>
        
        <!-- Index Button -->
        <button hx-post="/api/index/project"
                hx-confirm="Index entire project?"
                class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">
            🔍 Index Project
        </button>
    </div>
</body>
</html>
```

### Consideraciones de diseño:

1. **Simplicidad sobre features**: Empezar con lo mínimo útil
2. **Sin build complex**: Poder desarrollar con solo un navegador
3. **Progresivo**: Añadir complejidad solo cuando se justifique
4. **Localhost only**: No preocuparse por seguridad web
5. **Real-time first**: Aprovechar WebSockets desde el día 1

### Métricas de éxito:
- Tiempo de indexación visible < 2 segundos
- Actualización de progreso < 100ms latencia
- Dashboard funcional en < 500 líneas de código
- Cero dependencias externas para MVP

## 🚀 Prioridad y Esfuerzo

**Prioridad**: Media-Alta
- Los endpoints ya existen
- Mejora significativa en UX
- Facilita debugging y adopción

**Esfuerzo estimado**:
- MVP básico: 1-2 días
- Versión pulida: 1 semana
- Full-featured: 2-3 semanas

**ROI**: Alto - Gran mejora en usabilidad con esfuerzo moderado