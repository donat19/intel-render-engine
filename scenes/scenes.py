# Scene definitions for the raymarcher
# Each scene defines objects and their properties

import numpy as np

class Scene:
    def __init__(self, name: str = "Default Scene"):
        self.name = name
        self.objects = []
        self.lights = []
        self.camera_start_pos = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.camera_start_angles = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    
    def add_object(self, obj_type: str, position: tuple, properties: dict):
        """Add an object to the scene"""
        self.objects.append({
            'type': obj_type,
            'position': np.array(position, dtype=np.float32),
            'properties': properties
        })
    
    def add_light(self, position: tuple, color: tuple = (1.0, 1.0, 1.0), intensity: float = 1.0):
        """Add a light to the scene"""
        self.lights.append({
            'position': np.array(position, dtype=np.float32),
            'color': np.array(color, dtype=np.float32),
            'intensity': intensity
        })

# Default demo scene
def create_demo_scene() -> Scene:
    """Create the default demo scene"""
    scene = Scene("Demo Scene")
    
    # Add animated sphere
    scene.add_object('sphere', (0.0, 0.0, 0.0), {
        'radius': 1.0,
        'animated': True,
        'animation_type': 'orbit'
    })
    
    # Add ground plane (large flat box)
    scene.add_object('box', (0.0, -2.0, 0.0), {
        'size': (8.0, 0.1, 8.0),
        'animated': False
    })
    
    # Add rotating torus
    scene.add_object('torus', (0.0, 1.0, 3.0), {
        'major_radius': 1.0,
        'minor_radius': 0.3,
        'animated': True,
        'animation_type': 'rotate'
    })
    
    # Add some cubes
    scene.add_object('box', (-3.0, 0.0, -2.0), {
        'size': (0.8, 0.8, 0.8),
        'animated': False
    })
    
    scene.add_object('box', (3.0, 0.5, -1.0), {
        'size': (0.6, 1.2, 0.6),
        'animated': False
    })
    
    # Add lights
    scene.add_light((5.0, 5.0, 5.0), (1.0, 1.0, 1.0), 1.0)
    scene.add_light((-3.0, 2.0, 2.0), (0.8, 0.6, 0.4), 0.7)
    
    return scene

def create_minimal_scene() -> Scene:
    """Create a minimal scene for testing"""
    scene = Scene("Minimal Scene")
    
    # Single sphere
    scene.add_object('sphere', (0.0, 0.0, 0.0), {
        'radius': 1.0,
        'animated': False
    })
    
    # Single light
    scene.add_light((2.0, 2.0, 2.0))
    
    return scene

def create_complex_scene() -> Scene:
    """Create a more complex scene"""
    scene = Scene("Complex Scene")
    
    # Multiple spheres in a pattern
    for i in range(-2, 3):
        for j in range(-2, 3):
            if (i + j) % 2 == 0:
                scene.add_object('sphere', (i * 2.0, 0.0, j * 2.0), {
                    'radius': 0.5,
                    'animated': True,
                    'animation_type': 'bob',
                    'phase': (i + j) * 0.5
                })
    
    # Central torus
    scene.add_object('torus', (0.0, 2.0, 0.0), {
        'major_radius': 1.5,
        'minor_radius': 0.4,
        'animated': True,
        'animation_type': 'rotate'
    })
    
    # Ground
    scene.add_object('box', (0.0, -1.0, 0.0), {
        'size': (10.0, 0.1, 10.0),
        'animated': False
    })
    
    # Multiple lights
    scene.add_light((5.0, 5.0, 5.0), (1.0, 0.8, 0.6))
    scene.add_light((-5.0, 3.0, -5.0), (0.6, 0.8, 1.0))
    scene.add_light((0.0, 8.0, 0.0), (0.8, 1.0, 0.8))
    
    scene.camera_start_pos = np.array([0.0, 3.0, 8.0], dtype=np.float32)
    
    return scene

def create_cloud_scene() -> Scene:
    """Create a scene with volumetric clouds"""
    scene = Scene("Volumetric Clouds")
    
    # Ground plane
    scene.add_object('box', (0.0, -1.0, 0.0), {
        'size': (20.0, 0.1, 20.0),
        'animated': False
    })
    
    # Some mountains (tall boxes)
    scene.add_object('box', (-8.0, 1.0, -10.0), {
        'size': (2.0, 3.0, 2.0),
        'animated': False
    })
    
    scene.add_object('box', (5.0, 2.0, -8.0), {
        'size': (1.5, 4.0, 1.5),
        'animated': False
    })
    
    scene.add_object('box', (0.0, 1.5, -12.0), {
        'size': (3.0, 3.5, 2.0),
        'animated': False
    })
    
    # Cloud volumes (using sphere type but will be handled differently in shader)
    scene.add_object('cloud', (0.0, 8.0, 0.0), {
        'size': (15.0, 6.0, 10.0),
        'density': 0.3,
        'animated': True,
        'animation_type': 'drift'
    })
    
    scene.add_object('cloud', (-10.0, 12.0, -5.0), {
        'size': (8.0, 4.0, 8.0),
        'density': 0.25,
        'animated': True,
        'animation_type': 'drift'
    })
    
    scene.add_object('cloud', (12.0, 10.0, 5.0), {
        'size': (6.0, 5.0, 6.0),
        'density': 0.4,
        'animated': True,
        'animation_type': 'drift'
    })
    
    # Sun light (bright directional)
    scene.add_light((20.0, 30.0, 10.0), (1.0, 0.95, 0.8), 2.0)
    
    # Ambient sky light
    scene.add_light((0.0, 50.0, 0.0), (0.5, 0.7, 1.0), 0.8)
    
    # Set camera position for good cloud view
    scene.camera_start_pos = np.array([0.0, 5.0, 20.0], dtype=np.float32)
    scene.camera_start_angles = np.array([0.0, -0.2, 0.0], dtype=np.float32)
    
    return scene

# Available scenes
SCENES = {
    'demo': create_demo_scene,
    'minimal': create_minimal_scene,
    'complex': create_complex_scene,
    'clouds': create_cloud_scene
}

def get_scene(name: str = 'demo') -> Scene:
    """Get a scene by name"""
    if name in SCENES:
        return SCENES[name]()
    else:
        print(f"Scene '{name}' not found, using demo scene")
        return create_demo_scene()
