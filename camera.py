"""
Advanced Camera System for Intel Render Engine
Implements proper 3D camera with quaternion-based rotation and local movement
"""

import numpy as np
from typing import Tuple, Dict, Any

class Camera:
    """
    Advanced 3D camera with proper quaternion-based rotation and local movement.
    Uses right-handed coordinate system where:
    - X axis points right
    - Y axis points up  
    - Z axis points towards the camera (negative Z is forward)
    """
    
    def __init__(self, position: np.ndarray = None, target: np.ndarray = None, up: np.ndarray = None):
        """
        Initialize camera
        
        Args:
            position: Camera position in world space
            target: Point the camera looks at (optional, will compute from angles)
            up: Up vector (default: Y up)
        """
        # Default values
        if position is None:
            position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        if up is None:
            up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
            
        self.position = position.copy()
        self.world_up = up.copy()
        
        # Euler angles (in radians)
        self.pitch = 0.0  # Rotation around X axis (up/down)
        self.yaw = 0.0    # Rotation around Y axis (left/right)
        self.roll = 0.0   # Rotation around Z axis (tilt)
        
        # Camera vectors
        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32)  # Forward direction
        self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32)   # Right direction
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)      # Up direction
        
        # Movement parameters
        self.movement_speed = 5.0      # Units per second
        self.mouse_sensitivity = 0.1   # Radians per pixel
        self.max_pitch = np.pi / 2.0 - 0.01  # Slightly less than 90 degrees
        
        # Smooth movement
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.angular_velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.damping = 8.0  # Damping factor for smooth movement
        
        # Initialize camera vectors if target is provided
        if target is not None:
            self.look_at(target)
        else:
            self._update_camera_vectors()
    
    def _update_camera_vectors(self):
        """Update camera front, right, and up vectors based on current angles"""
        # Calculate front vector from pitch and yaw
        front = np.array([
            np.cos(self.yaw) * np.cos(self.pitch),
            np.sin(self.pitch),
            np.sin(self.yaw) * np.cos(self.pitch)
        ], dtype=np.float32)
        
        self.front = front / np.linalg.norm(front)
        
        # Calculate right vector (cross product of front and world up)
        self.right = np.cross(self.front, self.world_up)
        self.right = self.right / np.linalg.norm(self.right)
        
        # Calculate up vector (cross product of right and front)
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)
    
    def look_at(self, target: np.ndarray):
        """Point camera at specific target position"""
        direction = target - self.position
        direction = direction / np.linalg.norm(direction)
        
        # Calculate yaw and pitch from direction vector
        self.yaw = np.arctan2(direction[2], direction[0])
        self.pitch = np.arcsin(direction[1])
        
        self._update_camera_vectors()
    
    def move(self, direction: str, delta_time: float, speed_multiplier: float = 1.0):
        """
        Move camera in specified direction (local space)
        
        Args:
            direction: 'forward', 'backward', 'left', 'right', 'up', 'down'
            delta_time: Time since last frame
            speed_multiplier: Speed multiplier (for running, etc.)
        """
        velocity = self.movement_speed * speed_multiplier * delta_time
        
        if direction == 'forward':
            self.position += self.front * velocity
        elif direction == 'backward':
            self.position -= self.front * velocity
        elif direction == 'left':
            self.position -= self.right * velocity
        elif direction == 'right':
            self.position += self.right * velocity
        elif direction == 'up':
            self.position += self.up * velocity
        elif direction == 'down':
            self.position -= self.up * velocity
    
    def move_smooth(self, direction: str, delta_time: float, speed_multiplier: float = 1.0):
        """
        Smooth camera movement with acceleration and damping
        
        Args:
            direction: 'forward', 'backward', 'left', 'right', 'up', 'down'
            delta_time: Time since last frame
            speed_multiplier: Speed multiplier
        """
        acceleration = self.movement_speed * speed_multiplier
        
        # Apply acceleration based on input
        if direction == 'forward':
            self.velocity += self.front * acceleration * delta_time
        elif direction == 'backward':
            self.velocity -= self.front * acceleration * delta_time
        elif direction == 'left':
            self.velocity -= self.right * acceleration * delta_time
        elif direction == 'right':
            self.velocity += self.right * acceleration * delta_time
        elif direction == 'up':
            self.velocity += self.up * acceleration * delta_time
        elif direction == 'down':
            self.velocity -= self.up * acceleration * delta_time
        
        # Apply damping
        self.velocity *= (1.0 - self.damping * delta_time)
        
        # Update position
        self.position += self.velocity * delta_time
    
    def rotate(self, delta_pitch: float, delta_yaw: float, delta_roll: float = 0.0):
        """
        Rotate camera by specified angles
        
        Args:
            delta_pitch: Pitch rotation in radians
            delta_yaw: Yaw rotation in radians  
            delta_roll: Roll rotation in radians
        """
        self.pitch += delta_pitch
        self.yaw += delta_yaw
        self.roll += delta_roll
        
        # Constrain pitch to avoid gimbal lock
        self.pitch = np.clip(self.pitch, -self.max_pitch, self.max_pitch)
        
        # Normalize yaw to [-pi, pi]
        while self.yaw > np.pi:
            self.yaw -= 2 * np.pi
        while self.yaw < -np.pi:
            self.yaw += 2 * np.pi
        
        self._update_camera_vectors()
    
    def rotate_smooth(self, delta_pitch: float, delta_yaw: float, delta_roll: float = 0.0, delta_time: float = 1.0):
        """
        Smooth camera rotation with damping
        
        Args:
            delta_pitch: Pitch rotation in radians
            delta_yaw: Yaw rotation in radians
            delta_roll: Roll rotation in radians
            delta_time: Time since last frame
        """
        # Apply angular acceleration
        self.angular_velocity[0] += delta_pitch * self.mouse_sensitivity
        self.angular_velocity[1] += delta_yaw * self.mouse_sensitivity
        self.angular_velocity[2] += delta_roll * self.mouse_sensitivity
        
        # Apply damping
        self.angular_velocity *= (1.0 - self.damping * delta_time)
        
        # Update angles
        self.pitch += self.angular_velocity[0] * delta_time
        self.yaw += self.angular_velocity[1] * delta_time
        self.roll += self.angular_velocity[2] * delta_time
        
        # Constrain pitch
        self.pitch = np.clip(self.pitch, -self.max_pitch, self.max_pitch)
        
        # Normalize yaw
        while self.yaw > np.pi:
            self.yaw -= 2 * np.pi
        while self.yaw < -np.pi:
            self.yaw += 2 * np.pi
        
        self._update_camera_vectors()
    
    def handle_mouse_movement(self, x_offset: float, y_offset: float, constrain_pitch: bool = True):
        """
        Handle mouse movement for camera rotation
        
        Args:
            x_offset: Mouse movement in X direction (pixels)
            y_offset: Mouse movement in Y direction (pixels)
            constrain_pitch: Whether to constrain pitch angle
        """
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity
        
        self.yaw += x_offset
        self.pitch += y_offset  # Natural mouse control: mouse up = look up
        
        if constrain_pitch:
            self.pitch = np.clip(self.pitch, -self.max_pitch, self.max_pitch)
        
        self._update_camera_vectors()
    
    def get_view_matrix(self) -> np.ndarray:
        """
        Get view matrix for rendering
        
        Returns:
            4x4 view matrix as row-major numpy array
        """
        # Calculate view matrix using look-at
        target = self.position + self.front
        
        # Build view matrix
        z_axis = -(target - self.position)  # Forward vector (negated)
        z_axis = z_axis / np.linalg.norm(z_axis)
        
        x_axis = np.cross(self.world_up, z_axis)
        x_axis = x_axis / np.linalg.norm(x_axis)
        
        y_axis = np.cross(z_axis, x_axis)
        
        # Create view matrix
        view_matrix = np.array([
            [x_axis[0], y_axis[0], z_axis[0], 0.0],
            [x_axis[1], y_axis[1], z_axis[1], 0.0],
            [x_axis[2], y_axis[2], z_axis[2], 0.0],
            [-np.dot(x_axis, self.position), -np.dot(y_axis, self.position), -np.dot(z_axis, self.position), 1.0]
        ], dtype=np.float32)
        
        return view_matrix
    
    def get_rotation_matrix(self) -> np.ndarray:
        """
        Get 3x3 rotation matrix for ray direction calculation
        
        Returns:
            3x3 rotation matrix as numpy array
        """
        # Build rotation matrix from camera vectors
        rotation_matrix = np.array([
            [self.right[0], self.up[0], -self.front[0]],
            [self.right[1], self.up[1], -self.front[1]], 
            [self.right[2], self.up[2], -self.front[2]]
        ], dtype=np.float32)
        
        return rotation_matrix
    
    def get_camera_matrix_flat(self) -> np.ndarray:
        """
        Get flattened camera matrix for OpenCL kernel
        
        Returns:
            16-element flat array representing camera rotation matrix
        """
        rotation = self.get_rotation_matrix()
        
        # Extend to 4x4 matrix and flatten
        matrix_4x4 = np.eye(4, dtype=np.float32)
        matrix_4x4[:3, :3] = rotation
        
        return matrix_4x4.flatten()
    
    def reset(self, position: np.ndarray = None, pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0):
        """
        Reset camera to specified state
        
        Args:
            position: New camera position (if None, keeps current)
            pitch: New pitch angle in radians
            yaw: New yaw angle in radians
            roll: New roll angle in radians
        """
        if position is not None:
            self.position = position.copy()
        
        self.pitch = pitch
        self.yaw = yaw
        self.roll = roll
        
        # Reset velocities
        self.velocity.fill(0.0)
        self.angular_velocity.fill(0.0)
        
        self._update_camera_vectors()
    
    def update(self, delta_time: float):
        """
        Update camera state (for smooth movement)
        
        Args:
            delta_time: Time since last frame
        """
        # Apply velocity damping even when no input
        self.velocity *= (1.0 - self.damping * delta_time)
        self.angular_velocity *= (1.0 - self.damping * delta_time)
        
        # Update position and angles
        self.position += self.velocity * delta_time
        
        self.pitch += self.angular_velocity[0] * delta_time
        self.yaw += self.angular_velocity[1] * delta_time
        self.roll += self.angular_velocity[2] * delta_time
        
        # Constrain angles
        self.pitch = np.clip(self.pitch, -self.max_pitch, self.max_pitch)
        
        while self.yaw > np.pi:
            self.yaw -= 2 * np.pi
        while self.yaw < -np.pi:
            self.yaw += 2 * np.pi
        
        self._update_camera_vectors()
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get camera information for debugging
        
        Returns:
            Dictionary with camera state information
        """
        return {
            'position': self.position.copy(),
            'angles': np.array([self.pitch, self.yaw, self.roll]),
            'front': self.front.copy(),
            'right': self.right.copy(),
            'up': self.up.copy(),
            'velocity': self.velocity.copy(),
            'angular_velocity': self.angular_velocity.copy(),
            'movement_speed': self.movement_speed,
            'mouse_sensitivity': self.mouse_sensitivity
        }
    
    def set_movement_speed(self, speed: float):
        """Set camera movement speed"""
        self.movement_speed = max(0.1, speed)
    
    def set_mouse_sensitivity(self, sensitivity: float):
        """Set mouse sensitivity"""
        self.mouse_sensitivity = max(0.01, sensitivity)
    
    def __str__(self) -> str:
        """String representation of camera"""
        return (f"Camera(pos={self.position}, "
                f"pitch={np.degrees(self.pitch):.1f}°, "
                f"yaw={np.degrees(self.yaw):.1f}°, "
                f"roll={np.degrees(self.roll):.1f}°)")
