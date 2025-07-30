"""
Base Instana API Client Module

This module provides the base client for interacting with the Instana API.
"""

import sys
import requests
from typing import Dict, Any, AsyncIterator
from contextlib import asynccontextmanager

# Registry to store all tools
MCP_TOOLS = {}

def register_as_tool(func):
    """Decorator to register a method as an MCP tool."""
    MCP_TOOLS[func.__name__] = func
    return func

class BaseInstanaClient:
    """Base client for Instana API with common functionality."""
    
    def __init__(self, read_token: str, base_url: str):
        self.read_token = read_token
        self.base_url = base_url
    
    def get_headers(self):
        """Get standard headers for Instana API requests."""
        return {
            "Authorization": f"apiToken {self.read_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def make_request(self, endpoint: str, params: Dict[str, Any] = None, method: str = "GET", json: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the Instana API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.get_headers()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, verify=False)
            elif method.upper() == "POST":
                # Use the json parameter if provided, otherwise use params
                data_to_send = json if json is not None else params
                response = requests.post(url, headers=headers, json=data_to_send, verify=False)
            elif method.upper() == "PUT":
                data_to_send = json if json is not None else params
                response = requests.put(url, headers=headers, json=data_to_send, verify=False)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params, verify=False)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}", file=sys.stderr)
            return {"error": f"HTTP Error: {err}"}
        except requests.exceptions.RequestException as err:
            print(f"Error: {err}", file=sys.stderr)
            return {"error": f"Error: {err}"}
        except Exception as e:
            print(f"Unexpected error: {str(e)}", file=sys.stderr)
            return {"error": f"Unexpected error: {str(e)}"}

@asynccontextmanager
async def instana_api_token(read_token: str, base_url: str) -> AsyncIterator[Dict[str, BaseInstanaClient]]:
    """
    Context manager for creating and managing Instana API clients.
    Returns a dictionary of client instances for different API groups.
    """
    # Import here to avoid circular imports
    from .infrastructure_mcp_tools import InfrastructureMCPTools
    from .application_mcp_tools import ApplicationClient
    
    # Create the standard clients
    infra_client = InfrastructureMCPTools(read_token=read_token, base_url=base_url)
    app_client = ApplicationClient(read_token=read_token, base_url=base_url)
    
    # Initialize clients dictionary
    clients = {
        "infrastructure": infra_client,
        "application": app_client,
    }
    
    try:
        yield clients
    except Exception as e:
        print(f"Error in Instana API client: {e}", file=sys.stderr)
    finally:
        # Clean up resources if needed
        pass
