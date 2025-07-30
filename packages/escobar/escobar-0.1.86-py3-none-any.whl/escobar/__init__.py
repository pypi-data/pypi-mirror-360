from ._version import __version__

# NEW: Jupyter Server 2.x ExtensionApp (preferred for 2.16.0+)
try:
    from jupyter_server.extension.application import ExtensionApp
    from jupyter_server.extension.application import ExtensionAppJinjaMixin
    
    class EscobarExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
        name = "escobar"
        description = "Escobar JupyterLab Extension Server"
        
        def initialize_handlers(self):
            """Initialize the server extension handlers for Jupyter Server 2.x"""
            from .handlers import setup_handlers
            setup_handlers(self.serverapp.web_app)
            
            # Only setup demo auth handlers if explicitly enabled via environment variable
            import os
            if os.environ.get('ESCOBAR_DEMO_MODE', '').lower() in ('true', '1', 'yes'):
                from .auth_handlers import setup_auth_handlers
                setup_auth_handlers(self.serverapp.web_app)
                self.log.info("Registered escobar server extension with demo auth (Jupyter Server 2.x)")
            else:
                self.log.info("Registered escobar server extension (Jupyter Server 2.x)")
            
except ImportError:
    # Fallback for older Jupyter Server versions that don't have ExtensionApp
    EscobarExtensionApp = None

# OLD: Jupyter Server 1.x functions (for backward compatibility)
def _jupyter_labextension_paths():
    """Return the labextension paths (compatible with all Jupyter Server versions)"""
    return [{
        "src": "labextension",
        "dest": "escobar"
    }]

def _jupyter_server_extension_points():
    """Return the server extension points (Jupyter Server 1.x compatible)"""
    return [{
        "module": "escobar"
    }]

def _load_jupyter_server_extension(server_app):
    """
    Register the server extension handlers (Jupyter Server 1.x compatible)
    This function is kept for backward compatibility with older Jupyter Server versions.
    """
    from .handlers import setup_handlers
    setup_handlers(server_app.web_app)
    
    # Only setup demo auth handlers if explicitly enabled via environment variable
    import os
    if os.environ.get('ESCOBAR_DEMO_MODE', '').lower() in ('true', '1', 'yes'):
        from .auth_handlers import setup_auth_handlers
        setup_auth_handlers(server_app.web_app)
        server_app.log.info("Registered escobar server extension with demo auth (Jupyter Server 1.x)")
    else:
        server_app.log.info("Registered escobar server extension (Jupyter Server 1.x)")
