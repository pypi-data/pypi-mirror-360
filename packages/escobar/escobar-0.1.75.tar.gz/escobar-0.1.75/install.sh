#!/bin/bash

# Escobar Chat Extension Installer
# This script installs the Escobar Chat extension for JupyterLab

set -e  # Exit immediately if a command exits with a non-zero status

rm -rf node_modules

echo "Installing Escobar Chat Extension for JupyterLab..."

pip3 install -r requirements.txt

# Install dependencies
echo "Installing dependencies..."
npm install || { echo "Failed to install dependencies. Please check the error message above."; exit 1; }

# Clean previous builds
echo "Cleaning previous builds..."
npm run clean:all || { echo "Failed to clean previous builds. Continuing anyway..."; }

# Build the extension
echo "Building extension..."
npm run build:prod || { echo "Failed to build the extension. Please check the error message above."; exit 1; }

# Install the extension in development mode
echo "Installing extension..."
pip3 install -e . || { echo "Failed to install the extension. Please check the error message above."; exit 1; }

# Rebuild JupyterLab to ensure all dependencies are resolved
echo "Rebuilding JupyterLab..."
jupyter lab build  || { echo "Failed to rebuild JupyterLab. Please check the error message above."; exit 1; }

echo "Installation complete!"

# List the directory where the plugin is installed
echo "Plugin installation location:"
jupyter labextension list --verbose | grep escobar || echo "Warning: Extension not found in labextension list. It may not have been installed correctly."

# Show the full path of the installation directory
echo "Full installation path:"
python3 -c "import os, jupyter_core.paths; print(os.path.join(jupyter_core.paths.jupyter_data_dir(), 'labextensions', 'escobar'))" || echo "Could not determine installation path."

# Show where the extension is symlinked
echo "Symlink information:"
python3 -c "
import site
import os
import escobar

# Get the package location
package_location = os.path.dirname(escobar.__file__)
print(f'Package location: {package_location}')

# Find where it's symlinked in site-packages
site_packages = site.getsitepackages()
for sp in site_packages:
    escobar_egg_link = os.path.join(sp, 'escobar.egg-link')
    if os.path.exists(escobar_egg_link):
        with open(escobar_egg_link, 'r') as f:
            source_path = f.readline().strip()
            print(f'Symlinked from: {source_path}')
            print(f'Symlinked to: {sp}/escobar')
        break
" || echo "Could not determine symlink information."

echo "To use the extension, run: jupyter lab"
echo "Install script finished."
