# Volumetric Cloud Scene Documentation

## Overview
The cloud rendering engine branch now includes a realistic volumetric cloud scene that demonstrates advanced ray marching techniques for rendering atmospheric effects.

## Features

### Volumetric Cloud Rendering
- **Noise-based density fields**: Uses fractal Brownian motion (FBM) with multiple octaves for realistic cloud shapes
- **Multiple cloud layers**: Three different cloud clusters with varying densities and sizes
- **Animated drift**: Clouds slowly drift in different directions over time
- **Volumetric lighting**: Proper light attenuation and scattering through cloud volumes
- **Atmospheric scattering**: Rayleigh scattering approximation for realistic lighting

### Technical Implementation
- **Custom OpenCL kernel**: `volumetric_clouds.cl` implements all cloud rendering logic
- **Hybrid rendering**: Solid objects (ground, mountains) + volumetric clouds + sky
- **Performance optimized**: 64 volume samples with 8 shadow samples for good quality/performance balance

## Scene Controls

### Camera Movement
- **WASD**: Move camera forward/backward/left/right
- **Space/Shift**: Move camera up/down
- **Mouse**: Look around (when mouse is captured)
- **Arrow keys**: Look around (alternative to mouse)

### Scene Controls
- **TAB**: Cycle through all available scenes
- **C**: Switch directly to cloud scene
- **R**: Reset camera to scene default position

### Display Options
- **F1**: Toggle FPS display
- **F2**: Toggle camera info (shows current scene name)
- **F3**: Toggle mouse capture
- **F11**: Toggle fullscreen
- **F12**: Cycle through resolution presets

## Cloud Scene Details

### Camera Setup
- **Start position**: (0, 5, 20) - positioned to give good view of clouds
- **Start angles**: (0, -0.2, 0) - slightly looking down at clouds

### Cloud Configurations

#### Main Cloud Cluster
- **Position**: (0, 8, 0)
- **Size**: 15×6×10 units
- **Density**: 0.3
- **Features**: Large, puffy cumulus-style clouds

#### Secondary Cloud Cluster
- **Position**: (-10, 12, -5)  
- **Size**: 8×4×8 units
- **Density**: 0.25
- **Features**: Smaller, wispy clouds at higher altitude

#### Tertiary Cloud Cluster
- **Position**: (12, 10, 5)
- **Size**: 6×5×6 units  
- **Density**: 0.4
- **Features**: Dense, compact clouds

### Lighting Setup
- **Sun light**: (20, 30, 10) with warm white color (1.0, 0.95, 0.8)
- **Sky light**: (0, 50, 0) with cool blue color (0.5, 0.7, 1.0)
- **Dynamic shadows**: Clouds cast shadows on themselves and ground

### Terrain
- **Ground plane**: Large flat surface at y=-1
- **Mountains**: Three box-shaped peaks for depth and scale reference

## Usage Examples

### Launch Cloud Scene Directly
```bash
python cloud_launcher.py clouds
```

### Launch Cloud Scene in Fullscreen
```bash
python cloud_launcher.py fullscreen
```

### Launch with Specific Parameters
```bash
python main.py --scene clouds --width 1920 --height 1080
```

## Technical Notes

### Shader Compatibility
The volumetric cloud shader uses custom `fract3()` and `fract1()` functions instead of OpenCL's built-in `fract()` to ensure compatibility across different OpenCL implementations.

### Performance Considerations
- Volume rendering is computationally expensive
- 64 volume samples provide good quality but can be reduced for better performance
- Shadow samples can be reduced from 8 to 4 for faster rendering on slower hardware

### Noise Implementation
- Uses hash-based noise for GPU efficiency
- Fractal Brownian Motion with 3-4 octaves for detail
- Multiple noise scales create realistic cloud-like density patterns

## Future Enhancements
- Weather system integration
- Time-of-day lighting changes
- More cloud types (cirrus, stratus, cumulonimbus)
- Precipitation effects
- Cloud-ground interaction
- Improved atmospheric scattering model
