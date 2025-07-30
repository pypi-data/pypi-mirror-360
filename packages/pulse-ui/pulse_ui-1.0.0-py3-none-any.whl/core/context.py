"""
Context - Provides context data that can be shared across components
"""
from typing import Dict, Any


class Context:
    """Provides context data that can be shared across components"""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.themes: Dict[str, Any] = {}
        self.fonts: Dict[str, Any] = {}
        
        # Default theme
        self.set_theme('default', {
            'colors': {
                'primary': (0.2, 0.6, 1.0, 1.0),
                'secondary': (0.6, 0.6, 0.6, 1.0),
                'success': (0.2, 0.8, 0.2, 1.0),
                'warning': (1.0, 0.8, 0.2, 1.0),
                'error': (1.0, 0.2, 0.2, 1.0),
                'background': (0.1, 0.1, 0.1, 1.0),
                'surface': (0.2, 0.2, 0.2, 1.0),
                'text': (1.0, 1.0, 1.0, 1.0)
            },
            'spacing': {
                'xs': 4,
                'sm': 8,
                'md': 16,
                'lg': 24,
                'xl': 32
            },
            'border_radius': {
                'sm': 4,
                'md': 8,
                'lg': 16,
                'full': 9999
            }
        })
        
        self.current_theme = 'default'
        
    def set_data(self, key: str, value: Any):
        """Set a value in the context"""
        self.data[key] = value
        
    def get_data(self, key: str, default: Any = None) -> Any:
        """Get a value from the context"""
        return self.data.get(key, default)
        
    def set_theme(self, name: str, theme: Dict[str, Any]):
        """Set a theme"""
        self.themes[name] = theme
        
    def get_theme(self, name: str = None) -> Dict[str, Any]:
        """Get a theme"""
        if name is None:
            name = self.current_theme
        return self.themes.get(name, {})
        
    def set_current_theme(self, name: str):
        """Set the current theme"""
        if name in self.themes:
            self.current_theme = name
            
    def get_theme_color(self, color_name: str) -> tuple:
        """Get a color from the current theme"""
        theme = self.get_theme()
        colors = theme.get('colors', {})
        return colors.get(color_name, (1.0, 1.0, 1.0, 1.0))
        
    def get_theme_spacing(self, spacing_name: str) -> int:
        """Get a spacing value from the current theme"""
        theme = self.get_theme()
        spacing = theme.get('spacing', {})
        return spacing.get(spacing_name, 8)
        
    def get_theme_border_radius(self, radius_name: str) -> int:
        """Get a border radius value from the current theme"""
        theme = self.get_theme()
        border_radius = theme.get('border_radius', {})
        return border_radius.get(radius_name, 4)