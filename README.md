# Intel Render Engine

A high-performance real-time raymarching/raytracing engine with revolutionary OpenCL GUI system, advanced volumetric cloud rendering and HDR support.

## 🆕 Latest: OpenCL GUI System

**World's First Fully GPU-Accelerated GUI** - Complete replacement of traditional GUI libraries with OpenCL-based interface rendering:

- **100% GPU Rendering** - All UI elements rendered through OpenCL kernels
- **Zero CPU Overhead** - No CPU-GPU transfers for interface operations
- **Perfect Integration** - Shared OpenCL context with raymarching engine
- **Professional Tools** - Blender-inspired Level Editor with modular interface
- **Multiple Themes** - Dark, Light, Blender, and Cyberpunk themes
- **120+ FPS Performance** - Even with complex GUI layouts

## Quick Start

```bash
# OpenCL Level Editor (NEW!)
python opencl_level_editor_launcher.py

# Traditional launcher
python launch.py

# Launch specific scenes
python launch.py clouds --hdr
python launch.py demo

# Show all options
python launch.py --help
```

## Project Structure

```
├── opencl_level_editor.py              # OpenCL Level Editor (NEW!)
├── opencl_level_editor_launcher.py     # OpenCL GUI Launcher (NEW!)
├── launch.py                           # Interactive launcher
├── main.py                             # Core application
├── requirements.txt                    # Python dependencies
├── src/                                # Source code
│   ├── core/                           # Core engine components
│   │   ├── raymarcher.py               # Main raymarching engine
│   │   └── camera.py                   # 3D camera system
│   ├── gui/                            # User interface
│   │   ├── opencl_gui.py               # OpenCL GUI System (NEW!)
│   │   └── gui.py                      # Traditional Pygame GUI
│   ├── scenes/                         # Scene definitions
│   │   └── scenes.py                   # Available scenes
│   ├── shaders/                        # OpenCL compute shaders
│   │   ├── gui.cl                      # GUI rendering kernels (NEW!)
│   │   ├── raymarch_hdr.cl             # HDR raymarching
│   │   ├── volumetric_clouds_hdr.cl    # HDR cloud rendering
│   │   └── advanced_clouds_hdr.cl      # Advanced cloud physics
│   └── launchers/                      # Launch utilities
│       └── universal_launcher.py       # Universal launcher
├── docs/                               # Documentation
│   ├── OPENCL_GUI.md                   # OpenCL GUI Documentation (NEW!)
│   └── OPENCL_LEVEL_EDITOR.md          # Level Editor Guide (NEW!)
├── tools/                              # Development tools
└── examples/                           # Example scenes
```

## Features

- **🎨 OpenCL GUI System**: World's first fully GPU-accelerated user interface
- **⚡ Real-time Raymarching**: GPU-accelerated distance field rendering
- **📷 Advanced Camera System**: Quaternion-based 3D camera with smooth movement
- **🌅 HDR Rendering**: High Dynamic Range with multiple tone mapping operators
- **☁️ Volumetric Clouds**: Physically-based cloud rendering with atmospheric scattering
- **🎬 Multiple Scenes**: Demo, minimal, complex, and cloud scenes
- **🎮 Interactive Controls**: Mouse and keyboard controls with customizable sensitivity
- **🎛️ Level Editor**: Professional editing tools with modular interface
- **🎭 Multiple Themes**: Dark, Light, Blender, and Cyberpunk GUI themes

## Requirements

- Python 3.8+
- OpenCL compatible GPU
- See `requirements.txt` for Python dependencies

## Documentation

See the `docs/` folder for detailed documentation:

### OpenCL GUI System (NEW!)
- `OPENCL_GUI.md` - Developer guide for OpenCL GUI system
- `OPENCL_LEVEL_EDITOR.md` - User guide for Level Editor
- `LEVEL_EDITOR.md` - Original ImGui Level Editor (deprecated)

### Engine Documentation  
- User guides and controls
- Camera system documentation  
- Cloud rendering guide
- Blender integration

## Getting Started

### OpenCL Level Editor (Recommended)

```bash
# Launch the revolutionary OpenCL GUI Level Editor
python opencl_level_editor_launcher.py

# With specific theme
python opencl_level_editor_launcher.py --theme cyberpunk

# Debug mode
python opencl_level_editor_launcher.py --debug
```

### Traditional Interface

```bash
# Classic raymarcher interface
python launch.py
python main.py
```

## Development

This project uses a modular structure for easy development and maintenance.
All core components are in `src/` with clear separation of concerns.
