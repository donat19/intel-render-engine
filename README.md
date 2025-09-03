# Python Raymarching/Raytracing with OpenCL

A real-time raymarching renderer using OpenCL for GPU acceleration with a GUI interface.

## Features

- Real-time raymarching/raytracing using OpenCL
- Interactive GUI using Pygame
- Support for various 3D primitives (spheres, boxes, torus)
- Real-time parameter adjustment
- GPU-accelerated rendering

## Requirements

- Python 3.8+
- OpenCL-compatible GPU/CPU
- Required packages listed in requirements.txt

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
# Default windowed mode (800x600)
python main.py

# Fullscreen with native resolution
python main.py --fullscreen --auto-resolution

# Specific resolution
python main.py --resolution 1920x1080

# Custom window size
python main.py --width 1280 --height 720
```

## Quick Launch
```bash
# Use launcher for quick access
python launcher.py fullscreen  # Native resolution fullscreen
python launcher.py hd         # 1920x1080 resolution  
python launcher.py 4k         # 4K resolution
```

## Controls

- Arrow keys: Rotate camera
- WASD: Move camera
- Mouse: Adjust parameters in real-time
- F11: Toggle fullscreen
- F12: Cycle through resolution presets
- ESC: Exit

## Project Structure

- `main.py` - Main application entry point
- `raymarcher.py` - OpenCL raymarching engine
- `gui.py` - GUI interface using Pygame
- `shaders/` - OpenCL kernel code
- `scenes/` - Scene definitions
