# Sistema Multi-Proyecto con Auto-Asignación de Puertos

ACOLYTE ahora soporta múltiples proyectos simultáneos con asignación automática de puertos para evitar conflictos.

## Cómo Funciona

### Rangos de Puertos ACOLYTE

Cada servicio tiene un rango base en el espacio 42XXX:
- **Weaviate**: 42080-42179
- **Ollama**: 42434-42533  
- **Backend**: 42000-42099

### Auto-Detección de Puertos

Cuando ejecutas `acolyte init` en un nuevo proyecto:

1. **Escanea automáticamente** los puertos en el rango ACOLYTE
2. **Encuentra los primeros disponibles** para cada servicio
3. **Te sugiere los puertos libres** (puedes cambiarlos si quieres)
4. **Guarda la configuración** específica para ese proyecto

### Ejemplo Práctico

```bash
# Primer proyecto
cd ~/proyectos/api-python
acolyte init
# Auto-detecta puertos libres:
# Weaviate port [42080]: ✅ (libre, usa 42080)
# Ollama port [42434]: ✅ (libre, usa 42434)
# Backend port [42000]: ✅ (libre, usa 42000)

# Segundo proyecto (con el primero corriendo)
cd ~/proyectos/web-react
acolyte init
# Auto-detecta conflictos y sugiere siguientes libres:
# Weaviate port [42081]: ✅ (42080 ocupado, sugiere 42081)
# Ollama port [42435]: ✅ (42434 ocupado, sugiere 42435)
# Backend port [42001]: ✅ (42000 ocupado, sugiere 42001)

# Tercer proyecto
cd ~/proyectos/mobile-app
acolyte init
# Weaviate port [42082]: ✅
# Ollama port [42436]: ✅
# Backend port [42002]: ✅
```

## Ventajas

1. **Sin conflictos** - Cada proyecto usa puertos únicos automáticamente
2. **Múltiples proyectos simultáneos** - Puedes tener varios ACOLYTE corriendo
3. **Transparente** - No necesitas recordar qué puertos usa cada proyecto
4. **Personalizable** - Siempre puedes especificar tus propios puertos

## Ver Puertos de un Proyecto

```bash
cd ~/mi-proyecto
acolyte status

# Output:
# 📊 ACOLYTE Status
# Project: mi-proyecto
# Services:
#   ✓ Weaviate: Running (port 42081)
#   ✓ Ollama: Running (port 42435)
#   ✓ Backend: Running (port 42001)
```

## Configuración Manual

Si prefieres puertos específicos, simplemente escríbelos durante `acolyte init`:

```bash
acolyte init
# Weaviate port [42081]: 19530  # Puerto personalizado
# Ollama port [42435]: 27017    # Puerto personalizado
# Backend port [42001]: 8888    # Puerto personalizado
```

## Límites

- Máximo ~100 proyectos simultáneos por rango
- Si todos los puertos del rango están ocupados, necesitarás especificar manualmente
- Los puertos deben estar en el rango 1024-65535

## Troubleshooting

### "Cannot find available port"
- Muchos proyectos corriendo simultáneamente
- Solución: Especifica un puerto manual fuera del rango ACOLYTE

### "Port X is not available"
- El puerto está siendo usado por otro servicio
- ACOLYTE automáticamente sugerirá el siguiente disponible

### Ver todos los proyectos
```bash
acolyte projects
# Lista todos los proyectos con sus puertos asignados
```
