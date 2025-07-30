"""
Application - The main application class that manages the entire GUI lifecycle
"""
import pygame
import sys
from typing import Optional
from .window import Window
from .events import EventManager
from .context import Context


class Application:
    """Main application class that manages the GUI lifecycle"""
    
    def __init__(self, name: str = "ModernGUI App"):
        self.name = name
        self.running = False
        self.window: Optional[Window] = None
        self.event_manager = EventManager()
        self.context = Context()
        
        # Initialize pygame
        pygame.init()
        
        # Set up OpenGL context
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        
    def create_window(self, title: str = "ModernGUI Window", width: int = 800, height: int = 600) -> Window:
        """Create the main application window"""
        self.window = Window(title, width, height, self.context)
        return self.window
        
    def run(self):
        """Main application loop"""
        if not self.window:
            raise RuntimeError("No window created. Call create_window() first.")
            
        self.running = True
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.event_manager.handle_event(event)
                    
            # Update window
            self.window.update()
            
            # Render window
            self.window.render()
            
            # Swap buffers
            pygame.display.flip()
            
            # Control frame rate
            clock.tick(60)
            
        self.quit()
        
    def quit(self):
        """Clean up and quit the application"""
        self.running = False
        if self.window:
            self.window.cleanup()
        pygame.quit()
        sys.exit()
        
    def on_event(self, event_type: str, callback):
        """Register an event callback"""
        self.event_manager.register_callback(event_type, callback)