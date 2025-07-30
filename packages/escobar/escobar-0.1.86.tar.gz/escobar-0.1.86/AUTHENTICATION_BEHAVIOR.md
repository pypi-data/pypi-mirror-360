# Authentication Behavior in Escobar Extension

This document explains how authentication and username handling works in the Escobar extension.

## 🎯 **Normal Operation (Default)**

By default, the Escobar extension does **NOT** implement any authentication system. It simply uses usernames for chat identification.

### **Non-Hub Environment (Standalone Jupyter)**
- ✅ **Username source**: Connection settings page (user can edit)
- ✅ **No authentication prompts**: Extension works without any login
- ✅ **User control**: Username can be changed in settings anytime

### **JupyterHub Environment**
- ✅ **Username source**: Extracted from URL automatically
- ✅ **No authentication prompts**: Uses existing JupyterHub authentication
- ✅ **Read-only username**: Settings page disables username editing
- ✅ **Automatic detection**: Extension detects JupyterHub environment

## 🔧 **Username Detection Logic**

### **JupyterHub Detection**
The extension automatically detects JupyterHub by checking:
1. URL pattern: `/user/{username}/lab/...`
2. JupyterHub config data in page
3. Document baseURI patterns
4. JupyterHub-related cookies

### **Username Extraction**
- **JupyterHub**: Extracted from URL path `/user/{username}/`
- **Standalone**: User enters in connection settings

### **Settings Page Behavior**
- **JupyterHub**: Username field is disabled and read-only
- **Standalone**: Username field is editable

## 🧪 **Demo Mode (Optional)**

For demonstration purposes, the extension can optionally enable a demo authentication system.

### **Enabling Demo Mode**
Set the environment variable:
```bash
export ESCOBAR_DEMO_MODE=true
```

Or in Docker:
```dockerfile
ENV ESCOBAR_DEMO_MODE=true
```

### **Demo Mode Behavior**
When demo mode is enabled:
- ❗ **Root URL hijacking**: `/` redirects to demo user selection
- ❗ **Demo user selection**: Shows page with predefined demo users
- ❗ **Demo authentication**: Users must select a demo user to proceed

### **Demo Users Configuration**
Demo users are configured via environment variable:
```bash
export DEMO_USERS="alice,bob,charlie"
```

If not set, defaults to a single demo user: `demo`

## 🚫 **What Was Fixed**

### **Problem (Before Fix)**
- Demo authentication was **always enabled**
- Root URL was **always hijacked**
- Users were **forced through demo user selection**
- Extension appeared to require authentication in all environments

### **Solution (After Fix)**
- Demo authentication is **only enabled when explicitly requested**
- Normal operation has **no authentication prompts**
- Extension works seamlessly in both JupyterHub and standalone environments
- Username handling is **passive and environment-appropriate**

## 📋 **Installation Behavior**

### **Default Installation**
```bash
pip install escobar
jupyter server extension enable escobar
```
**Result**: Extension works normally without any authentication prompts

### **Demo Installation**
```bash
pip install escobar
export ESCOBAR_DEMO_MODE=true
export DEMO_USERS="alice,bob,charlie"
jupyter server extension enable escobar
```
**Result**: Extension shows demo user selection page

## 🔍 **Troubleshooting**

### **If You See Authentication Prompts**
1. **Check environment variables**:
   ```bash
   echo $ESCOBAR_DEMO_MODE
   ```
   
2. **Disable demo mode**:
   ```bash
   unset ESCOBAR_DEMO_MODE
   # or
   export ESCOBAR_DEMO_MODE=false
   ```

3. **Restart Jupyter**:
   ```bash
   jupyter lab --stop
   jupyter lab
   ```

### **If Username is Not Working**
1. **Check environment detection**:
   - Open browser console in JupyterLab
   - Look for "Running in JupyterHub Mode" or "Running in Plugin Mode"

2. **Manually set username**:
   - Click the connection settings button in the chat widget
   - Enter your desired username

3. **Check URL pattern**:
   - JupyterHub URLs should contain `/user/{username}/`
   - If not detected, username will be editable in settings

## ✅ **Expected Behavior Summary**

| Environment | Username Source | Authentication | Settings Editable |
|-------------|----------------|----------------|-------------------|
| **Standalone Jupyter** | Settings page | None | ✅ Yes |
| **JupyterHub** | URL extraction | JupyterHub's | ❌ No (read-only) |
| **Demo Mode** | Demo selection | Demo system | Varies |

## 🎉 **Result**

The extension now works seamlessly without unwanted authentication prompts while maintaining proper username handling for both JupyterHub and standalone environments.
