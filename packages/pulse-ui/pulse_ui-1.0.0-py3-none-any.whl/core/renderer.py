"""
Renderer - GPU-accelerated rendering engine using OpenGL
"""
import moderngl
import numpy as np
from typing import Tuple, List
from .component import Component


class Renderer:
    """GPU-accelerated rendering engine using OpenGL"""
    
    def __init__(self, gl_context: moderngl.Context, width: int, height: int):
        self.ctx = gl_context
        self.width = width
        self.height = height
        
        # Create shaders
        self.create_shaders()
        
        # Create buffers
        self.create_buffers()
        
    def create_shaders(self):
        """Create basic shaders for rendering"""
        # Basic vertex shader
        vertex_shader = '''
        #version 330 core
        in vec2 position;
        in vec4 color;
        out vec4 fragColor;
        uniform mat4 projection;
        
        void main() {
            gl_Position = projection * vec4(position, 0.0, 1.0);
            fragColor = color;
        }
        '''
        
        # Basic fragment shader
        fragment_shader = '''
        #version 330 core
        in vec4 fragColor;
        out vec4 color;
        
        void main() {
            color = fragColor;
        }
        '''
        
        # Create shader program
        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        
        # Set up projection matrix (orthographic)
        self.update_projection()
        
    def create_buffers(self):
        """Create vertex buffers"""
        # Create vertex buffer object
        self.vbo = self.ctx.buffer(np.array([], dtype=np.float32))
        
        # Create vertex array object
        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '2f 4f', 'position', 'color')
        ])
        
    def update_projection(self):
        """Update the projection matrix"""
        # Create orthographic projection matrix
        projection = np.array([
            [2.0/self.width, 0, 0, -1],
            [0, -2.0/self.height, 0, 1],
            [0, 0, -1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        self.program['projection'].write(projection.tobytes())
        
    def resize(self, width: int, height: int):
        """Resize the renderer"""
        self.width = width
        self.height = height
        self.update_projection()
        
    def render_component(self, component: Component):
        """Render a component and its children"""
        # Render the component
        component.render(self)
        
        # Render children
        for child in component.children:
            self.render_component(child)
            
    def render_rectangle(self, x: float, y: float, width: float, height: float, color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)):
        """Render a rectangle"""
        # Create vertices for rectangle
        vertices = np.array([
            # Position     Color
            x, y,         color[0], color[1], color[2], color[3],          # Top-left
            x + width, y, color[0], color[1], color[2], color[3],          # Top-right
            x, y + height, color[0], color[1], color[2], color[3],         # Bottom-left
            x + width, y + height, color[0], color[1], color[2], color[3]  # Bottom-right
        ], dtype=np.float32)
        
        # Update buffer
        self.vbo.write(vertices)
        
        # Render
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        
    def render_circle(self, x: float, y: float, radius: float, color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0), segments: int = 32):
        """Render a circle"""
        vertices = []
        
        # Center vertex
        vertices.extend([x, y, color[0], color[1], color[2], color[3]])
        
        # Circle vertices
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            px = x + radius * np.cos(angle)
            py = y + radius * np.sin(angle)
            vertices.extend([px, py, color[0], color[1], color[2], color[3]])
            
        vertices_array = np.array(vertices, dtype=np.float32)
        
        # Update buffer
        self.vbo.write(vertices_array)
        
        # Render
        self.vao.render(mode=moderngl.TRIANGLE_FAN)
        
    def render_text(self, text: str, x: float, y: float, color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)):
        """Render text (basic implementation)"""
        # This is a basic text rendering implementation
        # In a full implementation, you would use a font rendering library
        pass
        
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'vao'):
            self.vao.release()
        if hasattr(self, 'vbo'):
            self.vbo.release()
        if hasattr(self, 'program'):
            self.program.release()