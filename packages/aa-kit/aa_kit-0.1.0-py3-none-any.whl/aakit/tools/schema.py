"""
Tool Schema Generation

Converts Python functions with type hints into MCP-compatible tool schemas.
"""

import inspect
import json
from typing import Any, Dict, List, Optional, Union, get_type_hints, get_origin, get_args
from dataclasses import dataclass
from enum import Enum


@dataclass
class ParameterSchema:
    """Schema for a tool parameter."""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True
    enum: Optional[List[str]] = None
    default: Any = None


@dataclass 
class ToolSchema:
    """Complete schema for a tool."""
    name: str
    description: str
    parameters: List[ParameterSchema]
    
    def to_mcp_schema(self) -> Dict[str, Any]:
        """Convert to MCP tool schema format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
            }
            
            if param.description:
                properties[param.name]["description"] = param.description
            
            if param.enum:
                properties[param.name]["enum"] = param.enum
            
            if param.required:
                required.append(param.name)
        
        schema = {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False
            }
        }
        
        return schema


class SchemaGenerator:
    """Generates MCP schemas from Python functions."""
    
    # Python type to JSON Schema type mapping
    TYPE_MAPPING = {
        str: "string",
        int: "integer", 
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        List: "array",
        Dict: "object",
        Any: "string",  # Default to string for Any type
    }
    
    @classmethod
    def from_function(cls, func: callable) -> ToolSchema:
        """
        Generate a tool schema from a Python function.
        
        Args:
            func: Function to analyze
            
        Returns:
            ToolSchema with extracted information
        """
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Extract function name and docstring
        name = func.__name__
        description = cls._extract_description(func)
        
        # Extract parameters
        parameters = []
        
        for param_name, param in sig.parameters.items():
            # Skip 'self' parameter
            if param_name == 'self':
                continue
            
            param_schema = cls._extract_parameter_schema(
                param_name, param, type_hints
            )
            parameters.append(param_schema)
        
        return ToolSchema(
            name=name,
            description=description,
            parameters=parameters
        )
    
    @classmethod
    def _extract_description(cls, func: callable) -> str:
        """Extract description from function docstring."""
        docstring = inspect.getdoc(func)
        if not docstring:
            return f"Execute {func.__name__}"
        
        # Take first line of docstring as description
        lines = docstring.strip().split('\n')
        description = lines[0].strip()
        
        # Remove trailing period if present
        if description.endswith('.'):
            description = description[:-1]
        
        return description
    
    @classmethod
    def _extract_parameter_schema(
        cls, 
        param_name: str, 
        param: inspect.Parameter,
        type_hints: Dict[str, Any]
    ) -> ParameterSchema:
        """Extract schema for a single parameter."""
        # Get type hint
        param_type = type_hints.get(param_name, str)
        
        # Convert to JSON Schema type
        json_type = cls._python_type_to_json_type(param_type)
        
        # Check if parameter is required
        required = param.default == inspect.Parameter.empty
        
        # Extract default value
        default = None if required else param.default
        
        # Extract enum values if applicable
        enum_values = cls._extract_enum_values(param_type)
        
        return ParameterSchema(
            name=param_name,
            type=json_type,
            description=f"The {param_name} parameter",
            required=required,
            enum=enum_values,
            default=default
        )
    
    @classmethod
    def _python_type_to_json_type(cls, python_type: Any) -> str:
        """Convert Python type to JSON Schema type."""
        # Handle Union types (including Optional)
        origin = get_origin(python_type)
        if origin is Union:
            args = get_args(python_type)
            # Check if it's Optional (Union with None)
            if len(args) == 2 and type(None) in args:
                # Get the non-None type
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return cls._python_type_to_json_type(non_none_type)
            else:
                # For other unions, default to string
                return "string"
        
        # Handle generic types
        if origin:
            return cls.TYPE_MAPPING.get(origin, "string")
        
        # Handle direct type mapping
        if python_type in cls.TYPE_MAPPING:
            return cls.TYPE_MAPPING[python_type]
        
        # Handle Enum types
        if inspect.isclass(python_type) and issubclass(python_type, Enum):
            return "string"
        
        # Default to string for unknown types
        return "string"
    
    @classmethod
    def _extract_enum_values(cls, python_type: Any) -> Optional[List[str]]:
        """Extract enum values if the type is an Enum."""
        if inspect.isclass(python_type) and issubclass(python_type, Enum):
            return [item.value for item in python_type]
        
        return None


def generate_schema(func: callable) -> ToolSchema:
    """
    Convenience function to generate schema from a function.
    
    Args:
        func: Function to analyze
        
    Returns:
        ToolSchema for the function
    """
    return SchemaGenerator.from_function(func)


def enhance_schema_from_docstring(schema: ToolSchema, func: callable) -> ToolSchema:
    """
    Enhance schema with parameter descriptions from docstring.
    
    Args:
        schema: Base schema to enhance
        func: Function with docstring
        
    Returns:
        Enhanced schema with parameter descriptions
    """
    docstring = inspect.getdoc(func)
    if not docstring:
        return schema
    
    # Parse docstring for parameter descriptions
    param_descriptions = _parse_docstring_parameters(docstring)
    
    # Update parameter descriptions
    for param in schema.parameters:
        if param.name in param_descriptions:
            param.description = param_descriptions[param.name]
    
    return schema


def _parse_docstring_parameters(docstring: str) -> Dict[str, str]:
    """
    Parse parameter descriptions from docstring.
    
    Supports Google, NumPy, and Sphinx docstring formats.
    """
    param_descriptions = {}
    lines = docstring.split('\n')
    
    current_param = None
    in_args_section = False
    
    for line in lines:
        line = line.strip()
        
        # Check for Args/Arguments/Parameters section
        if line.lower() in ['args:', 'arguments:', 'parameters:']:
            in_args_section = True
            continue
        
        # Check for end of args section
        if in_args_section and line.endswith(':') and not line.startswith(' '):
            in_args_section = False
            continue
        
        # Parse parameter line
        if in_args_section and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                param_name = parts[0].strip()
                description = parts[1].strip()
                
                # Handle type annotations in parameter name
                if '(' in param_name and ')' in param_name:
                    param_name = param_name.split('(')[0].strip()
                
                param_descriptions[param_name] = description
    
    return param_descriptions