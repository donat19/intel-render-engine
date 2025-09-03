#!/usr/bin/env python3
"""
Universal Launcher for Intel Render Engine

A comprehensive launcher that handles all rendering modes:
- LDR (Low Dynamic Range) rendering
- HDR (High Dynamic Range) rendering  
- Multiple scenes (demo, minimal, complex, clouds)
- Various display modes and resolutions
- Customizable parameters

Usage Examples:
  python universal_launcher.py                    # Interactive mode
  python universal_launcher.py clouds             # Launch cloud scene with HDR
  python universal_launcher.py demo --no-hdr      # Launch demo scene with LDR
  python universal_launcher.py fullscreen         # Launch in fullscreen HDR
  python universal_launcher.py clouds --exposure 1.5 --tone-mapping filmic
  python universal_launcher.py 4k --scene complex
  python universal_launcher.py --help            # Show detailed help

Author: AI Assistant
Date: September 2025
"""

import sys
import subprocess
import os
import argparse
from typing import List, Optional

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

class UniversalLauncher:
    """Universal launcher for the Intel Render Engine"""
    
    SCENES = ['demo', 'minimal', 'complex', 'clouds', 'advanced_clouds']
    TONE_MAPPING_MODES = ['linear', 'reinhard', 'filmic', 'aces']
    RESOLUTIONS = {
        'hd': '1280x720',
        'fhd': '1920x1080', 
        '1440p': '2560x1440',
        '4k': '3840x2160',
        '8k': '7680x4320'
    }
    
    def __init__(self):
        self.command = ['python', os.path.join(project_root, 'main.py')]
        
    def add_scene(self, scene: str):
        """Add scene parameter"""
        if scene in self.SCENES:
            self.command.extend(['--scene', scene])
        else:
            print(f"Warning: Unknown scene '{scene}'. Available: {', '.join(self.SCENES)}")
            
    def add_display_mode(self, mode: str, resolution: Optional[str] = None):
        """Add display mode parameters"""
        if mode == 'fullscreen':
            self.command.append('--fullscreen')
            self.command.append('--auto-resolution')
        elif mode == 'windowed' and resolution:
            if 'x' in resolution:
                # Direct resolution like 1920x1080
                self.command.extend(['--resolution', resolution])
            elif resolution in self.RESOLUTIONS:
                # Preset resolution like 'hd', '4k'
                self.command.extend(['--resolution', self.RESOLUTIONS[resolution]])
            else:
                print(f"Warning: Unknown resolution '{resolution}'")
                
    def add_hdr_settings(self, enable_hdr: bool = True, exposure: float = 1.0, 
                        tone_mapping: str = 'reinhard', gamma: float = 2.2):
        """Add HDR parameters"""
        if not enable_hdr:
            self.command.append('--no-hdr')
        else:
            self.command.extend(['--exposure', str(exposure)])
            self.command.extend(['--tone-mapping', tone_mapping])
            
    def add_window_size(self, width: int, height: int):
        """Add specific window dimensions"""
        self.command.extend(['--width', str(width)])
        self.command.extend(['--height', str(height)])
        
    def launch(self, show_controls: bool = True):
        """Launch the render engine with configured parameters"""
        
        # Determine if HDR is enabled
        hdr_enabled = '--no-hdr' not in self.command
        scene = 'demo'  # default
        
        # Extract scene name for display
        if '--scene' in self.command:
            scene_idx = self.command.index('--scene')
            if scene_idx + 1 < len(self.command):
                scene = self.command[scene_idx + 1]
        
        # Show launch information
        mode = "HDR" if hdr_enabled else "LDR"
        display_mode = "Fullscreen" if '--fullscreen' in self.command else "Windowed"
        
        print(f"🚀 Launching Intel Render Engine")
        print(f"   Rendering Mode: {mode}")
        print(f"   Scene: {scene.title()}")
        print(f"   Display: {display_mode}")
        
        if hdr_enabled and '--exposure' in self.command:
            exp_idx = self.command.index('--exposure')
            if exp_idx + 1 < len(self.command):
                exposure = self.command[exp_idx + 1]
                print(f"   Exposure: {exposure}")
                
        if hdr_enabled and '--tone-mapping' in self.command:
            tm_idx = self.command.index('--tone-mapping')
            if tm_idx + 1 < len(self.command):
                tone_mapping = self.command[tm_idx + 1]
                print(f"   Tone Mapping: {tone_mapping.title()}")
        
        print("")
        
        if show_controls:
            self._show_controls(hdr_enabled)
        
        try:
            result = subprocess.run(self.command, cwd=os.path.dirname(__file__))
            return result.returncode
        except Exception as e:
            print(f"❌ Error launching application: {e}")
            return 1
            
    def _show_controls(self, hdr_enabled: bool):
        """Show control information"""
        print("🎮 Controls:")
        print("   WASD - Move camera")
        print("   Mouse/Arrow keys - Look around")
        print("   F1 - Toggle FPS display")
        print("   F2 - Toggle camera info")
        print("   F3 - Toggle HDR info" if hdr_enabled else "   F3 - Toggle render info")
        print("   F4 - Toggle mouse capture")
        print("   F11 - Toggle fullscreen")
        print("   F12 - Cycle resolution")
        print("   TAB - Cycle scenes")
        print("   C - Switch to cloud scene")
        print("   R - Reset camera")
        
        if hdr_enabled:
            print("")
            print("🌟 HDR Controls:")
            print("   +/- - Adjust exposure")
            print("   T - Cycle tone mapping")
            print("   [ ] - Adjust gamma")
        
        print("   ESC - Exit")
        print("")

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Universal Launcher for Intel Render Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Interactive mode
  %(prog)s clouds                       # Launch cloud scene with HDR
  %(prog)s demo --no-hdr                # Launch demo scene with LDR
  %(prog)s fullscreen                   # Launch in fullscreen HDR
  %(prog)s clouds --exposure 1.5        # Cloud scene with custom exposure
  %(prog)s 4k --scene complex           # 4K resolution with complex scene
  %(prog)s --width 1280 --height 720    # Custom window size

Available scenes: demo, minimal, complex, clouds
Available resolutions: hd, fhd, 1440p, 4k, 8k
Available tone mapping: linear, reinhard, filmic, aces
        """
    )
    
    # Scene selection
    parser.add_argument('mode', nargs='?', choices=UniversalLauncher.SCENES + ['fullscreen'] + list(UniversalLauncher.RESOLUTIONS.keys()),
                       help='Scene to launch or display mode')
    
    # Display options
    parser.add_argument('--fullscreen', action='store_true',
                       help='Launch in fullscreen mode')
    parser.add_argument('--resolution', 
                       help='Resolution (e.g., 1920x1080 or preset like hd, 4k)')
    parser.add_argument('--width', type=int,
                       help='Window width')
    parser.add_argument('--height', type=int,
                       help='Window height')
    parser.add_argument('--auto-resolution', action='store_true',
                       help='Use native screen resolution in fullscreen')
    
    # Scene options
    parser.add_argument('--scene', choices=UniversalLauncher.SCENES,
                       help='Override scene selection')
    
    # HDR options
    parser.add_argument('--no-hdr', action='store_true',
                       help='Disable HDR rendering (use LDR)')
    parser.add_argument('--exposure', type=float, default=1.0,
                       help='HDR exposure value (default: 1.0)')
    parser.add_argument('--tone-mapping', choices=UniversalLauncher.TONE_MAPPING_MODES,
                       default='reinhard', help='HDR tone mapping mode (default: reinhard)')
    
    # Launcher options
    parser.add_argument('--no-controls', action='store_true',
                       help='Skip showing control information')
    parser.add_argument('--interactive', action='store_true',
                       help='Force interactive mode')
    
    return parser

def interactive_mode():
    """Interactive launcher mode"""
    print("🎯 Intel Render Engine - Universal Launcher")
    print("=" * 50)
    
    launcher = UniversalLauncher()
    
    # Scene selection
    print("\n📋 Available scenes:")
    for i, scene in enumerate(UniversalLauncher.SCENES, 1):
        print(f"  {i}. {scene.title()}")
    
    while True:
        try:
            choice = input(f"\nSelect scene (1-{len(UniversalLauncher.SCENES)}) [1]: ").strip()
            if not choice:
                choice = '1'
            scene_idx = int(choice) - 1
            if 0 <= scene_idx < len(UniversalLauncher.SCENES):
                scene = UniversalLauncher.SCENES[scene_idx]
                launcher.add_scene(scene)
                break
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Please enter a number.")
    
    # HDR selection
    hdr_choice = input("\n🌟 Enable HDR rendering? [Y/n]: ").strip().lower()
    enable_hdr = hdr_choice not in ['n', 'no', 'false']
    
    exposure = 1.0
    tone_mapping = 'reinhard'
    
    if enable_hdr:
        # HDR settings
        exp_input = input("   Exposure (0.1-5.0) [1.0]: ").strip()
        if exp_input:
            try:
                exposure = float(exp_input)
                exposure = max(0.1, min(5.0, exposure))
            except ValueError:
                print("   Using default exposure: 1.0")
        
        print("   Tone mapping modes:")
        for i, mode in enumerate(UniversalLauncher.TONE_MAPPING_MODES, 1):
            print(f"     {i}. {mode.title()}")
        
        tm_input = input("   Select tone mapping [2 - Reinhard]: ").strip()
        if tm_input:
            try:
                tm_idx = int(tm_input) - 1
                if 0 <= tm_idx < len(UniversalLauncher.TONE_MAPPING_MODES):
                    tone_mapping = UniversalLauncher.TONE_MAPPING_MODES[tm_idx]
            except ValueError:
                pass
    
    launcher.add_hdr_settings(enable_hdr, exposure, tone_mapping)
    
    # Display mode selection
    print("\n🖥️  Display mode:")
    print("  1. Windowed (800x600)")
    print("  2. Windowed HD (1280x720)")
    print("  3. Windowed FHD (1920x1080)")
    print("  4. Fullscreen (native resolution)")
    print("  5. Custom size")
    
    display_choice = input("Select display mode [1]: ").strip()
    if not display_choice:
        display_choice = '1'
    
    if display_choice == '1':
        launcher.add_window_size(800, 600)
    elif display_choice == '2':
        launcher.add_display_mode('windowed', 'hd')
    elif display_choice == '3':
        launcher.add_display_mode('windowed', 'fhd')
    elif display_choice == '4':
        launcher.add_display_mode('fullscreen')
    elif display_choice == '5':
        try:
            width = int(input("   Width: "))
            height = int(input("   Height: "))
            launcher.add_window_size(width, height)
        except ValueError:
            print("   Invalid input, using default 800x600")
            launcher.add_window_size(800, 600)
    
    return launcher

def main():
    """Main launcher function"""
    parser = create_parser()
    
    # Handle simple positional arguments like "clouds", "fullscreen", "4k"
    if len(sys.argv) == 1:
        # No arguments - interactive mode
        launcher = interactive_mode()
        return launcher.launch()
    
    # Quick launch modes
    if len(sys.argv) == 2 and sys.argv[1] in ['help', '--help', '-h']:
        parser.print_help()
        return 0
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.interactive:
        launcher = interactive_mode()
        return launcher.launch(not args.no_controls)
    
    # Create launcher
    launcher = UniversalLauncher()
    
    # Handle positional argument
    mode = args.mode  # This is the positional argument (scene, fullscreen, or resolution)
    override_scene = args.scene  # This is the --scene flag
    
    if mode:
        if mode == 'fullscreen':
            launcher.add_display_mode('fullscreen')
            # Use override scene if provided, otherwise default to clouds
            scene_to_use = override_scene if override_scene else 'clouds'
            launcher.add_scene(scene_to_use)
        elif mode in UniversalLauncher.RESOLUTIONS:
            # Resolution preset like '4k', 'hd'
            launcher.add_display_mode('windowed', mode)
            # Use override scene if provided, otherwise default to demo
            scene_to_use = override_scene if override_scene else 'demo'
            launcher.add_scene(scene_to_use)
        else:
            # Scene name as positional argument
            launcher.add_scene(mode)
    elif override_scene:
        # Only --scene flag provided, no positional argument
        launcher.add_scene(override_scene)
    
    # Display mode
    if args.fullscreen:
        launcher.add_display_mode('fullscreen')
    elif args.resolution:
        launcher.add_display_mode('windowed', args.resolution)
    elif args.width and args.height:
        launcher.add_window_size(args.width, args.height)
    
    # Auto resolution
    if args.auto_resolution:
        launcher.command.append('--auto-resolution')
    
    # HDR settings
    launcher.add_hdr_settings(
        enable_hdr=not args.no_hdr,
        exposure=args.exposure,
        tone_mapping=args.tone_mapping
    )
    
    return launcher.launch(not args.no_controls)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n🛑 Launcher interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        sys.exit(1)
