"""
Window - The main window class that manages the display and rendering
"""
import pygame
import moderngl
from typing import Optional, Tuple
from .component import Component
from .renderer import Renderer
from .context import Context


class Window:
    """Main window class that manages display and rendering"""
    
    def __init__(self, title: str, width: int, height: int, context: Context):
        self.title = title
        self.width = width
        self.height = height
        self.context = context
        self.root_component: Optional[Component] = None
        
        # Create pygame window
        self.screen = pygame.display.set_mode((width, height), pygame.OPENGL)
        pygame.display.set_caption(title)
        
        # Create OpenGL context
        self.gl_context = moderngl.create_context()
        
        # Initialize renderer
        self.renderer = Renderer(self.gl_context, width, height)
        
        # Set up viewport
        self.gl_context.viewport = (0, 0, width, height)
        
        # Enable blending for transparency
        self.gl_context.enable(moderngl.BLEND)
        self.gl_context.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        # Background color
        self.background_color = (0.1, 0.1, 0.1, 1.0)
        
    def set_root_component(self, component: Component):
        """Set the root component of the window"""
        self.root_component = component
        component.set_parent(None)
        component.set_context(self.context)
        
    def set_background_color(self, r: float, g: float, b: float, a: float = 1.0):
        """Set the background color of the window"""
        self.background_color = (r, g, b, a)
        
    def resize(self, width: int, height: int):
        """Resize the window"""
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.OPENGL)
        self.gl_context.viewport = (0, 0, width, height)
        self.renderer.resize(width, height)
        
    def update(self):
        """Update the window and all components"""
        if self.root_component:
            self.root_component.update()
            
    def render(self):
        """Render the window and all components"""
        # Clear the screen
        self.gl_context.clear(color=self.background_color)
        
        # Render root component
        if self.root_component:
            self.renderer.render_component(self.root_component)
            
    def cleanup(self):
        """Clean up resources"""
        if self.renderer:
            self.renderer.cleanup()
            
    def get_size(self) -> Tuple[int, int]:
        """Get the current window size"""
        return (self.width, self.height)
        
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position"""
        return pygame.mouse.get_pos()
        
    def is_mouse_pressed(self, button: int = 1) -> bool:
        """Check if mouse button is pressed"""
        return pygame.mouse.get_pressed()[button - 1]