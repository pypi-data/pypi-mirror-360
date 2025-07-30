"""
Style and Theme classes for ModernGUI
"""
from typing import Dict, Any, Optional, Tuple


class Style:
    """Represents a collection of style properties"""
    
    def __init__(self, **properties):
        self.properties = properties
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a style property"""
        return self.properties.get(key, default)
        
    def set(self, key: str, value: Any):
        """Set a style property"""
        self.properties[key] = value
        
    def update(self, other_style: 'Style'):
        """Update this style with properties from another style"""
        self.properties.update(other_style.properties)
        
    def merge(self, other_style: 'Style') -> 'Style':
        """Create a new style by merging with another style"""
        new_properties = self.properties.copy()
        new_properties.update(other_style.properties)
        return Style(**new_properties)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert style to dictionary"""
        return self.properties.copy()
        
    def __repr__(self):
        return f"Style({self.properties})"


class Theme:
    """Represents a complete theme with colors, spacing, and other design tokens"""
    
    def __init__(self, name: str):
        self.name = name
        self.colors: Dict[str, Tuple[float, float, float, float]] = {}
        self.spacing: Dict[str, int] = {}
        self.typography: Dict[str, Dict[str, Any]] = {}
        self.shadows: Dict[str, Dict[str, Any]] = {}
        self.border_radius: Dict[str, int] = {}
        self.animations: Dict[str, Dict[str, Any]] = {}
        
        # Set default values
        self._set_defaults()
        
    def _set_defaults(self):
        """Set default theme values"""
        # Default colors
        self.colors = {
            'primary': (0.23, 0.45, 1.0, 1.0),
            'secondary': (0.51, 0.51, 0.51, 1.0),
            'success': (0.23, 1.0, 0.24, 1.0),
            'warning': (1.0, 1.0, 0.23, 1.0),
            'error': (1.0, 0.24, 0.24, 1.0),
            'info': (0.23, 0.45, 1.0, 1.0),
            'background': (0.1, 0.1, 0.1, 1.0),
            'surface': (0.2, 0.2, 0.2, 1.0),
            'text': (1.0, 1.0, 1.0, 1.0),
            'text_secondary': (0.7, 0.7, 0.7, 1.0)
        }
        
        # Default spacing
        self.spacing = {
            'xs': 4,
            'sm': 8,
            'md': 16,
            'lg': 24,
            'xl': 32,
            '2xl': 48,
            '3xl': 64
        }
        
        # Default typography
        self.typography = {
            'xs': {'size': 12, 'weight': 'normal'},
            'sm': {'size': 14, 'weight': 'normal'},
            'base': {'size': 16, 'weight': 'normal'},
            'lg': {'size': 18, 'weight': 'normal'},
            'xl': {'size': 20, 'weight': 'normal'},
            '2xl': {'size': 24, 'weight': 'normal'},
            '3xl': {'size': 30, 'weight': 'normal'},
            '4xl': {'size': 36, 'weight': 'normal'},
            '5xl': {'size': 48, 'weight': 'normal'},
            '6xl': {'size': 64, 'weight': 'normal'}
        }
        
        # Default border radius
        self.border_radius = {
            'none': 0,
            'sm': 2,
            'md': 4,
            'lg': 8,
            'xl': 12,
            '2xl': 16,
            '3xl': 24,
            'full': 9999
        }
        
        # Default shadows
        self.shadows = {
            'sm': {'blur': 2, 'color': (0, 0, 0, 0.1)},
            'md': {'blur': 4, 'color': (0, 0, 0, 0.15)},
            'lg': {'blur': 8, 'color': (0, 0, 0, 0.2)},
            'xl': {'blur': 16, 'color': (0, 0, 0, 0.25)}
        }
        
    def get_color(self, color_name: str) -> Tuple[float, float, float, float]:
        """Get a color from the theme"""
        return self.colors.get(color_name, (1.0, 1.0, 1.0, 1.0))
        
    def set_color(self, color_name: str, color: Tuple[float, float, float, float]):
        """Set a color in the theme"""
        self.colors[color_name] = color
        
    def get_spacing(self, spacing_name: str) -> int:
        """Get a spacing value from the theme"""
        return self.spacing.get(spacing_name, 16)
        
    def set_spacing(self, spacing_name: str, value: int):
        """Set a spacing value in the theme"""
        self.spacing[spacing_name] = value
        
    def get_typography(self, type_name: str) -> Dict[str, Any]:
        """Get typography settings from the theme"""
        return self.typography.get(type_name, {'size': 16, 'weight': 'normal'})
        
    def set_typography(self, type_name: str, settings: Dict[str, Any]):
        """Set typography settings in the theme"""
        self.typography[type_name] = settings
        
    def get_border_radius(self, radius_name: str) -> int:
        """Get a border radius value from the theme"""
        return self.border_radius.get(radius_name, 4)
        
    def set_border_radius(self, radius_name: str, value: int):
        """Set a border radius value in the theme"""
        self.border_radius[radius_name] = value
        
    def get_shadow(self, shadow_name: str) -> Dict[str, Any]:
        """Get shadow settings from the theme"""
        return self.shadows.get(shadow_name, {'blur': 4, 'color': (0, 0, 0, 0.15)})
        
    def set_shadow(self, shadow_name: str, settings: Dict[str, Any]):
        """Set shadow settings in the theme"""
        self.shadows[shadow_name] = settings
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary"""
        return {
            'name': self.name,
            'colors': self.colors,
            'spacing': self.spacing,
            'typography': self.typography,
            'border_radius': self.border_radius,
            'shadows': self.shadows,
            'animations': self.animations
        }
        
    def __repr__(self):
        return f"Theme(name='{self.name}')"


# Predefined themes
def create_dark_theme() -> Theme:
    """Create a dark theme"""
    theme = Theme('dark')
    theme.colors.update({
        'background': (0.1, 0.1, 0.1, 1.0),
        'surface': (0.2, 0.2, 0.2, 1.0),
        'text': (1.0, 1.0, 1.0, 1.0),
        'text_secondary': (0.7, 0.7, 0.7, 1.0)
    })
    return theme


def create_light_theme() -> Theme:
    """Create a light theme"""
    theme = Theme('light')
    theme.colors.update({
        'background': (1.0, 1.0, 1.0, 1.0),
        'surface': (0.95, 0.95, 0.95, 1.0),
        'text': (0.1, 0.1, 0.1, 1.0),
        'text_secondary': (0.4, 0.4, 0.4, 1.0)
    })
    return theme