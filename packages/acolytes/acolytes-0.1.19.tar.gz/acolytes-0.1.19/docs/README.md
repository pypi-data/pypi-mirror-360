# ACOLYTE Documentation

Welcome to the ACOLYTE documentation!

## 📚 Documentation Structure

### Installation
- **[Installation Atomic Flow](INSTALLATION_ATOMIC_FLOW.md)** - Complete step-by-step installation guide
- **[Multi-Project Ports](MULTI_PROJECT_PORTS.md)** - How multi-project port assignment works

### Core Documentation
- **[Architecture](ARCHITECTURE.md)** - System design and components
- **[API Reference](API.md)** - API endpoints and usage
- **[Development](DEVELOPMENT.md)** - Development setup and guidelines
- **[Configuration](CONFIGURATION.md)** - Configuration options
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

## 🚀 Quick Links

### For Users
- [Getting Started](../README.md#quick-start)
- [Commands Reference](../README.md#commands)
- [FAQ](FAQ.md)

### For Developers
- [Contributing Guide](../CONTRIBUTING.md)
- [Project Structure](ARCHITECTURE.md#project-structure)
- [Testing Guide](DEVELOPMENT.md#testing)

## 📖 Main Documentation

### System Overview

ACOLYTE is a local AI programming assistant that:
- Runs 100% on your machine
- Remembers everything across sessions
- Understands your entire codebase
- Integrates with Git for history
- Provides deep code analysis

### Key Concepts

1. **Global Installation** - ACOLYTE installs to `~/.acolyte/`
2. **Per-Project Data** - Each project's data stored separately
3. **Clean Projects** - Only `.acolyte.project` added to repos
4. **Privacy First** - No cloud, no telemetry

### Architecture Highlights

- **FastAPI** - Async web framework
- **Weaviate** - Vector database
- **SQLite** - Conversation history
- **Ollama** - Local LLM server
- **Tree-sitter** - Code parsing

## 🆘 Need Help?

- Check [Troubleshooting](TROUBLESHOOTING.md)
- Read the [FAQ](FAQ.md)
- Open an [Issue](https://github.com/yourusername/acolyte/issues)
