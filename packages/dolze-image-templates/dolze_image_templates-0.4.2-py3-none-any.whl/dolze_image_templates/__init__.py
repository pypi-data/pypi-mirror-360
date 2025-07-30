"""
Dolze Templates - A flexible template generation library for creating social media posts, banners, and more.

This package provides a powerful and extensible system for generating images with text, shapes, and other
components in a template-based approach.
"""

import os
import logging
from pathlib import Path

# Version information
__version__ = "0.1.4"

# Set up logging
from .utils.logging_config import setup_logging

# Default log level (can be overridden by applications using this package)
LOG_LEVEL = os.environ.get("DOLZE_LOG_LEVEL", "WARNING").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL, logging.WARNING)

# Set up logging with default level
setup_logging(level=LOG_LEVEL)

# Core functionality
from .core import (
    Template,
    TemplateEngine,
    TemplateRegistry,
    get_template_registry,
    FontManager,
    get_font_manager as _get_font_manager,
)


# Initialize font manager with the package's fonts directory
import os
import sys
from pathlib import Path

# Get the absolute path to the package directory
package_dir = Path(os.path.abspath(os.path.dirname(__file__)))
fonts_dir = package_dir / "fonts"

# Debug information
print(f"[DEBUG] Package directory: {package_dir}")
print(f"[DEBUG] Fonts directory: {fonts_dir}")
print(f"[DEBUG] Fonts directory exists: {fonts_dir.exists()}")


# Create a new get_font_manager function that uses the package's fonts directory
def get_font_manager():
    """
    Get the font manager instance, initialized with the package's fonts directory.

    Returns:
        FontManager: The font manager instance
    """
    # Try multiple possible font directory locations
    possible_font_dirs = [
        str(fonts_dir.absolute()),  # Standard package location
        str((package_dir.parent / "fonts").absolute()),  # Parent directory
        str(
            Path(sys.prefix)
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
            / "dolze_image_templates"
            / "fonts"
        ),  # System site-packages
        str(
            Path.home()
            / ".local"
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
            / "dolze_image_templates"
            / "fonts"
        ),  # User site-packages
    ]

    # Find the first existing fonts directory
    for font_dir in possible_font_dirs:
        if os.path.isdir(font_dir):
            print(f"[DEBUG] Using fonts from: {font_dir}")
            return _get_font_manager(font_dir)

    # If no directory found, use the default one and log a warning
    print(
        f"[WARNING] No fonts directory found in any standard location. Using: {fonts_dir}"
    )
    return _get_font_manager(str(fonts_dir.absolute()))


from typing import Optional, Dict, Any, Union

# Import template variables function


def get_all_image_templates() -> list[str]:
    """
    Get a list of all available template names.

    Returns:
        List[str]: A list of all available template names
    """
    return get_template_registry().get_all_templates()


def render_template(
    template_name: str,
    variables: Optional[Dict[str, Any]] = None,
    output_format: str = "png",
    return_bytes: bool = True,
    output_dir: str = "output",
    output_path: Optional[str] = None,
) -> Union[bytes, str]:
    """
    Render a template with the given variables.

    This is a convenience function that creates a TemplateEngine instance and
    renders a template in one step. The template must be present in the templates directory.

    Args:
        template_name: Name of the template to render (must be in the templates directory)
        variables: Dictionary of variables to substitute in the template
        output_format: Output image format (e.g., 'png', 'jpg', 'jpeg')
        return_bytes: If True, returns the image as bytes instead of saving to disk
        output_dir: Directory to save the rendered image (used if return_bytes is False and output_path is None)
        output_path: Full path to save the rendered image. If None and return_bytes is False, a path will be generated.

    Returns:
        If return_bytes is True: Image bytes
        If return_bytes is False: Path to the rendered image

    Example:
        ```python
        from dolze_image_templates import render_template

        # Define template variables
        variables = {
            "title": "Welcome to Dolze",
            "subtitle": "Create amazing images with ease",
            "image_url": "https://example.com/hero.jpg"
        }

        # Render a template and get bytes
        image_bytes = render_template(
            template_name="my_template",
            variables=variables,
            return_bytes=True
        )

        # Use the bytes directly (e.g., send in API response)
        # Or save to file if needed
        with open('my_image.png', 'wb') as f:
            f.write(image_bytes)
        ```
    """
    engine = TemplateEngine(output_dir=output_dir)
    return engine.render_template(
        template_name=template_name,
        variables=variables or {},
        output_path=output_path if not return_bytes else None,
        output_format=output_format,
        return_bytes=return_bytes,
    )


# Resource management and caching
from .resources import load_image, load_font
from .utils.cache import clear_cache, get_cache_info

# Components
from .components import (
    Component,
    TextComponent,
    ImageComponent,
    CircleComponent,
    RectangleComponent,
    CTAButtonComponent,
    FooterComponent,
    create_component_from_config,
)

# Configuration
from .config import (
    Settings,
    get_settings,
    configure,
    DEFAULT_TEMPLATES_DIR,
    DEFAULT_FONTS_DIR,
    DEFAULT_OUTPUT_DIR,
)

# Version
__version__ = "0.1.2"


# Package metadata
__author__ = "Dolze Team"
__email__ = "support@dolze.com"
__license__ = "MIT"
__description__ = "A flexible template generation library for creating social media posts, banners, and more."


# Package-level initialization
def init() -> None:
    """
    Initialize the Dolze Templates package.
    This function ensures all required directories exist and performs any necessary setup.
    """
    logger = logging.getLogger(__name__)
    logger.info("Initializing Dolze Templates package")

    settings = get_settings()

    # Ensure required directories exist
    os.makedirs(settings.templates_dir, exist_ok=True)
    os.makedirs(settings.fonts_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)

    logger.debug("Package initialization complete")


# Initialize the package when imported
init()

# Re-export the function for direct import
__all__ = [
    "get_all_image_templates",
    "render_template",
    "clear_cache",
    "get_cache_info",
    "load_image",
    "load_font",
    "init",
]


# Clean up namespace
del init

__all__ = [
    # Core
    "Template",
    "TemplateEngine",
    "TemplateRegistry",
    "get_template_registry",
    "FontManager",
    "get_font_manager",
    # Components
    "Component",
    "TextComponent",
    "ImageComponent",
    "CircleComponent",
    "RectangleComponent",
    "CTAButtonComponent",
    "FooterComponent",
    "create_component_from_config",
    # Configuration
    "Settings",
    "get_settings",
    "configure",
    "DEFAULT_TEMPLATES_DIR",
    "DEFAULT_FONTS_DIR",
    "DEFAULT_OUTPUT_DIR",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]
