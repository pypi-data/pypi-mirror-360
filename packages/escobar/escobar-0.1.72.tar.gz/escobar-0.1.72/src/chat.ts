/* eslint-disable prettier/prettier */
import { JupyterFrontEnd } from '@jupyterlab/application';

import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';
import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { VoittaToolRouter } from "./voitta/voittaServer";
import { initPythonBridge, callPython, registerFunction, get_ws, voittal_call_log, stopped_messages, PYTHON_CALL_EVENTS } from './voitta/pythonBridge_browser'
import {
  IContinueRequest,
  ICreateNewChatRequest,
  IListChatsRequest,
  ILoadMessagesRequest,
  IChatInfo,
  ChatModel,
  createContextIDString
} from './types/protocol';

import { get_tools } from "./integrations/jupyter_integrations"

import { createEscobarSplitButton, createTopButtons, createChatSelectionInterface } from "./js/ui_elements"
import { createSettingsPage } from "./js/setting_page"
import { MessageHandler, ResponseMessage } from './messageHandler';
import { SettingsManager, IChatSettings, ILocalSettings, IRemoteSettings } from './utils/settingsManager';
import { jsonrepair } from 'jsonrepair';

import { INotebookTracker } from '@jupyterlab/notebook';

import { functions } from "./integrations/jupyter_integrations"

import { IDebugger } from '@jupyterlab/debugger';

// Default timeout for requests in milliseconds
const DEFAULT_TIMEOUT = 1000 * 60 * 60;

/**
 * Get the username for the current user
 * 
 * @returns The username string
 */
function getUserName(): string {
  // First check if we're in JupyterHub mode
  const isJupyterHub = window.location.href.includes('/user/');

  if (isJupyterHub) {
    // In JupyterHub mode, get the username from the URL
    const usernameInfo = getJupyterHubUsername();
    if (usernameInfo.fromJupyterHub) {
      return usernameInfo.username;
    }
  }

  const hostname = window.location.hostname || 'localhost';
  return `VoittaDefaultUser@${hostname}`;
}

/**
 * Get the JupyterHub username from the client side
 * 
 * @returns An object containing the username and a flag indicating if it's from JupyterHub
 */
function getJupyterHubUsername(): { username: string, fromJupyterHub: boolean } {
  // Method 1: Check URL pattern - most reliable in JupyterHub
  // JupyterHub URLs typically follow the pattern: /user/{username}/lab/...
  const hubUserRegex = /\/user\/([^\/]+)\//;

  // First try with the pathname
  const pathname = window.location.pathname;
  const hubUserMatch = pathname.match(hubUserRegex);

  if (hubUserMatch && hubUserMatch[1]) {
    // Make sure to decode the username to handle special characters like @ in email addresses
    const decodedUsername = decodeURIComponent(hubUserMatch[1]);
    // Successfully found username from URL
    return { username: decodedUsername, fromJupyterHub: true };
  }

  // If pathname didn't work, try with the full URL
  const fullUrl = window.location.href;
  const fullUrlMatch = fullUrl.match(hubUserRegex);

  if (fullUrlMatch && fullUrlMatch[1]) {
    // Make sure to decode the username to handle special characters like @ in email addresses
    const decodedUsername = decodeURIComponent(fullUrlMatch[1]);
    // Successfully found username from full URL
    return { username: decodedUsername, fromJupyterHub: true };
  }

  // Method 2: Check for JupyterHub data in the page config
  try {
    // JupyterLab stores config data in a script tag with id jupyter-config-data
    const configElement = document.getElementById('jupyter-config-data');
    if (configElement && configElement.textContent) {
      const config = JSON.parse(configElement.textContent);

      // JupyterHub might store user info in different properties
      if (config.hubUser) {
        // Found username in page config
        return { username: config.hubUser, fromJupyterHub: true };
      }

      if (config.hubUsername) {
        // Found username in page config
        return { username: config.hubUsername, fromJupyterHub: true };
      }

      // Some deployments might use a different property
      if (config.user) {
        // Found username in page config
        return { username: config.user, fromJupyterHub: true };
      }
    }
  } catch (error) {
    console.error('Error parsing JupyterHub config:', error);
  }

  // Method 3: Try to extract from document.baseURI
  // Sometimes the base URI contains the username
  try {
    const baseUri = document.baseURI;
    const baseMatch = baseUri.match(/\/user\/([^\/]+)\//);

    if (baseMatch && baseMatch[1]) {
      // Make sure to decode the username to handle special characters like @ in email addresses
      const decodedUsername = decodeURIComponent(baseMatch[1]);
      // Found username from baseURI
      return { username: decodedUsername, fromJupyterHub: true };
    }
  } catch (error) {
    console.error('Error checking baseURI:', error);
  }

  // Method 4: Check cookies for JupyterHub-related information
  try {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'jupyterhub-user') {
        // Found username in cookies
        return { username: decodeURIComponent(value), fromJupyterHub: true };
      }
    }
  } catch (error) {
    console.error('Error checking cookies:', error);
  }

  // Try a different regex pattern that might better handle complex usernames
  // This pattern is more permissive and might catch usernames with special characters
  const altRegex = /user\/([^\/]+)/;

  // Try with pathname first
  const altMatch = window.location.pathname.match(altRegex);
  if (altMatch && altMatch[1]) {
    const decodedUsername = decodeURIComponent(altMatch[1]);
    // Found username from alternative pattern
    return { username: decodedUsername, fromJupyterHub: true };
  }

  // Then try with full URL
  const altFullMatch = window.location.href.match(altRegex);
  if (altFullMatch && altFullMatch[1]) {
    const decodedUsername = decodeURIComponent(altFullMatch[1]);
    // Found username from alternative pattern in URL
    return { username: decodedUsername, fromJupyterHub: true };
  }

  // Try one more pattern specifically for email addresses in URLs
  const emailRegex = /user\/([^\/]+@[^\/]+)/;
  const emailMatch = window.location.href.match(emailRegex);
  if (emailMatch && emailMatch[1]) {
    const decodedUsername = decodeURIComponent(emailMatch[1]);
    // Found username with email pattern
    return { username: decodedUsername, fromJupyterHub: true };
  }

  // Not in a JupyterHub environment or username not found
  console.log('No JupyterHub username found, using default');
  return { username: "VoittaDefaultUser", fromJupyterHub: false };
}


/**
 * A simple chat widget for Jupyter.
 */
export class ChatWidget extends Widget {
  private chatContainer: HTMLDivElement;
  private buttonContainer: HTMLDivElement;
  private chatSelectionContainer: HTMLDivElement | null = null;
  private divider: HTMLDivElement;
  private inputContainer: HTMLDivElement;
  private chatInput: HTMLTextAreaElement;
  private sendButton: HTMLButtonElement;
  private settingsManager: SettingsManager;
  private stopIcon: HTMLDivElement;
  private currentChatID: string = 'temp-session';
  private availableChats: IChatInfo[] = [];
  private availableModels: Array<{ model: string, provider: string }> = [];

  private voittaToolRouter: VoittaToolRouter | undefined;
  private messageHandler: MessageHandler;

  // Bound event handlers to ensure proper cleanup
  private boundDisableInput: EventListener;
  private boundEnableInput: EventListener;

  // Counter for generating unique IDs
  private static idCounter = 0;
  private app: JupyterFrontEnd;
  private notebookTracker: INotebookTracker;
  private settingsRegistry: ISettingRegistry | null;
  private debuggerService: IDebugger | null;

  private call_id_log = {};

  constructor(app: JupyterFrontEnd,
    settingsRegistry: ISettingRegistry | null,
    notebookTracker: INotebookTracker | null,
    debuggerService: IDebugger | null
  ) {
    // Generate a unique ID for this widget instance
    const id = `escobar-chat-${ChatWidget.idCounter++}`;
    super();

    this.app = app;
    this.notebookTracker = notebookTracker;
    this.settingsRegistry = settingsRegistry;
    this.debuggerService = debuggerService;
    this.id = id;
    this.addClass('escobar-chat');
    this.title.label = 'Voitta';
    this.title.caption = 'Escobar Voitta';
    this.title.iconClass = 'jp-MessageIcon'; // Add an icon for the sidebar
    this.title.closable = true;

    // Initialize the settings manager
    this.settingsManager = new SettingsManager(settingsRegistry);

    // Create the main layout
    this.node.style.display = 'flex';
    this.node.style.flexDirection = 'column';
    this.node.style.height = '100%';
    this.node.style.padding = '5px';

    // Make sure the parent container has position relative for proper absolute positioning
    this.node.style.position = 'relative';

    // Create top buttons using the function from ui_elements.ts
    this.buttonContainer = createTopButtons(
      this.app,
      this.settingsRegistry,
      () => this.settingsManager.getCompleteSettings(), // Function to get the current settings
      this.createNewChat.bind(this),
      this.init.bind(this),
      this.onSettingsChanged.bind(this),
      this.availableChats, // Available chats array
      this.onChatSelect.bind(this), // Chat selection callback
      this.currentChatID, // Current chat ID
      this.availableModels // Available models array
    );

    // Add the button container to the DOM
    this.node.appendChild(this.buttonContainer);

    // Initialize chat state tracking
    this.updateChatStateInUI(this.currentChatID);

    // Create chat container
    this.chatContainer = document.createElement('div');
    this.chatContainer.className = 'escobar-chat-container';
    // Set initial height to 80% of the container
    this.chatContainer.style.height = '80%';
    this.chatContainer.style.flex = 'none';
    this.node.appendChild(this.chatContainer);

    // Create divider
    this.divider = document.createElement('div');
    this.divider.className = 'escobar-divider';
    this.node.appendChild(this.divider);

    // Add drag functionality to divider
    this.setupDividerDrag();

    // Create input container
    this.inputContainer = document.createElement('div');
    this.inputContainer.className = 'escobar-input-container';
    this.node.appendChild(this.inputContainer);

    // Create chat input
    this.chatInput = document.createElement('textarea');
    this.chatInput.className = 'escobar-chat-input';
    this.chatInput.placeholder = 'Type your message here...';
    this.chatInput.rows = 2;
    this.chatInput.addEventListener('keydown', (event: KeyboardEvent) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        this.sendMessage(this.sendButton.textContent);
      }
    });
    this.inputContainer.appendChild(this.chatInput);

    // Create stop icon (authentic traffic stop sign)
    this.stopIcon = document.createElement('div');
    this.stopIcon.className = 'escobar-stop-icon';
    this.stopIcon.innerHTML = `
      <svg viewBox="0 0 100 100" width="100" height="100">
        <!-- Octagonal stop sign shape with white border -->
        <polygon points="29,5 71,5 95,29 95,71 71,95 29,95 5,71 5,29" fill="#c0392b" />
        <polygon points="29,5 71,5 95,29 95,71 71,95 29,95 5,71 5,29" fill="none" stroke="white" stroke-width="1.5" />
        <!-- STOP text - highway style, positioned slightly higher -->
        <text x="50" y="53" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="white" letter-spacing="1">STOP</text>
      </svg>
    `;
    this.stopIcon.style.display = 'none'; // Initially hidden
    this.stopIcon.addEventListener('click', () => {
      window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.STOP));
    });
    this.inputContainer.appendChild(this.stopIcon);

    // Create bound event handlers for proper cleanup
    this.boundDisableInput = this.disableInput.bind(this);
    this.boundEnableInput = this.enableInput.bind(this);

    // Add event listeners for Python call events to disable/enable the input area
    window.addEventListener(PYTHON_CALL_EVENTS.START, this.boundDisableInput);
    window.addEventListener(PYTHON_CALL_EVENTS.END, this.boundEnableInput);

    const splitButton: HTMLDivElement = createEscobarSplitButton(["Talk", "Plan", "Act"]);
    this.sendButton = splitButton["mainButton"];
    this.inputContainer.appendChild(splitButton);

    this.sendButton.addEventListener('click', () => {
      this.sendMessage(this.sendButton.textContent);
    });

    // Initialize the message handler with default settings
    const currentUsername = getUserName();
    const defaultSettings = this.settingsManager.getCompleteSettings();
    this.messageHandler = new MessageHandler(
      defaultSettings.voittaApiKey,
      defaultSettings.openaiApiKey,
      defaultSettings.anthropicApiKey,
      defaultSettings.geminiApiKey,
      '', // selectedProvider will be determined dynamically
      currentUsername,
      this.chatContainer,
      defaultSettings.maxMessages
    );

    // Set up a callback for when the message handler creates a new chat
    this.messageHandler.onChatCreated = (chatId: string) => {
      this.currentChatID = chatId;
      this.updateChatStateInUI(chatId);
    };

    // Set up settings manager callbacks
    this.settingsManager.setMessageHandler(this.messageHandler);
    this.settingsManager.setOnSettingsChanged(this.onSettingsChanged.bind(this));
    this.settingsManager.setupLocalSettingsListener();

    // Expose the message handler globally for settings page access
    (window as any).escobarMessageHandler = this.messageHandler;

    // Set the username as a global variable for the Python bridge
    (window as any).escobarUsername = currentUsername;

    // Expose available models and current settings for settings page
    (window as any).escobarAvailableModels = this.availableModels;
    (window as any).escobarCurrentSettings = defaultSettings;

    // Initialize settings and start the application
    setTimeout(async () => {
      await this.initializeSettings();
      await this.init();
    }, 100);
  }

  private handlePythonResponse(response: any, responseMsg?: ResponseMessage): void {
    this.messageHandler.handlePythonResponse(response, responseMsg);
  }

  async say(args: any) {
    const msg = this.messageHandler.findMessageById(args["msg_call_id"]);
    if (msg.isNew) {
      msg.setContent(args["text"]);
      msg.isNew = false;
    } else {
      msg.setContent(msg.getContent() + args["text"]);
    }
  }

  async tool_say(args: any) {
    if ((typeof args["name"] != "string") || (typeof args["name"] == undefined)) {
      console.log(args);
      return;
    }

    if (voittal_call_log[args.id] != undefined) {
      // Streaming finished call
    }

    if (args["name"].includes("editExecuteCell_editExecuteCell") ||
      args["name"].includes("insertExecuteCell_insertExecuteCell") ||
      args["name"].includes("writeToFile_writeToFile") ||
      args["name"].includes("diffToFile_diffToFile")
    ) {
      try {
        if (this.call_id_log[args.id] == undefined) {
          this.call_id_log[args.id] = "";
        }
        this.call_id_log[args.id] += args.text;

        var parsed = {};

        try {
          parsed = JSON.parse(this.call_id_log[args.id]);
        } catch {
          parsed = JSON.parse(this.call_id_log[args.id] + '"}');
        }

        if (args["name"].includes("diffToFile_diffToFile")) {
          const search = parsed["search"];
          const replace = parsed["replace"];
          const filePath = parsed["filePath"];
          if ((search != undefined) && (replace != undefined)) {
            const funcion_name = args["name"].split("_").reverse()[1];
            const callResult = await functions[funcion_name].func(
              {
                "filePath": filePath, "search": search, "replace": replace
              }, true, args.id
            )
          }
        } else if (args["name"].includes("writeToFile_writeToFile")) {
          const content = parsed["content"];
          const filePath = parsed["filePath"];
          if (content) {
            const funcion_name = args["name"].split("_").reverse()[1];
            const callResult = await functions[funcion_name].func(
              {
                "filePath": filePath, "content": content
              }, true, args.id
            )
          }
        } else {
          const content = parsed["content"];
          const cellType = parsed["cellType"];
          const index = parseInt(parsed["index"], 10);
          if (content) {
            const funcion_name = args["name"].split("_").reverse()[1]; // this is super voitta-specific....
            const callResult = await functions[funcion_name].func({
              "index": index,
              "cellType": cellType,
              "content": content
            }, true, args.id);
          }
        }


      } catch (error) {
        //console.error('Failed to repair/parse JSON:', error);
      }
    }
  }

  /**
   * Initialize settings using the SettingsManager
   */
  private async initializeSettings(): Promise<void> {
    await this.settingsManager.initializeSettings();

    // Update global settings object
    const settings = this.settingsManager.getCompleteSettings();
    (window as any).escobarCurrentSettings = settings;
  }

  /**
   * Handle settings changes from the SettingsManager
   */
  private onSettingsChanged(settings: IChatSettings): void {
    console.log('🔧 SETTINGS: Settings change detected');

    // Update message handler with new settings
    const currentUsername = getUserName();
    this.messageHandler.updateSettings(
      settings.voittaApiKey,
      settings.openaiApiKey,
      settings.anthropicApiKey,
      settings.geminiApiKey,
      '', // selectedProvider will be determined dynamically
      currentUsername,
      settings.maxMessages
    );

    // Update global settings object
    (window as any).escobarCurrentSettings = settings;
    (window as any).escobarUsername = currentUsername;

    // Check if server URL changed and reinitialize if needed
    const currentSettings = this.settingsManager.getCompleteSettings();
    if (currentSettings.serverUrl) {
      // Only reinitialize if this is NOT from a settings save operation
      // (to avoid the timing issue where we reconnect during save)
      const isFromSettingsSave = (window as any).escobarSettingsSaveInProgress;
      if (!isFromSettingsSave) {
        console.log('🔧 SETTINGS: Server URL changed, reinitializing connection');
        this.reinitializeConnection();
      } else {
        console.log('🔧 SETTINGS: Skipping reconnection during settings save');
      }
    }
  }

  /**
   * Reinitialize WebSocket connection
   */
  private async reinitializeConnection(): Promise<void> {
    console.log('Reinitializing WebSocket connection...');

    // Close existing connection
    const ws = get_ws();
    if (ws) {
      ws.close();
    }

    // Wait a bit for cleanup
    setTimeout(() => {
      this.init();
    }, 100);
  }

  async init() {
    await this.messageHandler.clearMessages();
    this.voittaToolRouter = new VoittaToolRouter();
    const tools = await get_tools(this.app, this.notebookTracker, this.debuggerService);

    // Get the current username using the new getUserName function
    const currentUsername = getUserName();

    // Update global variable
    (window as any).escobarUsername = currentUsername;

    registerFunction('handleResponse', false, this.handlePythonResponse.bind(this));
    registerFunction('say', false, this.say.bind(this));
    registerFunction('tool_say', false, this.tool_say.bind(this));

    this.voittaToolRouter.tools = tools;

    try {
      // Use serverUrl from settings manager
      const settings = this.settingsManager.getCompleteSettings();
      console.log('🌐 WS: Attempting connection to', settings.serverUrl);
      await initPythonBridge(settings.serverUrl);
      console.log('🌐 WS: Connection established successfully');
    } catch (e) {
      console.error('🌐 WS: Connection failed:', e);
      return;
    }

    // NEW CHAT MANAGEMENT FLOW: Call listChats first
    try {
      const listChatsCallId = this.messageHandler.generateMessageId();
      const listChatsMessage: IListChatsRequest = {
        method: 'listChats',
        username: currentUsername,
        chatID: '', // Not needed for listChats
        call_id: listChatsCallId,
        message_type: 'request',
        intraspection: this.voittaToolRouter.intraspect(),
      };

      const listChatsResponse = await callPython(listChatsMessage, DEFAULT_TIMEOUT, true, false); // Don't show stop button for listChats

      // Store available chats, filtering out temp-session chats
      if (listChatsResponse && listChatsResponse.value && listChatsResponse.value.chats) {
        // Filter out temp-session chats to only get real persistent chats
        // Note: Server returns 'chatId' (camelCase) but we use 'chatID' (capital D) internally
        this.availableChats = listChatsResponse.value.chats.filter(chat =>
          chat.chatId && chat.chatId !== 'temp-session'
        );
      }

      // Extract available models from the response
      if (listChatsResponse && listChatsResponse.value && listChatsResponse.value.models) {
        this.availableModels = listChatsResponse.value.models;
        console.log('📋 MODELS: Received', this.availableModels.length, 'models from server');

        // Update the global models object for settings page
        (window as any).escobarAvailableModels = this.availableModels;

        // Dispatch event to notify settings page that models are available
        window.dispatchEvent(new CustomEvent('escobar-models-updated', {
          detail: { models: this.availableModels }
        }));
      } else {
        console.log('📋 MODELS: No models received from server');
        this.availableModels = [];
        (window as any).escobarAvailableModels = this.availableModels;

        // Still dispatch event so settings page knows models were attempted to load
        window.dispatchEvent(new CustomEvent('escobar-models-updated', {
          detail: { models: this.availableModels }
        }));
      }

      let selectedChatID = 'temp-session';

      if (this.availableChats.length > 0) {
        // Use the last chat in the list
        const lastChatIndex = this.availableChats.length - 1;
        const lastChat = this.availableChats[lastChatIndex];

        // Extract chatID from the chat object
        // Note: Server returns 'chatId' (camelCase) but we use 'chatID' (capital D) internally
        selectedChatID = lastChat.chatId;

        if (!selectedChatID) {
          console.error('No chatID found in chat object! Chat object structure may be incorrect.');
          console.log('Expected chatId property, but got:', lastChat);
          // Fallback to temp-session if no chatID
          selectedChatID = 'temp-session';
        }

        // Update current chat ID BEFORE loading messages
        this.currentChatID = selectedChatID;
        this.messageHandler.setCurrentChatID(selectedChatID);

        // Load messages for the selected chat
        try {
          await this.messageHandler.loadMessages();

          // Update UI to reflect that we have an active chat with messages
          this.updateChatStateInUI(selectedChatID);

          // Check if any messages were actually loaded and displayed
          const loadedMessages = this.messageHandler.getMessages();
          if (loadedMessages.length === 0) {
            // Don't show empty state - the chat exists, it just has no messages yet
          }

        } catch (error) {
          console.error('Error loading messages for chat:', selectedChatID, error);
          // Continue anyway - the chat is still selected, just without message history
          this.updateChatStateInUI(selectedChatID);
        }
      } else {

        // Set the temp session ID for the else case
        this.currentChatID = selectedChatID;
        this.messageHandler.setCurrentChatID(selectedChatID);

        // Update UI to reflect temp session state
        this.updateChatStateInUI(selectedChatID);

        // No empty state message needed
      }

      // Update the chat dropdown with the loaded chats
      this.updateChatDropdown();

      // Create typed continue message to continue with selected chat

      /*
      const continue_call_id = this.messageHandler.generateMessageId();
      const continueMessage: IContinueRequest = {
        method: 'continue',
        username: currentUsername,
        chatID: selectedChatID,
        call_id: continue_call_id,
        message_type: 'request',
        api_key: this.settings.voittaApiKey,
        openai_api_key: this.settings.openaiApiKey,
        anthropic_api_key: this.settings.anthropicApiKey,
        gemini_api_key: this.settings.geminiApiKey,
        selected_provider: '', // Will be determined dynamically
        intraspection: this.voittaToolRouter.intraspect(),
        root_path: '/tmp'
      };
      const response = await callPython(continueMessage, DEFAULT_TIMEOUT, true, false); // Don't show stop button for continue
      console.log('Bonnie says: ', response);

      */

    } catch (error) {
      console.error('Error in chat management flow:', error);
      // Fallback to old behavior if new flow fails
      await this.messageHandler.loadMessages();
    }


  }


  /**
   * Disable the input area during Python calls
   */
  private disableInput(): void {
    if (this.chatInput) {
      this.chatInput.disabled = true;
      this.chatInput.style.opacity = '0.6';
      this.chatInput.placeholder = 'Processing...';

      // Show the stop icon
      if (this.stopIcon) {
        this.stopIcon.style.display = 'flex';
      }
    }
  }

  /**
   * Enable the input area after Python calls complete
   */
  private enableInput(): void {
    if (this.chatInput) {
      this.chatInput.disabled = false;
      this.chatInput.style.opacity = '1';
      this.chatInput.placeholder = 'Type your message here...';

      // Hide the stop icon
      if (this.stopIcon) {
        this.stopIcon.style.display = 'none';
      }
    }
  }

  private updateChatStateInUI(chatId: string): void {
    if (this.buttonContainer && (this.buttonContainer as any).updateChatState) {
      (this.buttonContainer as any).updateChatState(chatId);
    }
  }

  /**
   * Update the chat dropdown with current available chats
   */
  private updateChatDropdown(): void {
    if (this.buttonContainer && (this.buttonContainer as any).updateChatDropdown) {
      (this.buttonContainer as any).updateChatDropdown(this.availableChats, this.currentChatID);
    }
  }

  /**
   * Update the model dropdown with current available models
   */
  private updateModelDropdown(): void {
    if (this.buttonContainer && (this.buttonContainer as any).updateModelDropdown) {
      (this.buttonContainer as any).updateModelDropdown(this.availableModels);
    }
  }

  private async createNewChat(provider?: string): Promise<void> {
    const newChatID = await this.messageHandler.createNewChat(provider);
    this.currentChatID = newChatID;

    // Update the message handler's current chat ID
    this.messageHandler.setCurrentChatID(newChatID);

    // Refresh the chat list to include the new chat
    await this.refreshChatList();

    // Update the dropdown with the new chat list and select the new chat
    this.updateChatDropdown();

    // Update UI state to reflect we're now in an active chat
    this.updateChatStateInUI(newChatID);

    // Don't call init() here as it would clear messages and reload
    // The new chat is already active and ready to use
  }

  /**
   * Handle chat selection from the dropdown
   */
  private async onChatSelect(chatId: string): Promise<void> {
    this.currentChatID = chatId;
    this.messageHandler.setCurrentChatID(chatId);
    console.log(`Selected chat: ${chatId}`);

    // Update UI to reflect we're now in an existing chat
    this.updateChatStateInUI(chatId);

    // Clear current messages and load the selected chat
    await this.messageHandler.clearMessages();
    await this.messageHandler.loadMessages();

    // Update the continue message with the new chat ID

    /*
    const currentUsername = getUserName();
    const continue_call_id = this.messageHandler.generateMessageId();
    const continueMessage: IContinueRequest = {
      method: 'continue',
      username: currentUsername,
      chatID: chatId,
      call_id: continue_call_id,
      message_type: 'request',
      api_key: this.settings.voittaApiKey,
      openai_api_key: this.settings.openaiApiKey,
      anthropic_api_key: this.settings.anthropicApiKey,
      gemini_api_key: this.settings.geminiApiKey,
      selected_provider: '', // Will be determined dynamically
      intraspection: this.voittaToolRouter?.intraspect() || [],
      root_path: '/tmp'
    };
    
    try {
      const response = await callPython(continueMessage, DEFAULT_TIMEOUT, true, false); // Don't show stop button for continue
      console.log('Switched to chat:', response);
    } catch (error) {
      console.error('Error switching to chat:', error);
    }
    */
  }

  /**
   * Refresh the list of available chats
   */
  private async refreshChatList(): Promise<IChatInfo[]> {
    const currentUsername = getUserName();

    try {
      const listChatsCallId = this.messageHandler.generateMessageId();
      const listChatsMessage: IListChatsRequest = {
        method: 'listChats',
        username: currentUsername,
        chatID: '',
        call_id: listChatsCallId,
        message_type: 'request',
        intraspection: this.voittaToolRouter.intraspect()
      };

      const listChatsResponse = await callPython(listChatsMessage, DEFAULT_TIMEOUT, true, false); // Don't show stop button for listChats

      if (listChatsResponse && listChatsResponse.value && listChatsResponse.value.chats) {
        this.availableChats = listChatsResponse.value.chats;
        return this.availableChats;
      }
    } catch (error) {
      console.error('Error refreshing chat list:', error);
    }

    return [];
  }


  /**
   * Get the currently selected provider from the dropdown
   */
  private getSelectedProvider(): string {
    if (this.buttonContainer && (this.buttonContainer as any).getSelectedProvider) {
      return (this.buttonContainer as any).getSelectedProvider();
    }
    return 'OpenAI'; // Default fallback
  }

  /**
   * Send a message from the input field.
   */
  private async sendMessage(mode: string): Promise<void> {
    const content = this.chatInput.value.trim();

    if (!content) {
      return;
    }

    // Clear input
    this.chatInput.value = '';

    // Get the current selected provider from the dropdown
    const selectedProvider = this.getSelectedProvider();

    // Send message using the message handler with the selected provider
    await this.messageHandler.sendMessage(content, mode, selectedProvider);
  }

  /**
   * Handle activation requests for the widget
   */
  protected onActivateRequest(msg: Message): void {
    super.onActivateRequest(msg);
    this.chatInput.focus();
  }

  /**
   * Setup drag functionality for the divider
   */
  private setupDividerDrag(): void {
    let isDragging = false;
    let startY = 0;
    let startHeight = 0;

    const isScrolledToBottom = () => {
      // Get the scroll position
      const scrollTop = this.chatContainer.scrollTop;
      // Get the visible height
      const clientHeight = this.chatContainer.clientHeight;
      // Get the total scrollable height
      const scrollHeight = this.chatContainer.scrollHeight;

      // If scrollTop + clientHeight is approximately equal to scrollHeight,
      // then the container is scrolled to the bottom
      // (using a small threshold to account for rounding errors)

      return Math.abs(scrollTop + clientHeight - scrollHeight) < 100;
    };

    // Mouse move event handler
    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;

      // Calculate exact delta from start position
      const delta = e.pageY - startY - 18;

      // Get container height to calculate minimum and maximum allowed height
      const containerHeight = this.node.offsetHeight;
      const minChatHeight = Math.max(100, containerHeight * 0.3); // At least 30% of container or 100px
      const maxChatHeight = containerHeight * 0.85; // At most 85% of container

      // Apply delta directly to the starting height with min/max constraints
      const newHeight = Math.min(maxChatHeight, Math.max(minChatHeight, startHeight + delta));

      // Update chat container height
      this.chatContainer.style.height = `${newHeight}px`;
      this.chatContainer.style.flex = 'none';

      if (isScrolledToBottom()) {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
      }
    };

    // Mouse up event handler
    const onMouseUp = () => {
      if (!isDragging) return;

      isDragging = false;

      // Remove temporary event listeners
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);

      // Restore text selection
      document.body.style.userSelect = '';
    };

    // Attach mousedown event to divider
    this.divider.addEventListener('mousedown', (e: MouseEvent) => {
      // Prevent default to avoid text selection
      e.preventDefault();
      e.stopPropagation();

      // Store initial values
      isDragging = true;
      startY = e.pageY;
      startHeight = this.chatContainer.offsetHeight;

      // Add temporary event listeners
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);

      // Prevent text selection during drag
      document.body.style.userSelect = 'none';
    });
  }

  /**
   * Dispose of the widget and clean up resources
   */
  dispose(): void {
    // Remove event listeners
    window.removeEventListener(PYTHON_CALL_EVENTS.START, this.boundDisableInput);
    window.removeEventListener(PYTHON_CALL_EVENTS.END, this.boundEnableInput);

    // Close WebSocket connection when widget is disposed
    const ws = get_ws();
    if (ws) {
      ws.close();
    }
    super.dispose();
  }
}
