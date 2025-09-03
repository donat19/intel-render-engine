# Intel Render Engine

A high-performance real-time raymarching/raytracing engine with advanced volumetric cloud rendering and HDR support.

## Quick Start

```bash
# Interactive launcher with all options
python launch.py

# Launch cloud scene with HDR
python launch.py clouds

# Launch demo scene in LDR mode  
python launch.py demo --no-hdr

# Show all available options
python launch.py --help
```

## Project Structure

```
├── launch.py              # Main entry point
├── main.py                # Core application
├── requirements.txt       # Python dependencies
├── src/                   # Source code
│   ├── core/              # Core engine components
│   │   ├── raymarcher.py  # Main raymarching engine
│   │   └── camera.py      # 3D camera system
│   ├── gui/               # User interface
│   │   └── gui.py         # Pygame-based GUI
│   ├── scenes/            # Scene definitions
│   │   └── scenes.py      # Available scenes
│   ├── shaders/           # OpenCL compute shaders
│   │   ├── raymarch_hdr.cl           # HDR raymarching
│   │   ├── volumetric_clouds_hdr.cl  # HDR cloud rendering
│   │   └── advanced_clouds_hdr.cl    # Advanced cloud physics
│   └── launchers/         # Launch utilities
│       └── universal_launcher.py     # Universal launcher
├── docs/                  # Documentation
├── tools/                 # Development tools
└── examples/              # Example scenes
```

## Features

- **Real-time Raymarching**: GPU-accelerated distance field rendering
- **Advanced Camera System**: Quaternion-based 3D camera with smooth movement
- **HDR Rendering**: High Dynamic Range with multiple tone mapping operators
- **Volumetric Clouds**: Physically-based cloud rendering with atmospheric scattering
- **Multiple Scenes**: Demo, minimal, complex, and cloud scenes
- **Interactive Controls**: Mouse and keyboard controls with customizable sensitivity

## Requirements

- Python 3.8+
- OpenCL compatible GPU
- See `requirements.txt` for Python dependencies

## Documentation

See the `docs/` folder for detailed documentation:
- User guides and controls
- Camera system documentation  
- Cloud rendering guide
- Blender integration

## Development

This project uses a modular structure for easy development and maintenance.
All core components are in `src/` with clear separation of concerns.
