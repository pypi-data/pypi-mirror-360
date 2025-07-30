"""
Display components - Image, Icon, Divider for visual elements
"""
from typing import Optional, Tuple
from ..core.component import Component
from ..styling.parser import StyleParser


class Image(Component):
    """Image display component"""
    
    def __init__(self, src: str = "", **props):
        super().__init__(**props)
        self.src = src
        self.alt = props.get('alt', '')
        self.fit = props.get('fit', 'contain')  # contain, cover, fill, none
        self.border_radius = props.get('border_radius', 0)
        
        # Image data (placeholder)
        self.image_data = None
        self.image_width = 0
        self.image_height = 0
        
        # Style properties
        self.background_color = (0.3, 0.3, 0.3, 1.0)  # Gray placeholder
        
    def load_image(self, src: str):
        """Load image from source"""
        self.src = src
        # In a full implementation, this would load the actual image
        # For now, just set placeholder dimensions
        self.image_width = 200
        self.image_height = 150
        
    def component_did_mount(self):
        """Load image when component mounts"""
        if self.src:
            self.load_image(self.src)
            
    def calculate_display_size(self) -> Tuple[int, int, int, int]:
        """Calculate image display size based on fit mode"""
        if not self.image_width or not self.image_height:
            return self.x, self.y, self.width, self.height
            
        if self.fit == 'fill':
            return self.x, self.y, self.width, self.height
            
        elif self.fit == 'contain':
            # Scale to fit within bounds while maintaining aspect ratio
            aspect_ratio = self.image_width / self.image_height
            container_ratio = self.width / self.height
            
            if aspect_ratio > container_ratio:
                # Image is wider, fit to width
                display_width = self.width
                display_height = int(self.width / aspect_ratio)
                display_x = self.x
                display_y = self.y + (self.height - display_height) // 2
            else:
                # Image is taller, fit to height
                display_width = int(self.height * aspect_ratio)
                display_height = self.height
                display_x = self.x + (self.width - display_width) // 2
                display_y = self.y
                
            return display_x, display_y, display_width, display_height
            
        elif self.fit == 'cover':
            # Scale to cover entire area while maintaining aspect ratio
            aspect_ratio = self.image_width / self.image_height
            container_ratio = self.width / self.height
            
            if aspect_ratio > container_ratio:
                # Image is wider, fit to height
                display_width = int(self.height * aspect_ratio)
                display_height = self.height
                display_x = self.x - (display_width - self.width) // 2
                display_y = self.y
            else:
                # Image is taller, fit to width
                display_width = self.width
                display_height = int(self.width / aspect_ratio)
                display_x = self.x
                display_y = self.y - (display_height - self.height) // 2
                
            return display_x, display_y, display_width, display_height
            
        else:  # none
            # Display at original size, centered
            display_x = self.x + (self.width - self.image_width) // 2
            display_y = self.y + (self.height - self.image_height) // 2
            return display_x, display_y, self.image_width, self.image_height
            
    def render(self, renderer):
        """Render the image"""
        # Render background/placeholder
        renderer.render_rectangle(self.x, self.y, self.width, self.height, self.background_color)
        
        if self.image_data:
            # In a full implementation, render the actual image
            display_x, display_y, display_width, display_height = self.calculate_display_size()
            # renderer.render_image(self.image_data, display_x, display_y, display_width, display_height)
        else:
            # Render placeholder with alt text
            if self.alt:
                text_x = self.x + self.width // 2 - len(self.alt) * 4
                text_y = self.y + self.height // 2
                # renderer.render_text(self.alt, text_x, text_y, (1.0, 1.0, 1.0, 1.0))


class Icon(Component):
    """Icon display component"""
    
    def __init__(self, name: str = "", **props):
        super().__init__(**props)
        self.name = name
        self.size = props.get('size', 24)
        self.color = props.get('color', (1.0, 1.0, 1.0, 1.0))
        
        # Icon library (simplified - in full implementation use icon fonts or SVG)
        self.icons = {
            'home': '🏠',
            'user': '👤',
            'settings': '⚙️',
            'search': '🔍',
            'heart': '❤️',
            'star': '⭐',
            'check': '✓',
            'close': '✕',
            'arrow_up': '↑',
            'arrow_down': '↓',
            'arrow_left': '←',
            'arrow_right': '→',
            'menu': '☰',
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅'
        }
        
    def render(self, renderer):
        """Render the icon"""
        icon_char = self.icons.get(self.name, '?')
        
        # Center the icon
        text_x = self.x + (self.width - self.size) // 2
        text_y = self.y + (self.height - self.size) // 2
        
        # In a full implementation, use proper icon rendering
        # For now, just render the character placeholder
        # renderer.render_text(icon_char, text_x, text_y, self.color)


class Divider(Component):
    """Divider component for visual separation"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.orientation = props.get('orientation', 'horizontal')  # horizontal or vertical
        self.thickness = props.get('thickness', 1)
        self.color = props.get('color', (0.5, 0.5, 0.5, 1.0))
        self.margin = props.get('margin', 0)
        
    def render(self, renderer):
        """Render the divider"""
        if self.orientation == 'horizontal':
            # Horizontal divider
            divider_x = self.x + self.margin
            divider_y = self.y + (self.height - self.thickness) // 2
            divider_width = self.width - 2 * self.margin
            divider_height = self.thickness
        else:
            # Vertical divider
            divider_x = self.x + (self.width - self.thickness) // 2
            divider_y = self.y + self.margin
            divider_width = self.thickness
            divider_height = self.height - 2 * self.margin
            
        renderer.render_rectangle(divider_x, divider_y, divider_width, divider_height, self.color)


class Card(Component):
    """Card component with shadow and rounded corners"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.background_color = props.get('background_color', (0.2, 0.2, 0.2, 1.0))
        self.border_radius = props.get('border_radius', 8)
        self.shadow_color = props.get('shadow_color', (0.0, 0.0, 0.0, 0.3))
        self.shadow_offset = props.get('shadow_offset', (2, 2))
        self.shadow_blur = props.get('shadow_blur', 4)
        self.padding = props.get('padding', 16)
        
    def render(self, renderer):
        """Render the card"""
        # Render shadow
        shadow_x = self.x + self.shadow_offset[0]
        shadow_y = self.y + self.shadow_offset[1]
        renderer.render_rectangle(shadow_x, shadow_y, self.width, self.height, self.shadow_color)
        
        # Render card background
        renderer.render_rectangle(self.x, self.y, self.width, self.height, self.background_color)
        
        # In a full implementation, apply border radius and blur effects


class Badge(Component):
    """Badge component for notifications and labels"""
    
    def __init__(self, text: str = "", **props):
        super().__init__(**props)
        self.text = text
        self.background_color = props.get('background_color', (1.0, 0.24, 0.24, 1.0))  # Red by default
        self.text_color = props.get('text_color', (1.0, 1.0, 1.0, 1.0))
        self.border_radius = props.get('border_radius', 12)
        self.padding = props.get('padding', 4)
        
    def render(self, renderer):
        """Render the badge"""
        # Render background
        renderer.render_rectangle(self.x, self.y, self.width, self.height, self.background_color)
        
        # Render text
        text_x = self.x + self.padding
        text_y = self.y + self.padding
        # renderer.render_text(self.text, text_x, text_y, self.text_color)


class Progress(Component):
    """Progress bar component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.value = props.get('value', 0)  # 0-100
        self.max_value = props.get('max_value', 100)
        self.background_color = props.get('background_color', (0.3, 0.3, 0.3, 1.0))
        self.fill_color = props.get('fill_color', (0.23, 0.45, 1.0, 1.0))
        self.border_radius = props.get('border_radius', 4)
        self.show_text = props.get('show_text', False)
        
    def render(self, renderer):
        """Render the progress bar"""
        # Render background
        renderer.render_rectangle(self.x, self.y, self.width, self.height, self.background_color)
        
        # Calculate fill width
        progress_ratio = min(max(self.value / self.max_value, 0), 1)
        fill_width = int(self.width * progress_ratio)
        
        # Render fill
        if fill_width > 0:
            renderer.render_rectangle(self.x, self.y, fill_width, self.height, self.fill_color)
            
        # Render text if enabled
        if self.show_text:
            progress_text = f"{int(progress_ratio * 100)}%"
            text_x = self.x + self.width // 2 - len(progress_text) * 4
            text_y = self.y + self.height // 2 - 8
            # renderer.render_text(progress_text, text_x, text_y, (1.0, 1.0, 1.0, 1.0))