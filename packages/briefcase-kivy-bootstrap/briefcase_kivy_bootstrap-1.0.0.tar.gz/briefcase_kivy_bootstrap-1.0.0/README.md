# Briefcase Kivy Bootstrap

**Kivy GUI framework bootstrap for Briefcase.** 

## Purpose

This plugin adds Kivy as a selectable GUI framework when creating new Briefcase projects. It generates standard Briefcase projects with Kivy applications that can be built for any platform using any Briefcase backend.

## Installation

```bash
pip install git+https://github.com/pyCino/briefcase-kivy-bootstrap.git
```

## Usage

After installation, Kivy will appear as an option in `briefcase new`:

```bash
briefcase new
# Select "Kivy" as GUI framework
```

## Features

- **Integration**: Uses standard Briefcase architecture
- **Cross-Platform**: Works with all Briefcase backends
- **Dependencies**: Automatically adds Kivy requirements
- **Standard Structure**: Generates normal Briefcase projects

## Generated Project Structure

```
myapp/
├── pyproject.toml          # Standard Briefcase configuration
├── src/myapp/
│   └── app.py              # Kivy application code
└── ...                     # Standard Briefcase files
```

## Example Generated App

```python
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class MyAppApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        # ... Kivy UI code
        return layout

def main():
    MyAppApp().run()
```

## Building for Different Platforms

The generated Kivy project can be built using any Briefcase backend:

```bash
# Standard Android build
briefcase build android

# P4A Android build (if briefcase-p4a-backend is installed)
briefcase build android p4a

# Desktop builds
briefcase build windows
briefcase build macOS
briefcase build linux
```


## Requirements

- Python 3.8+
- Briefcase 0.3.23+
- Kivy 2.3.1+

## Related Projects

- [Briefcase](https://github.com/beeware/briefcase) - Cross-platform packaging
- [Kivy](https://github.com/kivy/kivy) - Cross-platform GUI framework
- [Briefcase P4A Backend](https://github.com/pyCino/briefcase-p4a-backend) - P4A Android builds

## License

MIT License

---

**Al pyCino** 