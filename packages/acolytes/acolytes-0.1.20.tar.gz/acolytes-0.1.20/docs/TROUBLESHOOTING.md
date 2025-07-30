# 🔧 ACOLYTE Troubleshooting Guide

## Common Issues and Solutions

### 🐳 Docker Backend: "No module named uvicorn"

**Problem**: The backend container keeps restarting with error:
```
/usr/local/bin/python: No module named uvicorn
```

**Cause**: The Dockerfile is trying to install `acolyte` from PyPI (doesn't exist) instead of `acolytes`.

**Solution**:

#### For TestPyPI installations:

Set the environment variable before running `acolyte install`:
```bash
# Windows PowerShell
$env:ACOLYTE_USE_TESTPYPI = "true"
acolyte install

# Linux/Mac
export ACOLYTE_USE_TESTPYPI=true
acolyte install
```

This will generate a Dockerfile that:
1. Installs dependencies from PyPI (reliable)
2. Installs only `acolytes` from TestPyPI without dependencies

#### Manual fix for existing installations:

1. Edit the Dockerfile at `~/.acolyte/Dockerfile`
2. Change this line:
   ```dockerfile
   RUN pip install --no-cache-dir acolyte
   ```
   To:
   ```dockerfile
   # For TestPyPI
   RUN pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ acolytes
   
   # Or for PyPI (when published)
   RUN pip install acolytes
   ```

3. Also fix the port and command:
   ```dockerfile
   EXPOSE 42000  # Not 8000
   CMD ["python", "-m", "uvicorn", "acolyte.api.main:app", "--host", "0.0.0.0", "--port", "42000"]
   ```

4. Force rebuild:
   ```powershell
   # Windows
   docker system prune -a --volumes -f
   acolyte start
   
   # Linux/Mac
   docker system prune -a --volumes -f
   acolyte start
   ```

### 🔄 Installation from TestPyPI

Since ACOLYTE is published as `acolytes` on TestPyPI:

```bash
# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ acolytes

# The command is still 'acolyte'
acolyte --version
```

### 📦 Package Name Clarification

- **Package name**: `acolytes` (for pip install)
- **Command name**: `acolyte` (unchanged)
- **Import name**: `from acolyte.xxx` (unchanged)

### 🚨 SQLite Error: "index idx_session_id already exists"

**Problem**: During `acolyte install`, database initialization fails.

**Cause**: The `schemas.sql` file has a redundant index creation.

**Solution**: This has been fixed in the latest version. If you encounter it:
1. Reset the installation: `acolyte reset --force`
2. Update to the latest version
3. Try again

### 💡 General Tips

1. **Always check Docker is running** before `acolyte start`
2. **First indexing is crucial** - don't skip `acolyte index`
3. **Use `acolyte doctor`** to diagnose issues
4. **Check logs**: `acolyte logs` or `docker logs acolyte-backend`

## Need More Help?

- Check the [main documentation](../README.md)
- Report issues at: https://github.com/unmasSk/acolyte/issues
- Include output of `acolyte doctor` in bug reports
