## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Fundamento Científico](#fundamento-científico)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Arquetipos de Desarrolladores](#arquetipos-de-desarrolladores)
5. [Implementación Técnica](#implementación-técnica)
6. [Integración con Módulos Existentes](#integración-con-módulos-existentes)
7. [Evolución y Aprendizaje](#evolución-y-aprendizaje)
8. [Control del Usuario](#control-del-usuario)
9. [Métricas y Evaluación](#métricas-y-evaluación)
10. [Roadmap de Implementación](#roadmap-de-implementación)

## 🎯 Visión General

### ¿Qué es Developer DNA?

Developer DNA es un sistema de personalización ultra-ligero que captura el estilo y preferencias de programación de cada usuario en solo **10-15 palabras clave**. En lugar de almacenar historiales extensos que consumen ventana de contexto, el sistema sintetiza la \"esencia\" del desarrollador en un perfil compacto pero altamente efectivo.

### Principios de Diseño

1. **Minimalismo**: Máximo impacto con mínima complejidad
2. **Basado en Evidencia**: Fundamentado en investigación sobre personalidad y estilos de programación
3. **Transparente**: El usuario siempre puede ver y modificar su perfil
4. **No Invasivo**: Aprende de acciones naturales sin interrumpir el flujo
5. **Eficiente**: No consume ventana de contexto significativa

### Beneficios Clave

- **Búsquedas más relevantes**: Resultados alineados con el estilo del desarrollador
- **Cero configuración**: Detección automática del perfil
- **Adaptación continua**: Evoluciona con el desarrollador
- **Privacy-first**: Todo local, sin telemetría

## 🔬 Fundamento Científico

### Investigación Base

Múltiples estudios han demostrado que los programadores tienen estilos y personalidades distintivas que afectan significativamente cómo escriben código:

1. **Personalidad y Programación** (Capretz, 2003; Cruz et al., 2015):

   - Los programadores tienden hacia tipos INT- en MBTI
   - Introversión correlaciona con preferencia por código bien estructurado
   - Consciencia se relaciona con atención al detalle en código

2. **Estilos de Programación** (Universidad de Stuttgart, 2024):

   - La experiencia es el factor más influyente, pero la personalidad es evidente
   - Los estilos son preferencias personales estables
   - Diferentes personalidades prefieren diferentes patrones de código

3. **Impacto en Rendimiento** (Meta-análisis 2024):
   - Consciencia, apertura e introversión correlacionan con aptitud para programación
   - Los rasgos de personalidad explican varianza incremental más allá de habilidades generales
   - La asignación de tareas según personalidad mejora resultados

### Hallazgos Clave para ACOLYTE

- **Los desarrolladores tienen \"firmas\" consistentes** en cómo buscan y escriben código
- **Las preferencias son estables** pero pueden evolucionar lentamente
- **Pequeños ajustes** basados en personalidad tienen **gran impacto** en satisfacción

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                    Developer DNA System                   │
├─────────────────┬─────────────────┬────────────────────┤
│  DNA Detector   │   DNA Store     │   DNA Applicator   │
│  (Observa)      │   (Persiste)    │   (Personaliza)    │
└─────────────────┴─────────────────┴────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │         Integration Layer           │
        ├─────────────┬───────────────────────┤
        │   Search    │    Prompt Builder     │
        │   Enhancer  │    Context Injector   │
        └─────────────┴───────────────────────┘
```

### Flujo de Datos

1. **Observación**: Sistema detecta patrones en queries y selecciones
2. **Análisis**: Identificación de keywords representativos
3. **Síntesis**: Reducción a 10-15 keywords más significativos
4. **Aplicación**: Boost sutil en búsquedas y contexto mínimo en prompts
5. **Evolución**: Ajuste continuo basado en nuevas observaciones

## 🎭 Arquetipos de Desarrolladores

### 1. The Pragmatic Programmer

**Keywords**: `[pragmatic, kiss, yagni, working-code, ship-it, practical, simple]`

**Características**:

- Valora código que funciona sobre perfección teórica
- Prefiere soluciones simples y directas
- Documenta lo justo y necesario
- Refactoriza cuando añade valor real
- Skeptical de over-engineering

**Boost en búsquedas**:

- ✅ Implementaciones directas
- ✅ Soluciones probadas
- ❌ Patrones complejos sin justificación
- ❌ Abstracciones prematuras

### 2. The Clean Code Craftsman

**Keywords**: `[clean-code, solid, patterns, readable, uncle-bob, craftsmanship, refactor]`

**Características**:

- Obsesionado con código legible y mantenible
- Métodos cortos con nombres descriptivos
- Aplica principios SOLID religiosamente
- Refactoring constante
- Tests como documentación

**Boost en búsquedas**:

- ✅ Código bien estructurado
- ✅ Ejemplos con buenos nombres
- ✅ Implementaciones con patterns
- ❌ Código legacy sin refactorizar

### 3. The TDD Evangelist

**Keywords**: `[tdd, test-first, red-green-refactor, coverage, bdd, testing, spec]`

**Características**:

- Nunca escribe código sin test primero
- Alta cobertura de tests (>90%)
- Diseño emergente desde tests
- Tests como especificación
- Prefiere BDD para features

**Boost en búsquedas**:

- ✅ Tests antes que implementación
- ✅ Ejemplos con specs
- ✅ Código con alta cobertura
- ❌ Código sin tests

### 4. The Performance Optimizer

**Keywords**: `[performance, optimization, benchmark, profiling, efficiency, fast, memory]`

**Características**:

- Mide antes de optimizar
- Conoce Big-O de algoritmos
- Prefiere eficiencia sobre legibilidad (cuando justificado)
- Utiliza profilers regularmente
- Cache y optimización de memoria

**Boost en búsquedas**:

- ✅ Implementaciones optimizadas
- ✅ Benchmarks y mediciones
- ✅ Algoritmos eficientes
- ❌ Código naive sin considerar performance

### 5. The Architecture Astronaut

**Keywords**: `[architecture, patterns, design-first, abstraction, scalable, enterprise, ddd]`

**Características**:

- Diseña extensivamente antes de codificar
- Ama patrones de diseño y arquitectura
- Piensa en escalabilidad desde día 1
- Domain-Driven Design
- A veces over-engineer

**Boost en búsquedas**:

- ✅ Arquitecturas bien diseñadas
- ✅ Patrones aplicados correctamente
- ✅ Diseños escalables
- ❌ Soluciones quick & dirty

### 6. The Security Guardian

**Keywords**: `[security, validation, sanitization, auth, crypto, owasp, secure]`

**Características**:

- Security-first mindset
- Valida todo input
- Conoce OWASP top 10
- Implementa auth/authz correctamente
- Paranoid (en el buen sentido)

**Boost en búsquedas**:

- ✅ Código con validaciones
- ✅ Implementaciones seguras
- ✅ Mejores prácticas de seguridad
- ❌ Código vulnerable

### 7. The Documentation Champion

**Keywords**: `[documented, comments, readme, examples, tutorial, clarity, explain]`

**Características**:

- Cree que código no documentado es deuda técnica
- Escribe READMEs comprehensivos
- Comenta el \"por qué\", no el \"qué\"
- Crea ejemplos y tutoriales
- API docs siempre actualizados

**Boost en búsquedas**:

- ✅ Código bien comentado
- ✅ Proyectos con buena documentación
- ✅ Ejemplos claros
- ❌ Código críptico sin contexto

### 8. The Modern Minimalist

**Keywords**: `[minimal, functional, immutable, pure, composition, modern, clean-api]`

**Características**:

- Prefiere programación funcional
- Evita estado mutable
- APIs minimalistas
- Composición sobre herencia
- Less is more

**Boost en búsquedas**:

- ✅ Código funcional
- ✅ APIs limpias
- ✅ Soluciones elegantes
- ❌ Código con mucho estado

## 💻 Implementación Técnica

### 1. Módulo DNA Detector

```python
# src/acolyte/sage/dna_detector.py
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import re

from acolyte.core.logging import logger
from acolyte.models.base import AcolyteBaseModel


class DeveloperAction(AcolyteBaseModel):
    \"\"\"Representa una acción del desarrollador.\"\"\"
    action_type: str  # 'search', 'select', 'view', 'copy'
    query: Optional[str] = None
    selected_chunk_id: Optional[str] = None
    file_path: Optional[str] = None
    chunk_type: Optional[str] = None
    has_tests: bool = False
    is_refactoring: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class DNAObservation(AcolyteBaseModel):
    \"\"\"Observación de un rasgo de DNA.\"\"\"
    keyword: str
    confidence: float  # 0.0 a 1.0
    context: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)


class DeveloperDNADetector:
    \"\"\"Detecta el perfil del desarrollador analizando sus acciones.\"\"\"

    # Patrones para detectar diferentes estilos
    PATTERNS = {
        'tdd': {
            'queries': [r'\\btest\\b', r'\\bspec\\b', r'\\btdd\\b', r'\\bunit\\s*test'],
            'prefers_test_files': True,
            'searches_tests_first': True
        },
        'clean-code': {
            'queries': [r'\\brefactor', r'\\bclean\\b', r'\\bsolid\\b', r'\\bpattern'],
            'prefers_well_named': True,
            'frequent_refactoring': True
        },
        'performance': {
            'queries': [r'\\bbenchmark', r'\\boptimiz', r'\\bperformance', r'\\bprofil'],
            'prefers_optimized': True,
            'checks_complexity': True
        },
        'security': {
            'queries': [r'\\bsecur', r'\\bauth', r'\\bvalidat', r'\\bsaniti', r'\\bowasp'],
            'prefers_validated': True,
            'security_conscious': True
        },
        'pragmatic': {
            'queries': [r'\\bsimple', r'\\bwork', r'\\bquick', r'\\bpractical'],
            'avoids_overengineering': True,
            'prefers_simple': True
        },
        'architecture': {
            'queries': [r'\\barchitect', r'\\bdesign', r'\\bpattern', r'\\bscale'],
            'prefers_patterns': True,
            'design_first': True
        },
        'documented': {
            'queries': [r'\\bdoc', r'\\bcomment', r'\\breadme', r'\\bexample'],
            'prefers_documented': True,
            'values_clarity': True
        },
        'functional': {
            'queries': [r'\\bfunctional', r'\\bimmutable', r'\\bpure', r'\\blambda'],
            'prefers_functional': True,
            'avoids_state': True
        }
    }

    def __init__(self):
        self.observations: List[DNAObservation] = []
        self.action_history: List[DeveloperAction] = []
        self.keyword_scores: Dict[str, float] = defaultdict(float)
        self.keyword_counts: Dict[str, int] = defaultdict(int)

        # Configuración
        self.min_confidence = 0.7
        self.max_keywords = 15
        self.decay_factor = 0.95  # Decaimiento temporal
        self.observation_window = timedelta(days=30)

    async def observe_action(self, action: DeveloperAction) -> None:
        \"\"\"Observa una acción del desarrollador y extrae rasgos.\"\"\"
        self.action_history.append(action)

        # Limpiar historial viejo
        cutoff_time = datetime.now() - self.observation_window
        self.action_history = [a for a in self.action_history if a.timestamp > cutoff_time]

        # Analizar la acción
        observations = self._analyze_action(action)
        self.observations.extend(observations)

        # Actualizar scores
        for obs in observations:
            self._update_keyword_score(obs)

        logger.debug(f\"DNA observation: {len(observations)} traits detected from {action.action_type}\")

    def _analyze_action(self, action: DeveloperAction) -> List[DNAObservation]:
        \"\"\"Analiza una acción y extrae observaciones de DNA.\"\"\"
        observations = []

        # Analizar queries de búsqueda
        if action.query:
            for keyword, pattern_info in self.PATTERNS.items():
                for pattern in pattern_info['queries']:
                    if re.search(pattern, action.query, re.IGNORECASE):
                        observations.append(DNAObservation(
                            keyword=keyword,
                            confidence=0.8,
                            context={'query': action.query, 'pattern': pattern}
                        ))

        # Analizar selecciones
        if action.action_type == 'select' and action.selected_chunk_id:
            # TDD: selecciona tests primero
            if action.chunk_type == 'TEST' or (action.file_path and 'test' in action.file_path.lower()):
                observations.append(DNAObservation(
                    keyword='tdd',
                    confidence=0.9,
                    context={'selected_test': True}
                ))

            # Clean Code: selecciona código refactorizado
            if action.is_refactoring:
                observations.append(DNAObservation(
                    keyword='clean-code',
                    confidence=0.85,
                    context={'selected_refactored': True}
                ))

        # Analizar patrones de comportamiento
        observations.extend(self._analyze_behavioral_patterns())

        return observations

    def _analyze_behavioral_patterns(self) -> List[DNAObservation]:
        \"\"\"Analiza patrones de comportamiento en el historial.\"\"\"
        observations = []

        if len(self.action_history) < 10:
            return observations

        # Patrón TDD: busca tests antes de implementación
        test_first_count = 0
        for i in range(len(self.action_history) - 1):
            curr = self.action_history[i]
            next_action = self.action_history[i + 1]

            if (curr.query and 'test' in curr.query.lower() and
                next_action.query and 'implement' in next_action.query.lower()):
                test_first_count += 1

        if test_first_count > 3:
            observations.append(DNAObservation(
                keyword='tdd',
                confidence=0.95,
                context={'test_first_pattern': test_first_count}
            ))

        # Más análisis de patrones...

        return observations

    def _update_keyword_score(self, observation: DNAObservation) -> None:
        \"\"\"Actualiza el score de un keyword basado en observación.\"\"\"
        keyword = observation.keyword

        # Aplicar decaimiento temporal a scores existentes
        for kw in self.keyword_scores:
            self.keyword_scores[kw] *= self.decay_factor

        # Añadir nueva observación
        self.keyword_scores[keyword] += observation.confidence
        self.keyword_counts[keyword] += 1

    def synthesize_dna(self) -> List[str]:
        \"\"\"Sintetiza el DNA actual en keywords más representativos.\"\"\"
        # Calcular scores finales (promedio ponderado)
        final_scores = {}
        for keyword, total_score in self.keyword_scores.items():
            count = self.keyword_counts[keyword]
            if count > 0:
                avg_score = total_score / count
                # Bonus por frecuencia
                frequency_bonus = min(count / 10, 1.0) * 0.2
                final_scores[keyword] = avg_score + frequency_bonus

        # Filtrar por confianza mínima
        confident_keywords = [
            (kw, score) for kw, score in final_scores.items()
            if score >= self.min_confidence
        ]

        # Ordenar por score y tomar top N
        confident_keywords.sort(key=lambda x: x[1], reverse=True)
        top_keywords = [kw for kw, _ in confident_keywords[:self.max_keywords]]

        logger.info(f\"DNA synthesized: {top_keywords[:5]}...\")  # Log top 5

        return top_keywords

    def get_dna_profile(self) -> Dict[str, Any]:
        \"\"\"Retorna perfil completo con metadata.\"\"\"
        dna = self.synthesize_dna()

        return {
            'keywords': dna,
            'primary_style': dna[0] if dna else None,
            'confidence': self._calculate_confidence(),
            'observation_count': len(self.observations),
            'last_updated': datetime.now().isoformat(),
            'profile_age_days': self._calculate_profile_age()
        }

    def _calculate_confidence(self) -> float:
        \"\"\"Calcula confianza general del perfil.\"\"\"
        if not self.observations:
            return 0.0

        recent_observations = [
            obs for obs in self.observations
            if obs.timestamp > datetime.now() - timedelta(days=7)
        ]

        if not recent_observations:
            return 0.5  # Confianza media si no hay observaciones recientes

        avg_confidence = sum(obs.confidence for obs in recent_observations) / len(recent_observations)

        # Factor de cantidad
        quantity_factor = min(len(self.observations) / 100, 1.0)

        return avg_confidence * 0.7 + quantity_factor * 0.3

    def _calculate_profile_age(self) -> int:
        \"\"\"Calcula días desde primera observación.\"\"\"
        if not self.observations:
            return 0

        oldest = min(obs.timestamp for obs in self.observations)
        return (datetime.now() - oldest).days
```

### 2. Almacenamiento en Base de Datos

```sql
-- Añadir a schemas.sql

-- Tabla para DNA del desarrollador
CREATE TABLE developer_dna (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    score REAL DEFAULT 0.0,
    observation_count INTEGER DEFAULT 0,
    last_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keyword)
);

-- Tabla para historial de observaciones (opcional, para debugging)
CREATE TABLE dna_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    confidence REAL NOT NULL,
    action_type TEXT,
    context TEXT,  -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vista del DNA actual
CREATE VIEW current_dna AS
SELECT
    keyword,
    score,
    observation_count,
    ROUND(score / observation_count, 2) as avg_confidence
FROM developer_dna
WHERE score > 0.7
ORDER BY score DESC
LIMIT 15;

-- Índices para performance
CREATE INDEX idx_dna_score ON developer_dna(score DESC);
CREATE INDEX idx_observations_timestamp ON dna_observations(timestamp DESC);
```

### 3. Integración con Búsqueda

```python
# src/acolyte/rag/retrieval/dna_personalizer.py
from typing import List, Dict, Set
from dataclasses import dataclass

from acolyte.core.logging import logger
from acolyte.models.chunk import Chunk, ChunkType
from acolyte.rag.retrieval.hybrid_search import ScoredChunk


@dataclass
class DNABoostRule:
    \"\"\"Regla de boost basada en DNA.\"\"\"
    keyword: str
    condition: str  # 'has_tests', 'is_documented', 'is_refactored', etc
    boost_factor: float


class DNAPersonalizer:
    \"\"\"Personaliza resultados de búsqueda basado en Developer DNA.\"\"\"

    # Mapeo de keywords DNA a reglas de boost
    BOOST_RULES = {
        'tdd': [
            DNABoostRule('tdd', 'has_tests', 1.20),
            DNABoostRule('tdd', 'test_first', 1.25),
            DNABoostRule('tdd', 'high_coverage', 1.15)
        ],
        'clean-code': [
            DNABoostRule('clean-code', 'well_named', 1.15),
            DNABoostRule('clean-code', 'small_methods', 1.10),
            DNABoostRule('clean-code', 'low_complexity', 1.12)
        ],
        'performance': [
            DNABoostRule('performance', 'has_benchmarks', 1.18),
            DNABoostRule('performance', 'optimized', 1.20),
            DNABoostRule('performance', 'efficient_algorithm', 1.15)
        ],
        'security': [
            DNABoostRule('security', 'has_validation', 1.20),
            DNABoostRule('security', 'secure_patterns', 1.25),
            DNABoostRule('security', 'no_vulnerabilities', 1.15)
        ],
        'pragmatic': [
            DNABoostRule('pragmatic', 'simple_solution', 1.15),
            DNABoostRule('pragmatic', 'working_code', 1.10),
            DNABoostRule('pragmatic', 'not_overengineered', 1.12)
        ],
        'architecture': [
            DNABoostRule('architecture', 'uses_patterns', 1.18),
            DNABoostRule('architecture', 'well_structured', 1.15),
            DNABoostRule('architecture', 'scalable_design', 1.12)
        ],
        'documented': [
            DNABoostRule('documented', 'has_comments', 1.15),
            DNABoostRule('documented', 'has_readme', 1.20),
            DNABoostRule('documented', 'clear_examples', 1.18)
        ],
        'functional': [
            DNABoostRule('functional', 'immutable', 1.15),
            DNABoostRule('functional', 'pure_functions', 1.18),
            DNABoostRule('functional', 'no_side_effects', 1.12)
        ]
    }

    # Penalizaciones (boost negativo)
    PENALTY_RULES = {
        'pragmatic': [
            DNABoostRule('pragmatic', 'overengineered', 0.85),
            DNABoostRule('pragmatic', 'too_abstract', 0.88)
        ],
        'tdd': [
            DNABoostRule('tdd', 'no_tests', 0.80),
            DNABoostRule('tdd', 'low_coverage', 0.85)
        ],
        'clean-code': [
            DNABoostRule('clean-code', 'poor_naming', 0.85),
            DNABoostRule('clean-code', 'large_methods', 0.88)
        ],
        'security': [
            DNABoostRule('security', 'no_validation', 0.80),
            DNABoostRule('security', 'potential_vulnerability', 0.75)
        ]
    }

    def __init__(self, max_boost: float = 1.3, min_boost: float = 0.7):
        self.max_boost = max_boost
        self.min_boost = min_boost

    def personalize_results(
        self,
        chunks: List[ScoredChunk],
        dna_keywords: List[str]
    ) -> List[ScoredChunk]:
        \"\"\"Aplica personalización DNA a resultados de búsqueda.\"\"\"
        if not dna_keywords:
            return chunks

        # Aplicar reglas para cada chunk
        for chunk in chunks:
            original_score = chunk.score
            boost = self._calculate_boost(chunk, dna_keywords)

            # Aplicar boost con límites
            boost = max(self.min_boost, min(self.max_boost, boost))
            chunk.score *= boost

            if boost != 1.0:
                logger.debug(
                    f\"DNA boost applied: {original_score:.3f} → {chunk.score:.3f} \"
                    f\"(x{boost:.2f}) for {chunk.chunk.metadata.file_path}\"
                )

        # Re-ordenar por nuevo score
        chunks.sort(key=lambda x: x.score, reverse=True)

        return chunks

    def _calculate_boost(self, scored_chunk: ScoredChunk, dna_keywords: List[str]) -> float:
        \"\"\"Calcula boost total para un chunk basado en DNA.\"\"\"
        chunk = scored_chunk.chunk
        total_boost = 1.0

        # Aplicar boosts positivos
        for keyword in dna_keywords[:5]:  # Solo top 5 keywords
            if keyword in self.BOOST_RULES:
                for rule in self.BOOST_RULES[keyword]:
                    if self._check_condition(chunk, rule.condition):
                        total_boost *= rule.boost_factor

        # Aplicar penalizaciones
        for keyword in dna_keywords[:3]:  # Solo top 3 para penalties
            if keyword in self.PENALTY_RULES:
                for rule in self.PENALTY_RULES[keyword]:
                    if self._check_condition(chunk, rule.condition):
                        total_boost *= rule.boost_factor

        return total_boost

    def _check_condition(self, chunk: Chunk, condition: str) -> bool:
        \"\"\"Verifica si un chunk cumple una condición.\"\"\"
        metadata = chunk.metadata

        # Condiciones relacionadas con tests
        if condition == 'has_tests':
            return (metadata.chunk_type == ChunkType.TESTS or
                    'test' in metadata.file_path.lower())

        elif condition == 'test_first':
            # Heurística: archivo de test existe y es más viejo que implementación
            return metadata.chunk_type == ChunkType.TESTS

        elif condition == 'high_coverage':
            # Necesitaría metadata adicional
            return metadata.test_coverage and metadata.test_coverage > 0.8

        # Condiciones de clean code
        elif condition == 'well_named':
            # Heurística: nombres descriptivos
            return self._has_good_naming(chunk)

        elif condition == 'small_methods':
            # Heurística: pocas líneas
            lines = metadata.end_line - metadata.start_line
            return lines < 20

        elif condition == 'low_complexity':
            # Necesitaría análisis de complejidad ciclomática
            return metadata.complexity and metadata.complexity < 5

        # Condiciones de performance
        elif condition == 'has_benchmarks':
            return 'benchmark' in chunk.content.lower()

        elif condition == 'optimized':
            # Heurística: menciona optimización o performance
            keywords = ['optimized', 'performance', 'efficient', 'fast']
            return any(kw in chunk.content.lower() for kw in keywords)

        # Condiciones de seguridad
        elif condition == 'has_validation':
            validation_patterns = ['validate', 'sanitize', 'check', 'verify']
            return any(pattern in chunk.content.lower() for pattern in validation_patterns)

        # Condiciones de documentación
        elif condition == 'has_comments':
            # Heurística: ratio de comentarios
            comment_indicators = ['#', '//', '/*', '\"\"\"', \"'''\"]
            comment_lines = sum(1 for line in chunk.content.split('\
')
                              if any(indicator in line for indicator in comment_indicators))
            total_lines = len(chunk.content.split('\
'))
            return comment_lines / max(total_lines, 1) > 0.1

        # Condiciones pragmáticas
        elif condition == 'simple_solution':
            # Heurística: no muchas abstracciones
            abstraction_keywords = ['abstract', 'interface', 'factory', 'strategy']
            abstraction_count = sum(1 for kw in abstraction_keywords if kw in chunk.content.lower())
            return abstraction_count < 2

        elif condition == 'not_overengineered':
            return not self._is_overengineered(chunk)

        # Condiciones funcionales
        elif condition == 'immutable':
            return 'immutable' in chunk.content.lower() or 'const' in chunk.content

        elif condition == 'pure_functions':
            # Heurística: no side effects evidentes
            side_effect_patterns = ['print', 'write', 'save', 'delete', 'update']
            return not any(pattern in chunk.content.lower() for pattern in side_effect_patterns)

        # Por defecto
        return False

    def _has_good_naming(self, chunk: Chunk) -> bool:
        \"\"\"Heurística para detectar buen naming.\"\"\"
        # Buscar identificadores en el código
        import re

        # Patterns para diferentes lenguajes
        identifier_pattern = r'\\b[a-zA-Z_][a-zA-Z0-9_]*\\b'
        identifiers = re.findall(identifier_pattern, chunk.content)

        if not identifiers:
            return False

        # Calcular longitud promedio de identificadores
        avg_length = sum(len(id) for id in identifiers) / len(identifiers)

        # Good naming: ni muy corto ni muy largo
        good_length = 5 <= avg_length <= 20

        # Check for descriptive names (not single letters)
        single_letter_ratio = sum(1 for id in identifiers if len(id) == 1) / len(identifiers)
        not_too_many_single = single_letter_ratio < 0.2

        return good_length and not_too_many_single

    def _is_overengineered(self, chunk: Chunk) -> bool:
        \"\"\"Detecta si el código está sobre-ingenierizado.\"\"\"
        overengineering_indicators = [
            'AbstractFactory',
            'FactoryFactory',
            'Manager',
            'Facade',
            'Visitor',
            'AbstractAbstract'
        ]

        indicator_count = sum(1 for ind in overengineering_indicators
                            if ind in chunk.content)

        # Si tiene múltiples patterns en un chunk pequeño
        lines = chunk.metadata.end_line - chunk.metadata.start_line

        return indicator_count > 2 or (indicator_count > 0 and lines < 50)
```

### 4. Integración con ChatService

```python
# Modificación en services/chat_service.py

async def process_message(self, message: str, session_id: str) -> ChatResponse:
    \"\"\"Procesa mensaje con personalización DNA.\"\"\"
    # ... código existente ...

    # Obtener DNA del usuario
    dna_keywords = await self.dna_service.get_current_dna()

    # Búsqueda personalizada
    if dna_keywords:
        # Aplicar personalización a búsqueda
        chunks = await self.hybrid_search.search(message, max_chunks=20)
        personalized_chunks = self.dna_personalizer.personalize_results(
            chunks, dna_keywords
        )
        # Tomar top N después de personalización
        final_chunks = personalized_chunks[:10]
    else:
        # Búsqueda normal
        final_chunks = await self.hybrid_search.search(message, max_chunks=10)

    # Añadir contexto DNA mínimo al prompt
    system_prompt = self.prompt_builder.build_system_prompt(
        context=context,
        dna_keywords=dna_keywords[:5]  # Solo top 5
    )

    # ... resto del proceso ...

    # Registrar acción para aprendizaje
    await self._record_user_action(message, final_chunks, response)
```

### 5. Sistema de Control del Usuario

```python
# src/acolyte/api/dna.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from acolyte.sage.dna_service import DNAService
from acolyte.models.base import AcolyteBaseModel


router = APIRouter(prefix=\"/api/dna\", tags=[\"developer-dna\"])


class DNAProfile(AcolyteBaseModel):
    \"\"\"Perfil DNA del desarrollador.\"\"\"
    keywords: List[str]
    primary_style: Optional[str]
    confidence: float
    editable: bool = True
    stats: Dict[str, Any] = {}


class DNAUpdateRequest(AcolyteBaseModel):
    \"\"\"Request para actualizar DNA.\"\"\"
    keywords: List[str]
    reset: bool = False


@router.get(\"/profile\", response_model=DNAProfile)
async def get_developer_profile():
    \"\"\"Obtiene el perfil DNA actual del desarrollador.\"\"\"
    service = DNAService()
    profile = await service.get_profile()

    return DNAProfile(
        keywords=profile['keywords'][:10],  # Top 10
        primary_style=profile.get('primary_style'),
        confidence=profile.get('confidence', 0.0),
        stats={
            'observation_count': profile.get('observation_count', 0),
            'profile_age_days': profile.get('profile_age_days', 0),
            'last_updated': profile.get('last_updated')
        }
    )


@router.post(\"/update\")
async def update_developer_profile(request: DNAUpdateRequest):
    \"\"\"Permite al usuario editar su perfil DNA.\"\"\"
    service = DNAService()

    # Validar keywords
    valid_keywords = [
        'pragmatic', 'clean-code', 'tdd', 'performance',
        'security', 'architecture', 'documented', 'functional',
        'kiss', 'yagni', 'solid', 'patterns', 'refactor',
        'test-first', 'coverage', 'optimization', 'benchmark'
    ]

    if request.reset:
        await service.reset_profile()
        return {\"status\": \"reset\", \"message\": \"DNA profile reset\"}

    # Filtrar keywords válidos
    filtered = [kw for kw in request.keywords if kw in valid_keywords]

    if not filtered:
        raise HTTPException(400, \"No valid keywords provided\")

    # Limitar a 15 keywords
    filtered = filtered[:15]

    await service.update_keywords(filtered)

    return {
        \"status\": \"updated\",
        \"keywords\": filtered,
        \"message\": f\"DNA profile updated with {len(filtered)} keywords\"
    }


@router.get(\"/suggestions\")
async def get_keyword_suggestions():
    \"\"\"Sugiere keywords basado en actividad reciente.\"\"\"
    service = DNAService()
    suggestions = await service.get_keyword_suggestions()

    return {
        'suggested': suggestions[:5],
        'trending': await service.get_trending_keywords(),
        'all_available': [
            {
                'keyword': 'pragmatic',
                'description': 'Values working code over perfection'
            },
            {
                'keyword': 'clean-code',
                'description': 'Focuses on readability and maintainability'
            },
            {
                'keyword': 'tdd',
                'description': 'Test-driven development approach'
            },
            # ... más keywords con descripciones
        ]
    }


@router.get(\"/stats\")
async def get_dna_statistics():
    \"\"\"Estadísticas detalladas del sistema DNA.\"\"\"
    service = DNAService()
    stats = await service.get_detailed_stats()

    return {
        'detection_accuracy': stats.get('accuracy', 0.0),
        'most_detected_traits': stats.get('top_traits', []),
        'learning_progress': stats.get('progress', {}),
        'recommendation_impact': {
            'click_through_rate_improvement': stats.get('ctr_improvement', '0%'),
            'search_refinement_reduction': stats.get('refinement_reduction', '0%')
        }
    }


@router.post(\"/feedback\")
async def provide_feedback(
    helpful: bool,
    context: Optional[str] = None
):
    \"\"\"Usuario puede dar feedback sobre la personalización.\"\"\"
    service = DNAService()
    await service.record_feedback(helpful, context)

    return {\"status\": \"recorded\", \"thank_you\": True}
```

## 🔄 Evolución y Aprendizaje

### Algoritmo de Evolución

```python
class DNAEvolution:
    \"\"\"Gestiona la evolución del DNA con el tiempo.\"\"\"

    def __init__(self):
        self.evolution_rate = 0.1  # Qué tan rápido cambia
        self.stability_threshold = 100  # Observaciones antes de estabilizar
        self.mutation_probability = 0.05  # Chance de explorar nuevos traits

    async def evolve_dna(self, current_dna: List[str], new_observations: List[DNAObservation]) -> List[str]:
        \"\"\"Evoluciona el DNA basado en nuevas observaciones.\"\"\"
        # Calcular presión evolutiva
        pressure = self._calculate_evolutionary_pressure(new_observations)

        # DNA estable cambia más lento
        if len(new_observations) > self.stability_threshold:
            self.evolution_rate *= 0.5

        # Aplicar cambios graduales
        evolved_dna = self._apply_gradual_changes(current_dna, pressure)

        # Pequeña chance de mutación (exploración)
        if random.random() < self.mutation_probability:
            evolved_dna = self._mutate(evolved_dna)

        return evolved_dna
```

### Detección de Cambios de Contexto

```python
class ContextChangeDetector:
    \"\"\"Detecta cuando el desarrollador cambia de proyecto o estilo.\"\"\"

    async def detect_context_change(self, recent_actions: List[DeveloperAction]) -> bool:
        \"\"\"Detecta si hay un cambio significativo de contexto.\"\"\"
        if len(recent_actions) < 20:
            return False

        # Dividir en ventanas
        old_window = recent_actions[:10]
        new_window = recent_actions[-10:]

        # Comparar patrones
        old_patterns = self._extract_patterns(old_window)
        new_patterns = self._extract_patterns(new_window)

        # Calcular divergencia
        divergence = self._calculate_divergence(old_patterns, new_patterns)

        return divergence > 0.7  # Threshold para cambio significativo
```

## 🎮 Control del Usuario

### Dashboard Visual

```typescript
// Componente React para visualizar DNA
interface DNADashboardProps {
  profile: DNAProfile;
  onUpdate: (keywords: string[]) => void;
}

const DNADashboard: React.FC<DNADashboardProps> = ({ profile, onUpdate }) => {
  return (
    <div className=\"dna-dashboard\">
      <h2>Tu Developer DNA</h2>

      {/* Visualización tipo radar chart */}
      <DNARadarChart keywords={profile.keywords} />

      {/* Keywords editables */}
      <div className=\"dna-keywords\">
        <h3>Tus rasgos detectados:</h3>
        {profile.keywords.map(keyword => (
          <DNAKeywordChip
            key={keyword}
            keyword={keyword}
            confidence={getConfidence(keyword)}
            onRemove={() => removeKeyword(keyword)}
          />
        ))}
      </div>

      {/* Sugerencias */}
      <div className=\"dna-suggestions\">
        <h3>Rasgos sugeridos:</h3>
        {suggestions.map(suggestion => (
          <SuggestionChip
            key={suggestion}
            keyword={suggestion}
            onAdd={() => addKeyword(suggestion)}
          />
        ))}
      </div>

      {/* Estadísticas */}
      <DNAStats
        observationCount={profile.stats.observation_count}
        accuracy={profile.confidence}
        impact={profile.stats.recommendation_impact}
      />
    </div>
  );
};
```

### Configuración Avanzada

```yaml
# En .acolyte - configuración de DNA
developer_dna:
  # DNA actual (editado por usuario o detectado)
  keywords: [pragmatic, tdd, clean-code, performance]

  # Configuración del sistema
  settings:
    enabled: true
    evolution_rate: 0.1
    max_keywords: 15
    min_confidence: 0.7
    learning_mode: \"adaptive\" # 'adaptive', 'fixed', 'manual'

  # Preferencias de personalización
  personalization:
    search_boost_strength: 0.2 # 0.0 a 1.0
    prompt_injection: true
    explain_personalization: false

  # Privacidad
  privacy:
    store_observations: true
    observation_retention_days: 30
    anonymous_analytics: false
```

## 📊 Métricas y Evaluación

### KPIs del Sistema

1. **Efectividad de Búsqueda**

   - Click-through rate en top 3 resultados
   - Número de refinamientos de búsqueda
   - Tiempo hasta encontrar resultado deseado

2. **Precisión del DNA**

   - Estabilidad del perfil con el tiempo
   - Correlación entre DNA y selecciones
   - Feedback explícito del usuario

3. **Impacto en Productividad**
   - Tiempo promedio de búsqueda
   - Satisfacción del usuario (NPS)
   - Adopción de sugerencias

### Sistema de Métricas

```python
class DNAMetrics:
    \"\"\"Métricas para evaluar el sistema DNA.\"\"\"

    async def calculate_effectiveness_metrics(self) -> Dict[str, float]:
        \"\"\"Calcula métricas de efectividad.\"\"\"
        return {
            'ctr_top3': await self._calculate_ctr_top_n(3),
            'ctr_top5': await self._calculate_ctr_top_n(5),
            'avg_search_refinements': await self._avg_refinements(),
            'search_success_rate': await self._search_success_rate(),
            'dna_stability': await self._calculate_stability(),
            'user_satisfaction': await self._get_satisfaction_score()
        }

    async def generate_report(self) -> str:
        \"\"\"Genera reporte de métricas.\"\"\"
        metrics = await self.calculate_effectiveness_metrics()

        return f\"\"\"
        DNA System Performance Report
        ============================

        Search Effectiveness:
        - CTR Top 3: {metrics['ctr_top3']:.1%}
        - CTR Top 5: {metrics['ctr_top5']:.1%}
        - Avg Refinements: {metrics['avg_search_refinements']:.1f}
        - Success Rate: {metrics['search_success_rate']:.1%}

        DNA Quality:
        - Profile Stability: {metrics['dna_stability']:.1%}
        - User Satisfaction: {metrics['user_satisfaction']:.1f}/5.0

        Recommendation: {'System performing well' if metrics['ctr_top3'] > 0.7 else 'Needs tuning'}
        \"\"\"
```

## 🗺️ Roadmap de Implementación

### Fase 1: Fundación (2 semanas)

1. **Semana 1**:

   - [ ] Implementar DNADetector básico
   - [ ] Crear tablas en base de datos
   - [ ] Integración básica con ChatService
   - [ ] Tests unitarios

2. **Semana 2**:
   - [ ] DNAPersonalizer para búsquedas
   - [ ] API endpoints básicos
   - [ ] Logging y métricas básicas
   - [ ] Tests de integración

### Fase 2: Evolución (1 semana)

3. **Semana 3**:
   - [ ] Sistema de evolución de DNA
   - [ ] Detección de cambio de contexto
   - [ ] Dashboard básico (CLI)
   - [ ] Documentación de usuario

### Fase 3: Refinamiento (1 semana)

4. **Semana 4**:
   - [ ] Ajuste de algoritmos basado en métricas
   - [ ] UI web para dashboard
   - [ ] Sistema de feedback
   - [ ] Optimización de performance

### Fase 4: Pulido (continuo)

- [ ] A/B testing de estrategias
- [ ] Nuevos arquetipos basados en uso
- [ ] Mejoras en detección
- [ ] Integración con más módulos

## 🎯 Conclusión

Developer DNA representa un enfoque innovador para personalización en asistentes de código:

- **Ultra-ligero**: Solo 10-15 keywords
- **Basado en evidencia**: Fundamentado en investigación real
- **Efectivo**: Pequeños ajustes, gran impacto
- **Transparente**: Usuario tiene control total
- **Evolutivo**: Se adapta con el tiempo

El sistema balancea perfectamente la necesidad de personalización con las restricciones de ventana de contexto, creando una experiencia verdaderamente adaptada a cada desarrollador sin complejidad innecesaria.

---

_\"Your code style is as unique as your fingerprint. ACOLYTE learns to speak your language.\"_
`

---

# 📝 Prompt de Alta Fidelidad (HiFi Prompt)

Siempre arranca con una mezcla de:

Tu DNA

Tu proyecto actual

Tu historial de estilo

Tu sistema operativo / stack

Tus restricciones (p.ej., “no usar frameworks pesados”)

Ejemplo interno:

User prefers bottom-up implementation, avoids React, uses Poetry, targets AWS Lambda, prefers test-first strategy, dislikes nesting > 2 levels.

---

Generador Automático de Documentación:

Función: Al modificar una función o clase, ACOLYTE podría proponer automáticamente una actualización para su correspondiente documentación en los archivos Markdown (READMEs, guías, etc.), basándose en los cambios semánticos que ha detectado.
Ventaja: Mantiene la documentación sincronizada con el código, una tarea que suele descuidarse.

---

Gestor Inteligente de Tareas Pendientes (TODOs):

Función: Escanearía todo el proyecto en busca de comentarios TODO, FIXME, etc. Los centralizaría y te permitiría consultarlos de forma semántica. Por ejemplo: "¿Qué TODOs tengo relacionados con la base de datos?".
Ventaja: Convierte los comentarios de tareas pendientes de notas dispersas a una lista de trabajo organizada y consultable.

---

1. Adaptación a la Personalidad y Estilo de Comunicación
   ACOLYTE podría modificar cómo interactúa basándose en la personalidad del usuario.

Motor de Personalidad Adaptativa:
Cómo funcionaría: El usuario podría elegir un "arquetipo" de comunicación para la IA, o la IA podría aprenderlo analizando el tono de las conversaciones.
Modo "Profesor": Ofrece respuestas detalladas, con contexto teórico y enlaces a documentación. Ideal para cuando quieres aprender a fondo.
Modo "Colega" (Sparring Partner): Cuestiona tus decisiones, te pide justificaciones y actúa como un segundo programador que te reta a pensar mejor.
Modo "Mayordomo": Va directo al grano. Respuestas cortas, código preciso, cero conversación superflua. Eficiencia máxima.
Modo "Entrenador" (Coach): Usa un lenguaje más motivador, celebra los pequeños logros (tests que pasan, refactorizaciones exitosas) y te anima cuando detecta frustración.
Por qué es único: La comunicación se adapta a tu estado de ánimo y necesidad del momento, haciendo la interacción mucho más natural y efectiva.

---

Claro, aquí tienes ideas de funcionalidades que se centran en el perfil y la personalidad del programador para hacer a ACOLYTE verdaderamente personal.

1. Adaptación a la Personalidad y Estilo de Comunicación
   ACOLYTE podría modificar cómo interactúa basándose en la personalidad del usuario.

Motor de Personalidad Adaptativa:
Cómo funcionaría: El usuario podría elegir un "arquetipo" de comunicación para la IA, o la IA podría aprenderlo analizando el tono de las conversaciones.
Modo "Profesor": Ofrece respuestas detalladas, con contexto teórico y enlaces a documentación. Ideal para cuando quieres aprender a fondo.
Modo "Colega" (Sparring Partner): Cuestiona tus decisiones, te pide justificaciones y actúa como un segundo programador que te reta a pensar mejor.
Modo "Mayordomo": Va directo al grano. Respuestas cortas, código preciso, cero conversación superflua. Eficiencia máxima.
Modo "Entrenador" (Coach): Usa un lenguaje más motivador, celebra los pequeños logros (tests que pasan, refactorizaciones exitosas) y te anima cuando detecta frustración.
Por qué es único: La comunicación se adapta a tu estado de ánimo y necesidad del momento, haciendo la interacción mucho más natural y efectiva. 2. Análisis del Perfil y Habilidades del Programador
La IA puede crear un perfil dinámico de tus fortalezas y debilidades para ayudarte a crecer.

Plan de Crecimiento Personalizado:

Cómo funcionaría: ACOLYTE analiza tu código a lo largo del tiempo para identificar patrones:
Fortalezas: Detecta en qué eres rápido y eficiente (ej: lógica de negocio en FastAPI).
Áreas de mejora: Identifica dónde dudas más o cometes errores (ej: consultas complejas de base de datos, promesas en JavaScript).
A partir de ahí, puede sugerir proactivamente pequeños ejercicios prácticos dentro de tu propio proyecto, recomendarte artículos específicos o, al generar código en un área débil, explicarte el "porqué" de su solución con más detalle.
Por qué es único: Es un mentor personal que basa sus lecciones en tu trabajo real, no en ejemplos genéricos.
Refuerzo de Hábitos Positivos:

Cómo funcionaría: Si tu objetivo es, por ejemplo, mejorar la calidad de tus tests, ACOLYTE puede analizar la cobertura de las nuevas funciones que creas. Si es alta, te lo reconocerá. Si es baja, te recordará amablemente tu objetivo y te sugerirá casos de prueba que podrías añadir.
Por qué es único: Actúa como un recordatorio de tus propias metas de desarrollo, ayudándote a construir disciplina de forma consistente. 3. Soporte Cognitivo y Prevención del Agotamiento
Entender tus ritmos de trabajo para cuidarte y mejorar tu enfoque.

Monitor de Ritmo Cognitivo:

Cómo funcionaría: Analizando la frecuencia de commits, la hora, y la tasa de errores simples (typos, errores de sintaxis), ACOLYTE puede inferir tu nivel de fatiga.
Si detecta que llevas 3 horas programando de noche y tu tasa de errores aumenta, podría sugerir: "Llevas un buen rato y es tarde. Históricamente, el código que subes a estas horas requiere correcciones al día siguiente. Quizás sea un buen momento para un descanso."
Por qué es único: Es una red de seguridad contra el burnout y los errores por cansancio, algo que solo un asistente 1-a-1 puede hacer.
Sistema de Gamificación Personalizada:

Cómo funcionaría: Implementaría un sistema de logros, pero adaptado a lo que te motiva a ti:
Para el "Finalizador": Le daría satisfacción ver una barra de progreso de "TODOs" que se va llenando o un contador de bugs resueltos.
Para el "Artesano": Le premiaría por reducir la complejidad ciclomática de una función, lograr 100% de cobertura en un módulo crítico o escribir una documentación especialmente buena.
Para el "Explorador": Le daría logros por usar una nueva característica del lenguaje o una librería por primera vez en el proyecto.
Por qué es único: La motivación es personal. Este sistema se enfocaría en lo que a ti te genera satisfacción, no en métricas genéricas.

---
