#!/usr/bin/env python3
"""
Quick launch scripts for Raymarching Demo
"""

import os
import sys

def launch_fullscreen():
    """Launch in fullscreen mode with native resolution"""
    os.system('python main.py --fullscreen --auto-resolution')

def launch_hd():
    """Launch in 1920x1080 resolution"""
    os.system('python main.py --resolution 1920x1080')

def launch_4k():
    """Launch in 4K resolution if supported"""
    os.system('python main.py --resolution 3840x2160')

def show_help():
    """Show available launch options"""
    print("Raymarching Demo - Launch Options:")
    print("1. Fullscreen (native resolution): python launcher.py fullscreen")
    print("2. HD (1920x1080): python launcher.py hd") 
    print("3. 4K (3840x2160): python launcher.py 4k")
    print("4. Custom: python main.py --resolution WIDTHxHEIGHT")
    print("5. Windowed: python main.py --width WIDTH --height HEIGHT")
    print("6. Help: python main.py --help")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "fullscreen" or command == "fs":
        launch_fullscreen()
    elif command == "hd":
        launch_hd()
    elif command == "4k":
        launch_4k()
    elif command == "help" or command == "-h":
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()
