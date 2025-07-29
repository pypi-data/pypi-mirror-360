# 📚 Language-Specific Chunkers

This directory contains 31 specialized chunkers for different programming languages using tree-sitter AST parsing or pattern matching.

## 🎯 Overview

Each chunker:

1. Divides code into semantic units (functions, classes, methods)
2. Preserves context with 20% overlap between chunks
3. Extracts language-specific metadata when implemented
4. Respects minimum chunk size of 1 line (changed from 5 to avoid losing small functions)

## 📊 Metadata Implementation Status

### Metadata Scope

**What IS extracted**: All code-relevant metadata including:

- Code structure (functions, classes, methods)
- Language-specific features (async, generics, decorators)
- Quality metrics (complexity, TODOs, patterns)
- Security issues (hardcoded credentials, SQL injection)
- Dependencies and imports
- Configuration patterns

**What is NOT extracted**:

- Academic metadata (author, citations, publication date)
- License information
- Version history
- External documentation links

The chunkers focus exclusively on code analysis and searchability, not bibliographic information.

### Implementation Status

Based on actual code review:

| Language   | File           | Metadata Status     | What's Extracted                                                                                                                                                                                                               |
| ---------- | -------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Bash       | bash.py        | ✅ Full             | name, has_local_vars, calls_functions, uses_conditionals, uses_loops, uses_error_handling, uses_strict_mode                                                                                                                    |
| C          | c.py           | ✅ Full             | modifiers, return_type, parameters, is_static, is_inline, is_extern, storage_class, complexity, patterns, todos, security, memory_ops, preprocessor                                                                            |
| C++        | cpp.py         | ✅ Full             | modifiers, visibility, is_virtual, is_override, is_final, is_const, is_noexcept, is_template, template_params, base_classes, return_type, parameters, complexity, patterns, todos, security, modern_cpp, stl_usage             |
| C#         | csharp.py      | ✅ Full             | type_kind, modifiers, is_public, is_abstract, is_sealed, is_static, is_partial, generics, base_types, attributes, methods, properties, events, complexity, patterns, todos, security                                           |
| ConfigBase | config_base.py | 🔧 Base class       | Abstract base with shared methods (\_extract_env_vars, \_detect_secrets, etc.) used by JSON/YAML/TOML/INI                                                                                                                      |
| CSS        | css.py         | ✅ Full             | selectors, selector_types, specificity, properties, patterns (anti/performance/maintenance), variables_used, at_rule info, mixin/function info (SCSS), complexity, todos                                                       |
| Default    | default.py     | 🟡 Partial metadata | Enhanced heuristic chunker with pattern detection for functions/classes, TODO extraction, complexity hints, and structure-aware chunking                                                                                       |
| Dockerfile | dockerfile.py  | ✅ Full             | instruction type, is_multi_line, base_image, stage_name, ports, env_vars, format (exec/shell), multi_stage_copy                                                                                                                |
| Elisp      | elisp.py       | ✅ Full             | Functions: type, parameters, has_docstring, is_interactive, is_macro. Classes: superclasses, slots. Variables: is_customizable, is_constant                                                                                    |
| Go         | go.py          | ✅ Full             | Methods: receiver info, pointer vs value. Functions: parameters, returns, complexity, patterns. Goroutines, channels, defer count. Types: fields, embeds, struct tags. Security analysis                                       |
| HTML       | html.py        | ✅ Full             | tag_name, attributes, semantic_role, accessibility (aria-\*, alt), seo (meta, og tags), resources, scripts, forms, todos, security (inline scripts, CSRF), quality metrics                                                     |
| INI        | ini.py         | ✅ Full             | sections, security_summary (passwords, tokens, exposed ports/hosts), quality (comments, duplicates), dependencies (files, env_vars), patterns (config_type, frameworks), todos, settings, complexity                           |
| Java       | java.py        | ✅ Full             | modifiers, visibility, annotations, class metadata (implements, extends, generics), method metadata (parameters, throws), interface metadata, complexity, patterns, todos, quality, security, dependencies                     |
| JSON       | json.py        | ✅ Full             | config_type, structure (type, depth), size_metrics, patterns (json_schema, openapi_spec), env_vars, secrets, urls, paths, special fields for npm/typescript configs                                                            |
| Kotlin     | kotlin.py      | ✅ Full             | modifiers, visibility, is_suspend/inline/operator, parameters, return_type, annotations, class metadata (data/sealed/enum), property metadata, complexity, patterns, todos, quality, security                                  |
| Lua        | lua.py         | ✅ Full             | Functions: is_local, parameters, is_method, is_metamethod. Tables: fields, methods, has_metatable, is_class                                                                                                                    |
| Makefile   | makefile.py    | ✅ Full             | Rules: targets, prerequisites, is_phony, has_recipe, is_pattern_rule. Variables: variable_name, assignment_type, is_export, is_override                                                                                        |
| Markdown   | markdown.py    | ✅ Full             | Headings: level, text, is_title. Code blocks: language, is_executable, has_output. Lists: type, item_count, has_checkboxes. TODOs, links, structure metrics, quality analysis                                                  |
| Perl       | perl.py        | ✅ Full             | Subroutines: parameters, has_prototype, is_anonymous, attributes, uses_shift, uses_at_underscore. Packages: version, parent_classes, exports, imports                                                                          |
| PHP        | php.py         | ✅ Full             | Functions: visibility, modifiers, parameters (PHP 8), return_type, attributes, complexity, quality, dependencies, patterns, todos, security. Classes: type, extends, implements, uses (traits), methods, properties, constants |
| Python     | python.py      | ✅ Full             | is_async, decorators, type_hints, complexity, todos, security, parameters, return_type, visibility, modifiers, patterns, quality                                                                                               |
| R          | r.py           | ✅ Full             | parameters, has_return, uses_vectorization, assignment_type, complexity, todos, patterns, quality (roxygen docs, tidyverse usage, tests)                                                                                       |
| Ruby       | ruby.py        | ✅ Full             | visibility, is_singleton, parameters, has_yield, has_block_param, aliases, complexity, todos, patterns, base_classes, modules, attr_accessors                                                                                  |
| Rust       | rust.py        | ✅ Full             | visibility, is_async, is_unsafe, is_const, attributes, lifetimes, generics, complexity, patterns, todos, quality, security, dependencies                                                                                       |
| SQL        | sql.py         | ✅ Full             | statement_type, object_name, dependencies, is_temporary, has_conditions, complexity, todos, patterns, security (injection, dynamic SQL, grants), quality                                                                       |
| Swift      | swift.py       | ✅ Full             | visibility, modifiers, is_async, parameters, complexity, patterns, todos, security, generics, property wrappers, protocol conformances, SwiftUI detection                                                                      |
| TOML       | toml.py        | ✅ Full             | table_type, keys, has_subtables, todos, patterns (config detection), complexity (key_count, nesting), tree-sitter based                                                                                                        |
| TypeScript | typescript.py  | ✅ Full             | modifiers, visibility, is_async, parameters, return_type, generics, decorators, complexity, patterns, todos, security, dependencies, JSDoc detection, React/Angular/Vue patterns                                               |
| Vim        | vim.py         | ✅ Full             | scope (script-local/global), is_autoload, parameters, flags, complexity, patterns, todos, calls, variables by scope, plugin detection, augroup metadata                                                                        |
| XML        | xml.py         | ✅ Full             | tag_name, namespace, attributes, depth, namespaces, complexity, patterns, security (hardcoded passwords/credentials), todos, dependencies (Maven), schema detection                                                            |
| YAML       | yaml.py        | ✅ Full             | key_name, structure_type (mapping/sequence/scalar), depth, todos, references (anchors/aliases), complexity (nesting/child_count), patterns (config/security/quality), tree-sitter based                                        |

### Tree-sitter Based (25 languages)

Using `tree-sitter-languages` package for real AST parsing:

| Language              | File            | Chunk Size | AST Node Types Used                                                                          |
| --------------------- | --------------- | ---------- | -------------------------------------------------------------------------------------------- |
| Python                | `python.py`     | 150 lines  | function_definition, class_definition, decorated_definition, import_statement                |
| JavaScript/TypeScript | `typescript.py` | 150 lines  | function_declaration, class_declaration, method_definition, arrow_function, import_statement |
| Java                  | `java.py`       | 100 lines  | class_declaration, method_declaration, interface_declaration, import_declaration             |
| Go                    | `go.py`         | 100 lines  | function_declaration, method_declaration, type_declaration, import_declaration               |
| Rust                  | `rust.py`       | 100 lines  | function_item, impl_item, struct_item, use_declaration                                       |
| C                     | `c.py`          | 100 lines  | function_definition, struct_specifier, declaration                                           |
| C++                   | `cpp.py`        | 100 lines  | function_definition, class_specifier, namespace_definition                                   |
| Ruby                  | `ruby.py`       | 120 lines  | method, class, module, require/load                                                          |
| PHP                   | `php.py`        | 120 lines  | function_definition, class_declaration, namespace_definition                                 |
| Kotlin                | `kotlin.py`     | 100 lines  | function_declaration, class_declaration, import_list                                         |
| SQL                   | `sql.py`        | 100 lines  | create_table, select_statement, function_definition                                          |
| R                     | `r.py`          | 100 lines  | function_definition, call, assignment                                                        |
| Lua                   | `lua.py`        | 100 lines  | function_declaration, function_definition, assignment                                        |
| Bash                  | `bash.py`       | 100 lines  | function_definition, command, case_statement                                                 |
| Perl                  | `perl.py`       | 100 lines  | subroutine_declaration_statement, package_statement                                          |
| Dockerfile            | `dockerfile.py` | 100 lines  | from_instruction, run_instruction, cmd_instruction                                           |
| Makefile              | `makefile.py`   | 100 lines  | rule, variable_assignment, function_call                                                     |
| Elisp                 | `elisp.py`      | 100 lines  | defun, defvar, defmacro                                                                      |
| HTML                  | `html.py`       | 150 lines  | element, doctype, comment                                                                    |
| CSS                   | `css.py`        | 100 lines  | rule_set, media_statement, keyframes_statement                                               |
| JSON                  | `json.py`       | 50 lines   | object, array, pair                                                                          |
| YAML                  | `yaml.py`       | 50 lines   | block_mapping, block_sequence, key_value                                                     |
| TOML                  | `toml.py`       | 50 lines   | table, pair, array                                                                           |
| Markdown              | `markdown.py`   | 50 lines   | heading, code_block, list                                                                    |

### Pattern Matching Based (5 languages)

Using regex when tree-sitter grammar not available:

| Language  | File        | Chunk Size | Pattern Types                                           |
| --------- | ----------- | ---------- | ------------------------------------------------------- |
| C#        | `csharp.py` | 100 lines  | class/interface/struct, methods, properties, namespaces |
| Swift     | `swift.py`  | 100 lines  | class/struct/enum, functions, protocols, extensions     |
| XML       | `xml.py`    | 100 lines  | Elements via ElementTree + regex patterns               |
| VimScript | `vim.py`    | 100 lines  | functions, commands, autogroups                         |
| INI       | `ini.py`    | 50 lines   | sections, key-value pairs                               |

### Enhanced Fallback (Pattern Matching)

| Language | File         | Method                                                 | Features                                                            |
| -------- | ------------ | ------------------------------------------------------ | ------------------------------------------------------------------- |
| Default  | `default.py` | Heuristic pattern detection + structure-aware chunking | Function/class detection, metadata extraction, indentation analysis |

## ✅ Verified Implementations

These chunkers have been verified to correctly extract AND assign metadata:

- **bash.py**: Full function and script metadata
- **c.py**: Comprehensive C-specific metadata including security patterns
- **cpp.py**: Extensive C++ metadata with modern features detection
- **csharp.py**: Complete metadata despite using pattern matching instead of tree-sitter
- **config_base.py**: Abstract base class providing shared methods for JSON/YAML/TOML/INI chunkers
- **html.py**: Complete HTML-specific metadata including accessibility and SEO analysis
- **ini.py**: Comprehensive configuration analysis with security detection
- **java.py**: Full Java metadata with framework detection from annotations
- **json.py**: Smart config recognition with special handling for package.json, tsconfig.json
- **kotlin.py**: Extensive Kotlin/Android metadata including coroutines and null safety
- **swift.py**: Complete Swift metadata with SwiftUI, async/await, property wrappers
- **toml.py**: Full TOML table metadata with configuration pattern detection
- **typescript.py**: Comprehensive JS/TS/JSX/TSX metadata with framework detection
- **vim.py**: Rich VimScript metadata including functions, commands, autogroups, plugins
- **xml.py**: Extensive XML metadata with security analysis and Maven dependency extraction
- **yaml.py**: Complete YAML metadata with structure analysis and security patterns

## 🧪 Test Coverage

**Tests completos implementados para todos los 31 lenguajes**:
- Ver `/tests/rag/chunking/` para todos los archivos de test
- Cada lenguaje tiene su archivo `test_[language]_chunker_complete.py`
- Cobertura general del módulo RAG/chunking: >90%

## 🐛 Implementation Issues Found

### ✅ Fixed Issues

- **rust.py**: Had incorrect comment claiming "language_specific metadata is not supported" when it actually is. Now properly applies all metadata.
- **ruby.py**: Changed inheritance from BaseChunker to LanguageChunker for consistency with other language chunkers. This fixed the issue where methods were not being chunked properly.

### 📊 Metadata Implementation Summary

**Current Status**: All 31 chunkers have been verified:

- **27 chunkers**: ✅ Full metadata implementation (extract AND assign)
- **3 chunkers**: 🟡 Partial metadata (basic or incomplete)
- **1 non-chunker**: 🔧 ConfigBase (abstract base class)

### 🔧 Ruby Chunker Cleanup

- **Refactored**: Split 150+ line method into 6 smaller methods
- **Cleaned**: Removed all Spanish comments and debug prints
- **Documented**: Added proper docstrings and variable documentation
- **Tests**: Cleaned test files (removed Spanish, debug prints)

### Quick Fix Template

For chunkers that have metadata extraction methods but don't apply them, add this line in `_create_chunk_from_node()`:

```python
# After creating the chunk, before returning:
if chunk:
    chunk.metadata.language_specific = self._extract_[language]_metadata(node)
```

### Status Correction

The README previously claimed only Python, Java, and XML had metadata implemented. This is incorrect. Based on verified code review:

- Python: ✅ Full metadata (complex extraction and properly assigned)
- Ruby: ✅ Full metadata (comprehensive extraction and properly assigned)
- R: ✅ Full metadata (enhanced with complexity, patterns, todos, quality)
- SQL: ✅ Full metadata (enhanced with security analysis, patterns, quality)
- Rust: ✅ Full metadata (now properly applied after fix)
- Many other languages marked as ✅ Full also have metadata properly implemented

## 🚀 Usage Examples

### Direct Chunker Usage

```python
from acolyte.rag.chunking.languages import PythonChunker

# Create chunker
chunker = PythonChunker()

# Chunk content
content = '''def hello():
    print("Hello World")'''
chunks = await chunker.chunk(content, "example.py")

# Access chunk data
for chunk in chunks:
    print(f"Type: {chunk.metadata.chunk_type}")
    print(f"Lines: {chunk.metadata.start_line}-{chunk.metadata.end_line}")
    print(f"Metadata: {chunk.metadata.language_specific}")
```

### Using ChunkerFactory (Recommended)

```python
from acolyte.rag.chunking import ChunkerFactory

# Factory automatically selects the right chunker
factory = ChunkerFactory()
chunker = factory.get_chunker("example.py")  # Detects Python from extension

# Or use AdaptiveChunker for intelligent chunking
from acolyte.rag.chunking import AdaptiveChunker

adaptive = AdaptiveChunker()
chunks = await adaptive.chunk_file("complex_project.py")
```

### Output Structure

```python
# Each chunk returns a Chunk object with:
chunk = Chunk(
    content="def hello():\n    print('Hello')",  # Actual code
    metadata=ChunkMetadata(
        chunk_type=ChunkType.FUNCTION,
        start_line=1,
        end_line=2,
        language="python",
        file_path="example.py",
        name="hello",  # Function/class name
        language_specific={  # Rich metadata
            "is_async": False,
            "parameters": [],
            "complexity": {"cyclomatic": 1},
            "todos": [],
            "patterns": {"anti": [], "design": []}
        }
    )
)
```

## 📐 Common Configuration

All chunkers share these settings from base class:

```python
chunk_size = 100      # Default, overridden per language
overlap = 20          # 20% overlap between chunks
min_chunk_size = 1    # Minimum 1 line (was 5, changed to preserve small functions)
```

### Why Different Chunk Sizes?

| Size      | Languages                       | Reasoning                                                |
| --------- | ------------------------------- | -------------------------------------------------------- |
| 50 lines  | JSON, YAML, TOML, Markdown, INI | Config files are usually smaller, need finer granularity |
| 100 lines | Java, Go, C/C++, Rust, SQL      | Statically typed languages with verbose syntax           |
| 120 lines | Ruby, PHP                       | Dynamic languages with medium verbosity                  |
| 150 lines | Python, TypeScript, HTML        | Concise syntax allows larger semantic units              |

## 🔧 Key Implementation Details

### Chunker Selection Strategy

**Use tree-sitter when**:

- Grammar is available in `tree-sitter-languages`
- Need precise AST-based parsing
- Language has complex nested structures

**Use pattern matching when**:

- No tree-sitter grammar available
- Simple language structure
- Configuration files (INI, some XML)

### Integration with ACOLYTE

```python
# ChunkerFactory: Automatic language detection
from acolyte.rag.chunking import ChunkerFactory

factory = ChunkerFactory()
chunker = factory.get_chunker("file.py")  # Returns PythonChunker
chunker = factory.get_chunker("unknown.xyz")  # Returns DefaultChunker

# AdaptiveChunker: Intelligent multi-file processing
from acolyte.rag.chunking import AdaptiveChunker

adaptive = AdaptiveChunker()
# Automatically handles different file types in a project
chunks = await adaptive.chunk_directory("/path/to/project")
```

### BaseChunker Integration

All chunkers inherit from `BaseChunker` which provides:

- Tree-sitter setup via `_parse_with_tree_sitter()`
- Chunk validation with `_validate_chunks()`
- Overlap calculation
- Line counting utilities

### Tree-sitter Language Usage

Each tree-sitter chunker must implement:

```python
def _get_tree_sitter_language(self) -> Any:
    """Return the tree-sitter language object"""
    return get_language('python')  # Example

def _extract_chunks_from_tree(self, tree: tree_sitter.Tree, content: str) -> List[Tuple[str, int, int, str]]:
    """Extract chunks from AST"""
    # Custom logic per language
```

## 🛠️ Adding a New Language

1. Create file in `languages/`:

```python
from tree_sitter_languages import get_language
from ..base import BaseChunker

class NewLangChunker(BaseChunker):
    def _get_language_name(self) -> str:
        return 'newlang'

    def _get_tree_sitter_language(self) -> Any:
        return get_language('newlang')  # or None for pattern-based
```

2. Register in `__init__.py`:

```python
from .newlang import NewLangChunker
__all__.append('NewLangChunker')
```

3. Add to factory mapping in `language_mappings.py`:

```python
LANGUAGE_CHUNKER_MAP = {
    'newlang': 'NewLangChunker',
}
```

4. Add file extensions in `language_config.py`:

```python
'.nl': 'newlang',
'.newlang': 'newlang',
```

## 📊 Actual Performance

Based on testing:

- Tree-sitter parsing: ~50-100ms for 1000 lines
- Pattern matching: ~100-200ms for 1000 lines
- Memory usage: Minimal, chunks processed one at a time

## 🔍 Mixins Available

For pattern-based chunkers, these mixins add functionality:

- `ComplexityMixin` - Cyclomatic complexity calculation
- `TodoExtractionMixin` - Extract TODO/FIXME/HACK comments
- `SecurityAnalysisMixin` - Detect hardcoded passwords, SQL injection
- `PatternDetectionMixin` - Language-specific patterns

## ⚠️ Known Issues

1. **C# regex fix applied**: Fixed modifier capture groups
2. **YAML structure handling**: Fixed for nested block_node
3. **XML namespaces**: ElementTree strips them, manually re-added
4. **Small chunks**: Now preserves 1-line functions/imports
5. **Small functions**: Changed minimum chunk size from 5 to 1 line

## 💡 DefaultChunker - Enhanced Fallback

The DefaultChunker has been significantly enhanced to provide intelligent chunking even without tree-sitter:

### Features:

- **Pattern Detection**: Recognizes functions, classes, and imports across multiple languages
- **Metadata Extraction**: TODOs, complexity hints, code patterns
- **Structure-Aware**: Respects code blocks using indentation analysis
- **Smart Type Guessing**: Determines ChunkType based on content heuristics

### Supported Patterns:

```python
# Functions: def, function, func, fn, arrow functions, methods
def python_func():  # ✓ Detected
int c_func() {}     # ✓ Detected
const js = () => {} # ✓ Detected

# Classes: class, struct, interface, trait
class MyClass:      # ✓ Detected
struct Data {}      # ✓ Detected
```

### Metadata Extracted:

- Lines of code (non-empty)
- TODO/FIXME/HACK comments with line numbers
- Complexity hint based on control structures
- Pattern detection (anti-patterns: long_block, deep_nesting)
- Comment presence detection


