"""
schemagic_boo - Auto-generate Pydantic models from JSON/YAML structures
Created by: Boobesh (Boo) - GARI TECH
Goal: Make schema generation from JSON feel like magic ✨ — with Pythonic elegance.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union, Set, Tuple
from collections import defaultdict

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

__version__ = "0.1.0"
__author__ = "Boobesh (Boo) - GARI TECH"


class SchemaGenerator:
    """Core class for generating Pydantic models from JSON/YAML structures."""
    
    def __init__(self):
        self.model_names: Set[str] = set()
        self.generated_models: List[str] = []
        self.model_counter = defaultdict(int)
    
    def _sanitize_field_name(self, field_name: str) -> Tuple[str, Optional[str]]:
        """
        Sanitize field name to be a valid Python identifier.
        Returns (sanitized_name, alias) where alias is the original name if sanitization occurred.
        """
        # Convert to snake_case
        field_name = re.sub(r'(?<!^)(?=[A-Z])', '_', field_name).lower()
        
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', field_name)
        
        # Ensure it starts with a letter or underscore
        if not re.match(r'^[a-zA-Z_]', sanitized):
            sanitized = f"field_{sanitized}"
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_{2,}', '_', sanitized)
        
        # Return alias if sanitization changed the name
        alias = field_name if sanitized != field_name else None
        return sanitized, alias
    
    def _generate_unique_model_name(self, base_name: str) -> str:
        """Generate a unique CamelCase model name."""
        # Convert to CamelCase
        base_name = ''.join(word.capitalize() for word in re.split(r'[_\s-]+', base_name))
        
        # Ensure it's a valid Python identifier
        if not base_name or not base_name[0].isalpha():
            base_name = f"Model{base_name}"
        
        # Make it unique
        if base_name not in self.model_names:
            self.model_names.add(base_name)
            return base_name
        
        counter = 1
        while f"{base_name}{counter}" in self.model_names:
            counter += 1
        
        unique_name = f"{base_name}{counter}"
        self.model_names.add(unique_name)
        return unique_name
    
    def _infer_type(self, value: Any, field_name: str) -> Tuple[str, Optional[str]]:
        """
        Infer the type of a value and return (type_string, nested_model_name).
        """
        if value is None:
            return "Optional[str]", None
        
        if isinstance(value, bool):
            return "bool", None
        
        if isinstance(value, int):
            return "int", None
        
        if isinstance(value, float):
            return "float", None
        
        if isinstance(value, str):
            return "str", None
        
        if isinstance(value, list):
            if not value:
                return "List[Any]", None
            
            # Check if all items have the same type
            first_item = value[0]
            if isinstance(first_item, dict):
                # Generate model for list item
                model_name = self._generate_unique_model_name(f"{field_name}_item")
                self._generate_model_from_dict(first_item, model_name)
                return f"List[{model_name}]", model_name
            else:
                item_type, _ = self._infer_type(first_item, f"{field_name}_item")
                # Remove Optional wrapper for list items
                item_type = item_type.replace("Optional[", "").replace("]", "") if item_type.startswith("Optional[") else item_type
                return f"List[{item_type}]", None
        
        if isinstance(value, dict):
            # Generate nested model
            model_name = self._generate_unique_model_name(field_name)
            self._generate_model_from_dict(value, model_name)
            return model_name, model_name
        
        # Fallback
        return "Any", None
    
    def _generate_model_from_dict(self, data: Dict[str, Any], model_name: str) -> str:
        """Generate a Pydantic model from a dictionary."""
        fields = []
        
        for field_name, value in data.items():
            sanitized_name, alias = self._sanitize_field_name(field_name)
            field_type, nested_model = self._infer_type(value, sanitized_name)
            
            # Handle None values by making field optional
            if value is None:
                if not field_type.startswith("Optional["):
                    field_type = f"Optional[{field_type}]"
                field_line = f"    {sanitized_name}: {field_type} = None"
            else:
                field_line = f"    {sanitized_name}: {field_type}"
            
            # Add alias if field name was sanitized
            if alias:
                field_line += f' = Field(alias="{field_name}")'
            
            # Add inline comment with original field name if different
            if alias:
                field_line += f"  # Original field: '{field_name}'"
            
            fields.append(field_line)
        
        # Generate the class definition
        class_def = f"class {model_name}(BaseModel):\n"
        if fields:
            class_def += "\n".join(fields)
        else:
            class_def += "    pass  # Empty model"
        
        # Add to generated models (reverse order for proper definition sequence)
        self.generated_models.insert(0, class_def)
        
        return model_name
    
    def generate_from_dict(self, data: Dict[str, Any], model_name: str = "GeneratedModel") -> str:
        """Generate Pydantic model code from a dictionary."""
        self.model_names.clear()
        self.generated_models.clear()
        
        # Generate the root model
        root_model = self._generate_model_from_dict(data, model_name)
        
        # Build the complete code
        imports = [
            "from typing import Any, Dict, List, Optional, Union",
            "from pydantic import BaseModel, Field",
            ""
        ]
        
        code_parts = imports + self.generated_models
        
        return "\n\n".join(code_parts)
    
    def generate_from_json(self, json_str: str, model_name: str = "GeneratedModel") -> str:
        """Generate Pydantic model code from a JSON string."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        
        if not isinstance(data, dict):
            raise ValueError("JSON must represent an object/dictionary at the root level")
        
        return self.generate_from_dict(data, model_name)
    
    def generate_from_yaml(self, yaml_str: str, model_name: str = "GeneratedModel") -> str:
        """Generate Pydantic model code from a YAML string."""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML support. Install with: pip install PyYAML")
        
        try:
            data = yaml.safe_load(yaml_str)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
        
        if not isinstance(data, dict):
            raise ValueError("YAML must represent an object/dictionary at the root level")
        
        return self.generate_from_dict(data, model_name)


# Public API functions
def generate_model_code(
    data: Union[str, Dict[str, Any]], 
    model_name: str = "GeneratedModel",
    format_type: str = "auto"
) -> str:
    """
    Generate Pydantic model code from JSON string, YAML string, or Python dictionary.
    
    Args:
        data: JSON string, YAML string, or Python dictionary
        model_name: Name for the root model class
        format_type: 'json', 'yaml', or 'auto' (default: 'auto')
    
    Returns:
        String containing the generated Pydantic model code
    
    Example:
        >>> json_data = '{"user": {"name": "Alice", "age": 30}, "active": true}'
        >>> code = generate_model_code(json_data, "UserProfile")
        >>> print(code)
    """
    generator = SchemaGenerator()
    
    # Handle dictionary input
    if isinstance(data, dict):
        return generator.generate_from_dict(data, model_name)
    
    # Handle string input
    if isinstance(data, str):
        if format_type == "yaml":
            return generator.generate_from_yaml(data, model_name)
        elif format_type == "json":
            return generator.generate_from_json(data, model_name)
        else:  # auto-detect
            # Try JSON first
            try:
                return generator.generate_from_json(data, model_name)
            except ValueError:
                # Try YAML if JSON fails
                try:
                    return generator.generate_from_yaml(data, model_name)
                except (ValueError, ImportError):
                    raise ValueError("Unable to parse input as JSON or YAML")
    
    raise ValueError("Input must be a JSON string, YAML string, or Python dictionary")


def generate_from_json(json_str: str, model_name: str = "GeneratedModel") -> str:
    """Generate Pydantic model code from a JSON string."""
    generator = SchemaGenerator()
    return generator.generate_from_json(json_str, model_name)


def generate_from_yaml(yaml_str: str, model_name: str = "GeneratedModel") -> str:
    """Generate Pydantic model code from a YAML string."""
    generator = SchemaGenerator()
    return generator.generate_from_yaml(yaml_str, model_name)


def generate_from_dict(data: Dict[str, Any], model_name: str = "GeneratedModel") -> str:
    """Generate Pydantic model code from a Python dictionary."""
    generator = SchemaGenerator()
    return generator.generate_from_dict(data, model_name)


# Demo function
def demo():
    """Demonstrate the capabilities of schemagic_boo."""
    print("🔥 Welcome to schemagic_boo - by Boobesh (Boo) - GARI TECH ✨")
    print("-" * 60)
    
    # Example 1: Simple JSON
    json_data = '{"user": {"name": "Alice", "age": 30, "email": null}, "active": true}'
    print("📝 Example 1: Simple JSON")
    print(f"Input: {json_data}")
    print("\nGenerated Code:")
    print(generate_model_code(json_data, "UserProfile"))
    
    print("\n" + "=" * 60)
    
    # Example 2: Complex nested structure
    complex_data = {
        "api_response": {
            "status": "success",
            "data": {
                "users": [
                    {"id": 1, "name": "John", "tags": ["admin", "user"]},
                    {"id": 2, "name": "Jane", "tags": ["user"]}
                ],
                "meta": {
                    "total": 2,
                    "page": 1,
                    "per_page": 10
                }
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }
    
    print("📝 Example 2: Complex nested structure")
    print("Generated Code:")
    print(generate_model_code(complex_data, "ApiResponse"))


if __name__ == "__main__":
    demo()