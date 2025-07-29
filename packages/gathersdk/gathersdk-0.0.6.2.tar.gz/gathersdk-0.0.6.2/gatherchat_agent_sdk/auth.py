"""
Simple API Key Authentication for GatherChat Agents
"""

import os
import aiohttp
from typing import Dict, Optional


class SimpleAuth:
    """Simple API key authentication for SDK agents"""
    
    def __init__(self, agent_key: str, api_base_url: str = None):
        """
        Initialize authentication with agent key.
        
        Args:
            agent_key: The secret agent key provided when creating the agent
            api_base_url: The base URL of the GatherChat API (optional, will be auto-detected)
        """
        self.agent_key = agent_key
        self.api_base_url = api_base_url
        self._ws_url: Optional[str] = None
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for HTTP requests"""
        return {
            'Authorization': f'Bearer {self.agent_key}',
            'X-Agent-Key': self.agent_key
        }
    
    async def get_ws_url(self) -> str:
        """
        Get WebSocket URL from the server's config endpoint.
        
        Returns:
            Complete WebSocket URL with auth parameters
        """
        if self._ws_url:
            return self._ws_url
            
        # Get config from server
        config = await self._fetch_config()
        ws_url = config.get('websocket_url', 'ws://localhost:8000')
        
        # Add agent key as query parameter
        separator = '&' if '?' in ws_url else '?'
        self._ws_url = f"{ws_url}{separator}agent_key={self.agent_key}"
        
        return self._ws_url
    
    async def _fetch_config(self) -> Dict:
        """Fetch configuration from the server's /api/config endpoint."""
        base_urls = []
        
        # Try user-provided URL first
        if self.api_base_url:
            base_urls.append(self.api_base_url.rstrip('/'))
        
        # Try common URLs
        base_urls.extend([
            'https://gather.is',  # Production
            'http://157.90.20.176:8001',  # Production FastAPI internal
            'http://localhost:8001',  # Development FastAPI
            'http://localhost:8000',  # Direct WebSocket server
            'http://localhost:8085'   # Alternative
        ])
        
        async with aiohttp.ClientSession() as session:
            for base_url in base_urls:
                try:
                    config_url = f"{base_url}/api/config"
                    async with session.get(config_url, timeout=5) as response:
                        if response.status == 200:
                            return await response.json()
                except Exception:
                    continue
        
        # Fallback to default config
        return {
            'websocket_url': 'ws://localhost:8000',  # Direct to main WebSocket server
            'api_base_url': 'http://localhost:8001'
        }
    
    @classmethod
    def from_env(cls) -> 'SimpleAuth':
        """
        Create auth instance from environment variables.
        
        Required environment variables:
        - GATHERCHAT_AGENT_KEY: Your agent's secret key
        - GATHERCHAT_API_URL: The GatherChat API URL (optional, will auto-detect)
        
        Returns:
            SimpleAuth instance configured from environment
            
        Raises:
            ValueError: If required environment variables are missing
        """
        # Load .env from current working directory
        from dotenv import load_dotenv
        load_dotenv()
        
        agent_key = os.getenv('GATHERCHAT_AGENT_KEY')
        api_url = os.getenv('GATHERCHAT_API_URL')  # Optional
        
        if not agent_key:
            # Try to load .env again more explicitly
            import os as _os
            env_file = _os.path.join(_os.getcwd(), '.env')
            if _os.path.exists(env_file):
                load_dotenv(env_file)
                agent_key = os.getenv('GATHERCHAT_AGENT_KEY')
            
            if not agent_key:
                raise ValueError(
                    "Missing authentication credentials. "
                    "Please set GATHERCHAT_AGENT_KEY environment variable or create a .env file."
                )
            
        return cls(agent_key=agent_key, api_base_url=api_url)