"""
Application Alert MCP Tools Module

This module provides application alert configuration tools for Instana monitoring.
"""

import sys
import traceback
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# Import the necessary classes from the SDK
try:
    from instana_client.api.application_alert_configuration_api import ApplicationAlertConfigurationApi
    from instana_client.api_client import ApiClient
    from instana_client.configuration import Configuration
    from instana_client.models.application_alert_config import ApplicationAlertConfig
    from instana_client.models.application_alert_config_with_metadata import ApplicationAlertConfigWithMetadata
    from instana_client.models.config_version import ConfigVersion
except ImportError as e:
    traceback.print_exc(file=sys.stderr)
    raise

from .instana_client_base import BaseInstanaClient, register_as_tool

# Helper function for debug printing
def debug_print(*args, **kwargs):
    """Print debug information to stderr instead of stdout"""
    print(*args, file=sys.stderr, **kwargs)

class ApplicationAlertMCPTools(BaseInstanaClient):
    """Tools for application alerts in Instana MCP."""
    
    def __init__(self, read_token: str, base_url: str):
        """Initialize the Application Alert MCP tools client."""
        super().__init__(read_token=read_token, base_url=base_url)
        
        try:
            
            # Configure the API client with the correct base URL and authentication
            configuration = Configuration()
            configuration.host = base_url
            configuration.api_key['ApiKeyAuth'] = read_token
            configuration.api_key_prefix['ApiKeyAuth'] = 'apiToken'
            
            # Create an API client with this configuration
            api_client = ApiClient(configuration=configuration)
            
            # Initialize the Instana SDK's ApplicationAlertConfigurationApi with our configured client
            self.alert_api = ApplicationAlertConfigurationApi(api_client=api_client)
        except Exception as e:
            debug_print(f"Error initializing ApplicationAlertConfigurationApi: {e}")
            traceback.print_exc(file=sys.stderr)
            raise
    
    @register_as_tool
    async def find_application_alert_config(self, 
                                        id: str,
                                        valid_on: Optional[int] = None,
                                        ctx=None) -> Dict[str, Any]:
        """
        Get a specific Smart Alert Configuration.
        
        This tool retrieves a specific Smart Alert Configuration by its ID.
        This may return a deleted Configuration.
        
        Args:
            id: The ID of the Smart Alert Configuration
            valid_on: Optional timestamp (in milliseconds) to retrieve the configuration as it was at that time
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the Smart Alert Configuration or error information
        """
        try:
            debug_print(f"get_application_alert_config called with id={id}, valid_on={valid_on}")
            
            # Validate required parameters
            if not id:
                return {"error": "id is required"}
            
            # Call the find_application_alert_config method from the SDK
            debug_print(f"Calling find_application_alert_config with id={id}, valid_on={valid_on}")
            result = self.alert_api.find_application_alert_config(
                id=id,
                valid_on=valid_on
            )
            
            # Convert the result to a dictionary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result
                
            debug_print(f"Result from find_application_alert_config: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in get_application_alert_config: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to get application alert config: {str(e)}"}

    
    @register_as_tool
    async def find_application_alert_config_versions(self, 
                                                id: str,
                                                ctx=None) -> Dict[str, Any]:
        """
        Get Smart Alert Config Versions . Get all versions of a Smart Alert Configuration.
        
        This tool retrieves all versions of a Smart Alert Configuration by its ID.
        This may return deleted Configurations. Configurations are sorted by creation date in descending order.
        
        Args:
            id: The ID of the Smart Alert Configuration
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the Smart Alert Configuration versions or error information
        """
        try:
            debug_print(f"get_application_alert_config_versions called with id={id}")
            
            # Validate required parameters
            if not id:
                return {"error": "id is required"}
            
            # Call the find_application_alert_config_versions method from the SDK
            debug_print(f"Calling find_application_alert_config_versions with id={id}")
            result = self.alert_api.find_application_alert_config_versions(
                id=id
            )
            
            # Convert the result to a dictionary
            if isinstance(result, list):
                # If result is a list, convert each item to a dictionary
                result_dict = [item.to_dict() if hasattr(item, 'to_dict') else item for item in result]
            elif hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result
                
            debug_print(f"Result from find_application_alert_config_versions: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in get_application_alert_config_versions: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to get application alert config versions: {str(e)}"}
        
    @register_as_tool
    async def get_application_alert_configs(self, 
                                        application_id: Optional[str] = None,
                                        alert_ids: Optional[List[str]] = None,
                                        ctx=None) -> Dict[str, Any]:
        """
        Get Smart Alert Configurations for a specific application.
        
        This tool retrieves Smart Alert Configurations, optionally filtered by application ID and alert IDs.
        Configurations are sorted by creation date in descending order.
        
        Args:
            application_id: Optional ID of the application to filter configurations
            alert_ids: Optional list of alert IDs to filter configurations
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing Smart Alert Configurations or error information
        """
        try:
            debug_print(f"get_application_alert_configs called with application_id={application_id}, alert_ids={alert_ids}")
            
            # Call the find_active_application_alert_configs method from the SDK
            debug_print(f"Calling find_active_application_alert_configs with application_id={application_id}, alert_ids={alert_ids}")
            result = self.alert_api.find_active_application_alert_configs(
                application_id=application_id,
                alert_ids=alert_ids
            )
            
            # Convert the result to a dictionary
            if isinstance(result, list):
                # If result is a list, convert each item to a dictionary
                result_dict = [item.to_dict() if hasattr(item, 'to_dict') else item for item in result]
            elif hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result
                    
            debug_print(f"Result from find_active_application_alert_configs: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in get_application_alert_configs: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to get application alert configs: {str(e)}"}
    
    @register_as_tool
    async def delete_application_alert_config(self, 
                                        id: str,
                                        ctx=None) -> Dict[str, Any]:
        """
        Delete a Smart Alert Configuration.
        
        This tool deletes a specific Smart Alert Configuration by its ID.
        Once deleted, the configuration will no longer trigger alerts.
        
        Args:
            id: The ID of the Smart Alert Configuration to delete
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the result of the deletion operation or error information
        """
        try:
            debug_print(f"delete_application_alert_config called with id={id}")
            
            # Validate required parameters
            if not id:
                return {"error": "id is required"}
            
            # Call the delete_application_alert_config method from the SDK
            debug_print(f"Calling delete_application_alert_config with id={id}")
            self.alert_api.delete_application_alert_config(id=id)
            
            # The delete operation doesn't return a result, so we'll create a success message
            result_dict = {
                "success": True,
                "message": f"Smart Alert Configuration with ID '{id}' has been successfully deleted"
            }
                
            debug_print(f"Result from delete_application_alert_config: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in delete_application_alert_config: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to delete application alert config: {str(e)}"}
        
    @register_as_tool
    async def enable_application_alert_config(self, 
                                        id: str,
                                        ctx=None) -> Dict[str, Any]:
        """
        Enable a Smart Alert Configuration.
        
        This tool enables a specific Smart Alert Configuration by its ID.
        Once enabled, the configuration will start triggering alerts when conditions are met.
        
        Args:
            id: The ID of the Smart Alert Configuration to enable
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the result of the enable operation or error information
        """
        try:
            debug_print(f"enable_application_alert_config called with id={id}")
            
            # Validate required parameters
            if not id:
                return {"error": "id is required"}
            
            # Call the enable_application_alert_config method from the SDK
            debug_print(f"Calling enable_application_alert_config with id={id}")
            result = self.alert_api.enable_application_alert_config(id=id)
            
            # Convert the result to a dictionary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result or {
                    "success": True,
                    "message": f"Smart Alert Configuration with ID '{id}' has been successfully enabled"
                }
                
            debug_print(f"Result from enable_application_alert_config: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in enable_application_alert_config: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to enable application alert config: {str(e)}"}
    
    @register_as_tool
    async def disable_application_alert_config(self, 
                                            id: str,
                                            ctx=None) -> Dict[str, Any]:
        """
        Disable a Smart Alert Configuration.
        
        This tool disables a specific Smart Alert Configuration by its ID.
        Once disabled, the configuration will stop triggering alerts even when conditions are met.
        
        Args:
            id: The ID of the Smart Alert Configuration to disable
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the result of the disable operation or error information
        """
        try:
            debug_print(f"disable_application_alert_config called with id={id}")
            
            # Validate required parameters
            if not id:
                return {"error": "id is required"}
            
            # Call the disable_application_alert_config method from the SDK
            debug_print(f"Calling disable_application_alert_config with id={id}")
            result = self.alert_api.disable_application_alert_config(id=id)
            
            # Convert the result to a dictionary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result or {
                    "success": True,
                    "message": f"Smart Alert Configuration with ID '{id}' has been successfully disabled"
                }
                
            debug_print(f"Result from disable_application_alert_config: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in disable_application_alert_config: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to disable application alert config: {str(e)}"}
        
    @register_as_tool
    async def restore_application_alert_config(self, 
                                            id: str,
                                            created: int,
                                            ctx=None) -> Dict[str, Any]:
        """
        Restore a deleted Smart Alert Configuration.
        
        This tool restores a previously deleted Smart Alert Configuration by its ID and creation timestamp.
        Once restored, the configuration will be active again and can trigger alerts when conditions are met.
        
        Args:
            id: The ID of the Smart Alert Configuration to restore
            created: Unix timestamp representing the creation time of the specific Smart Alert Configuration version
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the result of the restore operation or error information
        """
        try:
            debug_print(f"restore_application_alert_config called with id={id}, created={created}")
            
            # Validate required parameters
            if not id:
                return {"error": "id is required"}
            
            if not created:
                return {"error": "created timestamp is required"}
            
            # Call the restore_application_alert_config method from the SDK
            debug_print(f"Calling restore_application_alert_config with id={id}, created={created}")
            result = self.alert_api.restore_application_alert_config(id=id, created=created)
            
            # Convert the result to a dictionary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result or {
                    "success": True,
                    "message": f"Smart Alert Configuration with ID '{id}' and creation timestamp '{created}' has been successfully restored"
                }
                
            debug_print(f"Result from restore_application_alert_config: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in restore_application_alert_config: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to restore application alert config: {str(e)}"}

    @register_as_tool
    async def update_application_alert_config_baseline(self, 
                                                    id: str,
                                                    ctx=None) -> Dict[str, Any]:
        """
        Recalculate the historic baseline for a Smart Alert Configuration.
        
        This tool recalculates and updates the historic baseline (static seasonal threshold) of a Smart Alert Configuration.
        The 'LastUpdated' field of the Configuration is changed to the current time.
        
        Args:
            id: The ID of the Smart Alert Configuration to recalculate
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the result of the baseline update operation or error information
        """
        try:
            debug_print(f"update_application_alert_config_baseline called with id={id}")
            
            # Validate required parameters
            if not id:
                return {"error": "id is required"}
            
            # Call the update_application_historic_baseline method from the SDK
            debug_print(f"Calling update_application_historic_baseline with id={id}")
            result = self.alert_api.update_application_historic_baseline(id=id)
            
            # Convert the result to a dictionary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result or {
                    "success": True,
                    "message": f"Historic baseline for Smart Alert Configuration with ID '{id}' has been successfully recalculated"
                }
                
            debug_print(f"Result from update_application_historic_baseline: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in update_application_alert_config_baseline: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to update application alert config baseline: {str(e)}"}
        
    @register_as_tool
    async def create_application_alert_config(self, 
                                        payload: Union[Dict[str, Any], str],
                                        ctx=None) -> Dict[str, Any]:
        """
        Create a new Smart Alert Configuration.
        
        This tool creates a new Smart Alert Configuration with the provided configuration details.
        Once created, the configuration will be active and can trigger alerts when conditions are met.
        
        Sample payload:
        {
            "name": "My Alert Config",
            "description": "Alert for high CPU usage",
            "severity": 10,
            "triggering": true,
            "enabled": true,
            "rule": {
                "alertType": "...",
                "metricName": "...",
                "aggregation": "...",
                "conditionOperator": "...",
                "conditionValue": 90
            },
            "applicationId": "your-application-id",
            "boundaryScope": "...",
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            },
            "granularity": 60000,
            "timeThreshold": 300000
        }
        
        Args:
            payload: The Smart Alert Configuration details as a dictionary or JSON string
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the created Smart Alert Configuration or error information
        """
        try:
            debug_print(f"create_application_alert_config called with payload={payload}")
            
            # Parse the payload if it's a string
            if isinstance(payload, str):
                debug_print(f"Payload is a string, attempting to parse")
                try:
                    import json
                    try:
                        parsed_payload = json.loads(payload)
                        debug_print(f"Successfully parsed payload as JSON")
                        request_body = parsed_payload
                    except json.JSONDecodeError as e:
                        debug_print(f"JSON parsing failed: {e}, trying with quotes replaced")
                        
                        # Try replacing single quotes with double quotes
                        fixed_payload = payload.replace("'", "\"")
                        try:
                            parsed_payload = json.loads(fixed_payload)
                            debug_print(f"Successfully parsed fixed JSON")
                            request_body = parsed_payload
                        except json.JSONDecodeError:
                            # Try as Python literal
                            import ast
                            try:
                                parsed_payload = ast.literal_eval(payload)
                                debug_print(f"Successfully parsed payload as Python literal")
                                request_body = parsed_payload
                            except (SyntaxError, ValueError) as e2:
                                debug_print(f"Failed to parse payload string: {e2}")
                                return {"error": f"Invalid payload format: {e2}", "payload": payload}
                except Exception as e:
                    debug_print(f"Error parsing payload string: {e}")
                    return {"error": f"Failed to parse payload: {e}", "payload": payload}
            else:
                # If payload is already a dictionary, use it directly
                debug_print(f"Using provided payload dictionary")
                request_body = payload
            
            # Validate the payload
            if not request_body:
                return {"error": "Payload is required"}
            
            # Import the ApplicationAlertConfig class
            try:
                from instana_client.models.application_alert_config import ApplicationAlertConfig
                debug_print("Successfully imported ApplicationAlertConfig")
            except ImportError as e:
                debug_print(f"Error importing ApplicationAlertConfig: {e}")
                return {"error": f"Failed to import ApplicationAlertConfig: {str(e)}"}
            
            # Create an ApplicationAlertConfig object from the request body
            try:
                debug_print(f"Creating ApplicationAlertConfig with params: {request_body}")
                config_object = ApplicationAlertConfig(**request_body)
                debug_print(f"Successfully created config object")
            except Exception as e:
                debug_print(f"Error creating ApplicationAlertConfig: {e}")
                return {"error": f"Failed to create config object: {str(e)}"}
            
            # Call the create_application_alert_config method from the SDK
            debug_print("Calling create_application_alert_config with config object")
            result = self.alert_api.create_application_alert_config(application_alert_config=config_object)
            
            # Convert the result to a dictionary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result
                
            debug_print(f"Result from create_application_alert_config: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in create_application_alert_config: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to create application alert config: {str(e)}"}
        
    @register_as_tool
    async def update_application_alert_config(self, 
                                        id: str,
                                        payload: Union[Dict[str, Any], str],
                                        ctx=None) -> Dict[str, Any]:
        """
        Update an existing Smart Alert Configuration.
        
        This tool updates an existing Smart Alert Configuration with the provided configuration details.
        The configuration is identified by its ID, and the payload contains the updated configuration.
        
        Sample payload:
        {
            "name": "Updated Alert Config",
            "description": "Updated alert for high CPU usage",
            "severity": 5,
            "triggering": true,
            "enabled": true,
            "rule": {
                "alertType": "...",
                "metricName": "...",
                "aggregation": "...",
                "conditionOperator": "...",
                "conditionValue": 95
            },
            "applicationId": "your-application-id",
            "boundaryScope": "...",
            "tagFilterExpression": {
                "type": "EXPRESSION",
                "logicalOperator": "AND",
                "elements": []
            },
            "granularity": 60000,
            "timeThreshold": 300000
        }
        
        Args:
            id: The ID of the Smart Alert Configuration to update
            payload: The updated Smart Alert Configuration details as a dictionary or JSON string
            ctx: The MCP context (optional)
                
        Returns:
            Dictionary containing the updated Smart Alert Configuration or error information
        """
        try:
            debug_print(f"update_application_alert_config called with id={id}, payload={payload}")
            
            # Validate required parameters
            if not id:
                return {"error": "id is required"}
            
            if not payload:
                return {"error": "payload is required"}
            
            # Parse the payload if it's a string
            if isinstance(payload, str):
                debug_print(f"Payload is a string, attempting to parse")
                try:
                    import json
                    try:
                        parsed_payload = json.loads(payload)
                        debug_print(f"Successfully parsed payload as JSON")
                        request_body = parsed_payload
                    except json.JSONDecodeError as e:
                        debug_print(f"JSON parsing failed: {e}, trying with quotes replaced")
                        
                        # Try replacing single quotes with double quotes
                        fixed_payload = payload.replace("'", "\"")
                        try:
                            parsed_payload = json.loads(fixed_payload)
                            debug_print(f"Successfully parsed fixed JSON")
                            request_body = parsed_payload
                        except json.JSONDecodeError:
                            # Try as Python literal
                            import ast
                            try:
                                parsed_payload = ast.literal_eval(payload)
                                debug_print(f"Successfully parsed payload as Python literal")
                                request_body = parsed_payload
                            except (SyntaxError, ValueError) as e2:
                                debug_print(f"Failed to parse payload string: {e2}")
                                return {"error": f"Invalid payload format: {e2}", "payload": payload}
                except Exception as e:
                    debug_print(f"Error parsing payload string: {e}")
                    return {"error": f"Failed to parse payload: {e}", "payload": payload}
            else:
                # If payload is already a dictionary, use it directly
                debug_print(f"Using provided payload dictionary")
                request_body = payload
            
            # Import the ApplicationAlertConfig class
            try:
                from instana_client.models.application_alert_config import ApplicationAlertConfig
                debug_print("Successfully imported ApplicationAlertConfig")
            except ImportError as e:
                debug_print(f"Error importing ApplicationAlertConfig: {e}")
                return {"error": f"Failed to import ApplicationAlertConfig: {str(e)}"}
            
            # Create an ApplicationAlertConfig object from the request body
            try:
                debug_print(f"Creating ApplicationAlertConfig with params: {request_body}")
                config_object = ApplicationAlertConfig(**request_body)
                debug_print(f"Successfully created config object")
            except Exception as e:
                debug_print(f"Error creating ApplicationAlertConfig: {e}")
                return {"error": f"Failed to create config object: {str(e)}"}
            
            # Call the update_application_alert_config method from the SDK
            debug_print(f"Calling update_application_alert_config with id={id} and config object")
            result = self.alert_api.update_application_alert_config(
                id=id,
                application_alert_config=config_object
            )
            
            # Convert the result to a dictionary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                # If it's already a dict or another format, use it as is
                result_dict = result or {
                    "success": True,
                    "message": f"Smart Alert Configuration with ID '{id}' has been successfully updated"
                }
                
            debug_print(f"Result from update_application_alert_config: {result_dict}")
            return result_dict
        except Exception as e:
            debug_print(f"Error in update_application_alert_config: {e}")
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to update application alert config: {str(e)}"}








