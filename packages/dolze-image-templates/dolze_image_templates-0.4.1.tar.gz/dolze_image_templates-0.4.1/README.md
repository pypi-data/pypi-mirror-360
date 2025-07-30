# Dolze Templates

A powerful Python library for generating beautiful, dynamic images using JSON templates.

## Features

- 🎨 Create dynamic images from JSON templates
- 🖼️ Support for text, shapes, and image components
- 🎯 Easy template management and rendering
- 🚀 Fast and efficient image generation
- 🧩 Extensible component system

## Installation

You can install the package using pip:

```bash
# Install from PyPI (when available)
pip install dolze-templates

# Or install directly from the repository
pip install git+https://github.com/yourusername/dolze-templates.git

# For development installation
pip install -e .
```

## Quick Start

```python
from dolze_image_templates import render_template, get_all_templates

# List all available templates
print("Available templates:", get_all_templates())

# Render a template
output_path = render_template(
    template_name="your_template_name",
    variables={
        "title": "Hello World",
        "subtitle": "Welcome to Dolze Templates"
    },
    output_dir="output"
)
print(f"Image saved to: {output_path}")
```

## Documentation

For detailed documentation, please refer to the [Documentation](https://github.com/yourusername/dolze-templates/wiki).

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before making a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Dolze Templates is a versatile Python library that enables developers to generate stunning, dynamic images programmatically using simple JSON templates. Perfect for creating social media posts, marketing materials, product showcases, and more with minimal code.

## ✨ Features

- 🎨 **Intuitive JSON-based Templates** - Define complex image compositions with a clean, readable JSON structure
- 🖼️ **Rich Component Library** - Extensive collection of built-in components (text, images, shapes, buttons, etc.)
- ⚡ **High Performance** - Smart caching for fonts and images to ensure fast generation times
- 🔄 **Dynamic Content** - Support for variables and expressions in templates
- 🛡️ **Robust Validation** - Comprehensive input validation and helpful error messages
- 🧩 **Extensible Architecture** - Easy to create and integrate custom components
- 📱 **Responsive Design** - Create templates that adapt to different dimensions
- 🧪 **Tested & Reliable** - Comprehensive test suite with high code coverage

## 📦 Installation

Dolze Templates requires Python 3.8 or higher. Install the latest stable version from PyPI:

```bash
pip install dolze-templates
```

### Optional Dependencies

Some features require additional dependencies. Install them using:

```bash
# For image processing
pip install dolze-templates[images]

# For advanced text rendering
pip install dolze-templates[text]

# For all optional dependencies
pip install dolze-templates[all]
```

### Development Installation

To contribute or modify the source code:

```bash
git clone https://github.com/yourusername/dolze-templates.git
cd dolze-templates

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from dolze_image_templates import TemplateEngine, get_template_registry

# Initialize the template engine
engine = TemplateEngine(
    output_dir="./output",  # Where to save generated images
    cache_dir="./cache"     # Cache directory for assets
)

# Load and process a template
result = engine.process_from_file("templates/social_media_post.json")
print(f"Generated: {result}")
```

### 2. Template with Variables

```python
from dolze_image_templates import TemplateEngine

engine = TemplateEngine()

# Define template variables
context = {
    "title": "Welcome to Dolze",
    "subtitle": "Create amazing images with ease",
    "image_url": "https://example.com/hero.jpg"
}

# Process template with variables
result = engine.process_template("my_template", template_config, context)
```

### 3. Using the Command Line Interface

The package includes a CLI for quick template processing:

```bash
# Render a single template
dolze-templates render templates/post.json -o output/

# Process all templates in a directory
dolze-templates render templates/ -o output/ --recursive

# Use a different config file
dolze-templates render template.json -c config.yaml -o output/

# Cache management
dolze-templates cache clear  # Clear all cached assets
dolze-templates cache info   # Show cache information
```

### 4. Available CLI Options

```
Usage: dolze-templates [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  render  Render templates to images.
  cache   Manage cached assets.
```

## 📋 Example Templates

Explore our collection of ready-to-use templates in the [examples/](examples/) directory. Each template demonstrates different features and can be customized to fit your needs.

### 1. Social Media Post

Create engaging social media posts with dynamic text and images.

```json
{
  "social_media_post": {
    "settings": {
      "size": [1080, 1080],
      "background_color": [255, 255, 255]
    },
    "components": [
      {
        "type": "rectangle",
        "position": [0, 0],
        "size": [1080, 1080],
        "color": [29, 161, 242, 30]
      },
      {
        "type": "text",
        "text": "{{title}}",
        "position": [100, 200],
        "font_size": 72,
        "font_weight": "bold",
        "max_width": 880
      },
      {
        "type": "image",
        "source": "{{image_url}}",
        "position": [100, 400],
        "size": [880, 500],
        "fit": "cover"
      }
    ]
  }
}
```

### 2. Quote Image

Generate beautiful quote images with custom styling.

```json
{
  "quote_image": {
    "settings": {
      "size": [1200, 630],
      "background_color": [18, 18, 18]
    },
    "components": [
      {
        "type": "text",
        "text": "\"{{quote}}\"",
        "position": [100, 200],
        "font_size": 48,
        "color": [255, 255, 255],
        "max_width": 1000,
        "align": "center"
      },
      {
        "type": "text",
        "text": "— {{author}}",
        "position": [600, 500],
        "font_size": 36,
        "color": [200, 200, 200],
        "align": "right"
      }
    ]
  }
}
```

### 3. Product Showcase

Showcase products with images, descriptions, and pricing.

```json
{
  "product_showcase": {
    "settings": {
      "size": [1200, 1600],
      "background_color": [245, 245, 245]
    },
    "components": [
      {
        "type": "image",
        "source": "{{product_image}}",
        "position": [0, 0],
        "size": [1200, 800],
        "fit": "cover"
      },
      {
        "type": "rectangle",
        "position": [0, 800],
        "size": [1200, 800],
        "color": [255, 255, 255]
      },
      {
        "type": "text",
        "text": "{{product_name}}",
        "position": [100, 900],
        "font_size": 64,
        "font_weight": "bold"
      },
      {
        "type": "text",
        "text": "{{product_description}}",
        "position": [100, 1000],
        "font_size": 36,
        "max_width": 1000,
        "color": [100, 100, 100]
      },
      {
        "type": "text",
        "text": "{{product_price}}",
        "position": [100, 1200],
        "font_size": 72,
        "font_weight": "bold",
        "color": [0, 150, 0]
      }
    ]
  }
}
```

## 🏗️ Advanced Usage

### Custom Components

Create your own components by extending the `Component` class:

```python
from dolze_image_templates.components import Component
from PIL import Image, ImageDraw

class CustomShapeComponent(Component):
    def __init__(self, position, size, color, **kwargs):
        super().__init__(position=position, **kwargs)
        self.size = size
        self.color = color

    def render(self, image, context):
        draw = ImageDraw.Draw(image)
        # Draw a custom shape
        draw.polygon([
            (self.x, self.y + self.size[1] // 2),
            (self.x + self.size[0] // 2, self.y),
            (self.x + self.size[0], self.y + self.size[1] // 2),
            (self.x + self.size[0] // 2, self.y + self.size[1])
        ], fill=tuple(self.color))
        return image

# Register the custom component
from dolze_image_templates import get_template_registry
registry = get_template_registry()
registry.register_component('custom_shape', CustomShapeComponent)
```

### Using Hooks

Dolze Templates provides hooks for extending functionality:

```python
from dolze_image_templates import hooks

@hooks.register('before_render')
def log_render_start(template_name, context):
    print(f"Rendering template: {template_name}")

@hooks.register('after_render')
def process_rendered_image(image, template_name, context):
    # Apply custom image processing
    return image.filter(ImageFilter.SHARPEN)
```

## 📚 API Reference

### Core Classes

#### `TemplateEngine`

The main class for processing templates.

```python
engine = TemplateEngine(
    output_dir='output',
    cache_dir='.cache',
    auto_create_dirs=True
)

# Process a template file
result = engine.process_from_file('template.json')

# Process a template dictionary
result = engine.process_template('template_name', template_config, context={})

# Clear cached assets
engine.clear_cache()
```

#### `TemplateRegistry`

Manages available components and template loaders.

```python
from dolze_image_templates import get_template_registry

registry = get_template_registry()

# Register a custom component
registry.register_component('custom', CustomComponent)


# Get a component class
component_cls = registry.get_component('text')
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Open a pull request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
flake8 dolze_image_templates tests

# Run type checking
mypy dolze_image_templates
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

For support or questions, please open an issue on GitHub or contact us at support@dolze.com.

## 📈 Versioning

This project uses [Semantic Versioning](https://semver.org/). For the versions available, see the [tags on this repository](https://github.com/yourusername/dolze-templates/tags).

## 🛠️ Template Structure

Templates in Dolze are defined using a JSON structure that describes the layout, styling, and content of the generated image. Here's a comprehensive guide to the template structure:

### Basic Template Structure

```json
{
  "template_name": {
    "metadata": {
      "name": "Social Media Post",
      "description": "A template for social media posts",
      "version": "1.0.0",
      "author": "Your Name"
    },
    "settings": {
      "size": [1080, 1080], // width, height in pixels
      "background_color": [255, 255, 255, 255], // RGBA values (0-255)
      "background_image": null, // Optional background image URL or path
      "output_format": "png", // png, jpg, webp, etc.
      "output_quality": 95 // 1-100 for lossy formats
    },
    "variables": {
      "title": "Default Title",
      "subtitle": "Default Subtitle",
      "image_url": "https://example.com/default.jpg"
    },
    "components": [
      // Component definitions go here
    ]
  }
}
```

### Available Components

#### 1. Text Component

```json
{
  "type": "text",
  "text": "{{title}}", // Supports template variables
  "position": [100, 100], // x, y coordinates
  "font_family": "Arial",
  "font_size": 48,
  "color": [0, 0, 0, 255], // RGBA
  "max_width": 800, // Optional: wrap text to this width
  "align": "left", // left, center, right
  "font_weight": "normal", // normal, bold, etc.
  "opacity": 1.0, // 0.0 to 1.0
  "rotation": 0 // degrees
}
```

#### 2. Image Component

```json
{
  "type": "image",
  "source": "{{image_url}}", // URL or local path
  "position": [200, 200],
  "size": [400, 300], // width, height
  "fit": "cover", // cover, contain, fill, etc.
  "opacity": 1.0,
  "border_radius": 10, // Rounded corners
  "rotation": 0
}
```

#### 3. Rectangle Component

```json
{
  "type": "rectangle",
  "position": [100, 100],
  "size": [300, 200],
  "color": [255, 0, 0, 128], // Semi-transparent red
  "border_radius": 5,
  "border_width": 2,
  "border_color": [0, 0, 0, 255]
}
```

#### 4. Circle Component

```json
{
  "type": "circle",
  "center": [300, 300],
  "radius": 100,
  "color": [0, 128, 255, 200],
  "border_width": 3,
  "border_color": [0, 0, 0, 255]
}
```

### Template Variables

Templates support dynamic content through variables:

```json
{
  "variables": {
    "username": "johndoe",
    "score": 95,
    "is_premium": true
  },
  "components": [
    {
      "type": "text",
      "text": "Hello, {{username}}! Your score is {{score}}",
      "color": "{{is_premium ? '#FFD700' : '#000000'}}"
    }
  ]
}
```

### Conditions and Loops

```json
{
  "components": [
    {
      "type": "text",
      "text": "{{user.name}}",
      "show": "{{user.is_active}}" // Conditional rendering
    },
    {
      "type": "loop",
      "for": "item in items",
      "components": [
        {
          "type": "text",
          "text": "{{item.name}}",
          "position": ["{{100 * loop.index}}", 100]
        }
      ]
    }
  ]
}
```

### Template Inheritance

Templates can extend other templates:

```json
{
  "base_template": {
    "settings": {
      "size": [1200, 630],
      "background_color": [240, 240, 240]
    },
    "components": [
      {
        "type": "text",
        "text": "Base Template Content"
      }
    ]
  },
  "derived_template": {
    "extends": "base_template",
    "components": [
      {
        "type": "text",
        "text": "Additional Content"
      }
    ]
  }
}
```

## 📚 Documentation

### Available Components

#### Text

Display text with various styling options.

```json
{
  "type": "text",
  "text": "Hello, World!",
  "position": [100, 100],
  "font_size": 36,
  "font_weight": "bold",
  "color": [0, 0, 0],
  "max_width": 800,
  "align": "center",
  "line_height": 1.5
}
```

#### Image

Display images from URLs or local files.

```json
{
  "type": "image",
  "image_url": "https://example.com/image.jpg",
  "position": [100, 100],
  "size": [400, 300],
  "border_radius": 10,
  "opacity": 0.9
}
```

#### Rectangle

Draw rectangles with customizable styles.

```json
{
  "type": "rectangle",
  "position": [50, 50],
  "size": [200, 100],
  "color": [255, 0, 0, 128],
  "border_radius": 10,
  "border_width": 2,
  "border_color": [0, 0, 0]
}
```

### Effects

Apply various visual effects to components:

```json
{
  "effects": ["shadow", "blur"],
  "shadow_color": [0, 0, 0, 100],
  "shadow_offset": [5, 5],
  "shadow_blur_radius": 10,
  "blur_radius": 5
}
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

````

### Available Templates

1. **Social Media Post** (`social_media_post.json`)
   - Perfect for sharing updates, announcements, and promotions
   - Includes logo, featured image, heading, subheading, and CTA button

2. **Quote Post** (`quote_post.json`)
   - Elegant design for sharing quotes and testimonials
   - Supports background images and custom styling

3. **Promotional Banner** (`promotional_banner.json`)
   - Eye-catching banner for promotions and announcements
   - Features gradient backgrounds and clear call-to-action

## Template Format

Templates are defined using a simple JSON structure. Here's an example:

```json
{
  "name": "social_media_post",
  "description": "A clean and modern social media post template",
  "size": {
    "width": 1080,
    "height": 1080
  },
  "background_color": [255, 255, 255, 255],
  "use_base_image": false,
  "components": [
    {
      "type": "rectangle",
      "position": {"x": 0, "y": 0},
      "size": {"width": 1080, "height": 1080},
      "fill_color": [245, 245, 245, 255]
    },
    {
      "type": "image",
      "image_url": "${logo_url}",
      "position": {"x": 40, "y": 40},
      "size": {"width": 100, "height": 100},
      "circle_crop": true
    },
    {
      "type": "text",
      "text": "${heading}",
      "position": {"x": 90, "y": 740},
      "font_size": 64,
      "color": [51, 51, 51, 255],
      "max_width": 900,
      "font_path": "Roboto-Bold"
    }
  ]
}
````

### Standard Template Variables

All templates support these standard variables that will be replaced with actual values:

- `logo_url`: URL to your logo/image
- `image_url`: URL to the main featured image
- `heading`: Main heading text
- `subheading`: Subheading text
- `cta_text`: Call-to-action button text
- `contact_email`: Contact email address
- `contact_phone`: Contact phone number
- `website_url`: Website URL for CTAs
- `quote`: For quote templates, the main quote text

## Examples

See the `examples/` directory for complete examples of how to use each template.

```bash
# Generate all example templates
python examples/generate_examples.py
```

## Customization

### Adding Custom Fonts

1. Place your font files in the `fonts/` directory
2. Reference them in your templates using the font name (without extension)

### Creating Custom Templates

1. Create a new JSON file in the `dolze_image_templates/templates/` directory
2. Define your template structure following the format shown above
3. Register your template in the `TemplateRegistry`

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Building the Package

```bash
python setup.py sdist bdist_wheel
```

## License

MIT
}
result = processor.process_json(json_data)

# Print paths to generated images

for key, path in result.items():
print(f"{key}: {path}")

````

## JSON Schema

The input JSON must contain at least an `image_url` field:

```json
{
  "image_url": "https://example.com/image.jpg"
}
````

Additional fields can be added for future extensions:

```json
{
  "image_url": "https://example.com/image.jpg",
  "text": {
    "title": "My Title",
    "description": "Description text"
  },
  "cta": {
    "text": "Click Here",
    "url": "https://example.com"
  }
}
```

## Extending the System

The `ImageProcessor` class is designed to be easily extended. To add new features:

1. Add new methods to the `ImageProcessor` class
2. Update the `process_json` method to use these new features

See the `extensions.py` file for examples of adding text and CTA buttons.
