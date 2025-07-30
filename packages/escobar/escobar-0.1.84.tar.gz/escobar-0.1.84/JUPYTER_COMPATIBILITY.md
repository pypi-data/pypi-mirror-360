# Jupyter Server Compatibility Guide

This document explains the compatibility changes made to support Jupyter Server 2.16.0+ and Python 3.12.

## Compatibility Matrix

| Jupyter Server Version | Python Version | Registration Method | Status |
|------------------------|----------------|-------------------|---------|
| 1.21.0 - 1.24.x       | 3.8 - 3.11     | Legacy functions  | ✅ Supported |
| 2.0.0 - 2.15.x        | 3.8 - 3.11     | Both methods      | ✅ Supported |
| 2.16.0+               | 3.8 - 3.12     | ExtensionApp      | ✅ Supported |

## What Changed

### 1. New Extension Registration (Jupyter Server 2.x)

Added modern `EscobarExtensionApp` class that follows Jupyter Server 2.x patterns:

```python
class EscobarExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    name = "escobar"
    description = "Escobar JupyterLab Extension Server"
    
    def initialize_handlers(self):
        # Handler setup for Jupyter Server 2.x
```

### 2. Backward Compatibility

Kept original registration functions for Jupyter Server 1.x:

```python
def _jupyter_server_extension_points():
    return [{"module": "escobar"}]

def _load_jupyter_server_extension(server_app):
    # Handler setup for Jupyter Server 1.x
```

### 3. Dual Entry Points

Added both entry point styles in `pyproject.toml`:

```toml
# Jupyter Server 2.x (preferred)
[project.entry-points."jupyter_server.extension"]
escobar = "escobar:EscobarExtensionApp"

# Jupyter Server 1.x (backward compatibility)
[project.entry-points."jupyter_server.extensions"]
escobar = "escobar:_load_jupyter_server_extension"
```

### 4. Python 3.12 Support

Added Python 3.12 classifier and updated dependencies for compatibility.

## Installation

### For Jupyter Server 2.16.0+ Users

```bash
pip install escobar
jupyter server extension enable escobar
```

### For Jupyter Server 1.x Users

```bash
pip install escobar
jupyter serverextension enable --py escobar
```

## Automatic Detection

The extension automatically detects your Jupyter Server version and uses the appropriate registration method:

- **Jupyter Server 2.x**: Uses `EscobarExtensionApp` class
- **Jupyter Server 1.x**: Uses `_load_jupyter_server_extension` function

## Troubleshooting

### Extension Not Loading

1. **Check Jupyter Server version**:
   ```bash
   jupyter --version
   ```

2. **Verify extension is enabled**:
   ```bash
   jupyter server extension list
   ```

3. **For Jupyter Server 1.x, use legacy command**:
   ```bash
   jupyter serverextension enable --py escobar
   ```

### Python 3.12 Issues

If you encounter issues with Python 3.12:

1. Ensure you have the latest version of escobar
2. Update Jupyter Server: `pip install --upgrade jupyter-server`
3. Check that all dependencies support Python 3.12

## Migration Guide

### From Jupyter Server 1.x to 2.x

No action required! The extension will automatically use the new registration method.

### Updating Dependencies

If you're upgrading Jupyter Server:

```bash
pip install --upgrade jupyter-server jupyterlab
pip install --upgrade escobar
```

## Development

### Testing Compatibility

To test with different Jupyter Server versions:

```bash
# Test with Jupyter Server 1.x
pip install "jupyter-server>=1.21,<2.0"
jupyter serverextension enable --py escobar

# Test with Jupyter Server 2.x
pip install "jupyter-server>=2.0"
jupyter server extension enable escobar
```

### Building from Source

```bash
git clone https://github.com/your-repo/escobar.git
cd escobar
pip install -e .
jupyter labextension develop --overwrite .
```

## Support

If you encounter compatibility issues:

1. Check this compatibility guide
2. Verify your Jupyter Server and Python versions
3. Report issues with version information included
