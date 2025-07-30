export var voittal_call_log = {}
export const stopped_messages = {}

export function generateUUID() {
  const timestamp = Date.now().toString(16);
  return 'M-xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  }) + '-' + timestamp;
}

// Interface for pending requests
interface PendingRequest {
  resolve: (value: any) => void;
  reject: (reason?: any) => void;
  timeout: any;
}

// Map to store pending requests by call_id
const pendingRequests: Map<string, PendingRequest> = new Map();

// Default timeout for requests in milliseconds
const DEFAULT_TIMEOUT = 1000 * 60 * 60;

// Function registry type definitions
interface FunctionRegistryEntry {
  fn: Function;
  obj: object | null;
  isAsync: boolean;
  returns: boolean;
}

type FunctionRegistry = {
  [key: string]: FunctionRegistryEntry;
};

// Function registry to store registered functions
const registry: FunctionRegistry = {};

let ws: WebSocket | null = null;
let isConnected = false;
export var connectionPromise: Promise<void> | null = null;

// Custom events for callPython execution state
export const PYTHON_CALL_EVENTS = {
  START: 'escobar-python-call-start',
  END: 'escobar-python-call-end',
  STOP: 'escobar-stop-event'
};

export function get_ws() {
  return ws;
}

/**
 * Resolve WebSocket URL for JupyterHub environment
 * @param url - The URL to resolve (can be relative or absolute)
 * @returns Resolved URL with proper JupyterHub user path if needed
 */
function resolveWebSocketURL(url: string): string {
  console.log(`##>>## Original URL: ${url}`);

  // If it's already an absolute URL (starts with ws:// or wss://), return as-is
  if (url.startsWith('ws://') || url.startsWith('wss://')) {
    console.log(`##>>## Absolute URL, using as-is: ${url}`);
    return url;
  }

  // Check if we're in JupyterHub environment
  const currentPath = window.location.pathname;
  const hubUserMatch = currentPath.match(/^\/user\/([^\/]+)\//);

  if (hubUserMatch) {
    // In JupyterHub - construct user-specific URL
    const userPath = hubUserMatch[0]; // "/user/roman.semein@gmail.com/"
    const resolvedPath = userPath.slice(0, -1) + url; // "/user/roman.semein@gmail.com/ws"

    // Construct full WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const fullURL = `${protocol}//${host}${resolvedPath}`;

    console.log(`##>>## JupyterHub detected, resolved URL: ${fullURL}`);
    console.log(`##>>## User path: ${userPath}`);
    console.log(`##>>## Resolved path: ${resolvedPath}`);

    return fullURL;
  } else {
    // Standalone JupyterLab - construct normal URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const fullURL = `${protocol}//${host}${url}`;

    console.log(`##>>## Standalone JupyterLab, resolved URL: ${fullURL}`);

    return fullURL;
  }
}

let stopEventListenerAdded = false;
let stopRequested = false;

/**
 * Initializes the WebSocket connection to the Python server.
 * If a connection attempt is already in progress or the connection is active, it returns that promise.
 *
 * @param url - The WebSocket URL (default: "ws://127.0.0.1:8777/ws")
 * @returns A Promise that resolves when the connection is successfully established.
 */
export function initPythonBridge(url: string = "ws://127.0.0.1:8777/ws"): Promise<void> {
  console.log("Entering initPythonBridge");
  // If already connected, return a resolved promise.
  if (ws && isConnected && ws.readyState === WebSocket.OPEN) {
    return Promise.resolve();
  }

  if (!stopEventListenerAdded) {
    window.addEventListener(PYTHON_CALL_EVENTS.STOP, handleStopEvent);
    stopEventListenerAdded = true;
  }


  // If a connection attempt is in progress, return that promise.

  /*
  if (connectionPromise) {
    return connectionPromise;
  }
  */

  connectionPromise = new Promise<void>((resolve, reject) => {
    // Always resolve the URL for JupyterHub environment (never connect directly to bonnieUrl)
    let resolvedURL = resolveWebSocketURL(url);

    // Check if we need to add bonnieUrl as query parameter for backend proxy
    const currentSettings = (window as any).escobarCurrentSettings;
    if (currentSettings?.bonnieUrl && url.startsWith('/')) {
      console.log(`>>> Adding bonnieUrl as proxy target: ${currentSettings.bonnieUrl}`);

      // Add bonnieUrl as query parameter for backend to use as proxy target
      const separator = resolvedURL.includes('?') ? '&' : '?';
      resolvedURL += `${separator}bonnie_url=${encodeURIComponent(currentSettings.bonnieUrl)}`;

      console.log(`>>> Final URL with bonnieUrl parameter: ${resolvedURL}`);
    } else {
      console.log(">>> No bonnieUrl parameter needed");
    }

    console.log(">>> Connecting to " + resolvedURL);
    ws = new WebSocket(resolvedURL);

    ws.addEventListener('open', (event) => {
      isConnected = true;
      // Connection established successfully
      resolve();
      connectionPromise = null;
    });


    ws.addEventListener('error', (event) => {

      console.error("Error connecting to Python server:", event);
      reject(event);
      connectionPromise = null;
    });

    ws.addEventListener('close', (event) => {
      isConnected = false;
      // Python server connection closed
    });

    ws.addEventListener('message', async (event: any) => {
      //const messageStr = typeof data === 'string' ? data : data.toString('utf-8');
      const messageStr = event.data;
      try {
        var jsonData: any = messageStr;
        if (typeof messageStr === 'string') {
          //console.log("parsing:", typeof messageStr, messageStr);
          jsonData = JSON.parse(messageStr);
        }

        let message_type = jsonData.message_type;

        if (message_type === "response") {
          // Check if this is a response to a pending request

          const call_id = jsonData.call_id;
          const finish_reason = jsonData.finish_reason;
          console.log(`Finish Reason: ${finish_reason}`);

          // Received response for call_id

          if (call_id && pendingRequests.has(call_id)) {
            // Found pending request for this call_id
            // Get the pending request
            const pendingRequest = pendingRequests.get(call_id)!;

            // Check if this is a final response or intermediate response
            const isFinalResponse = !finish_reason || finish_reason !== "tool_calls";

            if (isFinalResponse) {
              // Final response - clean up and resolve
              clearTimeout(pendingRequest.timeout);
              pendingRequests.delete(call_id);

              // Extract the response data
              const responseData = jsonData.data || jsonData.response || jsonData;

              // Pass finish_reason to the resolve callback for stop button control
              pendingRequest.resolve({ ...responseData, finish_reason });
            } else {
              // Intermediate response with tool_calls - handle but don't resolve yet
              console.log(`Intermediate response with finish_reason: ${finish_reason} - keeping request pending`);

              // TODO: Handle intermediate responses - could call a separate handler here
              // For now, we just log and keep the request pending for the final response
            }
          } else if (registry['handleResponse']) {
            // Using registered handleResponse function
            // Extract the response data
            const responseData = {
              ...(jsonData.data || jsonData.response || jsonData),
              function: "handleResponse",
              params: { value: jsonData.value || "-- value not found in response --" }
            };
            // Call the registered response handler
            callRegisteredFunction(responseData);
          } else {
            console.warn("Received response with no matching request or handler");
          }
        } else if (message_type === "request") {
          let function_name = jsonData.function;
          let msg_call_id = jsonData.__msg_call_id__;
          let call_id = jsonData.call_id;
          if (stopped_messages[msg_call_id] != undefined) {
            // Message ignored because it was stopped
            const entry = registry[function_name];
            if (entry.returns) {
              bridgeReturn(call_id, "__stopped__")
            }
            return;
          }

          let params = jsonData.params;

          //console.log(`<r> ${function_name}  ${jsonData.call_id} ${params.id} ${params.msg_call_id}`)

          // Check if the function exists in the registry
          if (!registry[function_name]) {
            console.error(`Function "${function_name}" not found in registry`);
            return;
          }

          let is_async = registry[function_name].isAsync;
          if (is_async) {
            let result = await callRegisteredFunctionAsync(jsonData);
          } else {
            let result = callRegisteredFunction(jsonData);
          }
        }
      } catch (error) {
        console.error("Error parsing JSON message:", error);
      }
    });
  });

  return connectionPromise;
}


function handleStopEvent() {
  stopRequested = true;

  // Clear all pending requests
  for (const [call_id, request] of pendingRequests.entries()) {
    clearTimeout(request.timeout);
    const error = new Error('Operation stopped by user');
    (error as any).stop = true;
    request.reject(error);
    pendingRequests.delete(call_id);
  }

  // Reset the flag after a short delay
  setTimeout(() => {
    stopRequested = false;
  }, 100);
}



/**
 * Sends a message to the Python server and waits for a response.
 * If the connection is not yet established, it attempts to initialize it.
 * Dispatches events when the call starts and ends to allow UI elements to respond.
 *
 * @param message - The typed message object to send.
 * @param timeoutMs - Optional timeout in milliseconds (default: 30000)
 * @param waitForResponse - Whether to wait for a response
 * @param showStopButton - Whether to show the stop button for this operation (default: false)
 * @returns A Promise that resolves with the response data when received.
 */
export async function callPython(message: import('../types/protocol').ProtocolMessage,
  timeoutMs: number = DEFAULT_TIMEOUT,
  waitForResponse: boolean = true,
  showStopButton: boolean = false
): Promise<any> {
  // Only dispatch start event for operations that should show the stop button
  if (showStopButton) {
    window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.START));
  }

  if (!ws || !isConnected || ws.readyState !== WebSocket.OPEN) {
    // Pass
  }

  // Generate a unique call ID
  const call_id = generateUUID();
  let user_id = '';
  let session_id = '';

  // Get username from global variable set by the chat widget
  if ((window as any).escobarUsername) {
    user_id = (window as any).escobarUsername;
  } else {
    // Fallback to default if global variable not available
    console.warn('Username not available from global variable, using default');
    user_id = 'VoittaDefaultUser';
  }

  // Get session_id from the message if it's a chat-related message
  if ('chatID' in message) {
    session_id = (message as any).chatID;
  } else {
    // Fallback to a default session ID
    session_id = 'temp-session';
  }

  // Enrich the message with metadata - ensure user_id and session_id are always sent
  const enrichedMessage = {
    ...message,
    user_id: user_id,
    session_id: session_id,
    call_id: call_id,
    msg_call_id: message.call_id || call_id,
    message_type: 'request' as const
  };

  // Send directly - no double JSON encoding!
  const payload = JSON.stringify(enrichedMessage);

  // Return a promise that resolves when the response is received
  return new Promise((resolve, reject) => {
    // If the connection is now open, send the message.
    if (ws && isConnected && ws.readyState === WebSocket.OPEN) {
      // Set up a timeout to reject the promise if no response is received
      const timeout = setTimeout(() => {
        // Remove from pending requests
        pendingRequests.delete(call_id);
        // Dispatch end event on timeout
        window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
        reject(new Error(`Request timed out after ${timeoutMs}ms`));
      }, timeoutMs);

      // Store the promise callbacks and timeout in the pending requests map

      if (waitForResponse) {
        pendingRequests.set(call_id, {
          resolve: (value: any) => {
            // Only dispatch END event if finish_reason is NOT "tool_calls"
            // Hide stop button when: finish_reason is undefined/null OR finish_reason !== "tool_calls"
            const shouldHideStopButton = !value.finish_reason || value.finish_reason !== "tool_calls";

            if (shouldHideStopButton) {
              window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
            }
            // TODO: Handle multiple responses in sequence - may need to track conversation state
            // TODO: Consider implementing a conversation state machine for complex tool call flows
            // TODO: May need to differentiate between intermediate and final responses

            resolve(value);
          },
          reject: (reason?: any) => {
            // Always hide stop button on errors
            window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
            reject(reason);
          },
          timeout
        });
      } else {
        pendingRequests.delete(call_id);
        window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
      }

      // Send the message
      ws.send(payload);
    } else {
      // Dispatch end event on immediate rejection
      window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
      reject(new Error("Cannot send message. WebSocket is not connected after attempting to reconnect."));
    }
  });
}





/**
 * Registers a function in the registry to be called later.
 * 
 * @param name - The name to register the function under
 * @param isAsync - Whether the function is asynchronous
 * @param fn - The function to register
 */
export function registerFunction(name: string, isAsync: boolean,
  fn: Function, obj: object | null = null, returns: boolean = false): void {

  if (registry[name]) {
    console.warn(`Function "${name}" already exists in the registry. Overwriting`);
  }

  registry[name] = {
    fn,
    obj,
    isAsync,
    returns
  };
}


export function bridgeReturn(call_id: string, value: any) {
  // Returning value to bridge

  const payload = {
    call_id: call_id,
    message_type: "response"
  }

  if (typeof value == "string") {
    payload["value"] = value;
  } else {
    payload["binary_value"] = value;
  }

  if (ws !== null) {
    if (typeof payload == "string") {
      ws.send(payload);
    } else {
      ws.send(JSON.stringify(payload));
    }
  } else {
    console.error("WebSocket is null. Cannot send message.");
  }
}


/**
 * Calls a registered function by name with the provided arguments.
 * 
 * @param name - The name of the registered function to call
 * @param args - The arguments to pass to the function
 * @returns The result of the function call, or a Promise if the function is async
 * @throws Error if the function is not found in the registry
 */

export async function callRegisteredFunctionAsync(jsonData: any): Promise<any> {
  const call_id = jsonData["call_id"] || "";

  const function_name = jsonData["function"] || "";
  var params = jsonData["params"] || {};
  const partial = params["partial"] || false;

  var param = params["param"] || {};
  if (partial) {
    param = params["text"] || "";
  }

  const entry = registry[function_name];

  if (!entry) {
    throw new Error(`Function "${function_name}" not found in registry`);
  }

  try {
    var result;
    if ((function_name == "diffToFile") || (function_name == "writeToFile") ||
      (function_name == "insertExecuteCell") || (function_name == "editExecuteCell")
    ) {
      result = await entry.fn.call(entry.obj, params, false, call_id);
    } else {
      result = await entry.fn.call(entry.obj, params);
    }
    if (entry.returns) {
      bridgeReturn(call_id, result);
    }
  } catch (error) {
    console.error(`Error calling function "${function_name}":`, error);
    throw error;
  }
  voittal_call_log[call_id] = true;
}


export function callRegisteredFunction(jsonData: any): any {
  const call_id = jsonData["call_id"] || "";
  const function_name = jsonData["function"] || "";
  var params = jsonData["params"] || {};
  const partial = params["partial"] || false;
  const msg_call_id = params["msg_call_id"] // effectively references the single query session

  if ((function_name != "tool_say") && (function_name != "say")) {
    const ours = true;
  }

  var param = params["param"] || {};
  if (partial) {
    param = params["text"] || "";
  }

  const entry = registry[function_name];

  if (!entry) {
    throw new Error(`Function "${function_name}" not found in registry`);
  }
  try {
    let result = entry.fn.call(entry.obj, params);
    if (entry.returns) {
      bridgeReturn(call_id, result);
    }
  } catch (error) {
    console.error(`Error calling function "${function_name}":`, error);
    throw error;
  }
}

/**
 * Gets the registry of functions.
 * 
 * @returns The function registry with an added call method for each function
 */
export function getFunctionRegistry(): FunctionRegistry & {
  [key: string]: FunctionRegistryEntry & {
    call: (name: string, args: any) => any
  }
} {
  // Create a proxy to add a 'call' method to each registry entry
  return new Proxy(registry, {
    get(target, prop) {
      if (typeof prop === 'string' && prop in target) {
        // Add a call method to the registry entry
        const entry = target[prop];
        return {
          ...entry,
          call: (name: string, args: any) => {
            try {
              return entry.fn.call(null, args);
            } catch (error) {
              console.error(`Error calling function "${name}":`, error);
              throw error;
            }
          }
        };
      }
      return Reflect.get(target, prop);
    }
  }) as any;
}
