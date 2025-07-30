"""
Standalone MCP Server for Instana Events and Infrastructure Resources

This module provides a dedicated MCP server that exposes Instana tools.
Supports stdio and Streamable HTTP transports.
"""

import argparse
import os
import sys
import warnings
import traceback
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, fields
from dotenv import load_dotenv
load_dotenv()

# Add the project root to the Python path
current_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_path))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the necessary modules
try:
    from src.client.events_mcp_tools import AgentMonitoringEventsMCPTools
    from src.client.infrastructure_resources_mcp_tools import InfrastructureResourcesMCPTools
    from src.client.infrastructure_catalog_mcp_tools import InfrastructureCatalogMCPTools
    from src.client.application_resources_mcp_tools import ApplicationResourcesMCPTools
    from src.client.application_metrics_mcp_tools import ApplicationMetricsMCPTools
    from src.client.infrastructure_topology_mcp_tools import InfrastructureTopologyMCPTools
    from src.client.infrastructure_analyze_mcp_tools import InfrastructureAnalyzeMCPTools
    from src.client.application_alert_config_mcp_tools import ApplicationAlertMCPTools
    
    from src.client.instana_client_base import register_as_tool, MCP_TOOLS
except ImportError as e:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

from mcp.server.fastmcp import FastMCP

@dataclass
class MCPState:
    """State for the MCP server."""
    events_client: AgentMonitoringEventsMCPTools = None
    infra_client: InfrastructureResourcesMCPTools = None
    app_resource_client: ApplicationResourcesMCPTools = None
    app_metrics_client: ApplicationMetricsMCPTools = None
    app_alert_client: ApplicationAlertMCPTools = None
    infra_catalog_client: InfrastructureCatalogMCPTools = None
    infra_topo_client: InfrastructureTopologyMCPTools = None
    infra_analyze_client: InfrastructureAnalyzeMCPTools = None

# Global variables to store credentials for lifespan
_global_token = ""
_global_base_url = ""

def get_client_configs():
    """Get client configurations dynamically from MCPState dataclass"""
    # Map field names to their corresponding client classes
    client_class_mapping = {
        'events_client': AgentMonitoringEventsMCPTools,
        'infra_client': InfrastructureResourcesMCPTools,
        'infra_catalog_client': InfrastructureCatalogMCPTools,
        'infra_topo_client': InfrastructureTopologyMCPTools,
        'infra_analyze_client': InfrastructureAnalyzeMCPTools,
        'app_resource_client': ApplicationResourcesMCPTools,
        'app_metrics_client': ApplicationMetricsMCPTools,
        'app_alert_client': ApplicationAlertMCPTools,
    }
    
    # Get all field names from MCPState dataclass
    state_fields = [field.name for field in fields(MCPState)]
    
    # Return configurations for fields that have corresponding client classes
    configs = []
    for field_name in state_fields:
        if field_name in client_class_mapping:
            configs.append((field_name, client_class_mapping[field_name]))
        else:
            print(f"Warning: No client class mapping found for field '{field_name}'", file=sys.stderr)
    
    return configs

def create_clients(token: str, base_url: str, enabled_categories: str = "all") -> MCPState:
    """Create only the enabled Instana clients"""
    state = MCPState()
    
    # Get enabled client configurations
    enabled_client_configs = get_enabled_client_configs(enabled_categories)
    
    for attr_name, client_class in enabled_client_configs:
        try:
            client = client_class(read_token=token, base_url=base_url)
            setattr(state, attr_name, client)
        except Exception as e:
            print(f"Failed to create {attr_name}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            setattr(state, attr_name, None)
    
    return state


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[MCPState]:
    """Set up and tear down the Instana clients."""
    # Use global credentials set by create_app
    token = _global_token or os.getenv("INSTANA_API_TOKEN", "")
    base_url = _global_base_url or os.getenv("INSTANA_BASE_URL", "")
    enabled_categories = os.getenv("INSTANA_ENABLED_TOOLS", "all")
    
    try:
        state = create_clients(token, base_url, enabled_categories)
        
        yield state
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        
        # Yield empty state if client creation failed
        yield MCPState()

def create_app(instana_api_token_value: str, instana_base_url: str) -> FastMCP:
    global _global_token, _global_base_url

    try:
        _global_token = instana_api_token_value
        _global_base_url = instana_base_url

        server = FastMCP("Instana Tools", lifespan=lifespan)

        # Use the enabled categories from the environment
        enabled_categories = os.getenv("INSTANA_ENABLED_TOOLS", "all")

        # Only create and register enabled clients/tools
        clients_state = create_clients(instana_api_token_value, instana_base_url, enabled_categories)

        tools_registered = 0
        for tool_name, tool_func in MCP_TOOLS.items():
            try:
                client_found = False
                client_attr_names = [field.name for field in fields(MCPState)]
                for attr_name in client_attr_names:
                    client = getattr(clients_state, attr_name, None)
                    if client and hasattr(client, tool_name):
                        bound_method = getattr(client, tool_name)
                        server.tool()(bound_method)
                        tools_registered += 1
                        client_found = True
                        break
            except Exception as e:
                print(f"Failed to register tool {tool_name}: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

        return server, tools_registered

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        fallback_server = FastMCP("Instana Tools")
        return fallback_server

async def execute_tool(tool_name: str, arguments: dict, clients_state) -> str:
    """Execute a tool and return result"""
    try:
        # Get all field names from MCPState dataclass
        client_attr_names = [field.name for field in fields(MCPState)]
        
        for attr_name in client_attr_names:
            client = getattr(clients_state, attr_name, None)
            if client and hasattr(client, tool_name):
                method = getattr(client, tool_name)
                result = await method(**arguments)
                return str(result)
        
        return f"Tool {tool_name} not found"
    except Exception as e:
        return f"Error executing tool {tool_name}: {str(e)}"


client_categories = {
    "infra": [
        ('infra_client', InfrastructureResourcesMCPTools),
        ('infra_catalog_client', InfrastructureCatalogMCPTools),
        ('infra_topo_client', InfrastructureTopologyMCPTools),
        ('infra_analyze_client', InfrastructureAnalyzeMCPTools),
    ],
    "app": [
        ('app_resource_client', ApplicationResourcesMCPTools),
        ('app_metrics_client', ApplicationMetricsMCPTools),
        ('app_alert_client', ApplicationAlertMCPTools),
    ],
    "events": [
        ('events_client', AgentMonitoringEventsMCPTools),
    ]
}

def get_enabled_client_configs(enabled_categories: str):
    """Get client configurations based on enabled categories"""
    # Use the global client_categories mapping
    if enabled_categories.lower() == "all":
        all_configs = []
        for category_clients in client_categories.values():
            all_configs.extend(category_clients)
        return all_configs
    categories = [cat.strip() for cat in enabled_categories.split(",")]
    enabled_configs = []
    for category in categories:
        if category in client_categories:
            enabled_configs.extend(client_categories[category])
        else:
            print(f"Warning: Unknown category '{category}'", file=sys.stderr)
    return enabled_configs


def main():
    """Main entry point for the MCP server."""
    try:
        # Get token from environment
        instana_api_token_value = os.getenv("INSTANA_API_TOKEN")
        if not instana_api_token_value:
            warnings.warn(
                "Instana API token not provided. Some functionality will be limited. "
                "Provide token via --api-token argument or INSTANA_API_TOKEN environment variable."
            )

        # Get base URL from environment
        instana_base_url = os.getenv("INSTANA_BASE_URL")

        # Create and configure the MCP server
        parser = argparse.ArgumentParser(description="Instana MCP Server", add_help=False)
        parser.add_argument(
                "-h", "--help",
                action="store_true",
                dest="help",
                help="show this help message and exit"
            )
        parser.add_argument(
            "--transport",
            type=str,
            choices=["streamable-http","stdio"],
            metavar='<mode>',
            help="Transport mode. Choose from: streamable-http, stdio."
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode with additional logging"
        )
        parser.add_argument(
            "--disable",
            type=str,
            metavar='<categories>',
            help="Disable categories: Choose from (infra (infrastructure), app (application), events (event-based))."
        )
        # Check for help arguments before parsing
        if len(sys.argv) > 1 and any(arg in ['-h','--h','--help','-help'] for arg in sys.argv[1:]):
            # Check if help is combined with other arguments
            help_args = ['-h','--h','--help','-help']
            other_args = [arg for arg in sys.argv[1:] if arg not in help_args]
            
            if other_args:
                print("error: argument -h/--h/--help/-help: not allowed with other arguments", file=sys.stderr)
                sys.exit(2)
            
            # Show help and exit
            print("options:")
            for action in parser._actions:
                # Only print options that start with '--' and have a help string
                if any(opt.startswith('--') for opt in action.option_strings) and action.help:
                    # Find the first long option
                    long_opt = next((opt for opt in action.option_strings if opt.startswith('--')), None)
                    metavar = action.metavar or ''
                    opt_str = f"{long_opt} {metavar}".strip()
                    print(f"{opt_str:<24} {action.help}")
            sys.exit(0)
        
        args = parser.parse_args()

        all_categories = {"infra", "app", "events"}

        # By default, enable all categories
        enabled = set(all_categories)
        invalid = set() 
        # Remove disabled categories if specified
        if args.disable:
            disabled = set(cat.strip() for cat in args.disable.split(","))
            invalid = disabled - all_categories
            enabled = enabled - disabled

        if invalid:
            print(f"Error: Unknown category/categories: {', '.join(invalid)}")
            print(f"Available categories: infra, app, events")
            sys.exit(2)

        if args.disable:
            disabled_tool_classes = []
            for category in disabled:
                if category in client_categories:
                    disabled_tool_classes.extend(
                        [cls.__name__ for _, cls in client_categories[category]]
                    )
            if disabled_tool_classes:
                print(
                    f"The following tools are disabled: {', '.join(disabled_tool_classes)}"
                )

        os.environ["INSTANA_ENABLED_TOOLS"] = ",".join(enabled)

        # Create and configure the MCP server
        app, registered_tool_count = create_app(instana_api_token_value or "", instana_base_url or "")

        # Run the server with the appropriate transport
        if args.transport == "streamable-http":
            if args.debug:
                print(f"FastMCP instance: {app}", file=sys.stderr)
                print(f"Registered tools: {registered_tool_count}", file=sys.stderr)
            try:
                app.run(transport="streamable-http")
            except Exception as e:
                print(f"Failed to start HTTP server: {e}", file=sys.stderr)
                if args.debug:
                    traceback.print_exc(file=sys.stderr)
                sys.exit(1)
        else:  
            print("Starting stdio transport", file=sys.stderr)
            app.run(transport="stdio")    
            
    except KeyboardInterrupt:
        print("Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:  
        print(f"Server error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
        