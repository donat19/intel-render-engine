import pyopencl as cl
import numpy as np
import time
import os
from typing import Tuple, Optional

class RayMarcher:
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        
        # Initialize OpenCL
        self.context = cl.create_some_context(interactive=False)
        self.queue = cl.CommandQueue(self.context)
        
        # Load and compile kernel
        self._load_kernel()
        
        # Create output buffer
        self.output_buffer = cl.Buffer(self.context, cl.mem_flags.WRITE_ONLY, 
                                     width * height * 4)  # RGBA
        
        # Camera parameters
        self.camera_pos = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.camera_angles = np.array([0.0, 0.0, 0.0], dtype=np.float32)  # pitch, yaw, roll
        
        # Animation parameters
        self.start_time = time.time()
        
        # Output array
        self.output_array = np.zeros((height, width, 4), dtype=np.uint8)
        
    def _load_kernel(self):
        """Load and compile the OpenCL kernel"""
        kernel_path = os.path.join(os.path.dirname(__file__), 'shaders', 'raymarch.cl')
        
        try:
            with open(kernel_path, 'r') as f:
                kernel_source = f.read()
            
            self.program = cl.Program(self.context, kernel_source).build()
            self.kernel = self.program.raymarch_kernel
            
        except Exception as e:
            print(f"Error loading kernel: {e}")
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
            'time': time.time() - self.start_time
        }
    
    def resize(self, width: int, height: int):
        """Resize the render target"""
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            
            # Recreate output buffer
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
