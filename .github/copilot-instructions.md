<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Python Raymarching/Raytracing Project with OpenCL

This workspace contains a complete Python implementation of a real-time raymarching/raytracing renderer using OpenCL for GPU acceleration and Pygame for the GUI interface.

## Project Status: ✅ COMPLETED

All implementation phases have been successfully completed:

✅ **Project Setup** - Complete project structure created
✅ **Core Implementation** - Full raymarching engine with OpenCL
✅ **GUI Interface** - Interactive Pygame interface with camera controls  
✅ **Dependencies** - All required packages installed (pyopencl, numpy, pygame, Pillow)
✅ **Testing** - Application launches and runs real-time raymarching demo
✅ **Documentation** - Complete README.md and usage guide

## Architecture

- **main.py** - Application entry point with dependency checks
- **raymarcher.py** - OpenCL raymarching engine with camera controls
- **gui.py** - Pygame GUI with real-time rendering and input handling
- **shaders/raymarch.cl** - OpenCL kernel implementing raymarching algorithms
- **scenes/** - Scene definitions and 3D object management

## Features

- Real-time GPU-accelerated raymarching using OpenCL
- Interactive 3D camera with full movement and rotation controls
- Multiple primitive types (spheres, boxes, torus) with animations
- Dynamic lighting with diffuse and specular reflection
- FPS monitoring and performance tracking
- Multiple scene configurations
- Fullscreen mode support with dynamic resolution scaling
- Resizable window support
- Multiple resolution presets (800x600 to 4K)
- Command-line arguments for custom launch configurations

## Launch Instructions

Run the application with:
```bash
# Default windowed mode
python main.py

# Fullscreen with native resolution  
python main.py --fullscreen --auto-resolution

# Quick launcher
python launcher.py fullscreen
```

Controls:
- WASD - Camera movement
- Mouse/Arrow keys - Camera rotation
- F1-F3 - Toggle display options
- F11 - Toggle fullscreen
- F12 - Cycle resolution
- R - Reset camera
- ESC - Exit
	<!--
	Ensure that the previous step has been marked as completed.
	Call project setup tool with projectType parameter.
	Run scaffolding command to create project files and folders.
	Use '.' as the working directory.
	If no appropriate projectType is available, search documentation using available tools.
	Otherwise, create the project structure manually using available file creation tools.
	-->

- [ ] Customize the Project
	<!--
	Verify that all previous steps have been completed successfully and you have marked the step as completed.
	Develop a plan to modify codebase according to user requirements.
	Apply modifications using appropriate tools and user-provided references.
	Skip this step for "Hello World" projects.
	-->

- [ ] Install Required Extensions
	<!-- ONLY install extensions provided mentioned in the get_project_setup_info. Skip this step otherwise and mark as completed. -->

- [ ] Compile the Project
	<!--
	Verify that all previous steps have been completed.
	Install any missing dependencies.
	Run diagnostics and resolve any issues.
	Check for markdown files in project folder for relevant instructions on how to do this.
	-->

- [ ] Create and Run Task
	<!--
	Verify that all previous steps have been completed.
	Check https://code.visualstudio.com/docs/debugtest/tasks to determine if the project needs a task. If so, use the create_and_run_task to create and launch a task based on package.json, README.md, and project structure.
	Skip this step otherwise.
	 -->

- [ ] Launch the Project
	<!--
	Verify that all previous steps have been completed.
	Prompt user for debug mode, launch only if confirmed.
	 -->

- [ ] Ensure Documentation is Complete
	<!--
	Verify that all previous steps have been completed.
	Verify that README.md and the copilot-instructions.md file in the .github directory exists and contains current project information.
	Clean up the copilot-instructions.md file in the .github directory by removing all HTML comments.
	 -->
