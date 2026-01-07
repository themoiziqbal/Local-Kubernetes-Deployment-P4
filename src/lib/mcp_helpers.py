"""MCP (Model Context Protocol) helper utilities for tool and resource registration."""

from typing import Any, Callable, Dict


class MCPHelpers:
    """
    Helper utilities for MCP tool and resource registration.

    Provides convenience methods for decorating functions as MCP tools
    and registering MCP resources.
    """

    @staticmethod
    def create_tool_schema(
        name: str,
        description: str,
        parameters: Dict[str, Any],
        required: list = None
    ) -> Dict[str, Any]:
        """
        Create a JSON Schema for an MCP tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: Parameter definitions (JSON Schema properties)
            required: List of required parameter names

        Returns:
            MCP tool schema dictionary
        """
        return {
            "name": name,
            "description": description,
            "inputSchema": {
                "type": "object",
                "properties": parameters,
                "required": required or []
            }
        }

    @staticmethod
    def create_resource_schema(
        uri: str,
        name: str,
        description: str,
        mime_type: str = "application/json"
    ) -> Dict[str, Any]:
        """
        Create a schema for an MCP resource.

        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            mime_type: MIME type of resource content

        Returns:
            MCP resource schema dictionary
        """
        return {
            "uri": uri,
            "name": name,
            "description": description,
            "mimeType": mime_type
        }

    @staticmethod
    def validate_tool_input(params: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate tool input parameters against schema.

        Args:
            params: Input parameters
            schema: Tool schema

        Returns:
            (is_valid, errors): Validation result and error messages
        """
        errors = []
        required = schema.get('inputSchema', {}).get('required', [])
        properties = schema.get('inputSchema', {}).get('properties', {})

        # Check required parameters
        for param in required:
            if param not in params:
                errors.append(f"Missing required parameter: {param}")

        # Type checking (basic)
        for param_name, param_value in params.items():
            if param_name in properties:
                expected_type = properties[param_name].get('type')
                actual_type = type(param_value).__name__

                type_map = {
                    'string': 'str',
                    'integer': 'int',
                    'number': ('int', 'float'),
                    'boolean': 'bool',
                    'array': 'list',
                    'object': 'dict'
                }

                expected_python_type = type_map.get(expected_type)
                if expected_python_type and actual_type not in (
                    expected_python_type if isinstance(expected_python_type, tuple) else (expected_python_type,)
                ):
                    errors.append(
                        f"Parameter '{param_name}' has wrong type. Expected {expected_type}, got {actual_type}"
                    )

        return len(errors) == 0, errors


# Singleton instance
mcp_helpers = MCPHelpers()
