"""
Infrastructure Resources MCP Tools Module

This module provides infrastructure resources-specific MCP tools for Instana monitoring.
"""

import sys
import traceback
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

# Import the necessary classes from the SDK
try:
    from instana_client.api.infrastructure_resources_api import InfrastructureResourcesApi
    from instana_client.api_client import ApiClient
    from instana_client.configuration import Configuration
    # Check if GetSnapshotsQuery exists, otherwise we'll handle it differently
    try:
        from instana_client.models.get_snapshots_query import GetSnapshotsQuery
        has_get_snapshots_query = True
    except ImportError:
        has_get_snapshots_query = False
except ImportError as e:
    traceback.print_exc(file=sys.stderr)
    raise

from .instana_client_base import BaseInstanaClient, register_as_tool

# Helper function for debug printing
def debug_print(*args, **kwargs):
    """Print debug information to stderr instead of stdout"""
    print(*args, file=sys.stderr, **kwargs)

class InfrastructureResourcesMCPTools(BaseInstanaClient):
    """Tools for infrastructure resources in Instana MCP."""
    
    def __init__(self, read_token: str, base_url: str):
        """Initialize the Infrastructure Resources MCP tools client."""
        super().__init__(read_token=read_token, base_url=base_url)
        
        try:
            
            # Configure the API client with the correct base URL and authentication
            configuration = Configuration()
            configuration.host = base_url
            configuration.api_key['ApiKeyAuth'] = read_token
            configuration.api_key_prefix['ApiKeyAuth'] = 'apiToken'
            
            # Create an API client with this configuration
            api_client = ApiClient(configuration=configuration)
            
            # Initialize the Instana SDK's InfrastructureResourcesApi with our configured client
            self.infra_api = InfrastructureResourcesApi(api_client=api_client)
        except Exception as e:
            debug_print(f"Error initializing InfrastructureResourcesApi: {e}")
            traceback.print_exc(file=sys.stderr)
            raise
    
    @register_as_tool
    async def get_monitoring_state(self, ctx=None) -> Dict[str, Any]:
        """
        Get the current monitoring state of the Instana system. This tool retrieves details about the number of monitored hosts and serverless entities in your environment.
        Use this when you need an overview of your monitoring coverage, want to check how many hosts are being monitored, or need to verify the scale of your Instana deployment. 
        Use this tool when asked about 'monitoring status', 'how many hosts are monitored', 'monitoring coverage', or when someone wants to 'check the monitoring state'.
        
        Args:
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing monitoring state information or error information
        """
        try:
            print("get_monitoring_state called", file=sys.stderr)
            
            # Call the get_monitoring_state method from the SDK
            result = self.infra_api.get_monitoring_state()
            
            print(f"Result from get_monitoring_state: {result}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"Error in get_monitoring_state: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to get monitoring state: {str(e)}"}
    
    @register_as_tool
    async def get_plugin_payload(self, 
                               snapshot_id: str, 
                               payload_key: str,
                               to_time: Optional[int] = None,
                               window_size: Optional[int] = None,
                               ctx=None) -> Dict[str, Any]:
        """
        Get detailed payload data for a specific snapshot in Instana. This tool retrieves raw monitoring data for a particular entity snapshot using its ID and a specific payload key. 
        Use this when you need to access detailed, low-level monitoring information that isn't available through other APIs. 
        This is particularly useful for deep troubleshooting, accessing specific metrics or configuration details, or when you need the complete raw data for a monitored 
        entity. For example, use this tool when asked about 'detailed snapshot data', 'raw monitoring information', 'plugin payload details', or when someone wants to 'get the complete data for a specific entity'.
        
        Args:
            snapshot_id: The ID of the snapshot
            payload_key: The key of the payload to retrieve
            to_time: End timestamp in milliseconds (optional)
            window_size: Window size in milliseconds (optional)
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing the payload data or error information
        """
        try:
            print(f"get_plugin_payload called with snapshot_id={snapshot_id}, payload_key={payload_key}", file=sys.stderr)
            
            # Call the get_plugin_payload method from the SDK
            result = self.infra_api.get_plugin_payload(
                snapshot_id=snapshot_id,
                payload_key=payload_key,
                to=to_time,
                window_size=window_size
            )
            
            print(f"Result from get_plugin_payload: {result}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"Error in get_plugin_payload: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to get plugin payload: {str(e)}"}
    
    @register_as_tool
    async def get_snapshot(self, 
                        snapshot_id: str,
                        to_time: Optional[int] = None,
                        window_size: Optional[int] = None,
                        ctx=None) -> Dict[str, Any]:
        """
        Get detailed information about a specific snapshot in Instana using its ID.
    
        This tool retrieves comprehensive data for a single, specific entity snapshot that you already have the ID for.
        Use this when you need to examine one particular entity in depth, such as investigating a specific host, container, 
        or process that you've already identified. This is NOT for searching or discovering entities - use get_snapshots for that purpose.
        
        For example, use this tool when:
        - You already have a specific snapshot ID and need its details
        - You want to examine one particular entity's configuration and metrics
        - You need to troubleshoot a specific component that's already been identified
        - Someone asks for "details about this specific entity" or "information about snapshot 12345"
        
        Args:
            snapshot_id: The ID of the snapshot to retrieve
            to_time: End timestamp in milliseconds (optional)
            window_size: Window size in milliseconds (optional)
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing snapshot details or error information
        """
        try:
            print(f"get_snapshot called with snapshot_id={snapshot_id}", file=sys.stderr)
            
            if not snapshot_id:
                return {"error": "snapshot_id parameter is required"}
            
            # Try using the standard SDK method
            try:
                # Call the get_snapshot method from the SDK
                result = self.infra_api.get_snapshot(
                    id=snapshot_id,
                    to=to_time,
                    window_size=window_size
                )
                
                # Convert the result to a dictionary
                if hasattr(result, 'to_dict'):
                    result_dict = result.to_dict()
                elif isinstance(result, dict):
                    result_dict = result
                else:
                    # For any other type, convert to string representation
                    result_dict = {"data": str(result), "snapshot_id": snapshot_id}
                    
                print(f"Result from get_snapshot: {result_dict}", file=sys.stderr)
                return result_dict
                
            except Exception as sdk_error:
                print(f"SDK method failed: {sdk_error}, trying fallback", file=sys.stderr)
                
                # Check if it's a "not found" error
                error_str = str(sdk_error).lower()
                if "not exist" in error_str or "not found" in error_str or "not available" in error_str:
                    return {
                        "error": f"Snapshot with ID '{snapshot_id}' does not exist or is not available.",
                        "details": str(sdk_error)
                    }
                
                # Check if it's a validation error
                if "validation error" in error_str:
                    # Try using the without_preload_content version to get the raw response
                    try:
                        response_data = self.infra_api.get_snapshot_without_preload_content(
                            id=snapshot_id,
                            to=to_time,
                            window_size=window_size
                        )
                        
                        # Check if the response was successful
                        if response_data.status != 200:
                            error_message = f"Failed to get snapshot: HTTP {response_data.status}"
                            print(error_message, file=sys.stderr)
                            return {"error": error_message}
                        
                        # Read the response content
                        response_text = response_data.data.decode('utf-8')
                        
                        # Try to parse as JSON
                        import json
                        try:
                            result_dict = json.loads(response_text)
                            print(f"Result from fallback method: {result_dict}", file=sys.stderr)
                            return result_dict
                        except json.JSONDecodeError:
                            # If not valid JSON, return as string
                            print(f"Result from fallback method (string): {response_text}", file=sys.stderr)
                            return {"message": response_text, "snapshot_id": snapshot_id}
                            
                    except Exception as fallback_error:
                        print(f"Fallback method failed: {fallback_error}", file=sys.stderr)
                        # Continue to the general error handling
                
                # Re-raise if we couldn't handle it specifically
                raise
                    
        except Exception as e:
            print(f"Error in get_snapshot: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to get snapshot: {str(e)}"}

    @register_as_tool
    async def get_snapshots(self, 
                        query: Optional[str] = None,
                        from_time: Optional[int] = None,
                        to_time: Optional[int] = None,
                        size: Optional[int] = 100,
                        plugin: Optional[str] = None,
                        offline: Optional[bool] = False,
                        detailed: Optional[bool] = False,
                        ctx=None) -> Dict[str, Any]:
        """
        Search and discover snapshots based on search criteria.

        This tool is for finding and retrieving MULTIPLE entities that match your search parameters.
        Use this when you need to discover entities, search across your infrastructure, or find components
        matching certain criteria. This is NOT for retrieving details about a specific entity you already know - 
        use get_snapshot (singular) for that purpose.

        For example, use this tool when:
        - Searching for all hosts with high CPU
        - Finding all containers in a specific namespace
        - Discovering entities matching a query pattern
        - You need to list multiple components of a certain type

        Args:
            query: Query string to filter snapshots (optional)
            from_time: Start timestamp in milliseconds (optional, defaults to 1 hour ago)
            to_time: End timestamp in milliseconds (optional, defaults to now)
            size: Maximum number of snapshots to return (optional, default 100)
            plugin: Entity type to filter by (optional)
            offline: Whether to include offline snapshots (optional, default False)
            detailed: If True, returns full raw data. If False (default), returns summarized data
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing matching snapshots (summarized by default) or error information
        """
        try:
            debug_print(f"get_snapshots called with query={query}, from_time={from_time}, to_time={to_time}, size={size}, detailed={detailed}")
            
            # Set default time range if not provided
            if not to_time:
                to_time = int(datetime.now().timestamp() * 1000)
                
            if not from_time:
                from_time = to_time - (60 * 60 * 1000)  # Default to 1 hour
            
            # Call the get_snapshots method from the SDK
            result = self.infra_api.get_snapshots(
                query=query,
                to=to_time,
                window_size=to_time - from_time if from_time else None,
                size=size,
                plugin=plugin,
                offline=offline
            )
            
            debug_print(f"SDK returned result type: {type(result)}")
            
            # Convert result to dictionary if needed
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            elif isinstance(result, dict):
                result_dict = result
            else:
                result_dict = {"data": str(result)}
            
            debug_print(f"Result dict keys: {list(result_dict.keys()) if isinstance(result_dict, dict) else 'Not a dict'}")
            
            # Return based on detailed parameter
            if detailed:
                debug_print("Returning detailed/raw response")
                return result_dict
            else:
                debug_print("Returning summarized response")
                return self._summarize_get_snapshots_response(result_dict)
                
        except Exception as e:
            debug_print(f"Error in get_snapshots: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to get snapshots: {str(e)}"}

    def _summarize_get_snapshots_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summarized version of the get_snapshots response.
        """
        try:
            debug_print("Creating summarized get_snapshots response...")
            items = response_data.get('items', [])
            
            if len(items) == 0:
                return {
                    "message": "No snapshots found matching your criteria.",
                    "total_found": 0,
                    "snapshots": []
                }
            
            # Create a readable summary
            summary_lines = [f"Found {len(items)} snapshot(s) matching your criteria:\n"]
            
            snapshots_list = []
            for i, item in enumerate(items, 1):
                snapshot_id = item.get('snapshotId', 'Unknown')
                label = item.get('label', 'No label')
                host = item.get('host', 'Unknown host')
                plugin = item.get('plugin', 'Unknown plugin')
                
                # Parse host information
                host_info = "Unknown"
                if 'arn:aws:ecs' in host:
                    parts = host.split(':')
                    if len(parts) >= 6:
                        cluster_info = parts[5].split('/') if len(parts) > 5 else []
                        region = parts[3] if len(parts) > 3 else "unknown"
                        cluster = cluster_info[1] if len(cluster_info) > 1 else "unknown"
                        task_id = cluster_info[2] if len(cluster_info) > 2 else "unknown"
                        host_info = f"AWS ECS Task in {region} (cluster: {cluster})"
                else:
                    host_info = host
                
                # Create readable entry
                snapshot_entry = {
                    "number": i,
                    "snapshotId": snapshot_id,
                    "label": label,
                    "plugin": plugin,
                    "host_info": host_info,
                    "full_host": host
                }
                
                snapshots_list.append(snapshot_entry)
                
                # Add to summary lines
                summary_lines.append(f"{i}. Snapshot ID: {snapshot_id}")
                summary_lines.append(f"   Label: {label}")
                summary_lines.append(f"   Plugin: {plugin}")
                summary_lines.append(f"   Host: {host_info}")
                summary_lines.append("")  # Empty line for spacing
            
            return {
                "summary": "\n".join(summary_lines),
                "total_found": len(items),
                "snapshots": snapshots_list,
                "message": f"Successfully found {len(items)} snapshot(s). See details above."
            }
            
        except Exception as e:
            debug_print(f"Error summarizing get_snapshots response: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {
                "error": "Failed to summarize response",
                "details": str(e)
            }



    @register_as_tool
    async def post_snapshots(self, 
                        snapshot_ids: Union[List[str], str],
                        to_time: Optional[int] = None,
                        window_size: Optional[int] = None,
                        detailed: Optional[bool] = False,
                        ctx=None) -> Dict[str, Any]:
        """
        Get details for multiple snapshots by their IDs using SDK.
        
        Args:
            snapshot_ids: List of snapshot IDs to retrieve, or a comma-separated string of IDs
            to_time: End timestamp in milliseconds (optional)
            window_size: Window size in milliseconds (optional)
            detailed: If True, returns full raw data. If False (default), returns summarized data
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing snapshot details (summarized by default) or error information
        """
        try:
            debug_print(f"post_snapshots called with snapshot_ids={snapshot_ids}, detailed={detailed}")
            
            # Handle string input conversion
            if isinstance(snapshot_ids, str):
                if snapshot_ids.startswith('[') and snapshot_ids.endswith(']'):
                    import ast
                    snapshot_ids = ast.literal_eval(snapshot_ids)
                else:
                    snapshot_ids = [id.strip() for id in snapshot_ids.split(',')]
            
            if not snapshot_ids:
                return {"error": "snapshot_ids parameter is required"}
            
            # Use working timeframe
            if not to_time:
                to_time = 1745389956000
            if not window_size:
                window_size = 3600000
            
            debug_print(f"Using to_time={to_time}, window_size={window_size}")
            
            if has_get_snapshots_query:
                from instana_client.models.get_snapshots_query import GetSnapshotsQuery
                
                query_obj = GetSnapshotsQuery(
                    snapshot_ids=snapshot_ids,
                    time_frame={
                        "to": to_time,
                        "windowSize": window_size
                    }
                )
                
                debug_print(f"Making SDK request with without_preload_content...")
                
                # Use the working SDK method that bypasses model validation
                response = self.infra_api.post_snapshots_without_preload_content(
                    get_snapshots_query=query_obj
                )
                
                debug_print(f"SDK response status: {response.status}")
                
                if response.status == 200:
                    # Parse the JSON response manually
                    import json
                    response_text = response.data.decode('utf-8')
                    result_dict = json.loads(response_text)
                    
                    debug_print(f"Successfully parsed response with {len(result_dict.get('items', []))} items")
                    
                    # Return based on detailed parameter
                    if detailed:
                        debug_print("Returning detailed/raw response")
                        return result_dict
                    else:
                        debug_print("Returning summarized response")
                        return self._summarize_snapshots_response(result_dict)
                else:
                    return {
                        "error": f"SDK returned status {response.status}",
                        "details": response.data.decode('utf-8') if response.data else None
                    }
            else:
                return {"error": "GetSnapshotsQuery model not available"}
                    
        except Exception as e:
            debug_print(f"Error in post_snapshots: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to post snapshots: {str(e)}"}

    def _summarize_snapshots_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summarized version of the snapshots response.
        """
        try:
            debug_print("Creating summarized response...")
            items = response_data.get('items', [])
            
            summary = {
                "total_snapshots": len(items),
                "snapshots": []
            }
            
            for item in items:
                debug_print(f"Processing snapshot: {item.get('snapshotId')} - {item.get('plugin')}")
                
                snapshot_summary = {
                    "snapshotId": item.get('snapshotId'),
                    "plugin": item.get('plugin'),
                    "label": item.get('label'),
                    "entityId": item.get('entityId', {}),
                    "timeframe": {
                        "from": item.get('from'),
                        "to": item.get('to')
                    },
                    "tags": item.get('tags', [])
                }
                
                # Extract key information from data based on plugin type
                data = item.get('data', {})
                
                if item.get('plugin') == 'jvmRuntimePlatform':
                    debug_print("Processing JVM snapshot...")
                    snapshot_summary["key_info"] = {
                        "process_name": data.get('name'),
                        "pid": data.get('pid'),
                        "jvm_version": data.get('jvm.version'),
                        "jvm_vendor": data.get('jvm.vendor'),
                        "jvm_name": data.get('jvm.name'),
                        "jvm_build": data.get('jvm.build'),
                        "memory_max": data.get('memory.max'),
                        "jvm_pools_count": len(data.get('jvm.pools', {})),
                        "jvm_args_count": len(data.get('jvm.args', [])),
                        "jvm_collectors": data.get('jvm.collectors', [])
                    }
                elif item.get('plugin') == 'nodeJsRuntimePlatform':
                    debug_print("Processing Node.js snapshot...")
                    versions = data.get('versions', {})
                    snapshot_summary["key_info"] = {
                        "app_name": data.get('name'),
                        "version": data.get('version'),
                        "description": data.get('description'),
                        "pid": data.get('pid'),
                        "node_version": versions.get('node'),
                        "v8_version": versions.get('v8'),
                        "uv_version": versions.get('uv'),
                        "sensor_version": data.get('sensorVersion'),
                        "dependencies_count": len(data.get('dependencies', {})),
                        "start_time": data.get('startTime'),
                        "http_endpoints": list(data.get('http', {}).keys()),
                        "gc_stats_supported": data.get('gc.statsSupported'),
                        "libuv_stats_supported": data.get('libuv.statsSupported')
                    }
                else:
                    # Generic summary for other plugin types
                    debug_print(f"Processing generic snapshot for plugin: {item.get('plugin')}")
                    snapshot_summary["key_info"] = {
                        "data_keys": list(data.keys())[:10],  # First 10 keys
                        "total_data_fields": len(data.keys())
                    }
                
                summary["snapshots"].append(snapshot_summary)
            
            debug_print(f"Created summary with {len(summary['snapshots'])} snapshots")
            return summary
            
        except Exception as e:
            debug_print(f"Error summarizing response: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {
                "error": "Failed to summarize response",
                "details": str(e),
                "raw_data_sample": str(response_data)[:500]  # First 500 chars for debugging
            }




    @register_as_tool
    async def software_versions(self, ctx=None) -> Dict[str, Any]:
        """
        Get information about installed software versions across the monitored infrastructure.
        Retrieve information about the software that are sensed by the agent remotely, natively, or both. This includes runtime and package manager information.
        Args:
            ctx: The MCP context (optional)
            
        Returns:
            Dictionary containing software version information or error information
        """
        try:
            print("Calling software_versions API...", file=sys.stderr)
            
            # Call the software_versions method from the SDK with no parameters
            result = self.infra_api.software_versions()
            
            print(f"API call successful. Result type: {type(result)}", file=sys.stderr)
            
            # Handle different response formats
            if hasattr(result, 'to_dict'):
                print("Converting result using to_dict() method", file=sys.stderr)
                result_dict = result.to_dict()
            elif isinstance(result, dict):
                print("Result is already a dictionary", file=sys.stderr)
                result_dict = result
            elif isinstance(result, list):
                print("Result is a list", file=sys.stderr)
                result_dict = {"items": result}
            else:
                print(f"Unexpected result format: {type(result)}", file=sys.stderr)
                # Try to convert to a dictionary or string representation
                try:
                    result_dict = {"data": str(result)}
                except Exception as str_error:
                    return {"error": f"Unexpected result format: {type(result)}", "details": str(str_error)}
            
            # Print a sample of the result for debugging
            if isinstance(result_dict, dict):
                keys = list(result_dict.keys())
                print(f"Result keys: {keys}", file=sys.stderr)
                
                # If the result is very large, return a summary
                if 'items' in result_dict and isinstance(result_dict['items'], list):
                    items_count = len(result_dict['items'])
                    print(f"Found {items_count} items in the response", file=sys.stderr)
                    
                    # Limit the number of items to return
                    if items_count > 10:
                        result_dict['summary'] = f"Showing 10 of {items_count} items"
                        result_dict['items'] = result_dict['items'][:10]
                
                # If tagTree exists, extract tag names
                if 'tagTree' in result_dict and isinstance(result_dict['tagTree'], list):
                    tag_names = []
                    for category in result_dict['tagTree']:
                        if isinstance(category, dict) and 'children' in category:
                            category_name = category.get('label', 'Unknown')
                            for tag in category['children']:
                                if isinstance(tag, dict) and 'tagName' in tag:
                                    tag_names.append({
                                        'category': category_name,
                                        'tagName': tag['tagName'],
                                        'description': tag.get('description', '')
                                    })
                    
                    # Replace the large tagTree with the extracted tag names
                    result_dict['tagNames'] = tag_names
                    del result_dict['tagTree']
            
            return result_dict
        except Exception as e:
            print(f"Error in software_versions: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {"error": f"Failed to get software versions: {str(e)}"}



