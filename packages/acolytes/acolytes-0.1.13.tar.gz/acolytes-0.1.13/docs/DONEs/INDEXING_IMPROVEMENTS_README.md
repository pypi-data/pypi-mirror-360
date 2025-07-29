# 📚 CÓMO USAR LA GUÍA DE MEJORAS DE INDEXACIÓN

## ⚠️ PARA IAs QUE VAYAN A IMPLEMENTAR MEJORAS ⚠️

### 1. **ANTES DE EMPEZAR**

Lee estos archivos EN ESTE ORDEN:
1. `PROMPT.md` - Entender el proyecto completo
2. `docs/AUDIT_DECISIONS.md` - Decisiones arquitectónicas críticas  
3. `INDEXING_IMPROVEMENTS_GUIDE.md` - La guía dividida en partes

### 2. **ELIGE UNA PARTE**

La guía está dividida en 12 partes. **SOLO IMPLEMENTA UNA PARTE A LA VEZ**.

- **Partes 1-3**: Solo análisis, no tocan código
- **Partes 4-6**: Fixes pequeños, bajo riesgo
- **Partes 7-9**: Mejoras medianas, riesgo medio
- **Partes 10-12**: Cambios grandes, ALTO RIESGO

### 3. **PROCESO OBLIGATORIO**

Para CADA parte:

```
1. INVESTIGAR
   - Lee TODOS los archivos mencionados en "QUÉ INVESTIGAR PRIMERO"
   - Busca dependencias con grep
   - Entiende qué puede romperse

2. VERIFICAR
   - ¿Los módulos/funciones que voy a usar EXISTEN?
   - ¿Hay tests que deben pasar?
   - ¿Qué servicios dependen de esto?

3. PREGUNTAR
   - Si algo no está claro, PREGUNTA
   - Si no encuentras algo, NO LO INVENTES
   - Si te quedas sin contexto, PARA

4. IMPLEMENTAR
   - Cambios mínimos
   - Tests deben pasar
   - No romper nada existente

5. DOCUMENTAR
   - Actualiza CHANGELOG
   - Documenta decisiones
   - Explica qué hiciste y por qué
```

### 4. **EJEMPLO DE FLUJO CORRECTO**

Si vas a implementar PARTE 4 (Eliminar primer escaneo):

```bash
# 1. Verificar que entiendes el problema
grep -n "rglob" src/acolyte/api/index.py

# 2. Ver qué tests existen
ls tests/api/test_index*
pytest tests/api/test_index.py::test_index_project -xvs

# 3. Hacer el cambio MÍNIMO
# Solo eliminar el escaneo redundante, nada más

# 4. Verificar que todo sigue funcionando
pytest tests/api/test_index.py -xvs
pytest tests/integration/test_indexing* -xvs

# 5. Si algo falla, REVERTIR
git checkout -- src/acolyte/api/index.py
```

### 5. **🚨 SEÑALES DE ALARMA 🚨**

Si te encuentras:
- Creando nuevos archivos → PARA
- Inventando funciones que no existen → PARA  
- Modificando más de 3 archivos → PARA
- Sin entender por qué algo es como es → PARA

### 6. **CONTEXTO CRÍTICO**

`acolyte index` es el **PRIMER COMANDO** que ejecuta un usuario nuevo. Es su primera impresión de ACOLYTE. Si es lento o falla, desinstalan.

Pero también es parte de un ecosistema complejo:
- `ReindexService` mantiene índices actualizados
- Git hooks disparan reindexación automática
- `Dream` analiza el código indexado
- `ChatService` busca en los índices

**NO ROMPAS NADA**.

---

## 📊 Estado de Implementación

| Parte | Estado | Implementado por | Fecha | Notas |
|-------|--------|------------------|-------|-------|
| 1 | ⬜ Pendiente | - | - | Análisis triple escaneo |
| 2 | ⬜ Pendiente | - | - | Análisis dependencias |
| 3 | ⬜ Pendiente | - | - | Análisis eventos |
| 4 | ⬜ Pendiente | - | - | Fix escaneo 1 |
| 5 | ⬜ Pendiente | - | - | Fix escaneo 2 |
| 6 | ⬜ Pendiente | - | - | Mejorar errores |
| 7 | ⬜ Pendiente | - | - | Fallback chunking |
| 8 | ⬜ Pendiente | - | - | Métricas |
| 9 | ⬜ Pendiente | - | - | CLI progress |
| 10 | ⬜ Pendiente | - | - | Paralelización |
| 11 | ⬜ Pendiente | - | - | Estado persistente |
| 12 | ⬜ Pendiente | - | - | Batch Weaviate |

---

**Última actualización**: 2025-01-07 por Claude (documentación inicial)