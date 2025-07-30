"""
Authentication command handler for AppSentinels CLI

This module handles authentication commands including login, logout,
token refresh, and authentication status.
"""

import argparse
import asyncio
import webbrowser
import urllib.parse
from typing import Dict, Any
import secrets
import string
import hashlib
import base64
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

from core.base_handler import BaseCommandHandler, SubcommandMixin
from core.cli_processor import register_command

@register_command
class AuthHandler(SubcommandMixin, BaseCommandHandler):
    """Handler for authentication commands"""
    
    @property
    def command_name(self) -> str:
        return "auth"
    
    @property
    def command_description(self) -> str:
        return "Manage authentication with AppSentinels"
    
    def __init__(self, config, auth_context):
        super().__init__(config, auth_context)
        self.register_subcommand("login", self._handle_login)
        self.register_subcommand("logout", self._handle_logout)
        self.register_subcommand("status", self._handle_status)
        self.register_subcommand("refresh", self._handle_refresh)
    
    def add_subcommands(self, parser: argparse.ArgumentParser) -> None:
        """Add authentication subcommands"""
        subparsers = parser.add_subparsers(dest="subcommand", help="Authentication commands")
        
        # Login command
        login_parser = subparsers.add_parser(
            "login",
            help="Login to AppSentinels using OAuth 2.1"
        )
        login_parser.add_argument(
            "--no-browser",
            action="store_true",
            help="Don't open browser automatically"
        )
        login_parser.add_argument(
            "--port",
            type=int,
            default=8080,
            help="Local server port for OAuth callback (default: 8080)"
        )
        
        # Logout command
        logout_parser = subparsers.add_parser(
            "logout",
            help="Logout and clear stored tokens"
        )
        logout_parser.add_argument(
            "--force",
            action="store_true",
            help="Force logout without confirmation"
        )
        
        # Status command
        status_parser = subparsers.add_parser(
            "status",
            help="Show authentication status"
        )
        
        # Refresh command
        refresh_parser = subparsers.add_parser(
            "refresh",
            help="Refresh access token"
        )
    
    async def handle_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Handle authentication commands"""
        return await self.route_subcommand(args)
    
    async def _handle_login(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Handle login command"""
        if self.auth_context.is_authenticated():
            return self.format_success_response(
                None,
                "Already logged in. Use 'auth logout' to logout first."
            )
        
        # Check if we have required OAuth configuration
        if not self.config.auth.client_id:
            return self.format_error_response(
                "OAuth client ID not configured. Set AS_CLIENT_ID environment variable."
            )
        
        try:
            # Perform OAuth 2.1 flow with PKCE
            tokens = await self._perform_oauth_flow(args.port, args.no_browser)
            
            # Store tokens
            self.auth_context.set_tokens(
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                expires_in=tokens.get("expires_in"),
                token_type=tokens.get("token_type", "Bearer"),
                scope=tokens.get("scope")
            )
            
            return self.format_success_response(
                None,
                "Successfully logged in to AppSentinels"
            )
            
        except Exception as e:
            return self.format_error_response(f"Login failed: {str(e)}")
    
    async def _handle_logout(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Handle logout command"""
        if not self.auth_context.is_authenticated():
            return self.format_success_response(
                None,
                "Not currently logged in"
            )
        
        if not args.force:
            # In a real implementation, you might want to prompt for confirmation
            # For now, we'll just proceed
            pass
        
        # Revoke tokens if possible
        try:
            await self._revoke_tokens()
        except Exception:
            # Continue with logout even if revocation fails
            pass
        
        # Clear stored tokens
        self.auth_context.clear_tokens()
        
        return self.format_success_response(
            None,
            "Successfully logged out"
        )
    
    async def _handle_status(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Handle status command"""
        status = self.auth_context.get_auth_status()
        
        if status["authenticated"]:
            return self.format_success_response(status, "Authentication status")
        else:
            return self.format_error_response("Not authenticated")
    
    async def _handle_refresh(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Handle refresh command"""
        if not self.auth_context.is_authenticated():
            return self.format_error_response("Not authenticated")
        
        refresh_token = self.auth_context.get_refresh_token()
        if not refresh_token:
            return self.format_error_response("No refresh token available")
        
        try:
            tokens = await self._refresh_access_token(refresh_token)
            
            # Update stored tokens
            self.auth_context.set_tokens(
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token", refresh_token),
                expires_in=tokens.get("expires_in"),
                token_type=tokens.get("token_type", "Bearer"),
                scope=tokens.get("scope")
            )
            
            return self.format_success_response(
                None,
                "Access token refreshed successfully"
            )
            
        except Exception as e:
            return self.format_error_response(f"Token refresh failed: {str(e)}")
    
    async def _perform_oauth_flow(self, port: int, no_browser: bool) -> Dict[str, Any]:
        """Perform OAuth 2.1 flow with PKCE"""
        # Generate PKCE parameters
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        state = self._generate_state()
        
        # Build authorization URL
        auth_params = {
            "client_id": self.config.auth.client_id,
            "response_type": "code",
            "redirect_uri": f"http://localhost:{port}/callback",
            "scope": self.config.auth.scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        auth_url = f"{self.config.auth.auth_url}/authorize?" + urllib.parse.urlencode(auth_params)
        
        # Start local server to handle callback
        callback_handler = CallbackHandler(state)
        server = HTTPServer(("localhost", port), callback_handler)
        
        # Start server in background thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"Starting OAuth flow...")
        print(f"Please visit: {auth_url}")
        
        if not no_browser:
            webbrowser.open(auth_url)
        
        # Wait for callback
        print("Waiting for authorization...")
        
        # Wait for callback (timeout after 5 minutes)
        timeout = 300
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if callback_handler.result:
                server.shutdown()
                break
            await asyncio.sleep(1)
        else:
            server.shutdown()
            raise TimeoutError("OAuth flow timed out")
        
        if callback_handler.error:
            raise Exception(f"OAuth error: {callback_handler.error}")
        
        # Exchange code for tokens
        tokens = await self._exchange_code_for_tokens(
            callback_handler.code,
            code_verifier,
            f"http://localhost:{port}/callback"
        )
        
        return tokens
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier"""
        code_verifier = ''.join(secrets.choice(string.ascii_letters + string.digits + '-._~') for _ in range(128))
        return code_verifier
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge"""
        code_sha = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_sha).decode('utf-8')
        return code_challenge.rstrip('=')
    
    def _generate_state(self) -> str:
        """Generate OAuth state parameter"""
        return secrets.token_urlsafe(32)
    
    async def _exchange_code_for_tokens(self, code: str, code_verifier: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        import httpx
        
        token_data = {
            "grant_type": "authorization_code",
            "client_id": self.config.auth.client_id,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier
        }
        
        # Add client secret if available
        if self.config.auth.client_secret:
            token_data["client_secret"] = self.config.auth.client_secret
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "AppSentinels-CLI/1.0.0"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.auth.token_url,
                data=token_data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def _refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        import httpx
        
        token_data = {
            "grant_type": "refresh_token",
            "client_id": self.config.auth.client_id,
            "refresh_token": refresh_token
        }
        
        # Add client secret if available
        if self.config.auth.client_secret:
            token_data["client_secret"] = self.config.auth.client_secret
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "AppSentinels-CLI/1.0.0"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.auth.token_url,
                data=token_data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def _revoke_tokens(self) -> None:
        """Revoke access and refresh tokens"""
        import httpx
        
        # Try to revoke tokens if revocation endpoint is available
        revoke_url = f"{self.config.auth.auth_url}/revoke"
        
        tokens_to_revoke = []
        if self.auth_context.get_token():
            tokens_to_revoke.append(self.auth_context.get_token())
        if self.auth_context.get_refresh_token():
            tokens_to_revoke.append(self.auth_context.get_refresh_token())
        
        async with httpx.AsyncClient() as client:
            for token in tokens_to_revoke:
                try:
                    await client.post(
                        revoke_url,
                        data={
                            "token": token,
                            "client_id": self.config.auth.client_id
                        },
                        headers={
                            "Content-Type": "application/x-www-form-urlencoded",
                            "User-Agent": "AppSentinels-CLI/1.0.0"
                        },
                        timeout=10.0
                    )
                except Exception:
                    # Ignore revocation errors
                    pass

class CallbackHandler:
    """HTTP handler for OAuth callback"""
    
    def __init__(self, expected_state: str):
        self.expected_state = expected_state
        self.result = None
        self.error = None
        self.code = None
    
    def __call__(self, *args, **kwargs):
        return CallbackHTTPHandler(self, *args, **kwargs)

class CallbackHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""
    
    def __init__(self, callback_handler: CallbackHandler, *args, **kwargs):
        self.callback_handler = callback_handler
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET request for OAuth callback"""
        try:
            # Parse query parameters
            from urllib.parse import urlparse, parse_qs
            
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            
            # Check for error
            if 'error' in params:
                self.callback_handler.error = params['error'][0]
                self.callback_handler.result = False
                self._send_response("Error: " + self.callback_handler.error)
                return
            
            # Check state
            if 'state' not in params or params['state'][0] != self.callback_handler.expected_state:
                self.callback_handler.error = "Invalid state parameter"
                self.callback_handler.result = False
                self._send_response("Error: Invalid state parameter")
                return
            
            # Get authorization code
            if 'code' not in params:
                self.callback_handler.error = "No authorization code received"
                self.callback_handler.result = False
                self._send_response("Error: No authorization code received")
                return
            
            self.callback_handler.code = params['code'][0]
            self.callback_handler.result = True
            self._send_response("Success! You can close this window.")
            
        except Exception as e:
            self.callback_handler.error = str(e)
            self.callback_handler.result = False
            self._send_response(f"Error: {str(e)}")
    
    def _send_response(self, message: str):
        """Send HTTP response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""
        <html>
        <head><title>AppSentinels CLI</title></head>
        <body>
        <h1>AppSentinels CLI</h1>
        <p>{message}</p>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass