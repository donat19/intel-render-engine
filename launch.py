#!/usr/bin/env python3
"""
Intel Render Engine - Entry Point

Simple entry point that launches the universal launcher.
This file should stay at the project root for easy access.

Usage:
  python launch.py                    # Interactive mode
  python launch.py clouds             # Launch cloud scene
  python launch.py demo --no-hdr      # Launch demo in LDR mode
  python launch.py --help             # Show all options
"""

import sys
import os

# Add src directory to path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

if __name__ == "__main__":
    from src.launchers.universal_launcher import main
    sys.exit(main())
