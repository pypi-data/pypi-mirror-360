import json
import os
from urllib.parse import urlencode
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join
import tornado.web

# Get demo users from environment variable, defaulting to empty string if not set
demo_users_env = os.environ.get('DEMO_USERS', '')

# Parse comma-separated list of usernames
user_list = [username.strip()
             for username in demo_users_env.split(',') if username.strip()]

# Create user dictionary dynamically
DEMO_USERS = {}
for username in user_list:
    DEMO_USERS[username] = {'name': username.capitalize(), 'role': 'admin'}

# If no users were defined in the environment, add a default user
if not DEMO_USERS:
    DEMO_USERS = {
        'demo': {'name': 'Demo User', 'role': 'admin'}
    }


class DemoUserHandler(JupyterHandler):
    """Handler for authenticating pre-defined demo users"""

    def get(self, user_id):
        """Handle GET requests to /demo-auth/{user_id}"""
        if user_id in DEMO_USERS:
            # Set user cookie
            self.set_secure_cookie('jupyter-user', user_id)
            # Store user info in session
            self.set_secure_cookie(
                'user-info', json.dumps(DEMO_USERS[user_id]))
            self.log.info(f"Demo user authenticated: {user_id}")

            # Redirect to JupyterLab
            self.redirect(url_path_join(self.base_url, 'lab'))
        else:
            self.log.warning(f"Invalid demo user attempted: {user_id}")
            self.redirect(url_path_join(self.base_url, 'demo-auth'))


class DemoAuthSelectorHandler(JupyterHandler):
    """Handler for the demo user selection page"""

    def get(self):
        """Render a simple page to select a demo user"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Escobar Demo - Select User</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #333;
                }
                .user-button {
                    display: inline-block;
                    margin: 10px;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    font-size: 16px;
                }
                .user-button:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <h1>Select a Demo User</h1>
            <p>Click on a user to access the Escobar demo:</p>
            <div>
        """

        # Add a button for each demo user
        for user_id, user_info in DEMO_USERS.items():
            html += f'<a href="{url_path_join(self.base_url, "demo-auth", user_id)}" class="user-button">{user_info["name"]}</a>\n'

        html += """
            </div>
        </body>
        </html>
        """

        self.write(html)


class LandingPageHandler(JupyterHandler):
    """Handler for the root URL to redirect to demo auth"""

    def get(self):
        """Redirect to the demo auth selector"""
        self.redirect(url_path_join(self.base_url, 'demo-auth'))


def setup_auth_handlers(web_app):
    """Setup the demo authentication handlers"""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    # Register the demo auth handlers
    handlers = [
        (url_path_join(base_url, "demo-auth", "(.*)"), DemoUserHandler),
        (url_path_join(base_url, "demo-auth"), DemoAuthSelectorHandler),
        (base_url, LandingPageHandler)  # Redirect root to demo auth
    ]

    web_app.add_handlers(host_pattern, handlers)
