"""
StyleParser - Parses TailwindCSS-like utility classes
"""
import re
from typing import Dict, Any, List
from .utilities import UtilityClasses


class StyleParser:
    """Parses TailwindCSS-like utility classes into style properties"""
    
    def __init__(self):
        self.utilities = UtilityClasses()
        
    def parse_classes(self, classes: str) -> Dict[str, Any]:
        """Parse a string of CSS classes into style properties"""
        if not classes:
            return {}
            
        # Split classes by whitespace
        class_list = classes.split()
        
        # Parse each class
        styles = {}
        for class_name in class_list:
            class_styles = self.parse_single_class(class_name)
            styles.update(class_styles)
            
        return styles
        
    def parse_single_class(self, class_name: str) -> Dict[str, Any]:
        """Parse a single CSS class"""
        # Color classes
        if class_name.startswith('bg-'):
            return self.parse_background_class(class_name)
        elif class_name.startswith('text-'):
            return self.parse_text_class(class_name)
        elif class_name.startswith('border-'):
            return self.parse_border_class(class_name)
        
        # Spacing classes
        elif class_name.startswith('p-') or class_name.startswith('padding-'):
            return self.parse_padding_class(class_name)
        elif class_name.startswith('m-') or class_name.startswith('margin-'):
            return self.parse_margin_class(class_name)
            
        # Size classes
        elif class_name.startswith('w-') or class_name.startswith('width-'):
            return self.parse_width_class(class_name)
        elif class_name.startswith('h-') or class_name.startswith('height-'):
            return self.parse_height_class(class_name)
            
        # Layout classes
        elif class_name in ['flex', 'block', 'inline', 'inline-block']:
            return self.parse_display_class(class_name)
        elif class_name.startswith('flex-'):
            return self.parse_flex_class(class_name)
            
        # Border radius classes
        elif class_name.startswith('rounded'):
            return self.parse_border_radius_class(class_name)
            
        return {}
        
    def parse_background_class(self, class_name: str) -> Dict[str, Any]:
        """Parse background color classes"""
        # Remove 'bg-' prefix
        color_name = class_name[3:]
        
        # Handle variants like 'bg-blue-500'
        if '-' in color_name:
            color_base, intensity = color_name.split('-', 1)
            color = self.utilities.get_color(color_base, intensity)
        else:
            color = self.utilities.get_color(color_name)
            
        return {'background_color': color}
        
    def parse_text_class(self, class_name: str) -> Dict[str, Any]:
        """Parse text classes"""
        # Remove 'text-' prefix
        text_property = class_name[5:]
        
        # Handle color classes
        if text_property in ['red', 'blue', 'green', 'yellow', 'purple', 'pink', 'gray', 'black', 'white']:
            color = self.utilities.get_color(text_property)
            return {'text_color': color}
        elif '-' in text_property:
            color_base, intensity = text_property.split('-', 1)
            if color_base in ['red', 'blue', 'green', 'yellow', 'purple', 'pink', 'gray']:
                color = self.utilities.get_color(color_base, intensity)
                return {'text_color': color}
                
        # Handle size classes
        size_map = {
            'xs': 12,
            'sm': 14,
            'base': 16,
            'lg': 18,
            'xl': 20,
            '2xl': 24,
            '3xl': 30,
            '4xl': 36,
            '5xl': 48,
            '6xl': 64
        }
        
        if text_property in size_map:
            return {'font_size': size_map[text_property]}
            
        return {}
        
    def parse_border_class(self, class_name: str) -> Dict[str, Any]:
        """Parse border classes"""
        # Remove 'border-' prefix
        border_property = class_name[7:]
        
        # Handle color classes
        if border_property in ['red', 'blue', 'green', 'yellow', 'purple', 'pink', 'gray', 'black', 'white']:
            color = self.utilities.get_color(border_property)
            return {'border_color': color}
        elif '-' in border_property:
            color_base, intensity = border_property.split('-', 1)
            if color_base in ['red', 'blue', 'green', 'yellow', 'purple', 'pink', 'gray']:
                color = self.utilities.get_color(color_base, intensity)
                return {'border_color': color}
                
        # Handle width classes
        width_map = {
            '0': 0,
            '1': 1,
            '2': 2,
            '4': 4,
            '8': 8
        }
        
        if border_property in width_map:
            return {'border_width': width_map[border_property]}
            
        return {}
        
    def parse_padding_class(self, class_name: str) -> Dict[str, Any]:
        """Parse padding classes"""
        # Handle different padding formats
        if class_name.startswith('p-'):
            value = class_name[2:]
        else:
            value = class_name[8:]  # padding-
            
        padding_map = {
            '0': 0,
            '1': 4,
            '2': 8,
            '3': 12,
            '4': 16,
            '5': 20,
            '6': 24,
            '8': 32,
            '10': 40,
            '12': 48,
            '16': 64
        }
        
        if value in padding_map:
            return {'padding': padding_map[value]}
            
        return {}
        
    def parse_margin_class(self, class_name: str) -> Dict[str, Any]:
        """Parse margin classes"""
        # Handle different margin formats
        if class_name.startswith('m-'):
            value = class_name[2:]
        else:
            value = class_name[7:]  # margin-
            
        margin_map = {
            '0': 0,
            '1': 4,
            '2': 8,
            '3': 12,
            '4': 16,
            '5': 20,
            '6': 24,
            '8': 32,
            '10': 40,
            '12': 48,
            '16': 64
        }
        
        if value in margin_map:
            return {'margin': margin_map[value]}
            
        return {}
        
    def parse_width_class(self, class_name: str) -> Dict[str, Any]:
        """Parse width classes"""
        # Implementation for width classes
        return {}
        
    def parse_height_class(self, class_name: str) -> Dict[str, Any]:
        """Parse height classes"""
        # Implementation for height classes
        return {}
        
    def parse_display_class(self, class_name: str) -> Dict[str, Any]:
        """Parse display classes"""
        return {'display': class_name}
        
    def parse_flex_class(self, class_name: str) -> Dict[str, Any]:
        """Parse flex classes"""
        # Implementation for flex classes
        return {}
        
    def parse_border_radius_class(self, class_name: str) -> Dict[str, Any]:
        """Parse border radius classes"""
        radius_map = {
            'rounded': 4,
            'rounded-sm': 2,
            'rounded-md': 6,
            'rounded-lg': 8,
            'rounded-xl': 12,
            'rounded-full': 9999
        }
        
        if class_name in radius_map:
            return {'border_radius': radius_map[class_name]}
            
        return {}