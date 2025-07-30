"""
Basic UI components - Container, Button, Text, Input
"""
from typing import Optional, Callable
from ..core.component import Component
from ..styling.parser import StyleParser


class Container(Component):
    """A basic container component that can hold other components"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.style_parser = StyleParser()
        self.background_color = (0.0, 0.0, 0.0, 0.0)  # Transparent by default
        self.border_color = (0.0, 0.0, 0.0, 0.0)
        self.border_width = 0
        self.padding = 0
        self.margin = 0
        
    def component_did_mount(self):
        """Apply styling when component mounts"""
        self.apply_styles()
        
    def apply_styles(self):
        """Apply TailwindCSS-like styles"""
        if self.classes:
            styles = self.style_parser.parse_classes(self.classes)
            self.background_color = styles.get('background_color', self.background_color)
            self.border_color = styles.get('border_color', self.border_color)
            self.border_width = styles.get('border_width', self.border_width)
            self.padding = styles.get('padding', self.padding)
            self.margin = styles.get('margin', self.margin)
            
    def render(self, renderer):
        """Render the container"""
        # Apply margin
        x = self.x + self.margin
        y = self.y + self.margin
        w = self.width - 2 * self.margin
        h = self.height - 2 * self.margin
        
        # Render background
        if self.background_color[3] > 0:  # Only render if not transparent
            renderer.render_rectangle(x, y, w, h, self.background_color)
            
        # Render border
        if self.border_width > 0:
            # Top border
            renderer.render_rectangle(x, y, w, self.border_width, self.border_color)
            # Bottom border
            renderer.render_rectangle(x, y + h - self.border_width, w, self.border_width, self.border_color)
            # Left border
            renderer.render_rectangle(x, y, self.border_width, h, self.border_color)
            # Right border
            renderer.render_rectangle(x + w - self.border_width, y, self.border_width, h, self.border_color)


class Button(Component):
    """A clickable button component"""
    
    def __init__(self, text: str = "", **props):
        super().__init__(**props)
        self.text = text
        self.style_parser = StyleParser()
        self.background_color = (0.2, 0.6, 1.0, 1.0)  # Blue by default
        self.text_color = (1.0, 1.0, 1.0, 1.0)  # White text
        self.border_radius = 4
        self.padding = 8
        self.is_hovered = False
        self.is_pressed = False
        
        # Event handlers
        self.on_click: Optional[Callable] = props.get('on_click')
        
    def component_did_mount(self):
        """Apply styling when component mounts"""
        self.apply_styles()
        
    def apply_styles(self):
        """Apply TailwindCSS-like styles"""
        if self.classes:
            styles = self.style_parser.parse_classes(self.classes)
            self.background_color = styles.get('background_color', self.background_color)
            self.text_color = styles.get('text_color', self.text_color)
            self.border_radius = styles.get('border_radius', self.border_radius)
            self.padding = styles.get('padding', self.padding)
            
    def handle_mouse_event(self, event_type: str, event_data):
        """Handle mouse events"""
        if event_type == 'mouse_down':
            self.is_pressed = True
            if self.on_click:
                self.on_click(self)
        elif event_type == 'mouse_up':
            self.is_pressed = False
        elif event_type == 'mouse_enter':
            self.is_hovered = True
        elif event_type == 'mouse_leave':
            self.is_hovered = False
            
    def render(self, renderer):
        """Render the button"""
        # Adjust color based on state
        color = self.background_color
        if self.is_pressed:
            color = tuple(c * 0.8 for c in color)  # Darker when pressed
        elif self.is_hovered:
            color = tuple(c * 1.1 for c in color)  # Lighter when hovered
            
        # Render background
        renderer.render_rectangle(self.x, self.y, self.width, self.height, color)
        
        # Render text (basic implementation)
        # In a full implementation, you would use proper text rendering
        text_x = self.x + self.padding
        text_y = self.y + self.padding
        # renderer.render_text(self.text, text_x, text_y, self.text_color)


class Text(Component):
    """A text display component"""
    
    def __init__(self, text: str = "", **props):
        super().__init__(**props)
        self.text = text
        self.style_parser = StyleParser()
        self.color = (1.0, 1.0, 1.0, 1.0)  # White by default
        self.font_size = 16
        self.font_weight = 'normal'
        
    def component_did_mount(self):
        """Apply styling when component mounts"""
        self.apply_styles()
        
    def apply_styles(self):
        """Apply TailwindCSS-like styles"""
        if self.classes:
            styles = self.style_parser.parse_classes(self.classes)
            self.color = styles.get('text_color', self.color)
            self.font_size = styles.get('font_size', self.font_size)
            self.font_weight = styles.get('font_weight', self.font_weight)
            
    def render(self, renderer):
        """Render the text"""
        # Basic text rendering
        # In a full implementation, you would use proper text rendering
        renderer.render_text(self.text, self.x, self.y, self.color)


class Input(Component):
    """A text input component"""
    
    def __init__(self, placeholder: str = "", **props):
        super().__init__(**props)
        self.placeholder = placeholder
        self.value = ""
        self.style_parser = StyleParser()
        self.background_color = (0.2, 0.2, 0.2, 1.0)
        self.text_color = (1.0, 1.0, 1.0, 1.0)
        self.border_color = (0.5, 0.5, 0.5, 1.0)
        self.border_width = 1
        self.padding = 8
        self.is_focused = False
        
    def component_did_mount(self):
        """Apply styling when component mounts"""
        self.apply_styles()
        
    def apply_styles(self):
        """Apply TailwindCSS-like styles"""
        if self.classes:
            styles = self.style_parser.parse_classes(self.classes)
            self.background_color = styles.get('background_color', self.background_color)
            self.text_color = styles.get('text_color', self.text_color)
            self.border_color = styles.get('border_color', self.border_color)
            self.border_width = styles.get('border_width', self.border_width)
            self.padding = styles.get('padding', self.padding)
            
    def handle_key_event(self, event_type: str, event_data):
        """Handle keyboard events"""
        if event_type == 'key_down':
            if event_data.key == 8:  # Backspace
                self.value = self.value[:-1]
            elif event_data.unicode:
                self.value += event_data.unicode
                
    def render(self, renderer):
        """Render the input field"""
        # Render background
        renderer.render_rectangle(self.x, self.y, self.width, self.height, self.background_color)
        
        # Render border
        if self.border_width > 0:
            border_color = self.border_color
            if self.is_focused:
                border_color = (0.2, 0.6, 1.0, 1.0)  # Blue when focused
                
            # Render border
            renderer.render_rectangle(self.x, self.y, self.width, self.border_width, border_color)
            renderer.render_rectangle(self.x, self.y + self.height - self.border_width, self.width, self.border_width, border_color)
            renderer.render_rectangle(self.x, self.y, self.border_width, self.height, border_color)
            renderer.render_rectangle(self.x + self.width - self.border_width, self.y, self.border_width, self.height, border_color)
            
        # Render text
        display_text = self.value if self.value else self.placeholder
        text_color = self.text_color if self.value else (0.5, 0.5, 0.5, 1.0)
        renderer.render_text(display_text, self.x + self.padding, self.y + self.padding, text_color)