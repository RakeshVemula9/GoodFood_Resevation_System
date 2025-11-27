"""
MCP Server for GoodFoods Reservation Tools

This implements the Model Context Protocol (MCP) to expose restaurant
reservation tools to LLM agents. MCP provides a standardized way for
LLMs to discover and invoke tools.

Reference: https://spec.modelcontextprotocol.io/
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field

# MCP Protocol Data Classes

@dataclass
class ToolInputSchema:
    """JSON Schema for tool input parameters"""
    type: str
    properties: Dict[str, Any]
    required: List[str] = field(default_factory=list)

@dataclass
class Tool:
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

@dataclass
class TextContent:
    """Text content in MCP response"""
    type: str = "text"
    text: str = ""

@dataclass
class ToolResponse:
    """MCP Tool execution response"""
    content: List[Dict[str, Any]]
    isError: bool = False

class MCPServer:
    """
    Model Context Protocol Server
    
    Exposes restaurant reservation tools following the MCP specification.
    This allows LLM agents to discover and invoke tools in a standardized way.
    """
    
    def __init__(self, tools_module):
        """
        Initialize MCP server with a tools module
        
        Args:
            tools_module: Module containing tool implementation functions
        """
        self.tools_module = tools_module
        self.tools = self._register_tools()
    
    def _register_tools(self) -> List[Tool]:
        """
        Register available tools with MCP-compliant schemas
        
        Returns:
            List of Tool objects with MCP-compliant definitions
        """
        return [
            Tool(
                name="search_branches",
                description="Search for GoodFoods branch locations based on filters. All parameters are optional.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": ["string", "null"],
                            "description": "City name to filter branches"
                        },
                        "locality": {
                            "type": ["string", "null"],
                            "description": "Locality or neighborhood name"
                        },
                        "features": {
                            "type": ["array", "null"],
                            "items": {"type": "string"},
                            "description": "List of required features (e.g., ['Rooftop Seating', 'Live Music'])"
                        },
                        "min_rating": {
                            "type": ["number", "null"],
                            "description": "Minimum rating filter (1.0-5.0)"
                        },
                        "min_capacity": {
                            "type": ["integer", "null"],
                            "description": "Minimum seating capacity required"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_recommendations",
                description="Get intelligent branch recommendations based on user preferences.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "preferences": {
                            "type": "string",
                            "description": "User preferences in natural language (e.g., 'romantic dinner with outdoor seating')"
                        }
                    },
                    "required": ["preferences"]
                }
            ),
            Tool(
                name="make_reservation",
                description="Make a reservation at a specific GoodFoods branch. Requires customer contact details.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "branch_id": {
                            "type": ["integer", "null"],
                            "description": "Unique branch ID (optional if branch_name is provided)"
                        },
                        "branch_name": {
                            "type": ["string", "null"],
                            "description": "Branch name including location (e.g., 'GoodFoods - Koramangala')"
                        },
                        "city": {
                            "type": ["string", "null"],
                            "description": "City name (helpful when using branch_name)"
                        },
                        "date": {
                            "type": "string",
                            "description": "Reservation date in YYYY-MM-DD format"
                        },
                        "time": {
                            "type": "string",
                            "description": "Reservation time in HH:MM format (24-hour)"
                        },
                        "party_size": {
                            "type": "integer",
                            "description": "Number of people in the party",
                            "minimum": 1,
                            "maximum": 20
                        },
                        "customer_name": {
                            "type": ["string", "null"],
                            "description": "Customer's full name"
                        },
                        "customer_phone": {
                            "type": ["string", "null"],
                            "description": "Customer's contact phone number"
                        },
                        "occasion": {
                            "type": ["string", "null"],
                            "description": "Occasion for the reservation (birthday, anniversary, etc.)"
                        }
                    },
                    "required": ["date", "time", "party_size"]
                }
            )
        ]
    
    def list_tools(self) -> Dict[str, Any]:
        """
        MCP Protocol: List available tools
        
        Returns:
            Dictionary with 'tools' key containing list of tool definitions
        """
        return {
            "tools": [asdict(tool) for tool in self.tools]
        }
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResponse:
        """
        MCP Protocol: Execute a tool by name with given arguments
        
        Args:
            name: Tool name to execute
            arguments: Dictionary of tool arguments
            
        Returns:
            ToolResponse with execution result or error
        """
        # Clean null values from arguments
        cleaned_args = {k: v for k, v in arguments.items() if v is not None and v != ""}
        
        try:
            # Route to appropriate tool function
            if name == "search_branches":
                result = self.tools_module.search_branches(**cleaned_args)
            elif name == "get_recommendations":
                result = self.tools_module.get_recommendations(**cleaned_args)
            elif name == "make_reservation":
                result = self.tools_module.make_reservation(**cleaned_args)
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            return ToolResponse(
                content=[{"type": "text", "text": str(result)}],
                isError=False
            )
            
        except TypeError as e:
            # Handle missing or invalid arguments
            return ToolResponse(
                content=[{"type": "text", "text": f"Invalid arguments for tool '{name}': {str(e)}"}],
                isError=True
            )
        except Exception as e:
            # Handle tool execution errors
            return ToolResponse(
                content=[{"type": "text", "text": f"Error executing tool '{name}': {str(e)}"}],
                isError=True
            )
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main MCP message handler
        
        Processes MCP protocol messages and routes to appropriate handlers
        
        Args:
            message: MCP protocol message with 'method' and optional 'params'
            
        Returns:
            MCP protocol response dictionary
        """
        method = message.get("method")
        params = message.get("params", {})
        
        if method == "tools/list":
            return self.list_tools()
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            response = self.call_tool(tool_name, arguments)
            return asdict(response)
        
        else:
            raise ValueError(f"Unknown MCP method: {method}")
    
    def to_openai_format(self) -> List[Dict[str, Any]]:
        """
        Convert MCP tool definitions to OpenAI function calling format
        
        This allows the same tools to work with OpenAI-compatible APIs
        that don't natively support MCP.
        
        Returns:
            List of tools in OpenAI format
        """
        openai_tools = []
        for tool in self.tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        return openai_tools


# Convenience function for easy integration
def create_mcp_server(tools_module):
    """
    Factory function to create an MCP server instance
    
    Args:
        tools_module: Module containing tool implementations
        
    Returns:
        Configured MCPServer instance
    """
    return MCPServer(tools_module)
