# 🧠 Módulo Semantic

Procesamiento de lenguaje natural y gestión inteligente de conversaciones usando técnicas extractivas simples y deterministas.

## 📑 Documentación

- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Principios de diseño, decisiones arquitectónicas y patrones
- **[docs/STATUS.md](./docs/STATUS.md)** - Estado actual, componentes implementados, TODOs y métricas
- **[docs/REFERENCE.md](./docs/REFERENCE.md)** - API completa con firmas de métodos y parámetros
- **[docs/WORKFLOWS.md](./docs/WORKFLOWS.md)** - Flujos de trabajo, ejemplos de código y casos de uso
- **[docs/INTEGRATION.md](./docs/INTEGRATION.md)** - Cómo se integra con ChatService, ConversationService y otros módulos

## 🔧 Componentes Principales

### summarizer.py
Genera resúmenes extractivos con 70-80% reducción. Formato: `[TIPO] Usuario: X | Contexto: Y | ACOLYTE: Z`.

### task_detector.py  
Detecta automáticamente nuevas tareas vs continuaciones usando patterns multiidioma y similitud de contexto.

### prompt_builder.py
Construye System Prompt dinámico con contexto del proyecto, sesión actual y decisiones técnicas.

### query_analyzer.py
Analiza queries para distribución dinámica de tokens (generation 75%, simple 20%, normal 10%).

### decision_detector.py
Detecta decisiones técnicas con marcador explícito (@decision) o patterns automáticos.

### reference_resolver.py
Identifica referencias a sesiones anteriores ("donde quedamos", "el archivo que modificamos").

### utils.py
Utilidades compartidas, principalmente `detect_language()` para detección automática es/en.

## ⚡ Quick Start

```python
from acolyte.semantic import QueryAnalyzer, Summarizer

# Analizar tipo de query
analyzer = QueryAnalyzer()
distribution = analyzer.analyze_query_intent("crea un componente completo de login")
# distribution.query_type = "generation"
# distribution.response_allocation = 0.75

# Generar resumen
summarizer = Summarizer()
result = summarizer.generate_summary(
    user_msg="hay un bug en el JWT",
    assistant_msg="El problema está en el tiempo de expiración...",
    context_chunks=chunks
)
# result.summary = "[DEBUGGING] Usuario: bug JWT | Contexto: auth.py | ACOLYTE: fix expiración"
# result.compression_ratio = 0.78
```

## 🎯 Características Clave

- **Sin ML/NLP**: Solo regex y patterns para determinismo
- **Multiidioma**: Español e inglés con detección automática  
- **Latencia <100ms**: Objetivo de performance garantizado
- **Configurable**: Patterns y thresholds desde `.acolyte`
- **Extractivo**: No genera contenido, solo extrae y reorganiza

## 📊 Estado

Módulo 100% funcional con 6 componentes operativos. Ver [docs/STATUS.md](./docs/STATUS.md) para detalles.

## ⚠️ Cambios Importantes

### Migración get_config → Settings (19/06/2025)

Se corrigió el uso incorrecto de `get_config()` en 3 archivos del módulo. Ver sección "Correcciones Aplicadas" en [docs/STATUS.md](./docs/STATUS.md) para detalles completos del cambio.

### Corrección de Tests del Módulo (19/06/2025)

Se corrigieron múltiples problemas en los tests:
- Patches de logger apuntando al módulo específico
- Fixtures sin campos auto-generados (id, created_at, updated_at)
- Mejora en detección de idioma para contracciones
- Manejo robusto de side_effects en mocks

Ver [docs/STATUS.md](./docs/STATUS.md#correcciones-en-tests-del-módulo-19062025) para detalles completos.
