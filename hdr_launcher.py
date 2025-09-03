#!/usr/bin/env python3
"""
HDR Cloud Launcher for Raymarching Demo

Quick launcher for HDR cloud scene with preset configurations.
"""

import sys
import subprocess
import os

def launch_hdr_demo(scene='clouds', mode='windowed', resolution=None, exposure=1.0, tone_mapping='reinhard'):
    """Launch the HDR raymarching demo with specified parameters"""
    
    # Build command
    cmd = ['python', 'main.py']
    
    # Scene selection
    cmd.extend(['--scene', scene])
    
    # HDR settings
    cmd.extend(['--exposure', str(exposure)])
    cmd.extend(['--tone-mapping', tone_mapping])
    
    # Display mode
    if mode == 'fullscreen':
        cmd.append('--fullscreen')
        cmd.append('--auto-resolution')
    elif resolution:
        cmd.extend(['--resolution', resolution])
    
    print(f"Launching HDR {scene} scene...")
    print("HDR Controls:")
    print("  +/- - Adjust exposure")
    print("  T - Cycle tone mapping modes")
    print("  [ ] - Adjust gamma")
    print("  F3 - Toggle HDR info display")
    print("  TAB - Cycle scenes")
    print("  C - Switch to cloud scene")
    print("  R - Reset camera")
    print("  F11 - Toggle fullscreen")
    print("  ESC - Exit")
    print("")
    
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return result.returncode
    except Exception as e:
        print(f"Error launching application: {e}")
        return 1

def main():
    """Main launcher function"""
    if len(sys.argv) < 2:
        print("HDR Raymarching Demo Launcher")
        print("Usage:")
        print("  python hdr_launcher.py clouds")
        print("  python hdr_launcher.py fullscreen")
        print("  python hdr_launcher.py demo")
        print("  python hdr_launcher.py clouds --exposure 1.5 --tone-mapping filmic")
        print("  python hdr_launcher.py clouds --resolution 1920x1080")
        print("")
        print("Available scenes: demo, minimal, complex, clouds")
        print("Available tone mapping: linear, reinhard, filmic, aces")
        sys.exit(1)
    
    # Parse arguments
    scene = 'clouds'
    mode = 'windowed'
    resolution = None
    exposure = 1.0
    tone_mapping = 'reinhard'
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == 'fullscreen':
            mode = 'fullscreen'
        elif arg in ['demo', 'minimal', 'complex', 'clouds']:
            scene = arg
        elif arg == '--exposure' and i + 1 < len(args):
            exposure = float(args[i + 1])
            i += 1
        elif arg == '--tone-mapping' and i + 1 < len(args):
            tone_mapping = args[i + 1]
            i += 1
        elif arg == '--resolution' and i + 1 < len(args):
            resolution = args[i + 1]
            i += 1
        
        i += 1
    
    # Launch the demo
    return launch_hdr_demo(scene, mode, resolution, exposure, tone_mapping)

if __name__ == "__main__":
    sys.exit(main())
