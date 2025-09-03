#!/usr/bin/env python3
"""
Quick launcher for the Raymarching Demo with presets

Usage:
  python cloud_launcher.py          # Launch with cloud scene in windowed mode
  python cloud_launcher.py clouds   # Launch cloud scene
  python cloud_launcher.py demo     # Launch demo scene
  python cloud_launcher.py fullscreen # Launch cloud scene in fullscreen
"""

import sys
import subprocess
import os

def main():
    """Launch the raymarching demo with cloud scene"""
    
    # Default arguments
    args = ['python', 'main.py']
    
    # Parse simple command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == 'fullscreen':
            args.extend(['--fullscreen', '--auto-resolution', '--scene', 'clouds'])
            print("Launching cloud scene in fullscreen mode...")
        elif arg == 'clouds':
            args.extend(['--scene', 'clouds'])
            print("Launching cloud scene...")
        elif arg == 'demo':
            args.extend(['--scene', 'demo'])
            print("Launching demo scene...")
        elif arg == 'minimal':
            args.extend(['--scene', 'minimal'])
            print("Launching minimal scene...")
        elif arg == 'complex':
            args.extend(['--scene', 'complex'])
            print("Launching complex scene...")
        else:
            print(f"Unknown option: {arg}")
            print("Available options: clouds, demo, minimal, complex, fullscreen")
            return
    else:
        # Default to cloud scene
        args.extend(['--scene', 'clouds'])
        print("Launching cloud scene (default)...")
    
    print("Controls:")
    print("  WASD - Move camera")
    print("  Mouse - Look around") 
    print("  TAB - Cycle scenes")
    print("  C - Switch to cloud scene")
    print("  R - Reset camera")
    print("  F11 - Toggle fullscreen")
    print("  ESC - Exit")
    print("")
    
    # Launch the main application
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching application: {e}")
    except KeyboardInterrupt:
        print("Launcher interrupted")

if __name__ == "__main__":
    main()
