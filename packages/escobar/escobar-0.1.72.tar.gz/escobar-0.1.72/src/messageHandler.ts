import { callPython, get_ws, PYTHON_CALL_EVENTS, stopped_messages } from './voitta/pythonBridge_browser';

// Default timeout for requests in milliseconds
const DEFAULT_TIMEOUT = 1000 * 60 * 60;
import { functions, get_opened_tabs } from "./integrations/jupyter_integrations"
import { ILoadMessagesRequest, ICreateNewChatRequest, ICreateNewChatResponse, IErrorResponse, IUserMessageRequest, IUserStopRequest, ISaveSettingsRequest, IRetrieveSettingsRequest, ISaveSettingsResponse, IRetrieveSettingsResponse } from './types/protocol';
import { IChatSettings } from './utils/settingsManager';
import MarkdownIt from 'markdown-it';
import sanitizeHtml from 'sanitize-html';
import hljs from 'highlight.js';
import markdownItHighlightjs from 'markdown-it-highlightjs';
import markdownItKatex from 'markdown-it-katex';
import markdownItQuestion from './markdown-it-question';

// Initialize markdown-it instance with all options enabled
const md = new MarkdownIt({
  html: true,        // Enable HTML tags in source
  breaks: true,      // Convert '\n' in paragraphs into <br>
  linkify: true,     // Autoconvert URL-like text to links
  typographer: true, // Enable some language-neutral replacement + quotes beautification
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang, ignoreIllegals: true }).value;
      } catch (__) { }
    }
    return ''; // Use external default escaping
  }
});

// Enable all markdown-it features
md.enable('emphasis');       // For italic and bold
md.enable('link');           // For links
md.enable('heading');        // For headers
md.enable('code');           // For inline code
md.enable('fence');          // For code blocks
md.enable('blockquote');     // For blockquotes
md.enable('list');           // For lists
md.enable('table');          // For tables
md.enable('image');          // For images
md.enable('strikethrough');  // For strikethrough

// Use the highlight.js plugin for code syntax highlighting
md.use(markdownItHighlightjs);

// Use the KaTeX plugin for math rendering
md.use(markdownItKatex);

// Use the question plugin for interactive questions
md.use(markdownItQuestion);


// Add a wrapper around tables for better responsive behavior
const defaultRender = md.renderer.rules.table_open || function (tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options);
};

md.renderer.rules.table_open = function (tokens, idx, options, env, self) {
  return '<div class="table-wrapper">' + defaultRender(tokens, idx, options, env, self);
};

const defaultRenderClose = md.renderer.rules.table_close || function (tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options);
};

md.renderer.rules.table_close = function (tokens, idx, options, env, self) {
  return defaultRenderClose(tokens, idx, options, env, self) + '</div>';
};

// Improve image rendering by adding loading="lazy" and error handling
const defaultImageRender = md.renderer.rules.image || function (tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options);
};

md.renderer.rules.image = function (tokens, idx, options, env, self) {
  // Get the token
  const token = tokens[idx];

  // Find the src attribute
  const srcIndex = token.attrIndex('src');
  const src = srcIndex >= 0 ? token.attrs[srcIndex][1] : '';

  // Add loading="lazy" attribute for better performance
  const loadingIndex = token.attrIndex('loading');
  if (loadingIndex < 0) {
    token.attrPush(['loading', 'lazy']);
  }

  // Add onerror handler to show a placeholder when image fails to load
  const onErrorIndex = token.attrIndex('onerror');
  if (onErrorIndex < 0) {
    token.attrPush(['onerror', "this.onerror=null;this.style.border='1px solid #ddd';this.style.padding='10px';this.style.width='auto';this.style.height='auto';this.alt='Image failed to load: ' + this.alt;this.src='data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\"%3E%3Cpath fill=\"%23ccc\" d=\"M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z\"/%3E%3C/svg%3E';"]);
  }

  // Render the token with the added attributes
  return defaultImageRender(tokens, idx, options, env, self);
};

// Markdown-it is initialized and ready to use

// Configure sanitize-html options
const sanitizeOptions = {
  allowedTags: [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'p', 'a', 'ul', 'ol',
    'nl', 'li', 'b', 'i', 'strong', 'em', 'strike', 'code', 'hr', 'br', 'div',
    'table', 'thead', 'caption', 'tbody', 'tr', 'th', 'td', 'pre', 'span', 'img',
    'button', // For question options
    // KaTeX elements
    'math', 'annotation', 'semantics', 'mrow', 'mn', 'mo', 'mi', 'mtext',
    'mspace', 'ms', 'mglyph', 'malignmark', 'mfrac', 'msqrt', 'mroot',
    'mstyle', 'merror', 'mpadded', 'mphantom', 'mfenced', 'menclose',
    'msub', 'msup', 'msubsup', 'munder', 'mover', 'munderover', 'mmultiscripts',
    'mtable', 'mtr', 'mtd', 'mlabeledtr', 'svg', 'path'
  ],
  allowedAttributes: {
    a: ['href', 'name', 'target', 'rel'],
    img: ['src', 'alt', 'title', 'width', 'height', 'loading', 'srcset', 'sizes', 'onerror', 'onload', 'style'],
    button: ['class', 'data-option', 'type', 'style'],
    code: ['class'],
    pre: ['class'],
    span: ['class', 'style'],
    '*': ['class', 'id', 'style', 'data-*']
  },
  selfClosing: ['img', 'br', 'hr', 'area', 'base', 'basefont', 'input', 'link', 'meta'],
  allowedSchemes: ['http', 'https', 'mailto', 'tel', 'data']
};


/**
 * A class representing a chat message
 */
export class ResponseMessage {
  public readonly id: string;
  public readonly role: 'user' | 'assistant' | 'action';
  public isNew: boolean;
  private messageElement: HTMLDivElement;
  private contentElement: HTMLDivElement;
  private content: string;
  private rawContent: string;

  /**
   * Create a new ResponseMessage
   * @param id Unique identifier for the message
   * @param role The role of the message sender ('user' or 'assistant')
   * @param initialContent Optional initial content for the message
   */
  constructor(id: string, role: 'user' | 'assistant' | 'action', initialContent: string = '') {
    this.id = id;
    this.role = role;
    this.isNew = true;
    this.content = initialContent;
    this.rawContent = initialContent;

    // Create message element
    this.messageElement = document.createElement('div');
    this.messageElement.className = `escobar-message escobar-message-${role}`;
    this.messageElement.dataset.messageId = id;

    // Create content element
    this.contentElement = document.createElement('div');
    this.contentElement.className = 'escobar-message-content markdown-content';

    // Set initial content with proper rendering for assistant and action messages
    if ((role === 'assistant' || role === 'action') && initialContent) {
      // Directly use markdown-it's HTML output without sanitization
      this.contentElement.innerHTML = md.render(initialContent);
    } else {
      this.contentElement.textContent = initialContent;
    }

    this.messageElement.appendChild(this.contentElement);
  }

  /**
   * Set the content of the message
   * @param content The new content
   */
  public setContent(content: string): void {
    this.content = content;
    this.rawContent = content;

    // Render markdown for assistant and action messages, keep plain text for user messages
    if (this.role === 'assistant' || this.role === 'action') {
      // Directly use markdown-it's HTML output without sanitization
      this.contentElement.innerHTML = md.render(content);

      // Log the rendered HTML for debugging
    } else {
      // For user messages, keep using textContent for security
      this.contentElement.textContent = content;
    }

    // Get the parent chat container and scroll to bottom
    const chatContainer = this.messageElement.closest('.escobar-chat-container');
    if (chatContainer) {
      setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }, 0);
    }
  }

  /**
   * Get the raw content of the message (original markdown)
   */
  public getRawContent(): string {
    return this.rawContent;
  }

  /**
   * Get the content of the message
   */
  public getContent(): string {
    return this.content;
  }

  /**
   * Get the DOM element for the message
   */
  public getElement(): HTMLDivElement {
    return this.messageElement;
  }
}


/**
 * A class to handle message operations and storage
 */
export class MessageHandler {
  private messages: ResponseMessage[] = [];
  private messageMap: Map<string, ResponseMessage> = new Map();
  private static messageCounter = 0;
  private voittaApiKey: string;
  private openaiApiKey: string;
  private anthropicApiKey: string;
  private geminiApiKey: string;
  private selectedProvider: string;
  private username: string;
  private chatContainer: HTMLDivElement;
  private maxMessages: number;
  private currentChatID = 'temp-session';
  public onChatCreated?: (chatId: string) => void;

  /**
   * Create a new MessageHandler
   * @param voittaApiKey Voitta API key for authentication
   * @param openaiApiKey OpenAI API key for authentication
   * @param anthropicApiKey Anthropic API key for authentication
   * @param geminiApiKey Gemini API key for authentication
   * @param selectedProvider Selected AI provider
   * @param username Username for the current user
   * @param chatContainer DOM element to display messages
   * @param maxMessages Maximum number of messages to keep
   */
  constructor(voittaApiKey: string, openaiApiKey: string, anthropicApiKey: string, geminiApiKey: string, selectedProvider: string, username: string, chatContainer: HTMLDivElement, maxMessages: number = 100) {
    this.voittaApiKey = voittaApiKey;
    this.openaiApiKey = openaiApiKey;
    this.anthropicApiKey = anthropicApiKey;
    this.geminiApiKey = geminiApiKey;
    this.selectedProvider = selectedProvider;
    this.username = username;
    this.chatContainer = chatContainer;
    this.maxMessages = maxMessages;

  }



  /**
   * Update the settings for the message handler
   * @param voittaApiKey New Voitta API key
   * @param openaiApiKey New OpenAI API key
   * @param anthropicApiKey New Anthropic API key
   * @param geminiApiKey New Gemini API key
   * @param selectedProvider New selected provider
   * @param username New username
   * @param maxMessages New maximum messages
   */
  public updateSettings(voittaApiKey: string, openaiApiKey: string, anthropicApiKey: string, geminiApiKey: string, selectedProvider: string, username: string, maxMessages: number): void {
    this.voittaApiKey = voittaApiKey;
    this.openaiApiKey = openaiApiKey;
    this.anthropicApiKey = anthropicApiKey;
    this.geminiApiKey = geminiApiKey;
    this.selectedProvider = selectedProvider;
    this.username = username;
    this.maxMessages = maxMessages;
  }

  /**
   * Set the current chat ID
   * @param chatID The chat ID to set
   */
  public setCurrentChatID(chatID: string): void {
    this.currentChatID = chatID;
  }

  /**
   * Get the current chat ID
   * @returns The current chat ID
   */
  public getCurrentChatID(): string {
    return this.currentChatID;
  }

  /**
   * Generate a unique message ID
   */
  public generateMessageId(prefix: string = ""): string {
    const timestamp = Date.now();
    const counter = MessageHandler.messageCounter++;
    const messageId = `${prefix}-msg-${timestamp}-${counter}`;
    return messageId;
  }

  /**
   * Find a message by ID
   * @param id The message ID to find
   */
  public findMessageById(id: string): ResponseMessage | undefined {
    return this.messageMap.get(id);
  }

  /**
   * Add a message to the chat
   * @param role The role of the message sender ('user', 'assistant', or 'action')
   * @param content The message content
   * @param id Optional message ID (generated if not provided)
   * @returns The created ResponseMessage
   */
  public addMessage(role: 'user' | 'assistant' | 'action', content: string, id?: string): ResponseMessage {
    // Generate ID if not provided
    const messageId = id || this.generateMessageId();

    // Create a new ResponseMessage
    const message = new ResponseMessage(messageId, role, content);

    // Add to messages array
    this.messages.push(message);

    // Add to message map
    this.messageMap.set(messageId, message);

    // Add to DOM
    this.chatContainer.appendChild(message.getElement());

    // Scroll to bottom
    this.chatContainer.scrollTop = this.chatContainer.scrollHeight;

    // Limit the number of messages if needed
    this.limitMessages();

    return message;
  }

  /**
   * Limit the number of messages based on settings
   */
  public limitMessages(): void {
    if (this.messages.length > this.maxMessages) {
      // Remove excess messages
      const excessCount = this.messages.length - this.maxMessages;
      const removedMessages = this.messages.splice(0, excessCount);

      // Remove from DOM and message map
      for (const message of removedMessages) {
        this.chatContainer.removeChild(message.getElement());
        this.messageMap.delete(message.id);
      }
    }
  }

  /**
   * Clear all messages from the chat area
   */
  public async clearMessages(): Promise<void> {
    // Create a copy of the messages array to safely iterate through
    const messagesToRemove = [...this.messages];

    // Clear the original arrays first
    this.messages = [];

    // Now safely remove each message from the DOM and the map
    for (const message of messagesToRemove) {
      try {
        if (this.chatContainer.contains(message.getElement())) {
          this.chatContainer.removeChild(message.getElement());
        }
        this.messageMap.delete(message.id);
      } catch (error) {
        console.error('Error removing message:', error);
      }
    }

    // Clear the message map as a final safety measure
    this.messageMap.clear();
  }

  /**
   * Load messages from the server
   */
  public async loadMessages(): Promise<void> {
    const call_id = this.generateMessageId();
    const loadMessage: ILoadMessagesRequest = {
      method: 'loadMessages',
      username: this.username,
      chatID: this.currentChatID,
      call_id: call_id,
      message_type: 'request'
    };

    try {
      const response = await callPython(loadMessage);

      if (!response.value || !Array.isArray(response.value)) {
        console.warn('Invalid response format for loadMessages:', response);
        return;
      }

      for (let i = 0; i < response.value.length; i++) {
        const message = response.value[i];

        switch (message.role) {
          case "user":
            if (typeof message.content === 'string' || message.content instanceof String) {
              this.addMessage('user', message.content);
            }
            break;

          case "assistant":
            if (typeof message.content === 'string' || message.content instanceof String) {
              this.addMessage('assistant', String(message.content));
            } else if (message.content && Array.isArray(message.content)) {
              // Handle complex content (tool calls, etc.)
              for (let j = 0; j < message.content.length; j++) {
                const contentItem = message.content[j];
                if (contentItem.type === "tool_use" && contentItem.name) {
                  this.addMessage('action', `🔧 ${contentItem.name}`);
                } else if (contentItem.type === "text" && contentItem.text) {
                  this.addMessage('assistant', contentItem.text);
                }
              }
            }
            break;

          default:
          // Skip unknown message types
        }
      }

    } catch (error) {
      console.error('Error loading messages:', error);
      throw error;
    }
  }

  /**
   * Create a new chat session with settings
   * @param provider The AI provider to use for this chat (optional, defaults to 'openai')
   * @returns The new chat ID returned by the server
   */
  public async createNewChat(provider?: string): Promise<string> {
    // First clear all local messages
    await this.clearMessages();

    // Convert UI provider names to protocol values
    let protocolProvider: 'gemini' | 'openai' | 'anthropic' = 'openai';
    if (provider) {
      switch (provider.toLowerCase()) {
        case 'openai':
          protocolProvider = 'openai';
          break;
        case 'anthropic':
          protocolProvider = 'anthropic';
          break;
        case 'gemini':
          protocolProvider = 'gemini';
          break;
        default:
          console.warn(`Unknown provider: ${provider}, defaulting to openai`);
          protocolProvider = 'openai';
      }
    }

    const call_id = this.generateMessageId();
    const createChatMessage: ICreateNewChatRequest = {
      method: 'createNewChat',
      username: this.username,
      call_id: call_id,
      message_type: 'request',
      provider: protocolProvider,
      // Use placeholder keys for chat creation - no real keys needed
      api_key: '--key--',
      openai_api_key: '--key--',
      anthropic_api_key: '--key--',
      gemini_api_key: '--key--'
    };

    console.log('Sending createNewChat request:', createChatMessage);
    const response = await callPython(createChatMessage);
    console.log('Received createNewChat response:', response);

    // Check if the response is an error
    if ('error_type' in response || (typeof response.value === 'string' && !response.value.includes('chatID'))) {
      const errorResponse = response as IErrorResponse;
      const errorMessage = errorResponse.value || 'Unknown error occurred while creating chat';
      console.error('Error creating new chat:', errorResponse);
      throw new Error(`Failed to create new chat: ${errorMessage}`);
    }

    // Extract the chatID from the successful response
    const successResponse = response as ICreateNewChatResponse;
    const newChatID = successResponse.value?.chatID;
    if (!newChatID) {
      console.error('Invalid server response for createNewChat:', response);
      throw new Error(`Server did not return a valid chatID. Response: ${JSON.stringify(response)}`);
    }

    console.log('Successfully created new chat with ID:', newChatID);

    // Update our current chat ID to the server-generated one
    this.currentChatID = newChatID;

    return newChatID;
  }

  /**
   * Send a message to the server
   * @param content Message content
   * @param mode Message mode (Talk, Plan, Act)
   * @param selectedProvider Selected AI provider from dropdown
   * @returns The response message
   */
  public async sendMessage(content: string, mode: string, selectedProvider?: string): Promise<ResponseMessage> {
    // Check if we're in a temporary session and should create a new chat
    if (this.currentChatID === 'temp-session') {
      // Show a message indicating we're starting a new chat
      const infoMessageId = this.generateMessageId();
      this.addMessage('assistant', '💡 **Starting a new chat session** - Your conversation will be saved automatically.', infoMessageId);

      // Create a new chat session and get the server-generated chatID
      const newChatID = await this.createNewChat();

      // Notify the parent widget about the new chat
      if (this.onChatCreated) {
        this.onChatCreated(newChatID);
      }
    }

    // Generate unique IDs for this message
    const userMessageId = this.generateMessageId();
    const messageId = this.generateMessageId();

    const opened_tabs = await get_opened_tabs();
    const current_notebook = await functions["listCells"].func()

    this.addMessage('user', content, userMessageId);

    // Create a placeholder response message with the same ID
    const responseMessage = this.addMessage('assistant', 'Waiting for response...', messageId);

    const ws = get_ws();

    var stop_detected = false;

    // Send message to WebSocket server if connected
    if (ws && ws.readyState === WebSocket.OPEN) {
      try {
        // Get model selections from settings
        const settings = (window as any).escobarCurrentSettings as any;
        const primaryModel = settings?.primaryModel || 'undefined';
        const secondaryProvider = settings?.secondaryProvider || 'undefined';
        const imageParseProvider = settings?.imageParseProvider || 'undefined';

        const userMessage: IUserMessageRequest = {
          method: 'userMessage',
          username: this.username,
          chatID: this.currentChatID,
          call_id: messageId,
          message_type: 'request',
          user_message: content,
          opened_tabs: opened_tabs,
          current_notebook: current_notebook,
          mode: mode,
          api_key: this.voittaApiKey,
          openai_api_key: this.openaiApiKey,
          anthropic_api_key: this.anthropicApiKey,
          gemini_api_key: this.geminiApiKey,
          selected_provider: primaryModel, // Primary model
          secondary_provider: secondaryProvider, // Secondary model
          image_parse_provider: imageParseProvider // Image parsing model
        };

        const response = await callPython(userMessage, DEFAULT_TIMEOUT, true, true); // Show stop button for user messages
        this.handlePythonResponse(response, responseMessage);

      } catch (error) {
        if (error.stop != undefined) {
          stop_detected = true;
          stopped_messages[messageId] = true;
          responseMessage.setContent('Interrupted by the user');
        } else {
          responseMessage.setContent('Error sending message to server');
        }
      }
    } else {
      // Fallback to echo response if not connected
      setTimeout(() => {
        responseMessage.setContent(`Echo: ${content} (WebSocket not connected)`);
      }, 500);
    }

    if (stop_detected) {
      const stopMessage: IUserStopRequest = {
        method: 'userStop',
        username: this.username,
        chatID: this.currentChatID,
        call_id: messageId,
        message_type: 'request'
      };
      const response = await callPython(stopMessage, 0, false);
    }

    return responseMessage;
  }

  /**
   * Handle response from Python server
   * @param response Response data
   * @param responseMsg Response message to update
   */
  public handlePythonResponse(response: any, responseMsg?: ResponseMessage): void {
    try {
      let responseText: string;

      var value = response.value;

      if (typeof value === 'string') {
        responseText = value;
      } else if (value && typeof value === 'object') {
        responseText = JSON.stringify(value);
      } else {
        responseText = 'Received empty response from server';
      }

      // Update the response message with the content
      if (responseMsg) {
        responseMsg.setContent(responseText);
      }
    } catch (error) {
      console.error('Error handling Python response:', error);
      if (responseMsg) {
        responseMsg.setContent('Error: Failed to process server response');
      }
    }
  }

  /**
   * Save settings to the server
   * @param settings The settings to save (excluding serverUrl)
   */
  public async saveSettingsToServer(settings: Partial<IChatSettings>): Promise<void> {
    const call_id = this.generateMessageId();
    const saveSettingsMessage: ISaveSettingsRequest = {
      method: 'saveSettings',
      username: this.username,
      call_id: call_id,
      message_type: 'request',
      openai_api_key: settings.openaiApiKey,
      gemini_api_key: settings.geminiApiKey,
      anthropic_api_key: settings.anthropicApiKey,
      voitta_api_key: settings.voittaApiKey,
      max_messages: settings.maxMessages,
      proxy_port: settings.proxyPort,
      primary_model: settings.primaryModel,
      secondary_provider: settings.secondaryProvider,
      image_parse_provider: settings.imageParseProvider
    };

    const response = await callPython(saveSettingsMessage);

    if ('error_type' in response) {
      const errorResponse = response as IErrorResponse;
      throw new Error(`Failed to save settings: ${errorResponse.value}`);
    }

    console.log('Settings saved to server successfully');
  }

  /**
   * Retrieve settings from the server
   * @returns The settings retrieved from the server
   */
  public async retrieveSettingsFromServer(): Promise<Partial<IChatSettings>> {
    const call_id = this.generateMessageId();
    const retrieveSettingsMessage: IRetrieveSettingsRequest = {
      method: 'retrieveSettings',
      username: this.username,
      call_id: call_id,
      message_type: 'request'
    };

    const response = await callPython(retrieveSettingsMessage);

    if ('error_type' in response) {
      const errorResponse = response as IErrorResponse;
      throw new Error(`Failed to retrieve settings: ${errorResponse.value}`);
    }

    const settingsResponse = response as IRetrieveSettingsResponse;

    return {
      openaiApiKey: settingsResponse.openai_api_key || '',
      geminiApiKey: settingsResponse.gemini_api_key || '',
      anthropicApiKey: settingsResponse.anthropic_api_key || '',
      voittaApiKey: settingsResponse.voitta_api_key || '',
      maxMessages: settingsResponse.max_messages || 100,
      proxyPort: settingsResponse.proxy_port || 3000,
      primaryModel: settingsResponse.primary_model,
      secondaryProvider: settingsResponse.secondary_provider,
      imageParseProvider: settingsResponse.image_parse_provider
    };
  }

  /**
   * Get all messages
   */
  public getMessages(): ResponseMessage[] {
    return [...this.messages];
  }
}
