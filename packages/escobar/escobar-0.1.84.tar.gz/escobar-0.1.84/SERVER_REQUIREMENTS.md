# Escobar Settings & Model Management - Server Requirements

## Overview

The Escobar JupyterLab extension has been refactored to implement a clean separation between local and remote settings, with comprehensive debugging and zero model assumptions. This document outlines the exact server-side changes required for full functionality.

## Current Client Changes Implemented

### ✅ Settings Architecture
- **Local Settings**: `serverUrl`, `username`, `usernameFromJupyterHub` stored in JupyterLab registry
- **Remote Settings**: API keys, model selections, and configuration stored on server
- **Default Server URL**: Changed from `wss://hubserver.voitta.ai/ws` to `/ws` (relative)
- **Clean Separation**: No API keys or sensitive data stored locally

### ✅ Model Management
- **Zero Assumptions**: Client makes no assumptions about available models
- **Server-Driven**: Model list comes entirely from server `listChats` response
- **Pure Passthrough**: Whatever server sends is displayed exactly as-is
- **No Validation**: No model format requirements or provider assumptions

### ✅ Debugging & Logging
- **Targeted Debugging**: Strategic console logs for settings and model flows
- **Clean Console**: Removed verbose/unnecessary logging
- **Protocol Tracking**: Clear visibility into WebSocket communication

## Required Server Changes

### 1. Update `listChats` Handler (CRITICAL)

The `listChats` response **MUST** include a `models` array:

```python
def handle_list_chats(self, request):
    """
    REQUIRED: Add models array to response
    """
    # Your existing chat list logic...
    chats = get_user_chats(request.username)
    
    # ADD THIS: Available models list
    available_models = get_available_models()  # Your implementation
    
    return {
        "message_type": "response",
        "call_id": request.call_id,
        "value": {
            "chats": chats,
            "models": available_models  # REQUIRED FIELD
        }
    }

def get_available_models():
    """
    Return whatever models are available in your system.
    Format: [{"model": "model_name", "provider": "provider_name"}, ...]
    
    Examples:
    - [{"model": "gpt-4o", "provider": "openai"}]
    - [{"model": "claude-3-5-sonnet", "provider": "anthropic"}]
    - [] (empty array is acceptable)
    """
    # Your implementation here - could be:
    # - Static configuration
    # - Dynamic API discovery  
    # - Database lookup
    # - Environment-based
    
    return []  # Replace with your actual model discovery
```

### 2. Implement `saveSettings` Handler (NEW)

```python
def handle_save_settings(self, request):
    """
    NEW: Save user settings to persistent storage
    Expected fields in request:
    - openai_api_key, anthropic_api_key, gemini_api_key, voitta_api_key
    - max_messages, proxy_port
    - primary_model, secondary_provider, image_parse_provider
    """
    try:
        # Extract settings from request
        user_settings = {
            "username": request.username,
            "openai_api_key": getattr(request, 'openai_api_key', ''),
            "anthropic_api_key": getattr(request, 'anthropic_api_key', ''),
            "gemini_api_key": getattr(request, 'gemini_api_key', ''),
            "voitta_api_key": getattr(request, 'voitta_api_key', ''),
            "max_messages": getattr(request, 'max_messages', 100),
            "proxy_port": getattr(request, 'proxy_port', 3000),
            "primary_model": getattr(request, 'primary_model', None),
            "secondary_provider": getattr(request, 'secondary_provider', None),
            "image_parse_provider": getattr(request, 'image_parse_provider', None)
        }
        
        # Save to your storage system (database, file, etc.)
        save_user_settings(user_settings)
        
        return {
            "message_type": "response", 
            "call_id": request.call_id,
            "value": "Settings saved successfully"
        }
    except Exception as e:
        return {
            "message_type": "response",
            "call_id": request.call_id, 
            "error_type": "save_error",
            "value": f"Failed to save settings: {str(e)}"
        }
```

### 3. Implement `retrieveSettings` Handler (NEW)

```python
def handle_retrieve_settings(self, request):
    """
    NEW: Retrieve user settings from persistent storage
    """
    try:
        # Load from your storage system
        settings = get_user_settings(request.username)
        
        return {
            "message_type": "response",
            "call_id": request.call_id,
            "openai_api_key": settings.get("openai_api_key", ""),
            "anthropic_api_key": settings.get("anthropic_api_key", ""),
            "gemini_api_key": settings.get("gemini_api_key", ""),
            "voitta_api_key": settings.get("voitta_api_key", ""),
            "max_messages": settings.get("max_messages", 100),
            "proxy_port": settings.get("proxy_port", 3000),
            "primary_model": settings.get("primary_model"),
            "secondary_provider": settings.get("secondary_provider"),
            "image_parse_provider": settings.get("image_parse_provider")
        }
    except Exception as e:
        return {
            "message_type": "response",
            "call_id": request.call_id,
            "error_type": "retrieve_error", 
            "value": f"Failed to retrieve settings: {str(e)}"
        }
```

### 4. Update Message Router

```python
# Add these to your message routing logic
MESSAGE_HANDLERS = {
    "listChats": handle_list_chats,
    "saveSettings": handle_save_settings,      # ADD THIS
    "retrieveSettings": handle_retrieve_settings,  # ADD THIS
    # ... your existing handlers
}
```

### 5. Handle Relative WebSocket URLs

Ensure your server can handle WebSocket connections to `/ws` relative URLs properly.

## Expected Client Debug Output

### When Working Correctly:

```
🔧 SETTINGS: Loading local settings from registry
🔧 SETTINGS: Loading remote settings from server
📤 PROTOCOL: Sending retrieveSettings request
📥 PROTOCOL: Received retrieveSettings response
🔧 SETTINGS: Remote settings loaded successfully
🌐 WS: Attempting connection to /ws
🌐 WS: Connection established successfully
📤 PROTOCOL: Sending listChats request
📥 PROTOCOL: Received listChats response
📋 MODELS: Received 6 models from server
```

### When Saving Settings:

```
🔧 SETTINGS: Saving local settings to registry
🔧 SETTINGS: Saving remote settings to server
📤 PROTOCOL: Sending saveSettings request
📥 PROTOCOL: Received saveSettings response
🔧 SETTINGS: Remote settings saved successfully
📋 SCHEMA: Registry save successful
```

## Storage Requirements

### User Settings Storage
You need to implement persistent storage for user settings. Recommended structure:

```python
# Database table or file structure
user_settings = {
    "username": str,
    "openai_api_key": str,
    "anthropic_api_key": str, 
    "gemini_api_key": str,
    "voitta_api_key": str,
    "max_messages": int,
    "proxy_port": int,
    "primary_model": str,
    "secondary_provider": str,
    "image_parse_provider": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Model Discovery
Implement `get_available_models()` based on your system:

```python
def get_available_models():
    """
    Examples of different approaches:
    """
    
    # Option 1: Static configuration
    return [
        {"model": "gpt-4o", "provider": "openai"},
        {"model": "claude-3-5-sonnet", "provider": "anthropic"}
    ]
    
    # Option 2: Environment-based
    models = []
    if os.getenv('OPENAI_API_KEY'):
        models.extend([
            {"model": "gpt-4o", "provider": "openai"},
            {"model": "gpt-4o-mini", "provider": "openai"}
        ])
    if os.getenv('ANTHROPIC_API_KEY'):
        models.append({"model": "claude-3-5-sonnet", "provider": "anthropic"})
    return models
    
    # Option 3: Database lookup
    return db.query("SELECT model, provider FROM available_models WHERE active = true")
    
    # Option 4: API discovery (check what's actually available)
    return discover_available_models_from_apis()
```

## Testing Checklist

### ✅ Client-Side (Already Implemented)
- [x] Default server URL is `/ws`
- [x] No hardcoded model lists
- [x] Settings separated (local vs remote)
- [x] Comprehensive debugging logs
- [x] Schema validation fixed
- [x] Model dropdowns work with any server response

### ⏳ Server-Side (Needs Implementation)
- [ ] `listChats` includes `models` array
- [ ] `saveSettings` handler implemented
- [ ] `retrieveSettings` handler implemented
- [ ] Message router updated
- [ ] User settings storage implemented
- [ ] Model discovery implemented
- [ ] WebSocket `/ws` endpoint working

## Validation Steps

1. **Start Extension**: Should see settings loading logs
2. **Check Models**: Should see "📋 MODELS: Received X models from server"
3. **Save Settings**: Should see successful save to both server and registry
4. **Reload Extension**: Settings should persist from server
5. **Model Dropdowns**: Should show exactly what server provides

## Error Scenarios

### No Models from Server
```
📋 MODELS: No models received from server
```
**Fix**: Ensure `listChats` response includes `models` array

### Settings Save Failure
```
🔧 SETTINGS: Failed to save remote settings: Error: Cannot send message
```
**Fix**: Implement `saveSettings` handler on server

### Connection Issues
```
🌐 WS: Connection failed: Error: ...
```
**Fix**: Ensure WebSocket server accepts connections to `/ws`

This completes the requirements for full Escobar settings and model management functionality.
