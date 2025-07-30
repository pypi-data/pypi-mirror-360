# snipserve_cli/api.py
import requests
import json
from typing import Optional, Dict, Any
from .config import get_api_key, get_base_url

class SnipServeAPI:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or get_api_key()
        self.base_url = (base_url or get_base_url()).rstrip('/')
        
        if not self.api_key:
            raise ValueError("API key is required. Set it with 'snipserve config set-key <your-api-key>'")
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })

    def create_paste(self, title: str, content: str, hidden: bool = False) -> Dict[str, Any]:
        """Create a new paste"""
        data = {
            'title': title,
            'content': content,
            'hidden': hidden
        }
        
        response = self.session.post(f'{self.base_url}/api/pastes/create', json=data)
        response.raise_for_status()
        return response.json()

    def get_paste(self, paste_id: str) -> Dict[str, Any]:
        """Get a paste by ID"""
        response = self.session.get(f'{self.base_url}/api/pastes/{paste_id}')
        response.raise_for_status()
        return response.json()

    def update_paste(self, paste_id: str, title: Optional[str] = None, 
                    content: Optional[str] = None, hidden: Optional[bool] = None) -> Dict[str, Any]:
        """Update an existing paste"""
        data = {}
        if title is not None:
            data['title'] = title
        if content is not None:
            data['content'] = content
        if hidden is not None:
            data['hidden'] = hidden
        
        response = self.session.put(f'{self.base_url}/api/pastes/{paste_id}', json=data)
        response.raise_for_status()
        return response.json()

    def delete_paste(self, paste_id: str) -> None:
        """Delete a paste"""
        response = self.session.delete(f'{self.base_url}/api/pastes/{paste_id}')
        response.raise_for_status()

    def list_pastes(self) -> Dict[str, Any]:
        """List user's pastes"""
        response = self.session.get(f'{self.base_url}/api/user/my-pastes')
        response.raise_for_status()
        return response.json()

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        response = self.session.get(f'{self.base_url}/api/user/me')
        response.raise_for_status()
        return response.json()