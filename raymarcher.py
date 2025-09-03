import pyopencl as cl
import numpy as np
import time
import os
from typing import Tuple, Optional
from scenes.scenes import get_scene

class RayMarcher:
    def __init__(self, width: int = 800, height: int = 600, scene_name: str = 'demo', enable_hdr: bool = True):
        self.width = width
        self.height = height
        self.scene_name = scene_name
        self.enable_hdr = enable_hdr
        
        # HDR settings
        self.exposure = 1.0
        self.tone_mapping_mode = 'reinhard'  # 'linear', 'reinhard', 'filmic', 'aces'
        self.gamma = 2.2
        
        # Initialize OpenCL
        self.context = cl.create_some_context(interactive=False)
        self.queue = cl.CommandQueue(self.context)
        
        # Load scene
        self.scene = get_scene(scene_name)
        
        # Load and compile appropriate kernel
        self._load_kernel()
        
        # Create buffers
        if enable_hdr:
            # HDR buffer (float4)
            self.hdr_buffer = cl.Buffer(self.context, cl.mem_flags.READ_WRITE, 
                                      width * height * 4 * 4)  # float4 (16 bytes per pixel)
            # LDR output buffer (uchar4)
            self.output_buffer = cl.Buffer(self.context, cl.mem_flags.WRITE_ONLY, 
                                         width * height * 4)  # RGBA uchar
            # HDR array for CPU processing
            self.hdr_array = np.zeros((height, width, 4), dtype=np.float32)
        else:
            # Standard LDR buffer
            self.output_buffer = cl.Buffer(self.context, cl.mem_flags.WRITE_ONLY, 
                                         width * height * 4)  # RGBA
        
        # Camera parameters (use scene defaults)
        self.camera_pos = self.scene.camera_start_pos.copy()
        self.camera_angles = self.scene.camera_start_angles.copy()
        
        # Animation parameters
        self.start_time = time.time()
        
        # Output array
        self.output_array = np.zeros((height, width, 4), dtype=np.uint8)
        
        print(f"Initialized RayMarcher with scene: {self.scene.name}")
        print(f"HDR enabled: {enable_hdr}")
        print(f"Camera start position: {self.camera_pos}")
        print(f"Camera start angles: {self.camera_angles}")
    
    def _load_kernel(self):
        """Load and compile the appropriate OpenCL kernel based on scene and HDR settings"""
        if self.scene_name == 'clouds':
            if self.enable_hdr:
                kernel_path = os.path.join(os.path.dirname(__file__), 'shaders', 'volumetric_clouds_hdr.cl')
                kernel_name = 'volumetric_clouds_hdr_kernel'
            else:
                kernel_path = os.path.join(os.path.dirname(__file__), 'shaders', 'volumetric_clouds.cl')
                kernel_name = 'volumetric_clouds_kernel'
        else:
            if self.enable_hdr:
                kernel_path = os.path.join(os.path.dirname(__file__), 'shaders', 'raymarch_hdr.cl')
                kernel_name = 'raymarch_hdr_kernel'
            else:
                kernel_path = os.path.join(os.path.dirname(__file__), 'shaders', 'raymarch.cl')
                kernel_name = 'raymarch_kernel'
        
        try:
            with open(kernel_path, 'r') as f:
                kernel_source = f.read()
            
            self.program = cl.Program(self.context, kernel_source).build()
            self.kernel = getattr(self.program, kernel_name)
            
            # Load tone mapping kernel if HDR is enabled
            if self.enable_hdr:
                self.tone_map_kernel = self.program.tone_map_kernel
            
            print(f"Loaded kernel: {kernel_name} from {os.path.basename(kernel_path)}")
            
        except Exception as e:
            print(f"Error loading kernel: {e}")
            # Fallback to non-HDR versions
            if self.enable_hdr:
                print("Falling back to non-HDR rendering")
                self.enable_hdr = False
                self._load_kernel()
            else:
                raise
    
    def _create_camera_matrix(self) -> np.ndarray:
        """Create camera rotation matrix from angles"""
        pitch, yaw, roll = self.camera_angles
        
        # Rotation matrices
        cos_p, sin_p = np.cos(pitch), np.sin(pitch)
        cos_y, sin_y = np.cos(yaw), np.sin(yaw)
        cos_r, sin_r = np.cos(roll), np.sin(roll)
        
        # Combined rotation matrix (simplified for OpenCL)
        matrix = np.array([
            cos_y * cos_r, -cos_y * sin_r, sin_y, 0,
            sin_p * sin_y * cos_r + cos_p * sin_r, 
            -sin_p * sin_y * sin_r + cos_p * cos_r, 
            -sin_p * cos_y, 0,
            -cos_p * sin_y * cos_r + sin_p * sin_r,
            cos_p * sin_y * sin_r + sin_p * cos_r,
            cos_p * cos_y, 0,
            0, 0, 0, 1
        ], dtype=np.float32)
        
        return matrix
    
    def render(self) -> np.ndarray:
        """Render a frame and return RGBA array"""
        current_time = time.time() - self.start_time
        camera_matrix = self._create_camera_matrix()
        
        if self.enable_hdr:
            # HDR rendering pipeline
            return self._render_hdr(current_time, camera_matrix)
        else:
            # Standard LDR rendering pipeline
            return self._render_ldr(current_time, camera_matrix)
    
    def _render_ldr(self, current_time: float, camera_matrix: np.ndarray) -> np.ndarray:
        """Standard LDR rendering pipeline"""
        # Set kernel arguments
        self.kernel.set_args(
            self.output_buffer,
            np.int32(self.width),
            np.int32(self.height),
            np.float32(current_time),
            camera_matrix,
            self.camera_pos
        )
        
        # Execute kernel
        global_size = (self.width, self.height)
        cl.enqueue_nd_range_kernel(self.queue, self.kernel, global_size, None)
        
        # Read result
        cl.enqueue_copy(self.queue, self.output_array, self.output_buffer)
        self.queue.finish()
        
        return self.output_array
    
    def _render_hdr(self, current_time: float, camera_matrix: np.ndarray) -> np.ndarray:
        """HDR rendering pipeline with tone mapping"""
        # Step 1: Render to HDR buffer
        self.kernel.set_args(
            self.hdr_buffer,
            np.int32(self.width),
            np.int32(self.height),
            np.float32(current_time),
            camera_matrix,
            self.camera_pos
        )
        
        # Execute HDR rendering kernel
        global_size = (self.width, self.height)
        cl.enqueue_nd_range_kernel(self.queue, self.kernel, global_size, None)
        
        # Step 2: Apply tone mapping
        self.tone_map_kernel.set_args(
            self.hdr_buffer,          # Input HDR buffer
            self.output_buffer,       # Output LDR buffer
            np.int32(self.width),
            np.int32(self.height),
            np.float32(self.exposure),
            np.int32(self._get_tone_mapping_mode_id()),
            np.float32(self.gamma)
        )
        
        # Execute tone mapping kernel
        cl.enqueue_nd_range_kernel(self.queue, self.tone_map_kernel, global_size, None)
        
        # Read result
        cl.enqueue_copy(self.queue, self.output_array, self.output_buffer)
        self.queue.finish()
        
        return self.output_array
    
    def _get_tone_mapping_mode_id(self) -> int:
        """Convert tone mapping mode string to integer ID"""
        modes = {
            'linear': 0,
            'reinhard': 1,
            'filmic': 2,
            'aces': 3
        }
        return modes.get(self.tone_mapping_mode, 1)  # Default to Reinhard
    
    def move_camera(self, direction: str, speed: float = 0.1):
        """Move camera in specified direction"""
        if direction == 'forward':
            self.camera_pos[2] -= speed
        elif direction == 'backward':
            self.camera_pos[2] += speed
        elif direction == 'left':
            self.camera_pos[0] -= speed
        elif direction == 'right':
            self.camera_pos[0] += speed
        elif direction == 'up':
            self.camera_pos[1] += speed
        elif direction == 'down':
            self.camera_pos[1] -= speed
    
    def rotate_camera(self, pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0):
        """Rotate camera by specified angles"""
        self.camera_angles[0] += pitch
        self.camera_angles[1] += yaw
        self.camera_angles[2] += roll
        
        # Clamp pitch to avoid gimbal lock
        self.camera_angles[0] = np.clip(self.camera_angles[0], -np.pi/2, np.pi/2)
    
    def set_camera_position(self, x: float, y: float, z: float):
        """Set absolute camera position"""
        self.camera_pos = np.array([x, y, z], dtype=np.float32)
    
    def set_camera_angles(self, pitch: float, yaw: float, roll: float = 0.0):
        """Set absolute camera angles"""
        self.camera_angles = np.array([pitch, yaw, roll], dtype=np.float32)
    
    def get_camera_info(self) -> dict:
        """Get current camera information"""
        return {
            'position': self.camera_pos.copy(),
            'angles': self.camera_angles.copy(),
            'time': time.time() - self.start_time,
            'scene': self.scene.name
        }
    
    def switch_scene(self, scene_name: str):
        """Switch to a different scene"""
        if scene_name != self.scene_name:
            print(f"Switching from {self.scene_name} to {scene_name}")
            self.scene_name = scene_name
            self.scene = get_scene(scene_name)
            
            # Reset camera to scene defaults
            self.camera_pos = self.scene.camera_start_pos.copy()
            self.camera_angles = self.scene.camera_start_angles.copy()
            
            # Reload appropriate kernel
            self._load_kernel()
            
            print(f"Switched to scene: {self.scene.name}")
            print(f"Camera position: {self.camera_pos}")
    
    def reset_camera(self):
        """Reset camera to scene default position"""
        self.camera_pos = self.scene.camera_start_pos.copy()
        self.camera_angles = self.scene.camera_start_angles.copy()
        print(f"Camera reset to: pos={self.camera_pos}, angles={self.camera_angles}")
    
    def get_available_scenes(self) -> list:
        """Get list of available scene names"""
        from scenes.scenes import SCENES
        return list(SCENES.keys())
    
    # HDR Control Methods
    def adjust_exposure(self, delta: float):
        """Adjust exposure by delta amount"""
        self.exposure = max(0.1, min(10.0, self.exposure + delta))
        print(f"Exposure: {self.exposure:.2f}")
    
    def set_exposure(self, exposure: float):
        """Set absolute exposure value"""
        self.exposure = max(0.1, min(10.0, exposure))
        print(f"Exposure: {self.exposure:.2f}")
    
    def cycle_tone_mapping(self):
        """Cycle through tone mapping modes"""
        modes = ['linear', 'reinhard', 'filmic', 'aces']
        current_index = modes.index(self.tone_mapping_mode)
        next_index = (current_index + 1) % len(modes)
        self.tone_mapping_mode = modes[next_index]
        print(f"Tone mapping: {self.tone_mapping_mode}")
    
    def set_tone_mapping(self, mode: str):
        """Set tone mapping mode"""
        valid_modes = ['linear', 'reinhard', 'filmic', 'aces']
        if mode in valid_modes:
            self.tone_mapping_mode = mode
            print(f"Tone mapping: {self.tone_mapping_mode}")
        else:
            print(f"Invalid tone mapping mode: {mode}. Valid modes: {valid_modes}")
    
    def adjust_gamma(self, delta: float):
        """Adjust gamma by delta amount"""
        self.gamma = max(1.0, min(3.0, self.gamma + delta))
        print(f"Gamma: {self.gamma:.2f}")
    
    def set_gamma(self, gamma: float):
        """Set absolute gamma value"""
        self.gamma = max(1.0, min(3.0, gamma))
        print(f"Gamma: {self.gamma:.2f}")
    
    def toggle_hdr(self):
        """Toggle HDR rendering on/off"""
        if hasattr(self, 'enable_hdr'):
            print("HDR toggle requires reinitialization - use switch_hdr_mode() instead")
        
    def get_hdr_info(self) -> dict:
        """Get current HDR settings"""
        return {
            'hdr_enabled': self.enable_hdr,
            'exposure': self.exposure,
            'tone_mapping': self.tone_mapping_mode,
            'gamma': self.gamma
        }
    
    def resize(self, width: int, height: int):
        """Resize the render target"""
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            
            # Recreate buffers
            if self.enable_hdr:
                # HDR buffer (float4)
                self.hdr_buffer = cl.Buffer(self.context, cl.mem_flags.READ_WRITE, 
                                          width * height * 4 * 4)
                # LDR output buffer
                self.output_buffer = cl.Buffer(self.context, cl.mem_flags.WRITE_ONLY, 
                                             width * height * 4)
                # HDR array
                self.hdr_array = np.zeros((height, width, 4), dtype=np.float32)
            else:
                # Standard LDR buffer
                self.output_buffer = cl.Buffer(self.context, cl.mem_flags.WRITE_ONLY, 
                                             width * height * 4)
            
            self.output_array = np.zeros((height, width, 4), dtype=np.uint8)
    
    def cleanup(self):
        """Clean up OpenCL resources"""
        if hasattr(self, 'output_buffer') and self.output_buffer is not None:
            try:
                self.output_buffer.release()
                self.output_buffer = None
            except:
                pass  # Already released
        if hasattr(self, 'queue') and self.queue is not None:
            try:
                self.queue.finish()
            except:
                pass
    
    def __del__(self):
        """Destructor"""
        try:
            self.cleanup()
        except:
            pass  # Ignore cleanup errors during destruction
