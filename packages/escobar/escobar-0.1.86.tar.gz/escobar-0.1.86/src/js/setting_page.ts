import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { showLoginUI } from '../utils/loginUI';
import { VERSION } from '../version';
import { MessageHandler } from '../messageHandler';
import { SettingsManager, IChatSettings, ILocalSettings, IRemoteSettings } from '../utils/settingsManager';

/**
 * Determines if the current environment is JupyterHub based on URL pattern
 * @returns True if running in JupyterHub environment, false otherwise
 */
export function isJupyterHubEnvironment(): boolean {
  // Check URL pattern - most reliable in JupyterHub
  // JupyterHub URLs typically follow the pattern: /user/{username}/lab/...
  const hubUserRegex = /\/user\/([^\/]+)\//;
  const hubUserMatch = window.location.pathname.match(hubUserRegex);

  if (hubUserMatch && hubUserMatch[1]) {
    return true;
  }

  // Check for JupyterHub data in the page config
  try {
    const configElement = document.getElementById('jupyter-config-data');
    if (configElement && configElement.textContent) {
      const config = JSON.parse(configElement.textContent);

      if (config.hubUser || config.hubUsername || config.user) {
        return true;
      }
    }
  } catch (error) {
    console.error('Error parsing JupyterHub config:', error);
  }

  // Try to extract from document.baseURI
  try {
    const baseUri = document.baseURI;
    const baseMatch = baseUri.match(/\/user\/([^\/]+)\//);

    if (baseMatch && baseMatch[1]) {
      return true;
    }
  } catch (error) {
    console.error('Error checking baseURI:', error);
  }

  // Check cookies for JupyterHub-related information
  try {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'jupyterhub-user') {
        return true;
      }
    }
  } catch (error) {
    console.error('Error checking cookies:', error);
  }

  // Try a different regex pattern that might better handle complex usernames
  const altRegex = /\/user\/([^\/]*)\//;
  const altMatch = window.location.pathname.match(altRegex);

  if (altMatch && altMatch[1]) {
    return true;
  }

  return false;
}

/**
 * Factory function to create the appropriate settings page based on environment
 * @param settingsRegistry The settings registry
 * @param currentSettings The current settings
 * @param onSave Callback function when settings are saved
 * @returns The appropriate settings page instance
 */
export function createSettingsPage(
  settingsRegistry: ISettingRegistry,
  currentSettings: IChatSettings,
  onSave: (settings: IChatSettings) => void
): BaseSettingsPage {
  const isJupyterHub = isJupyterHubEnvironment();

  if (isJupyterHub) {
    return new JupyterHubSettingsPage(settingsRegistry, currentSettings, onSave);
  } else {
    return new PluginSettingsPage(settingsRegistry, currentSettings, onSave);
  }
}

/**
 * Show connection settings modal
 * @param settingsRegistry The settings registry
 * @param currentSettings The current settings
 * @param onSave Callback function when settings are saved
 */
export function showConnectionSettings(
  settingsRegistry: ISettingRegistry,
  currentSettings: IChatSettings,
  onSave: (settings: IChatSettings) => void
): void {
  const connectionPage = new ConnectionSettingsPage(settingsRegistry, currentSettings, onSave);
  connectionPage.show();
}

/**
 * Abstract base class for settings pages
 */
export abstract class BaseSettingsPage {
  protected settingsRegistry: ISettingRegistry;
  protected container: HTMLDivElement;
  protected overlay: HTMLDivElement;
  protected currentSettings: IChatSettings;
  protected onSave: (settings: IChatSettings) => void;

  /**
   * Create a new SettingsPage
   * @param settingsRegistry The settings registry
   * @param currentSettings The current settings
   * @param onSave Callback function when settings are saved
   */
  constructor(
    settingsRegistry: ISettingRegistry,
    currentSettings: IChatSettings,
    onSave: (settings: IChatSettings) => void
  ) {
    this.settingsRegistry = settingsRegistry;
    this.currentSettings = currentSettings;
    this.onSave = onSave;

    // Create overlay
    this.overlay = document.createElement('div');
    this.overlay.className = 'escobar-settings-overlay';
    this.overlay.addEventListener('click', (e) => {
      if (e.target === this.overlay) {
        this.hide();
      }
    });

    // Create container
    this.container = this.createContainer();
    this.overlay.appendChild(this.container);
  }

  /**
   * Create the settings UI container
   * This is an abstract method that must be implemented by derived classes
   */
  protected abstract createContainer(): HTMLDivElement;

  /**
   * Create a standard header for the settings container
   * @param title The title to display in the header
   * @returns The created header element
   */
  protected createHeader(title: string): HTMLDivElement {
    const header = document.createElement('div');
    header.className = 'escobar-settings-header';

    const titleElement = document.createElement('h2');
    titleElement.textContent = title;
    header.appendChild(titleElement);

    const closeButton = document.createElement('button');
    closeButton.className = 'escobar-settings-close-button';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', () => this.hide());
    header.appendChild(closeButton);

    return header;
  }

  /**
   * Create a form group with label and description
   * @param id The ID for the input element
   * @param labelText The text for the label
   * @param descriptionText The description text
   * @returns The created form group element
   */
  protected createFormGroup(id: string, labelText: string, descriptionText: string): HTMLDivElement {
    const group = document.createElement('div');
    group.className = 'escobar-settings-group';

    const label = document.createElement('label');
    label.textContent = labelText;
    label.htmlFor = id;
    group.appendChild(label);

    const description = document.createElement('div');
    description.className = 'escobar-settings-description';
    description.textContent = descriptionText;
    group.appendChild(description);

    return group;
  }

  /**
   * Create a model dropdown with available models
   * @param id The ID for the select element
   * @param labelText The text for the label
   * @param descriptionText The description text
   * @param currentValue The current selected value
   * @returns The created form group element with model dropdown
   */
  protected createModelDropdown(id: string, labelText: string, descriptionText: string, currentValue?: string): HTMLDivElement {
    const group = this.createFormGroup(id, labelText, descriptionText);

    const select = document.createElement('select');
    select.id = id;
    select.className = 'escobar-settings-input';

    // Store the original currentValue for later use when models are loaded
    (select as any)._savedValue = currentValue;

    // Phase 1: If we have a saved value, show it immediately (before models are loaded)
    if (currentValue) {
      const initialOption = document.createElement('option');
      initialOption.value = currentValue;
      initialOption.textContent = `${currentValue} (Loading models...)`;
      initialOption.selected = true;
      select.appendChild(initialOption);
    } else {
      const placeholderOption = document.createElement('option');
      placeholderOption.value = 'undefined';
      placeholderOption.textContent = 'Loading models...';
      placeholderOption.selected = true;
      select.appendChild(placeholderOption);
    }

    // Function to populate the dropdown with full model list
    const populateDropdown = (models: Array<{ model: string, provider: string }>) => {
      // Get the saved value that was stored when dropdown was created
      const savedValue = (select as any)._savedValue;

      // Clear existing options
      select.innerHTML = '';

      if (models.length > 0) {
        // Add all available models - display exactly what server provides
        models.forEach(modelInfo => {
          const option = document.createElement('option');
          option.value = modelInfo.model;
          // Just display the model name, no assumptions about provider formatting
          option.textContent = modelInfo.model;
          select.appendChild(option);
        });

        // Set selection based on saved value
        if (savedValue) {
          // Try to select the saved value
          select.value = savedValue;

          // Check if the saved value was found in the model list
          if (select.value !== savedValue) {
            // Saved value not in model list - add it as a custom option and select it
            const customOption = document.createElement('option');
            customOption.value = savedValue;
            customOption.textContent = `${savedValue} (Custom)`;
            select.insertBefore(customOption, select.firstChild);
            select.value = savedValue;
          }
        } else {
          // No saved value, default to first model
          select.value = models[0].model;
        }
      } else {
        // No models available
        const placeholderOption = document.createElement('option');
        placeholderOption.value = 'undefined';
        placeholderOption.textContent = 'No models available';
        placeholderOption.selected = true;
        select.appendChild(placeholderOption);
      }
    };

    // Get available models from the global window object (set by chat widget)
    const availableModels = (window as any).escobarAvailableModels as Array<{ model: string, provider: string }> || [];

    // If models are already available, populate immediately
    if (availableModels.length > 0) {
      populateDropdown(availableModels);
    }

    // Listen for model updates from chat widget
    const handleModelUpdate = (event: CustomEvent) => {
      populateDropdown(event.detail.models);
    };

    // Add event listener for model updates
    window.addEventListener('escobar-models-updated', handleModelUpdate as EventListener);

    // Store the cleanup function on the select element for later removal
    (select as any)._modelUpdateCleanup = () => {
      window.removeEventListener('escobar-models-updated', handleModelUpdate as EventListener);
    };
    group.appendChild(select);
    return group;
  }


  /**
   * Create a standard buttons container with Save and Cancel buttons
   * @returns The created buttons container
   */
  protected createButtonsContainer(): HTMLDivElement {
    const buttonsContainer = document.createElement('div');
    buttonsContainer.className = 'escobar-settings-buttons';

    const cancelButton = document.createElement('button');
    cancelButton.className = 'escobar-settings-button escobar-settings-cancel-button';
    cancelButton.textContent = 'Cancel';
    cancelButton.type = 'button';
    cancelButton.addEventListener('click', () => this.hide());
    buttonsContainer.appendChild(cancelButton);

    const saveButton = document.createElement('button');
    saveButton.className = 'escobar-settings-button escobar-settings-save-button';
    saveButton.textContent = 'Save';
    saveButton.type = 'submit';
    buttonsContainer.appendChild(saveButton);

    return buttonsContainer;
  }

  /**
   * Show the settings page
   */
  public show(): void {
    console.log('🔧 SETTINGS: Opening settings page, loading latest settings...');

    // Load settings from both local registry and remote server
    this.loadCompleteSettings()
      .then(completeSettings => {
        console.log('🔧 SETTINGS: Complete settings loaded successfully');
        this.currentSettings = completeSettings;

        // Show the settings page first so DOM elements exist
        document.body.appendChild(this.overlay);

        // Update form fields with the complete settings AFTER DOM is added
        this.updateFormFields();

        // Add animation class after a small delay to trigger animation
        setTimeout(() => {
          this.overlay.classList.add('escobar-settings-overlay-visible');
          this.container.classList.add('escobar-settings-container-visible');
        }, 10);
      })
      .catch(error => {
        console.error('🔧 SETTINGS: Failed to load complete settings:', error);

        // Fall back to using the current settings
        console.log('🔧 SETTINGS: Using fallback settings');

        // Show the settings page anyway
        document.body.appendChild(this.overlay);
        this.updateFormFields();

        // Add animation class after a small delay to trigger animation
        setTimeout(() => {
          this.overlay.classList.add('escobar-settings-overlay-visible');
          this.container.classList.add('escobar-settings-container-visible');
        }, 10);
      });
  }

  /**
   * Load complete settings from both local registry and remote server
   */
  private async loadCompleteSettings(): Promise<IChatSettings> {
    console.log('🔧 SETTINGS: Loading local settings from registry');

    // Step 1: Load local settings from registry
    let localSettings: Partial<IChatSettings> = {};
    try {
      const settings = await this.settingsRegistry.load('escobar:plugin');
      const registrySettings = settings.composite as any;
      localSettings = {
        serverUrl: registrySettings.serverUrl || this.currentSettings.serverUrl,
        username: registrySettings.username || this.currentSettings.username,
        usernameFromJupyterHub: registrySettings.usernameFromJupyterHub || this.currentSettings.usernameFromJupyterHub,
        bonnieUrl: registrySettings.bonnieUrl || this.currentSettings.bonnieUrl
      };
      console.log('🔧 SETTINGS: Local settings loaded from registry');
    } catch (error) {
      console.error('🔧 SETTINGS: Failed to load from registry:', error);
      localSettings = {
        serverUrl: this.currentSettings.serverUrl,
        username: this.currentSettings.username,
        usernameFromJupyterHub: this.currentSettings.usernameFromJupyterHub
      };
    }

    // Step 2: Load remote settings from server
    let remoteSettings: Partial<IChatSettings> = {};
    try {
      console.log('🔧 SETTINGS: Loading remote settings from server');
      const messageHandler = (window as any).escobarMessageHandler as MessageHandler;

      if (messageHandler) {
        console.log('📤 PROTOCOL: Sending retrieveSettings request');
        const serverSettings = await messageHandler.retrieveSettingsFromServer();
        console.log('📥 PROTOCOL: Received retrieveSettings response');

        remoteSettings = {
          maxMessages: serverSettings.maxMessages || this.currentSettings.maxMessages,
          voittaApiKey: serverSettings.voittaApiKey || '',
          openaiApiKey: serverSettings.openaiApiKey || '',
          anthropicApiKey: serverSettings.anthropicApiKey || '',
          geminiApiKey: serverSettings.geminiApiKey || '',
          proxyPort: serverSettings.proxyPort || 3000,
          primaryModel: serverSettings.primaryModel,
          secondaryProvider: serverSettings.secondaryProvider,
          imageParseProvider: serverSettings.imageParseProvider
        };
        console.log('🔧 SETTINGS: Remote settings loaded successfully');
      } else {
        console.warn('🔧 SETTINGS: MessageHandler not available, using defaults for remote settings');
        remoteSettings = {
          maxMessages: this.currentSettings.maxMessages,
          voittaApiKey: this.currentSettings.voittaApiKey || '',
          openaiApiKey: this.currentSettings.openaiApiKey || '',
          anthropicApiKey: this.currentSettings.anthropicApiKey || '',
          geminiApiKey: this.currentSettings.geminiApiKey || '',
          proxyPort: this.currentSettings.proxyPort || 3000,
          primaryModel: this.currentSettings.primaryModel,
          secondaryProvider: this.currentSettings.secondaryProvider,
          imageParseProvider: this.currentSettings.imageParseProvider
        };
      }
    } catch (error) {
      console.error('🔧 SETTINGS: Failed to load remote settings from server:', error);
      // Use current settings as fallback
      remoteSettings = {
        maxMessages: this.currentSettings.maxMessages,
        voittaApiKey: this.currentSettings.voittaApiKey || '',
        openaiApiKey: this.currentSettings.openaiApiKey || '',
        anthropicApiKey: this.currentSettings.anthropicApiKey || '',
        geminiApiKey: this.currentSettings.geminiApiKey || '',
        proxyPort: this.currentSettings.proxyPort || 3000,
        primaryModel: this.currentSettings.primaryModel,
        secondaryProvider: this.currentSettings.secondaryProvider,
        imageParseProvider: this.currentSettings.imageParseProvider
      };
    }

    // Step 3: Merge local and remote settings
    const completeSettings: IChatSettings = {
      // Local settings (from registry)
      serverUrl: localSettings.serverUrl!,
      username: localSettings.username!,
      usernameFromJupyterHub: localSettings.usernameFromJupyterHub!,
      bonnieUrl: localSettings.bonnieUrl, // Include bonnieUrl from local settings

      // Remote settings (from server)
      maxMessages: remoteSettings.maxMessages!,
      voittaApiKey: remoteSettings.voittaApiKey!,
      openaiApiKey: remoteSettings.openaiApiKey!,
      anthropicApiKey: remoteSettings.anthropicApiKey!,
      geminiApiKey: remoteSettings.geminiApiKey!,
      proxyPort: remoteSettings.proxyPort!,
      primaryModel: remoteSettings.primaryModel,
      secondaryProvider: remoteSettings.secondaryProvider,
      imageParseProvider: remoteSettings.imageParseProvider
    };

    console.log('🔧 SETTINGS: Settings merged successfully');
    return completeSettings;
  }

  /**
   * Update form fields with current settings
   * This method should be implemented by derived classes to update their specific form fields
   */
  protected abstract updateFormFields(): void;

  /**
   * Hide the settings page
   */
  public hide(): void {
    this.overlay.classList.remove('escobar-settings-overlay-visible');
    this.container.classList.remove('escobar-settings-container-visible');

    // Remove from DOM after animation completes
    setTimeout(() => {
      if (this.overlay.parentNode) {
        this.overlay.parentNode.removeChild(this.overlay);
      }
    }, 300); // Match the CSS transition duration
  }

  /**
   * Save settings changes
   * This method should be implemented by derived classes to handle their specific form fields
   */
  protected abstract saveSettings(): void;

  /**
   * Validate and save common settings
   * @param formValues The form values to validate and save
   * @returns True if validation passed, false otherwise
   */
  protected validateAndSaveCommonSettings(formValues: {
    voittaApiKey: string,
    openaiApiKey: string,
    anthropicApiKey: string,
    proxyPort?: number
  }): boolean {
    // At least one API key is required
    if (!formValues.voittaApiKey && !formValues.openaiApiKey && !formValues.anthropicApiKey) {
      alert('At least one API Key is required');
      return false;
    }

    // Get geminiApiKey from form if available
    const geminiApiKeyInput = document.getElementById('escobar-gemini-api-key') as HTMLInputElement;
    const geminiApiKey = geminiApiKeyInput ? geminiApiKeyInput.value.trim() : (this.currentSettings.geminiApiKey || '');

    // Get model selections from form
    const primaryModelSelect = document.getElementById('escobar-primary-model') as HTMLSelectElement;
    const secondaryProviderSelect = document.getElementById('escobar-secondary-provider') as HTMLSelectElement;
    const imageParseProviderSelect = document.getElementById('escobar-image-parse-provider') as HTMLSelectElement;

    const primaryModel = primaryModelSelect ? primaryModelSelect.value : 'undefined';
    const secondaryProvider = secondaryProviderSelect ? secondaryProviderSelect.value : 'undefined';
    const imageParseProvider = imageParseProviderSelect ? imageParseProviderSelect.value : 'undefined';

    // Create new settings object (preserve connection settings from current settings)
    const newSettings: IChatSettings = {
      // Preserve connection settings from current settings
      maxMessages: this.currentSettings.maxMessages,
      serverUrl: this.currentSettings.serverUrl,
      username: this.currentSettings.username,
      usernameFromJupyterHub: this.currentSettings.usernameFromJupyterHub,

      // Update user preference settings from form
      voittaApiKey: formValues.voittaApiKey,
      openaiApiKey: formValues.openaiApiKey,
      anthropicApiKey: formValues.anthropicApiKey,
      geminiApiKey: geminiApiKey,
      proxyPort: formValues.proxyPort || 3000,
      primaryModel: primaryModel,
      secondaryProvider: secondaryProvider,
      imageParseProvider: imageParseProvider
    };

    // First update the current settings to ensure they're immediately available
    this.currentSettings = newSettings;

    // Update the global settings object immediately for message handler access
    (window as any).escobarCurrentSettings = newSettings;

    // Save settings to server only (no localStorage fallbacks)
    this.saveSettingsToServerOnly(newSettings);

    return true;
  }

  /**
   * Save settings to server only (clean, no fallbacks)
   * @param settings The settings to save
   */
  private async saveSettingsToServerOnly(settings: IChatSettings): Promise<void> {
    console.log('🔧 SETTINGS: Saving remote settings to server only');

    try {
      // Get the message handler from the global window object
      const messageHandler = (window as any).escobarMessageHandler as MessageHandler;

      if (!messageHandler) {
        throw new Error('Message handler not available - cannot save settings to server');
      }

      console.log('📤 PROTOCOL: Sending saveSettings request to server');
      // Save remote settings to server only (no localStorage fallback)
      await messageHandler.saveSettingsToServer({
        maxMessages: settings.maxMessages,
        voittaApiKey: settings.voittaApiKey,
        openaiApiKey: settings.openaiApiKey,
        anthropicApiKey: settings.anthropicApiKey,
        geminiApiKey: settings.geminiApiKey,
        proxyPort: settings.proxyPort,
        primaryModel: settings.primaryModel,
        secondaryProvider: settings.secondaryProvider,
        imageParseProvider: settings.imageParseProvider
      });

      console.log('✅ SETTINGS: Remote settings saved to server successfully');

      // Hide settings page after successful save
      this.hide();

    } catch (error) {
      console.error('❌ SETTINGS: Failed to save settings to server:', error);

      // Show clear error message to user
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Failed to save settings to server:\n\n${errorMessage}\n\nPlease check your connection and try again.`);

      // Don't hide the settings page so user can retry
    }
  }
}

/**
 * JupyterHub-specific settings page implementation
 */
export class JupyterHubSettingsPage extends BaseSettingsPage {
  /**
   * Create the settings UI container for JupyterHub environment
   */
  protected createContainer(): HTMLDivElement {
    // Create container
    const container = document.createElement('div');
    container.className = 'escobar-settings-container';

    // Create header with simplified title
    const header = this.createHeader('Settings');
    container.appendChild(header);

    // Add mode indicator label with version number
    const modeIndicator = document.createElement('div');
    modeIndicator.className = 'escobar-mode-indicator';
    modeIndicator.innerHTML = `Running in JupyterHub Mode <span style="font-size: 0.8em; opacity: 0.8;">v${VERSION}</span>`;
    modeIndicator.style.backgroundColor = '#f0f7ff';
    modeIndicator.style.color = '#0366d6';
    modeIndicator.style.padding = '8px 16px';
    modeIndicator.style.margin = '0 16px 16px 16px';
    modeIndicator.style.borderRadius = '4px';
    modeIndicator.style.fontWeight = 'bold';
    modeIndicator.style.textAlign = 'center';
    modeIndicator.style.border = '1px solid #c8e1ff';
    container.appendChild(modeIndicator);

    // Create form
    const form = document.createElement('form');
    form.className = 'escobar-settings-form';
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.saveSettings();
    });

    // Create form fields

    // Voitta API Key field
    const voittaApiKeyGroup = this.createFormGroup(
      'escobar-voitta-api-key',
      'Voitta API Key',
      'The API key for authentication with Voitta services. (Optional)'
    );

    const voittaApiKeyInput = document.createElement('input');
    voittaApiKeyInput.id = 'escobar-voitta-api-key';
    voittaApiKeyInput.className = 'escobar-settings-input';
    voittaApiKeyInput.type = 'text';
    voittaApiKeyInput.value = this.currentSettings.voittaApiKey || '';
    voittaApiKeyGroup.appendChild(voittaApiKeyInput);

    // Add "Get API Key" link for Voitta
    const getVoittaApiKeyLink = document.createElement('a');
    getVoittaApiKeyLink.href = '#';
    getVoittaApiKeyLink.className = 'escobar-get-api-key-link';
    getVoittaApiKeyLink.textContent = 'Get Voitta API Key';
    getVoittaApiKeyLink.style.display = this.currentSettings.voittaApiKey ? 'none' : 'block';
    getVoittaApiKeyLink.addEventListener('click', (e) => {
      e.preventDefault();

      // Show the login UI
      showLoginUI()
        .then((apiKey) => {
          // Update the API key input
          voittaApiKeyInput.value = apiKey;

          // Hide the link
          getVoittaApiKeyLink.style.display = 'none';

          // Show success message
          alert('Successfully obtained Voitta API key!');
        })
        .catch((error) => {
          if (error.message !== 'Authentication cancelled') {
            console.error('Authentication error:', error);
            alert('Failed to authenticate. Please try again.');
          }
        });
    });
    voittaApiKeyGroup.appendChild(getVoittaApiKeyLink);

    // Add event listener to show/hide the link based on input value
    voittaApiKeyInput.addEventListener('input', () => {
      getVoittaApiKeyLink.style.display = voittaApiKeyInput.value ? 'none' : 'block';
    });

    form.appendChild(voittaApiKeyGroup);

    // OpenAI API Key field
    const openaiApiKeyGroup = this.createFormGroup(
      'escobar-openai-api-key',
      'OpenAI API Key',
      'Your OpenAI API key for OpenAI-powered features. (Optional)'
    );

    const openaiApiKeyInput = document.createElement('input');
    openaiApiKeyInput.id = 'escobar-openai-api-key';
    openaiApiKeyInput.className = 'escobar-settings-input';
    openaiApiKeyInput.type = 'text';
    openaiApiKeyInput.value = this.currentSettings.openaiApiKey || '';
    openaiApiKeyGroup.appendChild(openaiApiKeyInput);

    form.appendChild(openaiApiKeyGroup);

    // Anthropic API Key field
    const anthropicApiKeyGroup = this.createFormGroup(
      'escobar-anthropic-api-key',
      'Anthropic API Key',
      'Your Anthropic API key for Claude-powered features. (Optional)'
    );

    const anthropicApiKeyInput = document.createElement('input');
    anthropicApiKeyInput.id = 'escobar-anthropic-api-key';
    anthropicApiKeyInput.className = 'escobar-settings-input';
    anthropicApiKeyInput.type = 'text';
    anthropicApiKeyInput.value = this.currentSettings.anthropicApiKey || '';
    anthropicApiKeyGroup.appendChild(anthropicApiKeyInput);

    form.appendChild(anthropicApiKeyGroup);

    // Gemini API Key field
    const geminiApiKeyGroup = this.createFormGroup(
      'escobar-gemini-api-key',
      'Gemini API Key',
      'Your Google Gemini API key for Gemini-powered features. (Optional)'
    );

    const geminiApiKeyInput = document.createElement('input');
    geminiApiKeyInput.id = 'escobar-gemini-api-key';
    geminiApiKeyInput.className = 'escobar-settings-input';
    geminiApiKeyInput.type = 'text';
    geminiApiKeyInput.value = this.currentSettings.geminiApiKey || '';
    geminiApiKeyGroup.appendChild(geminiApiKeyInput);

    form.appendChild(geminiApiKeyGroup);

    // Create placeholder containers for model dropdowns (will be populated after settings load)
    const primaryModelGroup = document.createElement('div');
    primaryModelGroup.id = 'primary-model-container';
    primaryModelGroup.className = 'escobar-settings-group';
    form.appendChild(primaryModelGroup);

    const secondaryProviderGroup = document.createElement('div');
    secondaryProviderGroup.id = 'secondary-provider-container';
    secondaryProviderGroup.className = 'escobar-settings-group';
    form.appendChild(secondaryProviderGroup);

    const imageParseProviderGroup = document.createElement('div');
    imageParseProviderGroup.id = 'image-parse-provider-container';
    imageParseProviderGroup.className = 'escobar-settings-group';
    form.appendChild(imageParseProviderGroup);

    // Proxy Port field (moved to end)
    const proxyPortGroup = this.createFormGroup(
      'escobar-proxy-port',
      'Proxy Port',
      'The port number for the proxy server.'
    );

    const proxyPortInput = document.createElement('input');
    proxyPortInput.id = 'escobar-proxy-port';
    proxyPortInput.className = 'escobar-settings-input';
    proxyPortInput.type = 'number';
    proxyPortInput.min = '1';
    proxyPortInput.max = '65535';
    proxyPortInput.value = (this.currentSettings.proxyPort || 3000).toString();
    proxyPortGroup.appendChild(proxyPortInput);

    form.appendChild(proxyPortGroup);

    // Create buttons
    const buttonsContainer = this.createButtonsContainer();
    form.appendChild(buttonsContainer);

    container.appendChild(form);

    return container;
  }

  /**
   * Update form fields with current settings
   */
  protected updateFormFields(): void {
    // Get form elements
    const maxMessagesInput = document.getElementById('escobar-max-messages') as HTMLInputElement;
    const serverUrlInput = document.getElementById('escobar-server-url') as HTMLInputElement;
    const voittaApiKeyInput = document.getElementById('escobar-voitta-api-key') as HTMLInputElement;
    const openaiApiKeyInput = document.getElementById('escobar-openai-api-key') as HTMLInputElement;
    const anthropicApiKeyInput = document.getElementById('escobar-anthropic-api-key') as HTMLInputElement;
    const geminiApiKeyInput = document.getElementById('escobar-gemini-api-key') as HTMLInputElement;

    const usernameInput = document.getElementById('escobar-username') as HTMLInputElement;
    const proxyPortInput = document.getElementById('escobar-proxy-port') as HTMLInputElement;

    // Update values with current settings
    if (maxMessagesInput) maxMessagesInput.value = this.currentSettings.maxMessages.toString();
    if (serverUrlInput) serverUrlInput.value = this.currentSettings.serverUrl;
    if (voittaApiKeyInput) voittaApiKeyInput.value = this.currentSettings.voittaApiKey || '';
    if (openaiApiKeyInput) openaiApiKeyInput.value = this.currentSettings.openaiApiKey || '';
    if (anthropicApiKeyInput) anthropicApiKeyInput.value = this.currentSettings.anthropicApiKey || '';
    if (geminiApiKeyInput) geminiApiKeyInput.value = this.currentSettings.geminiApiKey || '';

    if (usernameInput) usernameInput.value = this.currentSettings.username;
    if (proxyPortInput) proxyPortInput.value = (this.currentSettings.proxyPort || 3000).toString();

    // Create model dropdowns now that settings are loaded
    // Get placeholder containers
    const primaryModelContainer = document.getElementById('primary-model-container');
    const secondaryProviderContainer = document.getElementById('secondary-provider-container');
    const imageParseProviderContainer = document.getElementById('image-parse-provider-container');

    if (primaryModelContainer) {
      primaryModelContainer.innerHTML = ''; // Clear placeholder
      const primaryModelGroup = this.createModelDropdown(
        'escobar-primary-model',
        'Primary Model',
        'The main AI model used for chat responses.',
        this.currentSettings.primaryModel
      );
      primaryModelContainer.appendChild(primaryModelGroup);
    }

    if (secondaryProviderContainer) {
      secondaryProviderContainer.innerHTML = ''; // Clear placeholder
      const secondaryProviderGroup = this.createModelDropdown(
        'escobar-secondary-provider',
        'Secondary Provider',
        'Secondary AI model for specialized tasks.',
        this.currentSettings.secondaryProvider
      );
      secondaryProviderContainer.appendChild(secondaryProviderGroup);
    }

    if (imageParseProviderContainer) {
      imageParseProviderContainer.innerHTML = ''; // Clear placeholder
      const imageParseProviderGroup = this.createModelDropdown(
        'escobar-image-parse-provider',
        'Image Parse Provider',
        'AI model used for image analysis and parsing.',
        this.currentSettings.imageParseProvider
      );
      imageParseProviderContainer.appendChild(imageParseProviderGroup);
    }
  }

  /**
   * Save settings changes
   */
  protected saveSettings(): void {
    // Get values from form
    const voittaApiKeyInput = document.getElementById('escobar-voitta-api-key') as HTMLInputElement;
    const openaiApiKeyInput = document.getElementById('escobar-openai-api-key') as HTMLInputElement;
    const anthropicApiKeyInput = document.getElementById('escobar-anthropic-api-key') as HTMLInputElement;
    const proxyPortInput = document.getElementById('escobar-proxy-port') as HTMLInputElement;

    // Validate and save settings
    this.validateAndSaveCommonSettings({
      voittaApiKey: voittaApiKeyInput.value.trim(),
      openaiApiKey: openaiApiKeyInput.value.trim(),
      anthropicApiKey: anthropicApiKeyInput.value.trim(),
      proxyPort: proxyPortInput ? parseInt(proxyPortInput.value, 10) : 3000
    });
  }
}

/**
 * Connection settings page implementation (simplified for connection parameters only)
 */
export class ConnectionSettingsPage extends BaseSettingsPage {
  /**
   * Create the connection settings UI container
   */
  protected createContainer(): HTMLDivElement {
    // Create container
    const container = document.createElement('div');
    container.className = 'escobar-settings-container';
    container.style.maxWidth = '400px'; // Smaller than main settings

    // Create header
    const header = this.createHeader('Connection Settings');
    container.appendChild(header);

    // Add connection indicator
    const connectionIndicator = document.createElement('div');
    connectionIndicator.className = 'escobar-mode-indicator';
    connectionIndicator.innerHTML = `Connection Parameters <span style="font-size: 0.8em; opacity: 0.8;">v${VERSION}</span>`;
    connectionIndicator.style.backgroundColor = '#e8f5e8';
    connectionIndicator.style.color = '#2d5a2d';
    connectionIndicator.style.padding = '8px 16px';
    connectionIndicator.style.margin = '0 16px 16px 16px';
    connectionIndicator.style.borderRadius = '4px';
    connectionIndicator.style.fontWeight = 'bold';
    connectionIndicator.style.textAlign = 'center';
    connectionIndicator.style.border = '1px solid #a8d8a8';
    container.appendChild(connectionIndicator);

    // Create form
    const form = document.createElement('form');
    form.className = 'escobar-settings-form';
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.saveSettings();
    });

    // Server URL field
    const serverUrlGroup = this.createFormGroup(
      'escobar-connection-server-url',
      'Server URL',
      'The WebSocket server URL. Changing this will trigger a reconnection.'
    );

    const serverUrlInput = document.createElement('input');
    serverUrlInput.id = 'escobar-connection-server-url';
    serverUrlInput.className = 'escobar-settings-input';
    serverUrlInput.type = 'text';
    serverUrlInput.value = this.currentSettings.serverUrl;
    serverUrlGroup.appendChild(serverUrlInput);

    form.appendChild(serverUrlGroup);

    // Username field - behavior depends on environment
    const isJupyterHub = isJupyterHubEnvironment();
    const usernameGroup = this.createFormGroup(
      'escobar-connection-username',
      'Username',
      isJupyterHub
        ? 'Username extracted from JupyterHub (read-only).'
        : 'Your display name for chat messages.'
    );

    const usernameInput = document.createElement('input');
    usernameInput.id = 'escobar-connection-username';
    usernameInput.className = 'escobar-settings-input';
    usernameInput.type = 'text';
    usernameInput.value = this.currentSettings.username;

    if (isJupyterHub) {
      usernameInput.disabled = true;
      usernameInput.style.opacity = '0.7';
      usernameInput.style.cursor = 'not-allowed';

      // Add JupyterHub note
      const jupyterHubNote = document.createElement('div');
      jupyterHubNote.className = 'escobar-settings-note';
      jupyterHubNote.style.fontSize = '0.85em';
      jupyterHubNote.style.fontStyle = 'italic';
      jupyterHubNote.style.marginTop = '5px';
      jupyterHubNote.style.color = '#666';
      jupyterHubNote.textContent = 'Username is extracted from JupyterHub URL and cannot be changed.';
      usernameGroup.appendChild(jupyterHubNote);
    }

    usernameGroup.appendChild(usernameInput);
    form.appendChild(usernameGroup);

    // Bonnie URL field
    const bonnieUrlGroup = this.createFormGroup(
      'escobar-connection-bonnie-url',
      'Bonnie URL',
      'The WebSocket URL for the Bonnie backend server. If specified, this overrides the WEBSOCKET_PROXY_TARGET environment variable. (Optional)'
    );

    const bonnieUrlInput = document.createElement('input');
    bonnieUrlInput.id = 'escobar-connection-bonnie-url';
    bonnieUrlInput.className = 'escobar-settings-input';
    bonnieUrlInput.type = 'text';
    bonnieUrlInput.placeholder = 'ws://bonnie:8777/ws';
    bonnieUrlInput.value = this.currentSettings.bonnieUrl || '';
    bonnieUrlGroup.appendChild(bonnieUrlInput);

    // Add help text for Bonnie URL
    const bonnieUrlHelp = document.createElement('div');
    bonnieUrlHelp.className = 'escobar-settings-note';
    bonnieUrlHelp.style.fontSize = '0.85em';
    bonnieUrlHelp.style.fontStyle = 'italic';
    bonnieUrlHelp.style.marginTop = '5px';
    bonnieUrlHelp.style.color = '#666';
    bonnieUrlHelp.innerHTML = 'Examples: <code>ws://localhost:8777/ws</code>, <code>wss://api.example.com/ws</code>';
    bonnieUrlGroup.appendChild(bonnieUrlHelp);

    form.appendChild(bonnieUrlGroup);

    // Warning message
    const warningMessage = document.createElement('div');
    warningMessage.style.cssText = `
      background: #fff3cd;
      color: #856404;
      border: 1px solid #ffeaa7;
      border-radius: 4px;
      padding: 12px;
      margin: 16px;
      font-size: 14px;
    `;
    warningMessage.innerHTML = `
      <strong>⚠️ Connection Settings</strong><br>
      Saving these settings will trigger a WebSocket reconnection. 
      Any ongoing chat operations will be interrupted.
    `;
    form.appendChild(warningMessage);

    // Create buttons
    const buttonsContainer = this.createButtonsContainer();
    form.appendChild(buttonsContainer);

    container.appendChild(form);

    return container;
  }

  /**
   * Update form fields with current settings
   */
  protected updateFormFields(): void {
    const serverUrlInput = document.getElementById('escobar-connection-server-url') as HTMLInputElement;
    const usernameInput = document.getElementById('escobar-connection-username') as HTMLInputElement;
    const bonnieUrlInput = document.getElementById('escobar-connection-bonnie-url') as HTMLInputElement;

    if (serverUrlInput) serverUrlInput.value = this.currentSettings.serverUrl;
    if (usernameInput) usernameInput.value = this.currentSettings.username;
    if (bonnieUrlInput) bonnieUrlInput.value = this.currentSettings.bonnieUrl || '';
  }

  /**
   * Save connection settings changes
   */
  protected saveSettings(): void {
    const serverUrlInput = document.getElementById('escobar-connection-server-url') as HTMLInputElement;
    const usernameInput = document.getElementById('escobar-connection-username') as HTMLInputElement;
    const bonnieUrlInput = document.getElementById('escobar-connection-bonnie-url') as HTMLInputElement;

    // Validate inputs
    const serverUrl = serverUrlInput.value.trim();
    const username = usernameInput.value.trim();
    const bonnieUrl = bonnieUrlInput.value.trim();

    if (!serverUrl) {
      alert('Server URL is required');
      return;
    }

    if (!username) {
      alert('Username is required');
      return;
    }

    // Validate Bonnie URL format if provided (allow empty string to clear the setting)
    if (bonnieUrl && bonnieUrl.length > 0) {
      try {
        const url = new URL(bonnieUrl);
        if (!['ws:', 'wss:'].includes(url.protocol)) {
          alert('Bonnie URL must use ws:// or wss:// protocol');
          return;
        }
      } catch (error) {
        alert('Invalid Bonnie URL format. Please enter a valid WebSocket URL.');
        return;
      }
    }

    // Create new settings object with only connection changes
    const newSettings: IChatSettings = {
      ...this.currentSettings,
      serverUrl: serverUrl,
      username: username,
      bonnieUrl: bonnieUrl || undefined
    };

    console.log('🔗 CONNECTION: Saving connection settings');

    // Save connection settings to registry (triggers reconnection)
    this.saveConnectionSettings(newSettings);
  }

  /**
   * Save connection settings to registry and trigger reconnection
   */
  private async saveConnectionSettings(settings: IChatSettings): Promise<void> {
    try {
      const settingsPlugin = await this.settingsRegistry.load('escobar:plugin');

      console.log('🔗 CONNECTION: Saving to registry (will trigger reconnection)');
      // Save connection settings to registry
      await settingsPlugin.set('serverUrl', settings.serverUrl);
      await settingsPlugin.set('username', settings.username);
      await settingsPlugin.set('usernameFromJupyterHub', settings.usernameFromJupyterHub);
      // Always save bonnieUrl, even if it's empty (to clear the setting)
      await settingsPlugin.set('bonnieUrl', settings.bonnieUrl || '');

      console.log('🔗 CONNECTION: Registry save successful');

      // Update current settings
      this.currentSettings = settings;

      // Update global settings
      (window as any).escobarCurrentSettings = settings;

      // Call onSave callback (this will trigger reconnection)
      this.onSave(settings);

      console.log('🔗 CONNECTION: Connection settings save completed');

      // Hide settings page
      this.hide();

    } catch (error) {
      console.error('🔗 CONNECTION: Failed to save connection settings:', error);
      alert(`Failed to save connection settings:\n\n${error instanceof Error ? error.message : 'Unknown error'}\n\nPlease try again.`);
    }
  }
}

/**
 * Plugin-specific settings page implementation
 */
export class PluginSettingsPage extends BaseSettingsPage {
  /**
   * Create the settings UI container for plugin environment
   */
  protected createContainer(): HTMLDivElement {
    // Create container
    const container = document.createElement('div');
    container.className = 'escobar-settings-container';

    // Create header with simplified title
    const header = this.createHeader('Settings');
    container.appendChild(header);

    // Add mode indicator label with version number
    const modeIndicator = document.createElement('div');
    modeIndicator.className = 'escobar-mode-indicator';
    modeIndicator.innerHTML = `Running in Plugin Mode <span style="font-size: 0.8em; opacity: 0.8;">v${VERSION}</span>`;
    modeIndicator.style.backgroundColor = '#f6f8fa';
    modeIndicator.style.color = '#24292e';
    modeIndicator.style.padding = '8px 16px';
    modeIndicator.style.margin = '0 16px 16px 16px';
    modeIndicator.style.borderRadius = '4px';
    modeIndicator.style.fontWeight = 'bold';
    modeIndicator.style.textAlign = 'center';
    modeIndicator.style.border = '1px solid #e1e4e8';
    container.appendChild(modeIndicator);

    // Create form
    const form = document.createElement('form');
    form.className = 'escobar-settings-form';
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.saveSettings();
    });

    // Create form fields

    // Voitta API Key field
    const voittaApiKeyGroup = this.createFormGroup(
      'escobar-voitta-api-key',
      'Voitta API Key',
      'The API key for authentication with Voitta services. (Optional)'
    );

    const voittaApiKeyInput = document.createElement('input');
    voittaApiKeyInput.id = 'escobar-voitta-api-key';
    voittaApiKeyInput.className = 'escobar-settings-input';
    voittaApiKeyInput.type = 'text';
    voittaApiKeyInput.value = this.currentSettings.voittaApiKey || '';
    voittaApiKeyGroup.appendChild(voittaApiKeyInput);

    // Add "Get API Key" link for Voitta
    const getVoittaApiKeyLink = document.createElement('a');
    getVoittaApiKeyLink.href = '#';
    getVoittaApiKeyLink.className = 'escobar-get-api-key-link';
    getVoittaApiKeyLink.textContent = 'Get Voitta API Key';
    getVoittaApiKeyLink.style.display = this.currentSettings.voittaApiKey ? 'none' : 'block';
    getVoittaApiKeyLink.addEventListener('click', (e) => {
      e.preventDefault();

      // Show the login UI
      showLoginUI()
        .then((apiKey) => {
          // Update the API key input
          voittaApiKeyInput.value = apiKey;

          // Hide the link
          getVoittaApiKeyLink.style.display = 'none';

          // Show success message
          alert('Successfully obtained Voitta API key!');
        })
        .catch((error) => {
          if (error.message !== 'Authentication cancelled') {
            console.error('Authentication error:', error);
            alert('Failed to authenticate. Please try again.');
          }
        });
    });
    voittaApiKeyGroup.appendChild(getVoittaApiKeyLink);

    // Add event listener to show/hide the link based on input value
    voittaApiKeyInput.addEventListener('input', () => {
      getVoittaApiKeyLink.style.display = voittaApiKeyInput.value ? 'none' : 'block';
    });

    form.appendChild(voittaApiKeyGroup);

    // OpenAI API Key field
    const openaiApiKeyGroup = this.createFormGroup(
      'escobar-openai-api-key',
      'OpenAI API Key',
      'Your OpenAI API key for OpenAI-powered features. (Optional)'
    );

    const openaiApiKeyInput = document.createElement('input');
    openaiApiKeyInput.id = 'escobar-openai-api-key';
    openaiApiKeyInput.className = 'escobar-settings-input';
    openaiApiKeyInput.type = 'text';
    openaiApiKeyInput.value = this.currentSettings.openaiApiKey || '';
    openaiApiKeyGroup.appendChild(openaiApiKeyInput);

    form.appendChild(openaiApiKeyGroup);

    // Anthropic API Key field
    const anthropicApiKeyGroup = this.createFormGroup(
      'escobar-anthropic-api-key',
      'Anthropic API Key',
      'Your Anthropic API key for Claude-powered features. (Optional)'
    );

    const anthropicApiKeyInput = document.createElement('input');
    anthropicApiKeyInput.id = 'escobar-anthropic-api-key';
    anthropicApiKeyInput.className = 'escobar-settings-input';
    anthropicApiKeyInput.type = 'text';
    anthropicApiKeyInput.value = this.currentSettings.anthropicApiKey || '';
    anthropicApiKeyGroup.appendChild(anthropicApiKeyInput);

    form.appendChild(anthropicApiKeyGroup);

    // Gemini API Key field
    const geminiApiKeyGroup = this.createFormGroup(
      'escobar-gemini-api-key',
      'Gemini API Key',
      'Your Google Gemini API key for Gemini-powered features. (Optional)'
    );

    const geminiApiKeyInput = document.createElement('input');
    geminiApiKeyInput.id = 'escobar-gemini-api-key';
    geminiApiKeyInput.className = 'escobar-settings-input';
    geminiApiKeyInput.type = 'text';
    geminiApiKeyInput.value = this.currentSettings.geminiApiKey || '';
    geminiApiKeyGroup.appendChild(geminiApiKeyInput);

    form.appendChild(geminiApiKeyGroup);

    // Create placeholder containers for model dropdowns (will be populated after settings load)
    const primaryModelGroup = document.createElement('div');
    primaryModelGroup.id = 'primary-model-container';
    primaryModelGroup.className = 'escobar-settings-group';
    form.appendChild(primaryModelGroup);

    const secondaryProviderGroup = document.createElement('div');
    secondaryProviderGroup.id = 'secondary-provider-container';
    secondaryProviderGroup.className = 'escobar-settings-group';
    form.appendChild(secondaryProviderGroup);

    const imageParseProviderGroup = document.createElement('div');
    imageParseProviderGroup.id = 'image-parse-provider-container';
    imageParseProviderGroup.className = 'escobar-settings-group';
    form.appendChild(imageParseProviderGroup);

    // Proxy Port field (moved to end)
    const proxyPortGroup = this.createFormGroup(
      'escobar-proxy-port',
      'Proxy Port',
      'The port number for the proxy server.'
    );

    const proxyPortInput = document.createElement('input');
    proxyPortInput.id = 'escobar-proxy-port';
    proxyPortInput.className = 'escobar-settings-input';
    proxyPortInput.type = 'number';
    proxyPortInput.min = '1';
    proxyPortInput.max = '65535';
    proxyPortInput.value = (this.currentSettings.proxyPort || 3000).toString();
    proxyPortGroup.appendChild(proxyPortInput);

    form.appendChild(proxyPortGroup);

    // Create buttons
    const buttonsContainer = this.createButtonsContainer();
    form.appendChild(buttonsContainer);

    container.appendChild(form);

    return container;
  }

  /**
   * Update form fields with current settings
   */
  protected updateFormFields(): void {
    // Get form elements
    const maxMessagesInput = document.getElementById('escobar-max-messages') as HTMLInputElement;
    const serverUrlInput = document.getElementById('escobar-server-url') as HTMLInputElement;
    const voittaApiKeyInput = document.getElementById('escobar-voitta-api-key') as HTMLInputElement;
    const openaiApiKeyInput = document.getElementById('escobar-openai-api-key') as HTMLInputElement;
    const anthropicApiKeyInput = document.getElementById('escobar-anthropic-api-key') as HTMLInputElement;
    const geminiApiKeyInput = document.getElementById('escobar-gemini-api-key') as HTMLInputElement;

    const usernameInput = document.getElementById('escobar-username') as HTMLInputElement;
    const proxyPortInput = document.getElementById('escobar-proxy-port') as HTMLInputElement;

    // Get model dropdown elements
    const primaryModelSelect = document.getElementById('escobar-primary-model') as HTMLSelectElement;
    const secondaryProviderSelect = document.getElementById('escobar-secondary-provider') as HTMLSelectElement;
    const imageParseProviderSelect = document.getElementById('escobar-image-parse-provider') as HTMLSelectElement;

    // Update values with current settings
    if (maxMessagesInput) maxMessagesInput.value = this.currentSettings.maxMessages.toString();
    if (serverUrlInput) serverUrlInput.value = this.currentSettings.serverUrl;
    if (voittaApiKeyInput) voittaApiKeyInput.value = this.currentSettings.voittaApiKey || '';
    if (openaiApiKeyInput) openaiApiKeyInput.value = this.currentSettings.openaiApiKey || '';
    if (anthropicApiKeyInput) anthropicApiKeyInput.value = this.currentSettings.anthropicApiKey || '';
    if (geminiApiKeyInput) geminiApiKeyInput.value = this.currentSettings.geminiApiKey || '';

    if (usernameInput) usernameInput.value = this.currentSettings.username;
    if (proxyPortInput) proxyPortInput.value = (this.currentSettings.proxyPort || 3000).toString();

    // Create model dropdowns now that settings are loaded
    // Get placeholder containers
    const primaryModelContainer = document.getElementById('primary-model-container');
    const secondaryProviderContainer = document.getElementById('secondary-provider-container');
    const imageParseProviderContainer = document.getElementById('image-parse-provider-container');

    if (primaryModelContainer) {
      primaryModelContainer.innerHTML = ''; // Clear placeholder
      const primaryModelGroup = this.createModelDropdown(
        'escobar-primary-model',
        'Primary Model',
        'The main AI model used for chat responses.',
        this.currentSettings.primaryModel
      );
      primaryModelContainer.appendChild(primaryModelGroup);
    }

    if (secondaryProviderContainer) {
      secondaryProviderContainer.innerHTML = ''; // Clear placeholder
      const secondaryProviderGroup = this.createModelDropdown(
        'escobar-secondary-provider',
        'Secondary Provider',
        `Current value: ${this.currentSettings.secondaryProvider || 'Not set'}`,
        this.currentSettings.secondaryProvider
      );
      secondaryProviderContainer.appendChild(secondaryProviderGroup);
    }

    if (imageParseProviderContainer) {
      imageParseProviderContainer.innerHTML = ''; // Clear placeholder
      const imageParseProviderGroup = this.createModelDropdown(
        'escobar-image-parse-provider',
        'Image Parse Provider',
        'AI model used for image analysis and parsing.',
        this.currentSettings.imageParseProvider
      );
      imageParseProviderContainer.appendChild(imageParseProviderGroup);
    }
  }

  /**
   * Save settings changes
   */
  protected saveSettings(): void {
    // Get values from form
    const voittaApiKeyInput = document.getElementById('escobar-voitta-api-key') as HTMLInputElement;
    const openaiApiKeyInput = document.getElementById('escobar-openai-api-key') as HTMLInputElement;
    const anthropicApiKeyInput = document.getElementById('escobar-anthropic-api-key') as HTMLInputElement;
    const proxyPortInput = document.getElementById('escobar-proxy-port') as HTMLInputElement;

    // Validate and save settings
    this.validateAndSaveCommonSettings({
      voittaApiKey: voittaApiKeyInput.value.trim(),
      openaiApiKey: openaiApiKeyInput.value.trim(),
      anthropicApiKey: anthropicApiKeyInput.value.trim(),
      proxyPort: proxyPortInput ? parseInt(proxyPortInput.value, 10) : 3000
    });
  }
}
