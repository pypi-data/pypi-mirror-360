"""
schemagic_boo - Auto-generate Pydantic models from JSON/YAML structures
Created by: Boobesh (Boo) - GARI TECH
"""

from .core import (
    generate_model_code,
    generate_from_json,
    generate_from_yaml,
    generate_from_dict,
    SchemaGenerator
)

__version__ = "0.1.0"
__author__ = "Boobesh (Boo) - GARI TECH"
__email__ = "boobeshganesan@gmail.com"
__description__ = "Auto-generate Pydantic models from JSON/YAML structures"

__all__ = [
    "generate_model_code",
    "generate_from_json", 
    "generate_from_yaml",
    "generate_from_dict",
    "SchemaGenerator"
]