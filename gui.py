import pygame
import numpy as np
import sys
from typing import Optional, Tuple
from raymarcher import RayMarcher

class RaymarchGUI:
    def __init__(self, width: int = 800, height: int = 600, title: str = "Raymarching Demo", 
                 fullscreen: bool = False, auto_resolution: bool = False):
        # Get display info first
        pygame.init()
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h
        
        # Set initial resolution
        if auto_resolution or fullscreen:
            self.width = self.screen_width
            self.height = self.screen_height
        else:
            self.width = width
            self.height = height
            
        self.title = title
        self.windowed_size = (width, height)  # Original requested size
        
        # Initialize Pygame
        if fullscreen:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
            self.is_fullscreen = True
            print(f"Started in fullscreen mode: {self.width}x{self.height}")
        else:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            self.is_fullscreen = False
            
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        # Initialize raymarcher
        try:
            self.raymarcher = RayMarcher(self.width, self.height)
        except Exception as e:
            print(f"Failed to initialize raymarcher: {e}")
            pygame.quit()
            sys.exit(1)
        
        # Control states
        self.keys_pressed = set()
        self.mouse_sensitivity = 0.005
        self.move_speed = 0.1
        self.last_mouse_pos = None
        self.mouse_captured = False
        
        # FPS tracking
        self.fps_font = pygame.font.Font(None, 36)
        self.show_fps = True
        self.show_camera_info = True
        
        # Performance tracking
        self.frame_times = []
        self.max_frame_samples = 60
        
        # Running state
        self.running = True
        
        # Fullscreen state
        self.auto_resolution = auto_resolution
        if not fullscreen:
            self.windowed_size = (self.width, self.height)
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                # Toggle features
                if event.key == pygame.K_F1:
                    self.show_fps = not self.show_fps
                elif event.key == pygame.K_F2:
                    self.show_camera_info = not self.show_camera_info
                elif event.key == pygame.K_F3:
                    self.mouse_captured = not self.mouse_captured
                    pygame.mouse.set_visible(not self.mouse_captured)
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    self.toggle_fullscreen()
                elif event.key == pygame.K_F12:
                    # Cycle through resolution presets
                    self.cycle_resolution()
                elif event.key == pygame.K_ESCAPE:
                    # ESC exits fullscreen mode or closes application
                    if self.is_fullscreen:
                        self.toggle_fullscreen()
                    else:
                        self.running = False
                elif event.key == pygame.K_r:
                    # Reset camera
                    self.raymarcher.set_camera_position(0, 0, 5)
                    self.raymarcher.set_camera_angles(0, 0, 0)
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            
            elif event.type == pygame.MOUSEMOTION and self.mouse_captured:
                if self.last_mouse_pos is not None:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    
                    # Apply mouse look (correct horizontal/vertical)
                    self.raymarcher.rotate_camera(
                        pitch=dy * self.mouse_sensitivity,
                        yaw=-dx * self.mouse_sensitivity
                    )
                
                self.last_mouse_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_captured = True
                    pygame.mouse.set_visible(False)
                    self.last_mouse_pos = event.pos
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                if not self.is_fullscreen:
                    self.windowed_size = (event.w, event.h)
                    self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
                    self.raymarcher.resize(event.w, event.h)
                    self.width, self.height = event.w, event.h
                    print(f"Window resized to: {event.w}x{event.h}")
            
            elif event.type == pygame.ACTIVEEVENT:
                # Handle window focus changes in fullscreen
                if hasattr(event, 'gain') and not event.gain and self.is_fullscreen:
                    # Lost focus while in fullscreen - exit fullscreen
                    self.toggle_fullscreen()
    
    def handle_continuous_input(self):
        """Handle continuous key input"""
        # Camera movement
        if pygame.K_w in self.keys_pressed:
            self.raymarcher.move_camera('forward', self.move_speed)
        if pygame.K_s in self.keys_pressed:
            self.raymarcher.move_camera('backward', self.move_speed)
        if pygame.K_a in self.keys_pressed:
            self.raymarcher.move_camera('left', self.move_speed)
        if pygame.K_d in self.keys_pressed:
            self.raymarcher.move_camera('right', self.move_speed)
        if pygame.K_SPACE in self.keys_pressed:
            self.raymarcher.move_camera('up', self.move_speed)
        if pygame.K_LSHIFT in self.keys_pressed:
            self.raymarcher.move_camera('down', self.move_speed)
        
        # Arrow key rotation
        rotation_speed = 0.02
        if pygame.K_LEFT in self.keys_pressed:
            self.raymarcher.rotate_camera(yaw=-rotation_speed)
        if pygame.K_RIGHT in self.keys_pressed:
            self.raymarcher.rotate_camera(yaw=rotation_speed)
        if pygame.K_UP in self.keys_pressed:
            self.raymarcher.rotate_camera(pitch=-rotation_speed)
        if pygame.K_DOWN in self.keys_pressed:
            self.raymarcher.rotate_camera(pitch=rotation_speed)
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # Switch to fullscreen
            if self.auto_resolution:
                fullscreen_size = (self.screen_width, self.screen_height)
            else:
                info = pygame.display.Info()
                fullscreen_size = (info.current_w, info.current_h)
            
            self.screen = pygame.display.set_mode(fullscreen_size, pygame.FULLSCREEN)
            
            # Resize raymarcher
            self.raymarcher.resize(fullscreen_size[0], fullscreen_size[1])
            self.width, self.height = fullscreen_size
            
            print(f"Switched to fullscreen: {fullscreen_size[0]}x{fullscreen_size[1]}")
        else:
            # Switch back to windowed
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
            
            # Resize raymarcher back to windowed size
            self.raymarcher.resize(self.windowed_size[0], self.windowed_size[1])
            self.width, self.height = self.windowed_size
            
            print(f"Switched to windowed: {self.windowed_size[0]}x{self.windowed_size[1]}")
    
    def cycle_resolution(self):
        """Cycle through different resolution presets"""
        # Define resolution presets
        resolutions = [
            (800, 600),    # SVGA
            (1024, 768),   # XGA
            (1280, 720),   # HD
            (1366, 768),   # WXGA
            (1920, 1080),  # Full HD
            (2560, 1440),  # QHD
            (self.screen_width, self.screen_height)  # Native
        ]
        
        # Find current resolution and switch to next
        current = (self.width, self.height)
        try:
            current_idx = resolutions.index(current)
            next_idx = (current_idx + 1) % len(resolutions)
        except ValueError:
            next_idx = 0
        
        new_resolution = resolutions[next_idx]
        
        # Don't switch to resolution larger than screen
        if new_resolution[0] > self.screen_width or new_resolution[1] > self.screen_height:
            new_resolution = (self.screen_width, self.screen_height)
        
        self.set_resolution(new_resolution[0], new_resolution[1])
    
    def set_resolution(self, width: int, height: int):
        """Set specific resolution"""
        # Clamp to screen size
        width = min(width, self.screen_width)
        height = min(height, self.screen_height)
        
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            self.windowed_size = (width, height)
        
        # Resize raymarcher
        self.raymarcher.resize(width, height)
        self.width, self.height = width, height
        
        print(f"Resolution changed to: {width}x{height}")
    
    def render_frame(self) -> float:
        """Render a single frame and return render time"""
        import time
        start_time = time.time()
        
        try:
            # Render with raymarcher
            image_array = self.raymarcher.render()
            
            # Convert to pygame surface
            # OpenCL output is RGBA, pygame expects RGB
            rgb_array = image_array[:, :, :3]  # Remove alpha channel
            surface = pygame.surfarray.make_surface(rgb_array.swapaxes(0, 1))
            
            # Blit to screen
            self.screen.blit(surface, (0, 0))
            
        except Exception as e:
            # Fallback to black screen on error
            self.screen.fill((0, 0, 0))
            error_text = self.fps_font.render(f"Render Error: {str(e)[:50]}...", True, (255, 0, 0))
            self.screen.blit(error_text, (10, 10))
        
        render_time = time.time() - start_time
        return render_time
    
    def draw_overlay(self, render_time: float):
        """Draw FPS and camera info overlay"""
        y_offset = 10
        
        if self.show_fps:
            # Calculate FPS
            self.frame_times.append(render_time)
            if len(self.frame_times) > self.max_frame_samples:
                self.frame_times.pop(0)
            
            avg_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / avg_time if avg_time > 0 else 0
            
            # Draw FPS
            fps_text = self.fps_font.render(f"FPS: {fps:.1f} ({avg_time*1000:.1f}ms)", True, (255, 255, 0))
            self.screen.blit(fps_text, (10, y_offset))
            y_offset += 30
        
        if self.show_camera_info:
            camera_info = self.raymarcher.get_camera_info()
            pos = camera_info['position']
            angles = camera_info['angles']
            
            pos_text = self.fps_font.render(f"Pos: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})", True, (255, 255, 0))
            self.screen.blit(pos_text, (10, y_offset))
            y_offset += 25
            
            angles_text = self.fps_font.render(f"Angles: ({np.degrees(angles[0]):.1f}°, {np.degrees(angles[1]):.1f}°)", True, (255, 255, 0))
            self.screen.blit(angles_text, (10, y_offset))
            y_offset += 25
            
            # Display mode info
            mode_text = "Fullscreen" if self.is_fullscreen else "Windowed"
            mode_surface = self.fps_font.render(f"Mode: {mode_text} ({self.width}x{self.height})", True, (255, 255, 0))
            self.screen.blit(mode_surface, (10, y_offset))
            y_offset += 25
            
            # Display native resolution
            native_surface = self.fps_font.render(f"Native: {self.screen_width}x{self.screen_height}", True, (255, 255, 0))
            self.screen.blit(native_surface, (10, y_offset))
            y_offset += 25
        
        # Controls help
        if not self.mouse_captured:
            help_texts = [
                "Controls:",
                "WASD - Move camera",
                "Mouse/Arrows - Look around",
                "Space/Shift - Up/Down",
                "F1 - Toggle FPS",
                "F2 - Toggle camera info",
                "F3 - Toggle mouse capture",
                "F11 - Toggle fullscreen",
                "F12 - Cycle resolution",
                "R - Reset camera",
                "ESC - Exit"
            ]
            
            for i, text in enumerate(help_texts):
                color = (255, 255, 255) if i == 0 else (200, 200, 200)
                help_surface = self.fps_font.render(text, True, color)
                self.screen.blit(help_surface, (self.width - 250, 10 + i * 25))
    
    def run(self):
        """Main game loop"""
        print("Starting Raymarching Demo...")
        print("Controls:")
        print("  WASD - Move camera")
        print("  Mouse/Arrow keys - Look around")
        print("  F1 - Toggle FPS display")
        print("  F2 - Toggle camera info")
        print("  F3 - Toggle mouse capture")
        print("  F11 - Toggle fullscreen")
        print("  F12 - Cycle resolution")
        print("  R - Reset camera")
        print("  ESC - Exit")
        print(f"Current resolution: {self.width}x{self.height}")
        print(f"Native resolution: {self.screen_width}x{self.screen_height}")
        
        while self.running:
            try:
                # Handle events
                self.handle_events()
                self.handle_continuous_input()
                
                # Render frame
                render_time = self.render_frame()
                
                # Draw overlay
                self.draw_overlay(render_time)
                
                # Update display
                pygame.display.flip()
                
                # Limit FPS to prevent overheating
                self.clock.tick(60)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"Unexpected error in main loop: {e}")
                self.running = False
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        if hasattr(self, 'raymarcher') and self.raymarcher is not None:
            try:
                self.raymarcher.cleanup()
                self.raymarcher = None
            except:
                pass  # Ignore cleanup errors
        try:
            pygame.quit()
        except:
            pass
    
    def __del__(self):
        """Destructor"""
        try:
            self.cleanup()
        except:
            pass  # Ignore cleanup errors during destruction


if __name__ == "__main__":
    # Create and run the GUI
    gui = RaymarchGUI(width=800, height=600)
    gui.run()
