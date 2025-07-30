"""
Advanced plotting components for real-time and interactive data visualization
"""
import time
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Callable
from ..core.component import Component
from .charts import Chart


class Plot(Chart):
    """Advanced plotting component with zooming and panning"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.zoom_x = 1.0
        self.zoom_y = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.is_dragging = False
        self.last_mouse_pos = (0, 0)
        
        # Plot styling
        self.axis_color = (0.7, 0.7, 0.7, 1.0)
        self.tick_color = (0.5, 0.5, 0.5, 1.0)
        
    def handle_mouse_event(self, event_type: str, event_data):
        """Handle mouse events for interaction"""
        if event_type == 'mouse_down':
            self.is_dragging = True
            self.last_mouse_pos = event_data.pos
        elif event_type == 'mouse_up':
            self.is_dragging = False
        elif event_type == 'mouse_move' and self.is_dragging:
            current_pos = event_data.pos
            dx = current_pos[0] - self.last_mouse_pos[0]
            dy = current_pos[1] - self.last_mouse_pos[1]
            
            # Pan the plot
            self.pan_x += dx / self.zoom_x
            self.pan_y += dy / self.zoom_y
            
            self.last_mouse_pos = current_pos
        elif event_type == 'mouse_wheel':
            # Zoom
            zoom_factor = 1.1 if event_data.y > 0 else 0.9
            self.zoom_x *= zoom_factor
            self.zoom_y *= zoom_factor
            
    def render_axes(self, renderer):
        """Render coordinate axes"""
        chart_x = self.x + self.chart_margin
        chart_y = self.y + self.chart_margin
        
        # X-axis
        y_axis_pos = chart_y + self.chart_height // 2
        renderer.render_rectangle(chart_x, y_axis_pos, self.chart_width, 2, self.axis_color)
        
        # Y-axis
        x_axis_pos = chart_x + self.chart_width // 2
        renderer.render_rectangle(x_axis_pos, chart_y, 2, self.chart_height, self.axis_color)
        
    def screen_to_data_coords(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to data coordinates"""
        chart_x = self.x + self.chart_margin
        chart_y = self.y + self.chart_margin
        
        # Normalize to 0-1 range
        norm_x = (screen_x - chart_x) / self.chart_width
        norm_y = 1.0 - (screen_y - chart_y) / self.chart_height  # Flip Y
        
        # Apply zoom and pan
        data_x = (norm_x - 0.5) / self.zoom_x + self.pan_x
        data_y = (norm_y - 0.5) / self.zoom_y + self.pan_y
        
        return data_x, data_y
        
    def data_to_screen_coords(self, data_x: float, data_y: float) -> Tuple[float, float]:
        """Convert data coordinates to screen coordinates"""
        chart_x = self.x + self.chart_margin
        chart_y = self.y + self.chart_margin
        
        # Apply pan and zoom
        norm_x = (data_x - self.pan_x) * self.zoom_x + 0.5
        norm_y = (data_y - self.pan_y) * self.zoom_y + 0.5
        
        # Convert to screen coordinates
        screen_x = chart_x + norm_x * self.chart_width
        screen_y = chart_y + (1.0 - norm_y) * self.chart_height  # Flip Y
        
        return screen_x, screen_y


class DataPlot(Plot):
    """Data plotting component with multiple series support"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.series = props.get('series', [])  # List of data series
        self.series_colors = props.get('series_colors', [
            (1.0, 0.24, 0.24, 1.0),  # Red
            (0.23, 0.45, 1.0, 1.0),  # Blue
            (0.23, 1.0, 0.24, 1.0),  # Green
            (1.0, 1.0, 0.23, 1.0),   # Yellow
            (0.45, 0.24, 1.0, 1.0),  # Purple
        ])
        
    def add_series(self, name: str, data: List[Tuple[float, float]], color: Optional[Tuple[float, float, float, float]] = None):
        """Add a data series to the plot"""
        series_data = {
            'name': name,
            'data': data,
            'color': color or self.series_colors[len(self.series) % len(self.series_colors)]
        }
        self.series.append(series_data)
        
    def clear_series(self):
        """Clear all data series"""
        self.series.clear()
        
    def render(self, renderer):
        """Render the data plot"""
        super().render(renderer)
        self.render_axes(renderer)
        
        # Render each series
        for series in self.series:
            self.render_series(renderer, series)
            
    def render_series(self, renderer, series: Dict[str, Any]):
        """Render a single data series"""
        data = series['data']
        color = series['color']
        
        if len(data) < 2:
            return
            
        # Convert data points to screen coordinates
        screen_points = []
        for x, y in data:
            screen_x, screen_y = self.data_to_screen_coords(x, y)
            screen_points.append((screen_x, screen_y))
            
        # Render lines between points
        for i in range(len(screen_points) - 1):
            x1, y1 = screen_points[i]
            x2, y2 = screen_points[i + 1]
            
            # Simple line rendering
            dx = x2 - x1
            dy = y2 - y1
            steps = max(abs(dx), abs(dy))
            
            if steps > 0:
                for j in range(int(steps)):
                    t = j / steps
                    x = x1 + t * dx
                    y = y1 + t * dy
                    renderer.render_rectangle(x, y, 2, 2, color)


class RealTimePlot(DataPlot):
    """Real-time plotting component for streaming data"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.max_points = props.get('max_points', 1000)
        self.update_interval = props.get('update_interval', 0.1)  # seconds
        self.last_update = time.time()
        self.data_callback: Optional[Callable] = props.get('data_callback')
        self.auto_scale = props.get('auto_scale', True)
        
        # Real-time data storage
        self.real_time_data: Dict[str, List[Tuple[float, float]]] = {}
        
    def add_real_time_series(self, name: str, color: Optional[Tuple[float, float, float, float]] = None):
        """Add a real-time data series"""
        self.real_time_data[name] = []
        series_data = {
            'name': name,
            'data': self.real_time_data[name],
            'color': color or self.series_colors[len(self.series) % len(self.series_colors)]
        }
        self.series.append(series_data)
        
    def add_data_point(self, series_name: str, x: float, y: float):
        """Add a data point to a real-time series"""
        if series_name in self.real_time_data:
            data_list = self.real_time_data[series_name]
            data_list.append((x, y))
            
            # Limit the number of points
            if len(data_list) > self.max_points:
                data_list.pop(0)
                
            # Auto-scale if enabled
            if self.auto_scale:
                self.update_scale()
                
    def update_scale(self):
        """Update the plot scale to fit all data"""
        all_x = []
        all_y = []
        
        for data_list in self.real_time_data.values():
            if data_list:
                x_vals = [point[0] for point in data_list]
                y_vals = [point[1] for point in data_list]
                all_x.extend(x_vals)
                all_y.extend(y_vals)
                
        if all_x and all_y:
            x_range = max(all_x) - min(all_x)
            y_range = max(all_y) - min(all_y)
            
            if x_range > 0:
                self.zoom_x = 0.8 / x_range
                self.pan_x = (max(all_x) + min(all_x)) / 2
                
            if y_range > 0:
                self.zoom_y = 0.8 / y_range
                self.pan_y = (max(all_y) + min(all_y)) / 2
                
    def update(self):
        """Update the real-time plot"""
        super().update()
        
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            # Call data callback if provided
            if self.data_callback:
                new_data = self.data_callback()
                if new_data:
                    for series_name, points in new_data.items():
                        if isinstance(points, list):
                            for x, y in points:
                                self.add_data_point(series_name, x, y)
                        else:
                            x, y = points
                            self.add_data_point(series_name, x, y)
                            
            self.last_update = current_time