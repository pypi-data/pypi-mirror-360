import json
import os
import re
import asyncio
import websockets
import ssl
import logging
import time
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join
import tornado
import tornado.web
import tornado.websocket
import aiohttp
from traitlets.config import LoggingConfigurable
import mimetypes

# Default proxy port
DEFAULT_PROXY_PORT = 3000

class ProxyHandler(JupyterHandler):
    """
    Handler for /proxy endpoint.
    Proxies requests to http://localhost:<port>/<path>
    """
    async def _proxy_request(self, path_with_port, method='GET', body=None):
        # Extract port and path from the URL
        # Expected format: <port>/<path>
        match = re.match(r'^(\d+)(?:/(.*))?$', path_with_port)
        
        if match:
            port = match.group(1)
            path = match.group(2) or ''
            
            # Ensure port is an integer
            try:
                port = int(port)
            except (ValueError, TypeError):
                self.set_status(400)
                self.finish({"error": f"Invalid port: {port}"})
                return
        else:
            # If no port is specified in the URL, use the default port
            # and treat the entire path_with_port as the path
            port = DEFAULT_PROXY_PORT
            path = path_with_port
        
        # Log the port and path for debugging
        self.log.info(f"Proxying request to port {port}, path: {path}")
        
        # Construct the target URL with query parameters
        target_url = f"http://localhost:{port}/{path}"
        if self.request.query:
            target_url += f"?{self.request.query}"
        
        try:
            # Copy request headers
            headers = dict(self.request.headers)
            # Remove headers that might cause issues
            headers.pop('Host', None)
            headers.pop('Content-Length', None)
            
            # Make the request to the target URL with the same method
            async with aiohttp.ClientSession() as session:
                method_fn = getattr(session, method.lower())
                async with method_fn(target_url, headers=headers, data=body) as response:
                    # Log response details for debugging
                    self.log.info(f"Response status: {response.status}")
                    self.log.info(f"Response headers: {response.headers}")
                    
                    # Set the status code
                    self.set_status(response.status)
                    
                    # Get the content type
                    content_type = response.headers.get("Content-Type", "text/plain")
                    self.log.info(f"Content-Type: {content_type}")
                    
                    # Special handling for HTML content
                    if 'text/html' in content_type:
                        # For HTML content, we need to be extra careful
                        content = await response.text()
                        
                        # Clear any automatically added headers
                        self._headers = tornado.httputil.HTTPHeaders()
                        
                        # Set the content type explicitly
                        self.set_header("Content-Type", "text/html; charset=UTF-8")
                        
                        # Copy important headers from the original response
                        for header_name, header_value in response.headers.items():
                            if header_name.lower() in ('cache-control', 'etag', 'last-modified'):
                                self.set_header(header_name, header_value)
                        
                        # Write the content directly
                        self.write(content)
                        await self.finish()
                        return
                    
                    # For all other content types, copy all headers from the original response
                    for header_name, header_value in response.headers.items():
                        # Skip headers that would cause issues
                        if header_name.lower() not in ('content-length', 'transfer-encoding', 'content-encoding', 'connection'):
                            self.set_header(header_name, header_value)
                    
                    # Always set the Content-Type header explicitly
                    self.set_header("Content-Type", content_type)
                    
                    # Handle content based on content type
                    if 'application/json' in content_type:
                        # For JSON, parse and re-serialize to ensure proper formatting
                        data = await response.json()
                        self.write(json.dumps(data))
                    elif 'text/' in content_type or 'application/javascript' in content_type or 'application/xml' in content_type:
                        # For other text-based content
                        content = await response.text()
                        self.write(content)
                    else:
                        # For binary content
                        content = await response.read()
                        self.write(content)
                    
                    # Finish the response
                    await self.finish()
        except Exception as e:
            self.log.error(f"Proxy error: {str(e)}")
            self.set_status(500)
            self.finish({"error": str(e)})

    async def get(self, path_with_port):
        await self._proxy_request(path_with_port, 'GET')
    
    async def post(self, path_with_port):
        await self._proxy_request(path_with_port, 'POST', self.request.body)
    
    async def put(self, path_with_port):
        await self._proxy_request(path_with_port, 'PUT', self.request.body)
    
    async def delete(self, path_with_port):
        await self._proxy_request(path_with_port, 'DELETE')
    
    async def patch(self, path_with_port):
        await self._proxy_request(path_with_port, 'PATCH', self.request.body)
    
    async def head(self, path_with_port):
        await self._proxy_request(path_with_port, 'HEAD')
    
    async def options(self, path_with_port):
        await self._proxy_request(path_with_port, 'OPTIONS')


class WebSocketProxyHandler(tornado.websocket.WebSocketHandler):
    """
    WebSocket proxy handler that forwards connections from /ws to target server
    """
    
    def __init__(self, *args, **kwargs):
        print(f"[ESCOBAR-WS] WebSocketProxyHandler.__init__ called")
        super().__init__(*args, **kwargs)
        self.target_ws = None
        
        # Debug environment information
        print(f"[ESCOBAR-WS] Environment WEBSOCKET_PROXY_TARGET: {os.getenv('WEBSOCKET_PROXY_TARGET', 'NOT_SET')}")
        print(f"[ESCOBAR-WS] Running in container: {os.path.exists('/.dockerenv')}")
        try:
            print(f"[ESCOBAR-WS] Hostname: {os.uname().nodename}")
        except:
            print(f"[ESCOBAR-WS] Could not get hostname")
        
        # Read target URL from environment variable
        self.target_url = os.getenv('WEBSOCKET_PROXY_TARGET', 'ws://localhost:8777/ws')
        print(f"[ESCOBAR-WS] Target URL will be: {self.target_url}")
        
        # Debug all WebSocket-related environment variables
        websocket_env_vars = [(k, v) for k, v in os.environ.items() if 'WEBSOCKET' in k.upper()]
        print(f"[ESCOBAR-WS] All WEBSOCKET environment vars: {websocket_env_vars}")
        
        self.is_closing = False
        
    def check_origin(self, origin):
        """Allow connections from any origin (adjust as needed for security)"""
        return True
    
    async def open(self):
        """Called when websocket connection is opened"""
        start_time = time.time()
        print(f"[ESCOBAR-WS] === CLIENT CONNECTION OPENED ===")
        print(f"[ESCOBAR-WS] Connection attempt started at {start_time}")
        print(f"[ESCOBAR-WS] Client origin: {self.request.headers.get('Origin', 'NO_ORIGIN')}")
        print(f"[ESCOBAR-WS] Client remote IP: {self.request.remote_ip}")
        print(f"[ESCOBAR-WS] Request headers: {dict(self.request.headers)}")
        print(f"[ESCOBAR-WS] Attempting to connect to target: {self.target_url}")
        
        logging.info(f"WebSocket connection opened, proxying to {self.target_url}")
        
        try:
            # Establish connection to target websocket server
            # Copy relevant headers from the original request
            headers = {}
            
            # Forward authentication headers if present
            if 'Authorization' in self.request.headers:
                headers['Authorization'] = self.request.headers['Authorization']
                print(f"[ESCOBAR-WS] Forwarding Authorization header")
            if 'Cookie' in self.request.headers:
                headers['Cookie'] = self.request.headers['Cookie']
                print(f"[ESCOBAR-WS] Forwarding Cookie header")
            
            print(f"[ESCOBAR-WS] Headers to forward: {headers}")
            
            # Determine if we need SSL based on URL scheme
            use_ssl = self.target_url.startswith('wss://')
            ssl_context = ssl.create_default_context() if use_ssl else None
            print(f"[ESCOBAR-WS] Using SSL: {use_ssl}")
            
            print(f"[ESCOBAR-WS] Attempting websockets.connect() to {self.target_url}")
            
            # Connect to target websocket (works with both ws:// and wss://)
            self.target_ws = await websockets.connect(
                self.target_url,
                additional_headers=headers,
                ssl=ssl_context,
                ping_interval=20,
                ping_timeout=10
            )
            
            end_time = time.time()
            print(f"[ESCOBAR-WS] Successfully connected to target server in {end_time - start_time:.2f} seconds")
            
            # Start listening for messages from target server
            print(f"[ESCOBAR-WS] Starting message forwarding task")
            asyncio.create_task(self._forward_from_target())
            
            print(f"[ESCOBAR-WS] === CONNECTION SETUP COMPLETE ===")
            logging.info(f"Successfully connected to target websocket server: {self.target_url}")
            
        except Exception as e:
            end_time = time.time()
            print(f"[ESCOBAR-WS] === CONNECTION FAILED ===")
            print(f"[ESCOBAR-WS] Connection failed after {end_time - start_time:.2f} seconds")
            print(f"[ESCOBAR-WS] Error: {str(e)}")
            print(f"[ESCOBAR-WS] Error type: {type(e).__name__}")
            print(f"[ESCOBAR-WS] Target URL: {self.target_url}")
            if hasattr(e, 'errno'):
                print(f"[ESCOBAR-WS] Errno: {e.errno}")
            if hasattr(e, 'strerror'):
                print(f"[ESCOBAR-WS] Strerror: {e.strerror}")
            print(f"[ESCOBAR-WS] === END CONNECTION FAILED ===")
            
            logging.error(f"Failed to connect to target websocket {self.target_url}: {str(e)}")
            self.close(code=1011, reason="Failed to connect to target server")
    
    async def on_message(self, message):
        """Called when a message is received from the client"""
        print(f"[ESCOBAR-WS] === CLIENT MESSAGE RECEIVED ===")
        print(f"[ESCOBAR-WS] Message length: {len(message)}")
        print(f"[ESCOBAR-WS] Message type: {type(message)}")
        print(f"[ESCOBAR-WS] Message preview: {message[:500]}...")
        print(f"[ESCOBAR-WS] Target WS exists: {self.target_ws is not None}")
        print(f"[ESCOBAR-WS] Is closing: {self.is_closing}")
        
        if self.target_ws and not self.is_closing:
            try:
                print(f"[ESCOBAR-WS] Forwarding message to target server")
                # Forward message to target server
                await self.target_ws.send(message)
                print(f"[ESCOBAR-WS] Message successfully forwarded to target")
                logging.debug(f"Forwarded message to target: {message[:100]}...")
            except Exception as e:
                print(f"[ESCOBAR-WS] ERROR forwarding message to target:")
                print(f"[ESCOBAR-WS]   Error: {str(e)}")
                print(f"[ESCOBAR-WS]   Error type: {type(e).__name__}")
                logging.error(f"Error forwarding message to target: {str(e)}")
                self.close(code=1011, reason="Target connection error")
        else:
            print(f"[ESCOBAR-WS] Cannot forward message - target_ws: {self.target_ws}, is_closing: {self.is_closing}")
        print(f"[ESCOBAR-WS] === END CLIENT MESSAGE ===")
    
    async def _forward_from_target(self):
        """Forward messages from target server to client"""
        print(f"[ESCOBAR-WS] === STARTING TARGET MESSAGE FORWARDING ===")
        print(f"[ESCOBAR-WS] Target WS state: {self.target_ws.state if self.target_ws else 'None'}")
        
        try:
            message_count = 0
            async for message in self.target_ws:
                message_count += 1
                print(f"[ESCOBAR-WS] === TARGET MESSAGE #{message_count} ===")
                print(f"[ESCOBAR-WS] Message length: {len(message)}")
                print(f"[ESCOBAR-WS] Message type: {type(message)}")
                print(f"[ESCOBAR-WS] Message preview: {message[:500]}...")
                print(f"[ESCOBAR-WS] Is closing: {self.is_closing}")
                
                if not self.is_closing:
                    print(f"[ESCOBAR-WS] Forwarding message to client")
                    # Forward message to client
                    self.write_message(message)
                    print(f"[ESCOBAR-WS] Message successfully forwarded to client")
                    logging.debug(f"Forwarded message from target: {message[:100]}...")
                else:
                    print(f"[ESCOBAR-WS] Breaking forwarding loop - connection is closing")
                    break
                print(f"[ESCOBAR-WS] === END TARGET MESSAGE #{message_count} ===")
                
        except websockets.exceptions.ConnectionClosed:
            print(f"[ESCOBAR-WS] Target websocket connection closed normally")
            logging.info("Target websocket connection closed")
            if not self.is_closing:
                print(f"[ESCOBAR-WS] Closing client connection due to target disconnect")
                self.close(code=1011, reason="Target server disconnected")
        except Exception as e:
            print(f"[ESCOBAR-WS] ERROR in target message forwarding:")
            print(f"[ESCOBAR-WS]   Error: {str(e)}")
            print(f"[ESCOBAR-WS]   Error type: {type(e).__name__}")
            logging.error(f"Error receiving from target websocket: {str(e)}")
            if not self.is_closing:
                print(f"[ESCOBAR-WS] Closing client connection due to target error")
                self.close(code=1011, reason="Target connection error")
        
        print(f"[ESCOBAR-WS] === TARGET MESSAGE FORWARDING ENDED ===")
    
    def on_close(self):
        """Called when websocket connection is closed"""
        print(f"[ESCOBAR-WS] === CLIENT CONNECTION CLOSED ===")
        print(f"[ESCOBAR-WS] Setting is_closing flag to True")
        self.is_closing = True
        print(f"[ESCOBAR-WS] Target WS exists: {self.target_ws is not None}")
        
        logging.info("WebSocket connection closed")
        
        # Close target connection if it exists
        if self.target_ws:
            print(f"[ESCOBAR-WS] Scheduling target connection cleanup")
            asyncio.create_task(self._close_target_connection())
        else:
            print(f"[ESCOBAR-WS] No target connection to clean up")
        
        print(f"[ESCOBAR-WS] === END CLIENT CONNECTION CLOSED ===")
    
    async def _close_target_connection(self):
        """Safely close the target websocket connection"""
        print(f"[ESCOBAR-WS] === CLOSING TARGET CONNECTION ===")
        try:
            if self.target_ws and not self.target_ws.closed:
                print(f"[ESCOBAR-WS] Target WS is open, closing it")
                await self.target_ws.close()
                print(f"[ESCOBAR-WS] Target connection closed successfully")
                logging.info("Target websocket connection closed")
            else:
                print(f"[ESCOBAR-WS] Target WS already closed or None")
        except Exception as e:
            print(f"[ESCOBAR-WS] ERROR closing target connection:")
            print(f"[ESCOBAR-WS]   Error: {str(e)}")
            print(f"[ESCOBAR-WS]   Error type: {type(e).__name__}")
            logging.error(f"Error closing target websocket: {str(e)}")
        
        print(f"[ESCOBAR-WS] === END CLOSING TARGET CONNECTION ===")


def setup_handlers(web_app):
    print(f"[ESCOBAR-WS] === SETTING UP HANDLERS ===")
    
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    print(f"[ESCOBAR-WS] Host pattern: {host_pattern}")
    print(f"[ESCOBAR-WS] Base URL: {base_url}")
    
    # Register the /proxy endpoint with a path parameter
    proxy_pattern = url_path_join(base_url, "proxy", "(.*)")
    print(f"[ESCOBAR-WS] Proxy pattern: {proxy_pattern}")
    
    # Register the /ws websocket proxy endpoint
    ws_proxy_pattern = url_path_join(base_url, "ws")
    print(f"[ESCOBAR-WS] WebSocket proxy pattern: {ws_proxy_pattern}")
    
    handlers = [
        (proxy_pattern, ProxyHandler),
        (ws_proxy_pattern, WebSocketProxyHandler)
    ]
    
    print(f"[ESCOBAR-WS] Registering {len(handlers)} handlers")
    print(f"[ESCOBAR-WS] Handler patterns: {[h[0] for h in handlers]}")
    
    web_app.add_handlers(host_pattern, handlers)
    
    print(f"[ESCOBAR-WS] Handlers registered successfully")
    print(f"[ESCOBAR-WS] WebSocket proxy available at: {ws_proxy_pattern}")
    print(f"[ESCOBAR-WS] === END SETTING UP HANDLERS ===")
