#!/usr/bin/env python3
"""
Raymarching/Raytracing Demo with OpenCL and Pygame

A real-time 3D renderer using raymarching techniques implemented in OpenCL
for GPU acceleration, with an interactive GUI built using Pygame.

Author: AI Assistant
Date: 2025
"""

import sys
import os
import argparse

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import pyopencl
    except ImportError:
        missing_deps.append("pyopencl")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import pygame
    except ImportError:
        missing_deps.append("pygame")
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install them using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_opencl():
    """Check if OpenCL is available"""
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        if not platforms:
            print("No OpenCL platforms found!")
            return False
        
        print("Available OpenCL platforms:")
        for i, platform in enumerate(platforms):
            print(f"  {i}: {platform.name}")
            devices = platform.get_devices()
            for j, device in enumerate(devices):
                print(f"    Device {j}: {device.name} ({device.type})")
        
        return True
    
    except Exception as e:
        print(f"OpenCL check failed: {e}")
        return False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Raymarching/Raytracing Demo with OpenCL and HDR')
    parser.add_argument('--width', type=int, default=800, help='Window width (default: 800)')
    parser.add_argument('--height', type=int, default=600, help='Window height (default: 600)')
    parser.add_argument('--fullscreen', action='store_true', help='Start in fullscreen mode')
    parser.add_argument('--auto-resolution', action='store_true', help='Use native screen resolution')
    parser.add_argument('--resolution', type=str, help='Set specific resolution (e.g., 1920x1080)')
    parser.add_argument('--scene', type=str, default='demo', 
                      help='Initial scene to load (demo, minimal, complex, clouds, advanced_clouds)')
    parser.add_argument('--no-hdr', action='store_true', help='Disable HDR rendering')
    parser.add_argument('--exposure', type=float, default=1.0, help='Initial HDR exposure (default: 1.0)')
    parser.add_argument('--tone-mapping', type=str, default='reinhard', 
                      choices=['linear', 'reinhard', 'filmic', 'aces'],
                      help='Initial tone mapping mode (default: reinhard)')
    return parser.parse_args()

def main():
    """Main application entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    print("Raymarching/Raytracing Demo with OpenCL and HDR")
    print("=" * 45)
    
    # Handle resolution argument
    width, height = args.width, args.height
    if args.resolution:
        try:
            res_parts = args.resolution.split('x')
            if len(res_parts) == 2:
                width, height = int(res_parts[0]), int(res_parts[1])
                print(f"Using specified resolution: {width}x{height}")
        except ValueError:
            print(f"Invalid resolution format: {args.resolution}. Using default.")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check OpenCL availability
    if not check_opencl():
        print("OpenCL is required but not available!")
        sys.exit(1)
    
    # Import and run the GUI
    try:
        from gui import RaymarchGUI
        
        # HDR settings
        enable_hdr = not args.no_hdr
        print(f"HDR rendering: {'Enabled' if enable_hdr else 'Disabled'}")
        if enable_hdr:
            print(f"Initial exposure: {args.exposure}")
            print(f"Initial tone mapping: {args.tone_mapping}")
        
        # Create and run the application
        print("\\nInitializing application...")
        if args.auto_resolution:
            print("Using native screen resolution")
        elif args.fullscreen:
            print("Starting in fullscreen mode")
            
        gui = RaymarchGUI(
            width=width, 
            height=height, 
            title="Raymarching Demo - OpenCL HDR",
            fullscreen=args.fullscreen,
            auto_resolution=args.auto_resolution,
            scene=args.scene,
            enable_hdr=enable_hdr
        )
        
        # Set initial HDR parameters
        if enable_hdr and hasattr(gui.raymarcher, 'enable_hdr') and gui.raymarcher.enable_hdr:
            gui.raymarcher.set_exposure(args.exposure)
            gui.raymarcher.set_tone_mapping(args.tone_mapping)
        
        gui.run()
        
    except KeyboardInterrupt:
        print("\\nApplication interrupted by user")
    except Exception as e:
        print(f"\\nApplication error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Application finished")

if __name__ == "__main__":
    main()
