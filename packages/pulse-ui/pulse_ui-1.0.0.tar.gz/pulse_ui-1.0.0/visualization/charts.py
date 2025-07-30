"""
Chart components for data visualization
"""
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from ..core.component import Component
from ..styling.parser import StyleParser


class Chart(Component):
    """Base chart component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.data = props.get('data', [])
        self.title = props.get('title', '')
        self.x_label = props.get('x_label', '')
        self.y_label = props.get('y_label', '')
        
        # Chart styling
        self.background_color = (0.1, 0.1, 0.1, 1.0)
        self.grid_color = (0.3, 0.3, 0.3, 1.0)
        self.text_color = (1.0, 1.0, 1.0, 1.0)
        self.border_color = (0.5, 0.5, 0.5, 1.0)
        
        # Chart dimensions
        self.chart_margin = 50
        self.chart_width = 0
        self.chart_height = 0
        
    def component_did_mount(self):
        """Calculate chart dimensions when mounted"""
        self.chart_width = self.width - 2 * self.chart_margin
        self.chart_height = self.height - 2 * self.chart_margin
        
    def render_background(self, renderer):
        """Render chart background"""
        # Render background
        renderer.render_rectangle(self.x, self.y, self.width, self.height, self.background_color)
        
        # Render border
        renderer.render_rectangle(self.x, self.y, self.width, 2, self.border_color)
        renderer.render_rectangle(self.x, self.y + self.height - 2, self.width, 2, self.border_color)
        renderer.render_rectangle(self.x, self.y, 2, self.height, self.border_color)
        renderer.render_rectangle(self.x + self.width - 2, self.y, 2, self.height, self.border_color)
        
    def render_grid(self, renderer, x_divisions: int = 10, y_divisions: int = 10):
        """Render chart grid"""
        chart_x = self.x + self.chart_margin
        chart_y = self.y + self.chart_margin
        
        # Vertical grid lines
        for i in range(x_divisions + 1):
            x_pos = chart_x + (self.chart_width * i / x_divisions)
            renderer.render_rectangle(x_pos, chart_y, 1, self.chart_height, self.grid_color)
            
        # Horizontal grid lines
        for i in range(y_divisions + 1):
            y_pos = chart_y + (self.chart_height * i / y_divisions)
            renderer.render_rectangle(chart_x, y_pos, self.chart_width, 1, self.grid_color)
            
    def render_title(self, renderer):
        """Render chart title"""
        if self.title:
            title_x = self.x + self.width // 2
            title_y = self.y + 20
            # renderer.render_text(self.title, title_x, title_y, self.text_color)
            
    def render(self, renderer):
        """Base render method"""
        self.render_background(renderer)
        self.render_grid(renderer)
        self.render_title(renderer)


class LineChart(Chart):
    """Line chart component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.line_color = props.get('line_color', (0.23, 0.45, 1.0, 1.0))
        self.line_width = props.get('line_width', 2)
        self.point_radius = props.get('point_radius', 3)
        self.show_points = props.get('show_points', True)
        
    def render(self, renderer):
        """Render line chart"""
        super().render(renderer)
        
        if not self.data or len(self.data) < 2:
            return
            
        chart_x = self.x + self.chart_margin
        chart_y = self.y + self.chart_margin
        
        # Find data range
        x_values = [point[0] for point in self.data]
        y_values = [point[1] for point in self.data]
        
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        
        # Avoid division by zero
        x_range = max(x_max - x_min, 1)
        y_range = max(y_max - y_min, 1)
        
        # Convert data points to screen coordinates
        screen_points = []
        for x, y in self.data:
            screen_x = chart_x + ((x - x_min) / x_range) * self.chart_width
            screen_y = chart_y + self.chart_height - ((y - y_min) / y_range) * self.chart_height
            screen_points.append((screen_x, screen_y))
            
        # Render lines between points
        for i in range(len(screen_points) - 1):
            x1, y1 = screen_points[i]
            x2, y2 = screen_points[i + 1]
            
            # Simple line rendering (in a full implementation, use proper line rendering)
            dx = x2 - x1
            dy = y2 - y1
            steps = max(abs(dx), abs(dy))
            
            if steps > 0:
                for j in range(int(steps)):
                    t = j / steps
                    x = x1 + t * dx
                    y = y1 + t * dy
                    renderer.render_rectangle(x, y, self.line_width, self.line_width, self.line_color)
                    
        # Render points
        if self.show_points:
            for x, y in screen_points:
                renderer.render_circle(x, y, self.point_radius, self.line_color)


class BarChart(Chart):
    """Bar chart component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.bar_color = props.get('bar_color', (0.23, 0.45, 1.0, 1.0))
        self.bar_spacing = props.get('bar_spacing', 5)
        
    def render(self, renderer):
        """Render bar chart"""
        super().render(renderer)
        
        if not self.data:
            return
            
        chart_x = self.x + self.chart_margin
        chart_y = self.y + self.chart_margin
        
        # Calculate bar dimensions
        bar_count = len(self.data)
        available_width = self.chart_width - (bar_count - 1) * self.bar_spacing
        bar_width = available_width / bar_count
        
        # Find data range
        if isinstance(self.data[0], tuple):
            values = [point[1] for point in self.data]
        else:
            values = self.data
            
        max_value = max(values) if values else 1
        min_value = min(values) if values else 0
        value_range = max(max_value - min_value, 1)
        
        # Render bars
        for i, item in enumerate(self.data):
            if isinstance(item, tuple):
                label, value = item
            else:
                value = item
                label = str(i)
                
            # Calculate bar position and height
            bar_x = chart_x + i * (bar_width + self.bar_spacing)
            bar_height = ((value - min_value) / value_range) * self.chart_height
            bar_y = chart_y + self.chart_height - bar_height
            
            # Render bar
            renderer.render_rectangle(bar_x, bar_y, bar_width, bar_height, self.bar_color)


class PieChart(Chart):
    """Pie chart component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.colors = props.get('colors', [
            (1.0, 0.24, 0.24, 1.0),  # Red
            (0.23, 0.45, 1.0, 1.0),  # Blue
            (0.23, 1.0, 0.24, 1.0),  # Green
            (1.0, 1.0, 0.23, 1.0),   # Yellow
            (0.45, 0.24, 1.0, 1.0),  # Purple
            (1.0, 0.24, 0.45, 1.0)   # Pink
        ])
        
    def render(self, renderer):
        """Render pie chart"""
        super().render(renderer)
        
        if not self.data:
            return
            
        # Calculate center and radius
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        radius = min(self.chart_width, self.chart_height) // 2 - 20
        
        # Calculate total value
        if isinstance(self.data[0], tuple):
            values = [item[1] for item in self.data]
        else:
            values = self.data
            
        total_value = sum(values)
        
        if total_value == 0:
            return
            
        # Render pie slices
        current_angle = 0
        for i, item in enumerate(self.data):
            if isinstance(item, tuple):
                label, value = item
            else:
                value = item
                label = str(i)
                
            # Calculate slice angle
            slice_angle = (value / total_value) * 360
            
            # Get color
            color = self.colors[i % len(self.colors)]
            
            # Render slice (simplified - in full implementation use proper arc rendering)
            # For now, just render a rectangle to indicate the slice
            slice_x = center_x + radius * np.cos(np.radians(current_angle))
            slice_y = center_y + radius * np.sin(np.radians(current_angle))
            renderer.render_rectangle(slice_x - 10, slice_y - 10, 20, 20, color)
            
            current_angle += slice_angle


class ScatterChart(Chart):
    """Scatter plot chart component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.point_color = props.get('point_color', (0.23, 0.45, 1.0, 1.0))
        self.point_radius = props.get('point_radius', 4)
        
    def render(self, renderer):
        """Render scatter chart"""
        super().render(renderer)
        
        if not self.data:
            return
            
        chart_x = self.x + self.chart_margin
        chart_y = self.y + self.chart_margin
        
        # Find data range
        x_values = [point[0] for point in self.data]
        y_values = [point[1] for point in self.data]
        
        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        
        # Avoid division by zero
        x_range = max(x_max - x_min, 1)
        y_range = max(y_max - y_min, 1)
        
        # Render points
        for x, y in self.data:
            screen_x = chart_x + ((x - x_min) / x_range) * self.chart_width
            screen_y = chart_y + self.chart_height - ((y - y_min) / y_range) * self.chart_height
            
            renderer.render_circle(screen_x, screen_y, self.point_radius, self.point_color)