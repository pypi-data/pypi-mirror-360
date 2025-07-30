"""
Log Alert Configuration MCP Tools Module

This module provides log alert configuration-specific MCP tools for Instana monitoring.
"""

import sys
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import the necessary classes from the SDK
try:
    from instana_client.api.log_alert_configuration_api import LogAlertConfigurationApi
    from instana_client.api_client import ApiClient
    from instana_client.configuration import Configuration
    from instana_client.models.log_alert_config import LogAlertConfig
except ImportError as e:
    traceback.print_exc(file=sys.stderr)
    raise

from .instana_client_base import BaseInstanaClient, register_as_tool

# Helper function for debug printing
def debug_print(*args, **kwargs):
    """Print debug information to stderr instead of stdout"""
    print(*args, file=sys.stderr, **kwargs)

class LogAlertConfigurationMCPTools(BaseInstanaClient):
    """Tools for log alert configuration in Instana MCP."""
    
    def __init__(self, read_token: str, base_url: str):
        """Initialize the Log Alert Configuration MCP tools client."""
        super().__init__(read_token=read_token, base_url=base_url)
        
        try:
            debug_print(f"Initializing LogAlertConfigurationMCPTools with base_url={base_url}")
            
            # Configure the API client with the correct base URL and authentication
            configuration = Configuration()
            configuration.host = base_url
            configuration.api_key['ApiKeyAuth'] = read_token
            configuration.api_key_prefix['ApiKeyAuth'] = 'apiToken'
            
            # Create an API client with this configuration
            api_client = ApiClient(configuration=configuration)
            
            # Initialize the Instana SDK's LogAlertConfigurationApi with our configured client
            self.log_alert_api = LogAlertConfigurationApi(api_client=api_client)
            debug_print(f"Initialized LogAlertConfigurationApi with host: {configuration.host}")
        except Exception as e:
            debug_print(f"Error initializing LogAlertConfigurationApi: {e}")
            traceback.print_exc(file=sys.stderr)
            raise
    
    @register_as_tool
    async def create_log_alert_config(self, config: Dict[str, Any], ctx=None) -> Dict[str, Any]:
        """
        Create a new log alert configuration.
        
        Args:
            config: Dictionary containing the log alert configuration
                Required fields:
                - name: Name of the alert
                - query: Log query string
                - threshold: Threshold value for the alert
                - timeThreshold: Time threshold in milliseconds
                - rule: Rule configuration
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing the created log alert configuration or error information
        """
        try:
            debug_print(f"create_log_alert_config called with config={config}")
            
            # Convert dictionary to LogAlertConfig model
            log_alert_config = LogAlertConfig(**config)
            
            # Call the API
            result = self.log_alert_api.create_log_alert_config(log_alert_config=log_alert_config)
            
            debug_print(f"Result from create_log_alert_config: {result}")
            return self._convert_to_dict(result)
        except Exception as e:
            debug_print(f"Error in create_log_alert_config: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to create log alert configuration: {str(e)}"}
    
    @register_as_tool
    async def delete_log_alert_config(self, id: str, ctx=None) -> Dict[str, Any]:
        """
        Delete a log alert configuration.
        
        Args:
            id: ID of the log alert configuration to delete
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing the result of the deletion operation or error information
        """
        try:
            debug_print(f"delete_log_alert_config called with id={id}")
            
            self.log_alert_api.delete_log_alert_config(id=id)
            
            debug_print(f"Successfully deleted log alert configuration with ID {id}")
            return {"success": True, "message": f"Log alert configuration with ID {id} deleted successfully"}
        except Exception as e:
            debug_print(f"Error in delete_log_alert_config: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to delete log alert configuration: {str(e)}"}
    
    @register_as_tool
    async def disable_log_alert_config(self, id: str, ctx=None) -> Dict[str, Any]:
        """
        Disable a log alert configuration.
        
        Args:
            id: ID of the log alert configuration to disable
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing the result of the disable operation or error information
        """
        try:
            debug_print(f"disable_log_alert_config called with id={id}")
            
            self.log_alert_api.disable_log_alert_config(id=id)
            
            debug_print(f"Successfully disabled log alert configuration with ID {id}")
            return {"success": True, "message": f"Log alert configuration with ID {id} disabled successfully"}
        except Exception as e:
            debug_print(f"Error in disable_log_alert_config: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to disable log alert configuration: {str(e)}"}
    
    @register_as_tool
    async def enable_log_alert_config(self, id: str, ctx=None) -> Dict[str, Any]:
        """
        Enable a log alert configuration.
        
        Args:
            id: ID of the log alert configuration to enable
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing the result of the enable operation or error information
        """
        try:
            debug_print(f"enable_log_alert_config called with id={id}")
            
            self.log_alert_api.enable_log_alert_config(id=id)
            
            debug_print(f"Successfully enabled log alert configuration with ID {id}")
            return {"success": True, "message": f"Log alert configuration with ID {id} enabled successfully"}
        except Exception as e:
            debug_print(f"Error in enable_log_alert_config: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to enable log alert configuration: {str(e)}"}
    
    @register_as_tool
    async def find_active_log_alert_configs(self, alert_ids: Optional[List[str]] = None, ctx=None) -> Dict[str, Any]:
        """
        Get all active log alert configurations.
        
        Args:
            alert_ids: Optional list of alert IDs to filter by
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing active log alert configurations or error information
        """
        try:
            debug_print(f"find_active_log_alert_configs called with alert_ids={alert_ids}")
            
            result = self.log_alert_api.find_active_log_alert_configs(alert_ids=alert_ids)
            
            debug_print(f"Result from find_active_log_alert_configs: {result}")
            return {"configs": [self._convert_to_dict(config) for config in result]}
        except Exception as e:
            debug_print(f"Error in find_active_log_alert_configs: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to find active log alert configurations: {str(e)}"}
    
    @register_as_tool
    async def find_log_alert_config(self, id: str, valid_on: Optional[int] = None, ctx=None) -> Dict[str, Any]:
        """
        Get a specific log alert configuration by ID.
        
        Args:
            id: ID of the log alert configuration to retrieve
            valid_on: Optional timestamp to get the configuration valid at that time
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing the log alert configuration or error information
        """
        try:
            debug_print(f"find_log_alert_config called with id={id}, valid_on={valid_on}")
            
            result = self.log_alert_api.find_log_alert_config(id=id, valid_on=valid_on)
            
            debug_print(f"Result from find_log_alert_config: {result}")
            return self._convert_to_dict(result)
        except Exception as e:
            debug_print(f"Error in find_log_alert_config: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to find log alert configuration: {str(e)}"}
    
    @register_as_tool
    async def find_log_alert_config_versions(self, id: str, ctx=None) -> Dict[str, Any]:
        """
        Get all versions of a log alert configuration.
        
        Args:
            id: ID of the log alert configuration to get versions for
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing versions of the log alert configuration or error information
        """
        try:
            debug_print(f"find_log_alert_config_versions called with id={id}")
            
            result = self.log_alert_api.find_log_alert_config_versions(id=id)
            
            debug_print(f"Result from find_log_alert_config_versions: {result}")
            return {"versions": [self._convert_to_dict(version) for version in result]}
        except Exception as e:
            debug_print(f"Error in find_log_alert_config_versions: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to find log alert configuration versions: {str(e)}"}
    
    @register_as_tool
    async def restore_log_alert_config(self, id: str, created: int, ctx=None) -> Dict[str, Any]:
        """
        Restore a log alert configuration to a previous version.
        
        Args:
            id: ID of the log alert configuration to restore
            created: Timestamp of the version to restore
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing the result of the restore operation or error information
        """
        try:
            debug_print(f"restore_log_alert_config called with id={id}, created={created}")
            
            self.log_alert_api.restore_log_alert_config(id=id, created=created)
            
            debug_print(f"Successfully restored log alert configuration with ID {id}")
            return {
                "success": True, 
                "message": f"Log alert configuration with ID {id} restored to version from {datetime.fromtimestamp(created/1000).isoformat()}"
            }
        except Exception as e:
            debug_print(f"Error in restore_log_alert_config: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to restore log alert configuration: {str(e)}"}
    
    @register_as_tool
    async def update_log_alert_config(self, id: str, config: Dict[str, Any], ctx=None) -> Dict[str, Any]:
        """
        Update a log alert configuration.
        
        Args:
            id: ID of the log alert configuration to update
            config: Dictionary containing the updated log alert configuration
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing the updated log alert configuration or error information
        """
        try:
            debug_print(f"update_log_alert_config called with id={id}, config={config}")
            
            # Convert dictionary to LogAlertConfig model
            log_alert_config = LogAlertConfig(**config)
            
            # Call the API
            result = self.log_alert_api.update_log_alert_config(id=id, log_alert_config=log_alert_config)
            
            debug_print(f"Result from update_log_alert_config: {result}")
            return self._convert_to_dict(result)
        except Exception as e:
            debug_print(f"Error in update_log_alert_config: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to update log alert configuration: {str(e)}"}
    
    def _convert_to_dict(self, obj: Any) -> Dict[str, Any]:
        """
        Convert an object to a dictionary.
        
        Args:
            obj: Object to convert
            
        Returns:
            Dictionary representation of the object
        """
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return obj
