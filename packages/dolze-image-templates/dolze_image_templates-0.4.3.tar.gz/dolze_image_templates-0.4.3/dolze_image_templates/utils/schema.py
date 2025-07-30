"""
JSON Schema validation for template configuration.
"""
from typing import Dict, Any, Optional
import jsonschema
from pathlib import Path
import json
import os

# Base schema for all components
COMPONENT_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["text", "image", "rectangle", "cta_button", "footer"]},
        "position": {
            "type": "object",
            "properties": {
                "x": {"type": "number"},
                "y": {"type": "number"}
            },
            "required": ["x", "y"],
            "additionalProperties": False
        },
        "size": {
            "type": "object",
            "properties": {
                "width": {"type": "number", "minimum": 1},
                "height": {"type": "number", "minimum": 1}
            },
            "required": ["width", "height"],
            "additionalProperties": False
        },
        "visible": {"type": "boolean", "default": True}
    },
    "required": ["type", "position"],
    "dependencies": {
        "type": {
            "oneOf": [
                {
                    "properties": {
                        "type": {"const": "text"},
                        "text": {"type": "string"},
                        "font_size": {"type": "number", "minimum": 1},
                        "color": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0, "maximum": 255},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "max_width": {"type": "number", "minimum": 1},
                        "font_path": {"type": "string"},
                        "alignment": {"type": "string", "enum": ["left", "center", "right"]}
                    },
                    "required": ["text", "font_size", "color"]
                },
                {
                    "properties": {
                        "type": {"const": "image"},
                        "image_url": {"type": "string"},
                        "circle_crop": {"type": "boolean"},
                        "opacity": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["image_url"]
                },
                {
                    "properties": {
                        "type": {"const": "rectangle"},
                        "fill_color": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0, "maximum": 255},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "fill_gradient": {
                            "type": "object",
                            "properties": {
                                "colors": {
                                    "type": "array",
                                    "items": {
                                        "type": "array",
                                        "items": {"type": "number", "minimum": 0, "maximum": 255},
                                        "minItems": 4,
                                        "maxItems": 4
                                    },
                                    "minItems": 2
                                },
                                "direction": {"type": "string", "enum": ["horizontal", "vertical", "diagonal"]}
                            },
                            "required": ["colors"]
                        },
                        "outline_color": {
                            "type": ["array", "null"],
                            "items": {"type": "number", "minimum": 0, "maximum": 255},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "outline_width": {"type": "number", "minimum": 0}
                    },
                    "anyOf": [
                        {"required": ["fill_color"]},
                        {"required": ["fill_gradient"]}
                    ]
                },
                {
                    "properties": {
                        "type": {"const": "cta_button"},
                        "text": {"type": "string"},
                        "bg_color": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0, "maximum": 255},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "text_color": {
                            "type": "array",
                            "items": {"type": "number", "minimum": 0, "maximum": 255},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "corner_radius": {"type": "number", "minimum": 0},
                        "url": {"type": "string"}
                    },
                    "required": ["text", "bg_color", "text_color"]
                },
                {
                    "properties": {
                        "type": {"const": "footer"},
                        "text": {"type": "string"},
                        "bg_color": {
                            "type": ["array", "null"],
                            "items": {"type": "number", "minimum": 0, "maximum": 255},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "padding": {"type": "number", "minimum": 0}
                    },
                    "required": ["text"]
                }
            ]
        }
    },
    "additionalProperties": False
}

# Main template schema
TEMPLATE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "size": {
            "type": "object",
            "properties": {
                "width": {"type": "number", "minimum": 1},
                "height": {"type": "number", "minimum": 1}
            },
            "required": ["width", "height"],
            "additionalProperties": False
        },
        "background_color": {
            "type": "array",
            "items": {"type": "number", "minimum": 0, "maximum": 255},
            "minItems": 4,
            "maxItems": 4
        },
        "use_base_image": {"type": "boolean"},
        "base_image_url": {"type": "string"},
        "components": {
            "type": "array",
            "items": COMPONENT_SCHEMA,
            "minItems": 1
        }
    },
    "required": ["name", "size", "components"],
    "additionalProperties": False
}


class TemplateValidationError(Exception):
    """Raised when a template fails validation."""
    pass


def validate_template(template_data: Dict[str, Any]) -> None:
    """
    Validate a template against the schema.

    Args:
        template_data: Template data to validate

    Raises:
        TemplateValidationError: If the template is invalid
    """
    try:
        jsonschema.validate(instance=template_data, schema=TEMPLATE_SCHEMA)
    except jsonschema.ValidationError as e:
        raise TemplateValidationError(f"Invalid template: {e}") from e


def validate_template_file(template_path: str) -> None:
    """
    Validate a template file against the schema.

    Args:
        template_path: Path to the template file

    Raises:
        TemplateValidationError: If the template is invalid
        FileNotFoundError: If the template file doesn't exist
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        try:
            template_data = json.load(f)
        except json.JSONDecodeError as e:
            raise TemplateValidationError(f"Invalid JSON in template: {e}") from e

    validate_template(template_data)


def get_template_schema() -> Dict[str, Any]:
    """
    Get the JSON schema for templates.

    Returns:
        The template schema as a dictionary
    """
    return TEMPLATE_SCHEMA


def get_component_schema() -> Dict[str, Any]:
    """
    Get the JSON schema for components.

    Returns:
        The component schema as a dictionary
    """
    return COMPONENT_SCHEMA
