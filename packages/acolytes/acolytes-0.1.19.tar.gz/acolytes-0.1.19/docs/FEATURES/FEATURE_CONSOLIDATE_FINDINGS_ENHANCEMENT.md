# 🔍 Feature: Mejora de Consolidación de Findings

## Estado Actual

El método `_consolidate_findings()` en `orchestrator.py` funciona correctamente pero es básico:

```python
async def _consolidate_findings(
    self, session_id: str, initial: Dict[str, Any], deep: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Consolidate findings from different analysis phases."""
    # Collect all findings in a structured format
    all_findings = {
        "bugs": [],
        "security_issues": [],
        "performance_issues": [],
        "architectural_issues": [],
        "patterns": [],
        "recommendations": [],
    }

    # Extract from initial findings (exploration phase)
    if "patterns_detected" in initial:
        all_findings["patterns"].extend(initial["patterns_detected"])
    
    # ... más extracción básica ...
    
    # Apply deduplication
    all_findings = self._deduplicate_findings(all_findings)
    
    # Apply prioritization
    all_findings = self._prioritize_findings(all_findings)
    
    return insights
```

### Limitaciones Actuales

1. **Deduplicación simple**: Solo compara JSON serializado
2. **Sin detección de similitud**: Findings parecidos no se agrupan
3. **Pérdida de contexto**: No preserva relaciones entre findings
4. **Sin análisis cruzado**: No detecta patrones entre categorías

## Propuesta de Solución

### 1. Sistema de Consolidación Inteligente

```python
# dream/consolidation.py
"""
Advanced consolidation system for Dream findings.

Groups similar findings, detects patterns, and provides intelligent summarization.
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from collections import defaultdict

from acolyte.core.logging import logger
from acolyte.embeddings import get_embeddings


class FindingType(Enum):
    """Types of findings for proper categorization."""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    PATTERN = "pattern"
    RECOMMENDATION = "recommendation"


@dataclass
class Finding:
    """Structured finding with metadata."""
    type: FindingType
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    confidence: float  # 0.0 - 1.0
    files: List[str]
    line_ranges: List[Tuple[int, int]]
    related_findings: List[str]  # IDs of related findings
    source_phase: str  # 'initial' or 'deep'
    metadata: Dict[str, Any]
    
    @property
    def id(self) -> str:
        """Generate unique ID based on content."""
        content = f"{self.type.value}:{self.title}:{self.description}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    @property
    def impact_score(self) -> float:
        """Calculate impact score for prioritization."""
        severity_scores = {
            "CRITICAL": 1.0,
            "HIGH": 0.8,
            "MEDIUM": 0.5,
            "LOW": 0.2
        }
        base_score = severity_scores.get(self.severity, 0.5)
        return base_score * self.confidence * (1 + len(self.files) * 0.1)


class FindingCluster:
    """Group of similar findings."""
    
    def __init__(self, representative: Finding):
        self.id = f"cluster_{representative.id}"
        self.representative = representative
        self.members: List[Finding] = [representative]
        self.pattern: Optional[str] = None
        
    def add(self, finding: Finding):
        """Add finding to cluster."""
        self.members.append(finding)
        # Update representative if new finding has higher impact
        if finding.impact_score > self.representative.impact_score:
            self.representative = finding
    
    @property
    def size(self) -> int:
        return len(self.members)
    
    @property
    def combined_severity(self) -> str:
        """Get highest severity in cluster."""
        severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        for severity in severities:
            if any(f.severity == severity for f in self.members):
                return severity
        return "MEDIUM"
    
    @property
    def affected_files(self) -> List[str]:
        """Get all unique affected files."""
        files = set()
        for finding in self.members:
            files.update(finding.files)
        return sorted(files)
    
    def detect_pattern(self) -> Optional[str]:
        """Detect common pattern in cluster."""
        if self.size < 3:
            return None
            
        # Analyze commonalities
        common_words = self._find_common_words()
        common_files = self._find_common_file_patterns()
        
        if common_words and common_files:
            return f"Pattern: {common_words} issues across {common_files}"
        elif common_words:
            return f"Pattern: Repeated {common_words} issues"
        elif common_files:
            return f"Pattern: Issues concentrated in {common_files}"
        
        return None
    
    def _find_common_words(self) -> Optional[str]:
        """Find common significant words in descriptions."""
        from collections import Counter
        
        # Extract words from all descriptions
        all_words = []
        for finding in self.members:
            words = finding.description.lower().split()
            # Filter out common words
            significant = [w for w in words if len(w) > 4 and w not in {
                'the', 'this', 'that', 'with', 'from', 'have', 'been'
            }]
            all_words.extend(significant)
        
        # Find most common
        if all_words:
            counter = Counter(all_words)
            most_common = counter.most_common(1)[0]
            if most_common[1] >= self.size * 0.6:  # Appears in 60%+ findings
                return most_common[0]
        
        return None
    
    def _find_common_file_patterns(self) -> Optional[str]:
        """Find common patterns in affected files."""
        if not self.affected_files:
            return None
            
        # Check for common directories
        dirs = ['/'.join(f.split('/')[:-1]) for f in self.affected_files]
        if dirs:
            from collections import Counter
            dir_counts = Counter(dirs)
            most_common_dir = dir_counts.most_common(1)[0]
            if most_common_dir[1] >= len(self.affected_files) * 0.7:
                return most_common_dir[0]
        
        # Check for common file patterns
        extensions = [f.split('.')[-1] for f in self.affected_files if '.' in f]
        if extensions:
            from collections import Counter
            ext_counts = Counter(extensions)
            most_common_ext = ext_counts.most_common(1)[0]
            if most_common_ext[1] >= len(self.affected_files) * 0.8:
                return f"*.{most_common_ext[0]} files"
        
        return None


class AdvancedConsolidator:
    """Advanced finding consolidation with clustering and pattern detection."""
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.embeddings = get_embeddings()
        
    async def consolidate(
        self,
        initial_findings: Dict[str, Any],
        deep_findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Consolidate findings with advanced techniques.
        
        Returns:
            Dict with consolidated findings, clusters, and insights
        """
        # 1. Convert to Finding objects
        all_findings = self._extract_all_findings(initial_findings, deep_findings)
        
        # 2. Calculate embeddings for similarity
        await self._calculate_finding_embeddings(all_findings)
        
        # 3. Cluster similar findings
        clusters = self._cluster_findings(all_findings)
        
        # 4. Detect cross-cutting patterns
        patterns = self._detect_cross_patterns(clusters)
        
        # 5. Generate insights
        insights = self._generate_insights(clusters, patterns)
        
        # 6. Prioritize and package results
        return self._package_results(clusters, patterns, insights)
    
    def _extract_all_findings(
        self,
        initial: Dict[str, Any],
        deep: Dict[str, Any]
    ) -> List[Finding]:
        """Extract and convert all findings to Finding objects."""
        findings = []
        
        # Map of source keys to FindingType
        type_mapping = {
            "bugs": FindingType.BUG,
            "security_issues": FindingType.SECURITY,
            "performance_issues": FindingType.PERFORMANCE,
            "architectural_issues": FindingType.ARCHITECTURE,
            "patterns": FindingType.PATTERN,
            "patterns_detected": FindingType.PATTERN,
        }
        
        # Extract from initial phase
        for key, finding_type in type_mapping.items():
            if key in initial:
                for item in initial[key]:
                    finding = self._convert_to_finding(
                        item, finding_type, "initial"
                    )
                    if finding:
                        findings.append(finding)
        
        # Extract from deep phase
        for key, finding_type in type_mapping.items():
            if key in deep:
                for item in deep[key]:
                    finding = self._convert_to_finding(
                        item, finding_type, "deep"
                    )
                    if finding:
                        findings.append(finding)
        
        # Handle special cases (areas_of_concern, etc)
        if "areas_of_concern" in initial:
            for concern in initial["areas_of_concern"]:
                finding = self._classify_concern(concern, "initial")
                if finding:
                    findings.append(finding)
        
        return findings
    
    def _convert_to_finding(
        self,
        item: Any,
        finding_type: FindingType,
        source: str
    ) -> Optional[Finding]:
        """Convert raw finding data to Finding object."""
        try:
            # Handle different formats
            if isinstance(item, dict):
                return Finding(
                    type=finding_type,
                    title=item.get("title", item.get("issue", str(item)[:100])),
                    description=item.get("description", str(item)),
                    severity=item.get("severity", "MEDIUM").upper(),
                    confidence=float(item.get("confidence", 0.7)),
                    files=self._extract_files(item),
                    line_ranges=self._extract_line_ranges(item),
                    related_findings=[],
                    source_phase=source,
                    metadata=item
                )
            else:
                # Simple string finding
                return Finding(
                    type=finding_type,
                    title=str(item)[:100],
                    description=str(item),
                    severity="MEDIUM",
                    confidence=0.7,
                    files=[],
                    line_ranges=[],
                    related_findings=[],
                    source_phase=source,
                    metadata={}
                )
        except Exception as e:
            logger.warning(f"Failed to convert finding: {e}")
            return None
    
    def _extract_files(self, item: Dict[str, Any]) -> List[str]:
        """Extract file references from finding."""
        files = []
        
        # Direct file references
        if "file" in item:
            files.append(item["file"])
        if "files" in item and isinstance(item["files"], list):
            files.extend(item["files"])
        if "file_path" in item:
            files.append(item["file_path"])
        
        # From entities
        if "entities_involved" in item:
            entities = item["entities_involved"]
            if isinstance(entities, list):
                files.extend([e for e in entities if '.' in e])
        
        return list(set(files))  # Unique
    
    def _extract_line_ranges(self, item: Dict[str, Any]) -> List[Tuple[int, int]]:
        """Extract line number ranges."""
        ranges = []
        
        if "line" in item:
            line = item["line"]
            ranges.append((line, line))
        
        if "start_line" in item and "end_line" in item:
            ranges.append((item["start_line"], item["end_line"]))
        
        return ranges
    
    def _classify_concern(self, concern: Any, source: str) -> Optional[Finding]:
        """Classify area_of_concern into proper finding type."""
        concern_str = str(concern).lower()
        
        if "architectural" in concern_str:
            finding_type = FindingType.ARCHITECTURE
        elif "security" in concern_str:
            finding_type = FindingType.SECURITY
        elif "performance" in concern_str:
            finding_type = FindingType.PERFORMANCE
        elif "bug" in concern_str or "error" in concern_str:
            finding_type = FindingType.BUG
        else:
            finding_type = FindingType.ARCHITECTURE  # Default
        
        return self._convert_to_finding(concern, finding_type, source)
    
    async def _calculate_finding_embeddings(self, findings: List[Finding]):
        """Calculate embeddings for similarity comparison."""
        for finding in findings:
            # Create searchable text
            text = f"{finding.title} {finding.description}"
            # Store embedding in metadata
            finding.metadata["embedding"] = self.embeddings.encode(text)
    
    def _cluster_findings(self, findings: List[Finding]) -> List[FindingCluster]:
        """Cluster similar findings using embeddings."""
        clusters: List[FindingCluster] = []
        clustered_ids = set()
        
        # Sort by impact score for better representative selection
        sorted_findings = sorted(
            findings, key=lambda f: f.impact_score, reverse=True
        )
        
        for finding in sorted_findings:
            if finding.id in clustered_ids:
                continue
                
            # Create new cluster
            cluster = FindingCluster(finding)
            clustered_ids.add(finding.id)
            
            # Find similar findings
            for other in sorted_findings:
                if other.id in clustered_ids or other.id == finding.id:
                    continue
                
                # Calculate similarity
                if self._are_similar(finding, other):
                    cluster.add(other)
                    clustered_ids.add(other.id)
                    # Mark as related
                    finding.related_findings.append(other.id)
                    other.related_findings.append(finding.id)
            
            # Detect pattern in cluster
            cluster.pattern = cluster.detect_pattern()
            
            clusters.append(cluster)
        
        return clusters
    
    def _are_similar(self, f1: Finding, f2: Finding) -> bool:
        """Check if two findings are similar."""
        # Same type requirement
        if f1.type != f2.type:
            return False
        
        # Check embedding similarity
        if "embedding" in f1.metadata and "embedding" in f2.metadata:
            similarity = f1.metadata["embedding"].cosine_similarity(
                f2.metadata["embedding"]
            )
            if similarity >= self.similarity_threshold:
                return True
        
        # Fallback: Check file overlap
        file_overlap = set(f1.files) & set(f2.files)
        if file_overlap and len(file_overlap) >= len(f1.files) * 0.5:
            return True
        
        return False
    
    def _detect_cross_patterns(
        self, clusters: List[FindingCluster]
    ) -> List[Dict[str, Any]]:
        """Detect patterns across different finding types."""
        patterns = []
        
        # 1. File hotspots (files with multiple issue types)
        file_issues = defaultdict(lambda: defaultdict(list))
        for cluster in clusters:
            for file in cluster.affected_files:
                file_issues[file][cluster.representative.type].append(cluster)
        
        for file, type_clusters in file_issues.items():
            if len(type_clusters) >= 3:  # Multiple issue types
                patterns.append({
                    "type": "hotspot",
                    "description": f"File '{file}' has multiple issue types",
                    "details": {
                        "file": file,
                        "issue_types": list(type_clusters.keys()),
                        "total_issues": sum(
                            c.size for clusters in type_clusters.values()
                            for c in clusters
                        )
                    }
                })
        
        # 2. Cascading issues (bugs causing performance issues)
        bug_clusters = [c for c in clusters if c.representative.type == FindingType.BUG]
        perf_clusters = [c for c in clusters if c.representative.type == FindingType.PERFORMANCE]
        
        for bug_cluster in bug_clusters:
            bug_files = set(bug_cluster.affected_files)
            for perf_cluster in perf_clusters:
                perf_files = set(perf_cluster.affected_files)
                if bug_files & perf_files:  # Overlap
                    patterns.append({
                        "type": "cascade",
                        "description": "Bug potentially causing performance issue",
                        "details": {
                            "bug": bug_cluster.representative.title,
                            "performance": perf_cluster.representative.title,
                            "common_files": list(bug_files & perf_files)
                        }
                    })
        
        # 3. Architectural decay (many architectural issues in one area)
        arch_clusters = [c for c in clusters if c.representative.type == FindingType.ARCHITECTURE]
        if len(arch_clusters) >= 3:
            # Group by directory
            dir_clusters = defaultdict(list)
            for cluster in arch_clusters:
                for file in cluster.affected_files:
                    dir_path = '/'.join(file.split('/')[:-1])
                    dir_clusters[dir_path].append(cluster)
            
            for dir_path, clusters_in_dir in dir_clusters.items():
                if len(clusters_in_dir) >= 2:
                    patterns.append({
                        "type": "architectural_decay",
                        "description": f"Multiple architectural issues in {dir_path}",
                        "details": {
                            "directory": dir_path,
                            "issue_count": len(clusters_in_dir),
                            "issues": [c.representative.title for c in clusters_in_dir]
                        }
                    })
        
        return patterns
    
    def _generate_insights(
        self,
        clusters: List[FindingCluster],
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate high-level insights from clusters and patterns."""
        insights = []
        
        # 1. Critical mass insight
        critical_clusters = [
            c for c in clusters 
            if c.combined_severity in ["CRITICAL", "HIGH"]
        ]
        if len(critical_clusters) >= 3:
            insights.append({
                "type": "critical_mass",
                "title": "Multiple critical issues detected",
                "description": f"Found {len(critical_clusters)} high-severity issue clusters",
                "recommendation": "Prioritize fixing critical issues before adding new features",
                "clusters": [c.id for c in critical_clusters]
            })
        
        # 2. Pattern insights
        if patterns:
            hotspots = [p for p in patterns if p["type"] == "hotspot"]
            if hotspots:
                worst_hotspot = max(
                    hotspots, 
                    key=lambda h: h["details"]["total_issues"]
                )
                insights.append({
                    "type": "code_hotspot",
                    "title": "Code quality hotspot detected",
                    "description": f"File {worst_hotspot['details']['file']} has issues across {len(worst_hotspot['details']['issue_types'])} categories",
                    "recommendation": "Consider refactoring this file to improve maintainability"
                })
        
        # 3. Cluster size insights
        large_clusters = [c for c in clusters if c.size >= 5]
        if large_clusters:
            largest = max(large_clusters, key=lambda c: c.size)
            insights.append({
                "type": "repeated_issue",
                "title": f"Repeated {largest.representative.type.value} pattern",
                "description": f"Found {largest.size} similar {largest.representative.type.value} issues",
                "recommendation": "This suggests a systematic problem that needs architectural solution",
                "pattern": largest.pattern
            })
        
        return insights
    
    def _package_results(
        self,
        clusters: List[FindingCluster],
        patterns: List[Dict[str, Any]],
        insights: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Package results in expected format."""
        # Group clusters by type
        categorized = defaultdict(list)
        
        for cluster in clusters:
            # Use representative for cleaner output
            finding = cluster.representative
            enhanced_finding = {
                **finding.metadata,  # Original data
                "cluster_id": cluster.id,
                "cluster_size": cluster.size,
                "combined_severity": cluster.combined_severity,
                "pattern": cluster.pattern,
                "affected_files_count": len(cluster.affected_files),
                "impact_score": finding.impact_score
            }
            
            # Map to expected keys
            if finding.type == FindingType.BUG:
                categorized["bugs"].append(enhanced_finding)
            elif finding.type == FindingType.SECURITY:
                categorized["security_issues"].append(enhanced_finding)
            elif finding.type == FindingType.PERFORMANCE:
                categorized["performance_issues"].append(enhanced_finding)
            elif finding.type == FindingType.ARCHITECTURE:
                categorized["architectural_issues"].append(enhanced_finding)
            elif finding.type == FindingType.PATTERN:
                categorized["patterns"].append(enhanced_finding)
        
        # Sort each category by impact
        for category in categorized:
            categorized[category].sort(
                key=lambda x: x.get("impact_score", 0),
                reverse=True
            )
        
        # Add insights as recommendations
        categorized["recommendations"] = [
            {
                "type": "recommendation",
                "title": insight["title"],
                "description": insight["description"],
                "action": insight.get("recommendation", ""),
                "metadata": insight
            }
            for insight in insights
        ]
        
        # Add summary statistics
        categorized["_summary"] = {
            "total_clusters": len(clusters),
            "total_findings": sum(c.size for c in clusters),
            "patterns_detected": len(patterns),
            "insights_generated": len(insights),
            "critical_clusters": len([
                c for c in clusters 
                if c.combined_severity in ["CRITICAL", "HIGH"]
            ])
        }
        
        return dict(categorized)
```

### 2. Integración en DreamOrchestrator

```python
# En orchestrator.py
async def _consolidate_findings(
    self, session_id: str, initial: Dict[str, Any], deep: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Consolidate findings from different analysis phases.
    
    Now uses advanced consolidation with clustering and pattern detection.
    """
    # Use advanced consolidator if available
    try:
        from .consolidation import AdvancedConsolidator
        
        consolidator = AdvancedConsolidator(similarity_threshold=0.8)
        consolidated = await consolidator.consolidate(initial, deep)
        
        # Convert to list format expected by InsightWriter
        return self._convert_to_insight_list(session_id, consolidated)
        
    except ImportError:
        logger.info("Advanced consolidator not available, using basic method")
        # Fallback to current implementation
        return await self._basic_consolidate_findings(session_id, initial, deep)
```

## Plan de Implementación

### Fase 1: Core Development (3-4 horas)
1. Crear `dream/consolidation.py`
2. Implementar clases Finding, FindingCluster
3. Implementar AdvancedConsolidator
4. Escribir tests unitarios

### Fase 2: Integration (1-2 horas)
1. Modificar orchestrator.py para usar consolidator
2. Asegurar compatibilidad con InsightWriter
3. Mantener fallback a método actual
4. Tests de integración

### Fase 3: Tuning (1 hora)
1. Ajustar similarity_threshold basado en pruebas
2. Refinar detección de patrones
3. Optimizar clustering para performance

## Consideraciones Especiales

### 1. Performance

Con proyectos grandes (1000+ findings):
- Usar batching para embeddings
- Implementar early stopping en clustering
- Cache de similaridades calculadas

### 2. Memoria

Para limitar uso de memoria:
```python
MAX_FINDINGS_TO_PROCESS = 1000
if len(all_findings) > MAX_FINDINGS_TO_PROCESS:
    # Procesar solo los más importantes
    all_findings.sort(key=lambda f: f.impact_score, reverse=True)
    all_findings = all_findings[:MAX_FINDINGS_TO_PROCESS]
```

### 3. Configuración

Agregar a `.acolyte`:
```yaml
dream:
  consolidation:
    similarity_threshold: 0.8
    max_cluster_size: 20
    min_pattern_size: 3
    enable_embeddings: true
```

## Beneficios Esperados

1. **Reducción de ruido**: 50-70% menos findings duplicados
2. **Mejores insights**: Detección automática de patrones
3. **Priorización inteligente**: Focus en problemas sistémicos
4. **Actionable results**: Recomendaciones específicas

## Métricas de Éxito

- [ ] Reducción 60%+ en findings mostrados al usuario
- [ ] Detección de 3+ patrones cross-cutting por análisis
- [ ] Tiempo de consolidación <2 segundos para 500 findings
- [ ] 0 pérdida de findings críticos

## Ejemplos de Mejora

### Antes
```
Found 47 bugs:
- NullPointerException in UserService.java:45
- NullPointerException in UserService.java:67  
- NullPointerException in UserService.java:89
- Unhandled exception in OrderService.java:23
- Unhandled exception in OrderService.java:45
... 42 more similar issues
```

### Después
```
Found 2 bug clusters (47 total issues):

Cluster 1: Null safety issues (23 occurrences)
- Pattern: Missing null checks in service layer
- Severity: HIGH
- Affected files: 8 service classes
- Recommendation: Implement @NonNull annotations and validation layer

Cluster 2: Exception handling (24 occurrences)  
- Pattern: Unhandled exceptions in API endpoints
- Severity: CRITICAL
- Affected files: 12 controller classes
- Recommendation: Global exception handler needed
```

## Referencias

- [Semantic Similarity in NLP](https://www.sbert.net/docs/usage/semantic_textual_similarity.html)
- [DBSCAN Clustering](https://scikit-learn.org/stable/modules/clustering.html#dbscan)
- [Code Smell Detection Patterns](https://refactoring.guru/refactoring/smells)
