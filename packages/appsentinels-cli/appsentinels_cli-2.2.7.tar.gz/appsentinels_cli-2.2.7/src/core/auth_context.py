"""
Authentication Context for AppSentinels CLI

This module manages authentication state, token storage, and OAuth flows.
It provides a consistent interface for authentication across CLI and MCP modes.
"""

import os
import json
import time
from typing import Optional, Dict, Any
from pathlib import Path
import keyring

class AuthContext:
    """Manages authentication context and token storage"""
    
    KEYRING_SERVICE = "appsentinels-cli"
    KEYRING_TOKEN_KEY = "access_token"
    KEYRING_REFRESH_KEY = "refresh_token"
    
    def __init__(self):
        """Initialize authentication context"""
        self.config_dir = Path.home() / ".as-cli"
        self.config_dir.mkdir(exist_ok=True)
        self.token_file = self.config_dir / "auth.json"
        self._token_data = None
        self._load_token_data()
    
    def _load_token_data(self) -> None:
        """Load token data from storage"""
        # Try to load from environment first (for MCP mode)
        if os.getenv("AUTH_TOKEN"):
            self._token_data = {
                "access_token": os.getenv("AUTH_TOKEN"),
                "token_type": "Bearer",
                "expires_at": None  # Assume long-lived for env tokens
            }
            return
        
        # Try to load from keyring
        try:
            access_token = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_TOKEN_KEY)
            if access_token:
                refresh_token = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_REFRESH_KEY)
                
                # Try to load additional data from file
                if self.token_file.exists():
                    try:
                        with open(self.token_file, 'r') as f:
                            file_data = json.load(f)
                        
                        self._token_data = {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": file_data.get("token_type", "Bearer"),
                            "expires_at": file_data.get("expires_at"),
                            "scope": file_data.get("scope")
                        }
                    except (json.JSONDecodeError, IOError):
                        # Fall back to basic token data
                        self._token_data = {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": "Bearer"
                        }
                else:
                    self._token_data = {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "Bearer"
                    }
        except Exception:
            # Keyring not available or other error
            pass
        
        # Fall back to file storage if keyring fails
        if not self._token_data and self.token_file.exists():
            try:
                with open(self.token_file, 'r') as f:
                    self._token_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_token_data(self) -> None:
        """Save token data to storage"""
        if not self._token_data:
            return
        
        # Save to keyring if available
        try:
            if self._token_data.get("access_token"):
                keyring.set_password(
                    self.KEYRING_SERVICE, 
                    self.KEYRING_TOKEN_KEY, 
                    self._token_data["access_token"]
                )
            
            if self._token_data.get("refresh_token"):
                keyring.set_password(
                    self.KEYRING_SERVICE, 
                    self.KEYRING_REFRESH_KEY, 
                    self._token_data["refresh_token"]
                )
            
            # Save metadata to file
            metadata = {
                "token_type": self._token_data.get("token_type", "Bearer"),
                "expires_at": self._token_data.get("expires_at"),
                "scope": self._token_data.get("scope"),
                "created_at": time.time()
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception:
            # Fall back to file storage
            try:
                with open(self.token_file, 'w') as f:
                    json.dump(self._token_data, f, indent=2)
            except IOError:
                pass
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated
        
        Returns:
            True if authenticated, False otherwise
        """
        if not self._token_data:
            return False
        
        access_token = self._token_data.get("access_token")
        if not access_token:
            return False
        
        # Check if token is expired
        expires_at = self._token_data.get("expires_at")
        if expires_at and time.time() >= expires_at:
            return False
        
        return True
    
    def get_token(self) -> Optional[str]:
        """Get the current access token
        
        Returns:
            Access token or None if not authenticated
        """
        if not self.is_authenticated():
            return None
        
        return self._token_data.get("access_token")
    
    def get_refresh_token(self) -> Optional[str]:
        """Get the current refresh token
        
        Returns:
            Refresh token or None if not available
        """
        if not self._token_data:
            return None
        
        return self._token_data.get("refresh_token")
    
    def set_tokens(self, access_token: str, refresh_token: str = None, 
                   expires_in: int = None, token_type: str = "Bearer",
                   scope: str = None) -> None:
        """Set authentication tokens
        
        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token (optional)
            expires_in: Token expiration time in seconds (optional)
            token_type: Token type (default: Bearer)
            scope: Token scope (optional)
        """
        expires_at = None
        if expires_in:
            expires_at = time.time() + expires_in
        
        self._token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": token_type,
            "expires_at": expires_at,
            "scope": scope
        }
        
        self._save_token_data()
    
    def clear_tokens(self) -> None:
        """Clear all authentication tokens"""
        self._token_data = None
        
        # Clear from keyring
        try:
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_TOKEN_KEY)
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_REFRESH_KEY)
        except Exception:
            pass
        
        # Remove token file
        if self.token_file.exists():
            try:
                self.token_file.unlink()
            except IOError:
                pass
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status information
        
        Returns:
            Dictionary with authentication status details
        """
        if not self.is_authenticated():
            return {
                "authenticated": False,
                "message": "Not authenticated"
            }
        
        status = {
            "authenticated": True,
            "token_type": self._token_data.get("token_type", "Bearer"),
            "scope": self._token_data.get("scope"),
            "has_refresh_token": bool(self._token_data.get("refresh_token"))
        }
        
        expires_at = self._token_data.get("expires_at")
        if expires_at:
            status["expires_at"] = expires_at
            status["expires_in"] = max(0, int(expires_at - time.time()))
        
        return status
    
    def needs_refresh(self, threshold_seconds: int = 300) -> bool:
        """Check if token needs to be refreshed
        
        Args:
            threshold_seconds: Refresh threshold in seconds (default: 5 minutes)
            
        Returns:
            True if token should be refreshed, False otherwise
        """
        if not self._token_data:
            return False
        
        expires_at = self._token_data.get("expires_at")
        if not expires_at:
            return False
        
        return time.time() >= (expires_at - threshold_seconds)
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests
        
        Returns:
            Dictionary of headers
        """
        headers = {}
        
        if self.is_authenticated():
            token = self.get_token()
            token_type = self._token_data.get("token_type", "Bearer")
            headers["Authorization"] = f"{token_type} {token}"
        
        return headers