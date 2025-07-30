import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime

class EchoSyncClient:
    """Client for interacting with the Echo Sync API."""
    
    def __init__(self, api_url: str, token: str):
        """Initialize the client with API URL and authentication token."""
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def push_state(self, node_id: str, data: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """Push state to a node.
        
        Args:
            node_id: Target node ID
            data: State data to push
            force: Whether to force push despite conflicts
            
        Returns:
            Dict containing the sync response
        """
        url = f"{self.api_url}/api/v1/echo-sync/nodes/{node_id}/push"
        payload = {
            "state": {
                "node_id": node_id,
                "data": data,
                "version": "1.0",  # TODO: Implement version tracking
                "metadata": {
                    "source": "tushell-cli",
                    "timestamp": datetime.utcnow().isoformat()
                }
            },
            "force": force
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def pull_state(self, node_id: str) -> Dict[str, Any]:
        """Pull state from a node.
        
        Args:
            node_id: Source node ID
            
        Returns:
            Dict containing the node state
        """
        url = f"{self.api_url}/api/v1/echo-sync/nodes/{node_id}/pull"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_node_status(self, node_id: str) -> Dict[str, Any]:
        """Get the current status of a node.
        
        Args:
            node_id: Target node ID
            
        Returns:
            Dict containing the node status
        """
        url = f"{self.api_url}/api/v1/echo-sync/nodes/{node_id}/status"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def resolve_conflicts(self, node_id: str, strategy: str = "merge") -> Dict[str, Any]:
        """Resolve conflicts for a node.
        
        Args:
            node_id: Target node ID
            strategy: Conflict resolution strategy
            
        Returns:
            Dict containing the resolution result
        """
        url = f"{self.api_url}/api/v1/echo-sync/nodes/{node_id}/conflicts/resolve"
        payload = {
            "strategy": strategy,
            "resolution_data": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_node_history(self, node_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get the state history of a node.
        
        Args:
            node_id: Target node ID
            limit: Maximum number of history entries to return
            
        Returns:
            Dict containing the node history
        """
        url = f"{self.api_url}/api/v1/echo-sync/nodes/{node_id}/history"
        params = {"limit": limit}
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json() 