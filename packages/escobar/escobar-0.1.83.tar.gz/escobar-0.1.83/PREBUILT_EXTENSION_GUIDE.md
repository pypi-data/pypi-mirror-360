# Prebuilt Extension Guide

This guide explains how to create, build, and publish the escobar extension as a prebuilt JupyterLab extension.

## What is a Prebuilt Extension?

A prebuilt extension includes:
- ✅ **Compiled JavaScript/TypeScript** bundled into the Python package
- ✅ **No Node.js required** for installation
- ✅ **Simple pip install** - users get everything they need
- ✅ **Docker-friendly** - works in containers without build tools

## Build Process

### 1. Development Build
```bash
# For development with source maps and debugging
npm run build
```

### 2. Production Build (Prebuilt)
```bash
# Clean build for distribution
npm run build:prod
```

This creates:
- `escobar/labextension/` - Contains all prebuilt assets
- `escobar/labextension/static/` - Compiled JavaScript bundles
- `escobar/labextension/package.json` - Extension metadata
- `escobar/labextension/schemas/` - JSON schemas

### 3. Package Build
```bash
# Create wheel with prebuilt extension
python -m build --wheel
```

## Verification

### Check Prebuilt Files
```bash
# Verify labextension directory exists and has content
ls -la escobar/labextension/
ls -la escobar/labextension/static/

# Check wheel contents
python -c "
import zipfile
z = zipfile.ZipFile('dist/escobar-*.whl')
files = [f for f in z.namelist() if 'labextensions' in f]
print(f'Found {len(files)} extension files in wheel')
"
```

### Test Installation
```bash
# Test in clean environment
pip install dist/escobar-*.whl
jupyter server extension enable escobar
jupyter server extension list
```

## Publishing to PyPI

### 1. Build Production Version
```bash
# Clean everything first
npm run clean:all

# Build production version
npm run build:prod

# Create wheel
python -m build --wheel
```

### 2. Verify Package
```bash
# Check wheel contents
python -c "
import zipfile
z = zipfile.ZipFile('dist/escobar-*.whl')
labext_files = [f for f in z.namelist() if 'labextensions' in f]
print(f'✅ Extension files: {len(labext_files)}')
print('Key files:')
for f in labext_files[:5]:
    print(f'  {f}')
"

# Test import
python -c "import escobar; print('✅ Import successful')"
```

### 3. Upload to PyPI
```bash
# Upload using your publish script
./publish_to_pypi.sh

# Or manually
python -m twine upload dist/*
```

## Docker Usage

### Corrected Dockerfile
```dockerfile
FROM quay.io/jupyter/base-notebook:latest

# Install prebuilt extension (no Node.js needed!)
RUN pip install --no-cache-dir --upgrade escobar

# Enable server extension
RUN jupyter server extension enable escobar

# That's it! No jupyter labextension install needed
```

### What NOT to do
```dockerfile
# ❌ DON'T DO THIS (deprecated and requires Node.js)
RUN jupyter labextension install escobar

# ❌ DON'T DO THIS (not needed for prebuilt)
RUN npm install && npm run build
```

## Troubleshooting

### Extension Not Found
If you get "module 'escobar' could not be found":

1. **Check installation**:
   ```bash
   pip list | grep escobar
   python -c "import escobar; print('OK')"
   ```

2. **Check extension files**:
   ```bash
   python -c "
   import escobar
   import os
   print('Extension path:', os.path.dirname(escobar.__file__))
   labext_path = os.path.join(os.path.dirname(escobar.__file__), 'labextension')
   print('Labextension exists:', os.path.exists(labext_path))
   if os.path.exists(labext_path):
       print('Files:', os.listdir(labext_path))
   "
   ```

3. **Check Jupyter paths**:
   ```bash
   jupyter --paths
   jupyter server extension list
   ```

### Build Issues

1. **Missing files after build**:
   ```bash
   # Clean and rebuild
   npm run clean:all
   npm run build:prod
   
   # Check output
   ls -la escobar/labextension/static/
   ```

2. **Wheel missing extension files**:
   ```bash
   # Check pyproject.toml shared-data configuration
   grep -A 5 "shared-data" pyproject.toml
   ```

## File Structure

### Source Structure
```
escobar/
├── src/                    # TypeScript source
├── style/                  # CSS source  
├── schema/                 # JSON schemas
├── package.json           # Build configuration
├── pyproject.toml         # Python packaging
└── escobar/               # Python package
    ├── __init__.py        # Server extension
    └── handlers.py        # Request handlers
```

### Built Structure (after npm run build:prod)
```
escobar/
├── escobar/
│   ├── __init__.py
│   ├── handlers.py
│   └── labextension/      # ← Prebuilt extension
│       ├── package.json   # Extension metadata
│       ├── static/        # Compiled JS/CSS
│       │   ├── remoteEntry.*.js
│       │   ├── style.js
│       │   └── *.js       # Chunk files
│       └── schemas/       # JSON schemas
└── lib/                   # Compiled TypeScript
```

### Installed Structure (after pip install)
```
site-packages/
├── escobar/
│   ├── __init__.py
│   ├── handlers.py  
│   └── labextension/      # Available to JupyterLab
└── share/jupyter/labextensions/escobar/  # ← JupyterLab finds it here
    ├── package.json
    ├── static/
    └── schemas/
```

## Key Points

1. **Prebuilt = No Node.js needed** for installation
2. **Files go to share/jupyter/labextensions/** in the wheel
3. **Docker containers** can install with just `pip install`
4. **No deprecated commands** like `jupyter labextension install`
5. **Modern JupyterLab** automatically discovers prebuilt extensions

## Success Indicators

✅ **Build successful**: `escobar/labextension/static/` contains JS files  
✅ **Package correct**: Wheel contains `share/jupyter/labextensions/escobar/`  
✅ **Installation works**: `pip install` + `jupyter server extension enable`  
✅ **Docker works**: No Node.js needed in container  
✅ **Extension loads**: Appears in JupyterLab interface
