"""
Complete example demonstrating all ModernGUI features
"""
import sys
import os
import math
import random
import time

# Add the pulse_ui package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pulse_ui.core.application import Application
from pulse_ui.core.window import Window
from pulse_ui.components.basic import Container, Button, Text, Input
from pulse_ui.components.layout import Row, Column, Grid
from pulse_ui.components.display import Card, Badge, Progress, Divider, Icon
from pulse_ui.visualization.charts import LineChart, BarChart
from pulse_ui.visualization.plots import RealTimePlot
from pulse_ui.animation.animator import Animator
from pulse_ui.animation.transitions import Transition


class CompleteExample:
    """Complete example showcasing all ModernGUI features"""
    
    def __init__(self):
        self.app = Application("Complete ModernGUI Demo")
        self.window = self.app.create_window("ModernGUI - Complete Demo", 1400, 900)
        
        # Initialize animation system
        self.animator = Animator()
        self.transitions = Transition(self.animator)
        
        # Data for visualizations
        self.setup_data()
        
        # Create UI components
        self.create_ui()
        
    def setup_data(self):
        """Setup sample data for charts and visualizations"""
        # Sample data for charts
        self.sales_data = [
            ("Jan", 65), ("Feb", 78), ("Mar", 92), ("Apr", 81),
            ("May", 95), ("Jun", 88), ("Jul", 102), ("Aug", 96)
        ]
        
        self.performance_data = [(i, 50 + 30 * math.sin(i * 0.3) + random.uniform(-10, 10)) for i in range(30)]
        
    def create_ui(self):
        """Create the complete user interface"""
        # Main container
        main_container = Container(classes="bg-gray-900")
        main_container.set_size(1400, 900)
        
        # Header section
        self.create_header(main_container)
        
        # Navigation sidebar
        self.create_sidebar(main_container)
        
        # Main content area
        self.create_main_content(main_container)
        
        # Footer
        self.create_footer(main_container)
        
        # Set container as root
        self.window.set_root_component(main_container)
        
    def create_header(self, parent):
        """Create the application header"""
        header = Container(classes="bg-gray-800 border-b border-gray-700")
        header.set_position(0, 0)
        header.set_size(1400, 70)
        
        # Logo and title
        logo_container = Row(gap=12, align_items='center')
        logo_container.set_position(20, 15)
        logo_container.set_size(300, 40)
        
        logo_icon = Icon("star", size=32, color=(0.23, 0.45, 1.0, 1.0))
        logo_icon.set_size(40, 40)
        
        app_title = Text("ModernGUI Demo", classes="text-white text-xl font-bold")
        app_title.set_size(200, 30)
        
        logo_container.add_child(logo_icon)
        logo_container.add_child(app_title)
        
        # Header actions
        header_actions = Row(gap=10, align_items='center', justify_content='end')
        header_actions.set_position(1200, 15)
        header_actions.set_size(180, 40)
        
        # Search input
        search_input = Input(placeholder="Search...", classes="bg-gray-700 text-white border border-gray-600 rounded px-3 py-2")
        search_input.set_size(120, 30)
        
        # User menu button
        user_btn = Button("User", classes="bg-blue-600 hover:bg-blue-700 text-white rounded px-3 py-2")
        user_btn.set_size(50, 30)
        
        header_actions.add_child(search_input)
        header_actions.add_child(user_btn)
        
        header.add_child(logo_container)
        header.add_child(header_actions)
        parent.add_child(header)
        
    def create_sidebar(self, parent):
        """Create the navigation sidebar"""
        sidebar = Container(classes="bg-gray-800 border-r border-gray-700")
        sidebar.set_position(0, 70)
        sidebar.set_size(250, 780)
        
        # Navigation menu
        nav_menu = Column(gap=5, align_items='start')
        nav_menu.set_position(20, 30)
        nav_menu.set_size(210, 600)
        
        menu_items = [
            {"name": "Dashboard", "icon": "home"},
            {"name": "Analytics", "icon": "chart"},
            {"name": "Data Tables", "icon": "table"},
            {"name": "Settings", "icon": "settings"},
            {"name": "Help", "icon": "info"}
        ]
        
        for item in menu_items:
            menu_item = self.create_menu_item(item["name"], item["icon"])
            nav_menu.add_child(menu_item)
            
        sidebar.add_child(nav_menu)
        parent.add_child(sidebar)
        
    def create_menu_item(self, name, icon_name):
        """Create a navigation menu item"""
        item_container = Row(gap=10, align_items='center')
        item_container.set_size(210, 40)
        
        # Icon
        icon = Icon(icon_name, size=20, color=(0.7, 0.7, 0.7, 1.0))
        icon.set_size(30, 30)
        
        # Text
        text = Text(name, classes="text-gray-300 hover:text-white")
        text.set_size(170, 25)
        
        item_container.add_child(icon)
        item_container.add_child(text)
        
        return item_container
        
    def create_main_content(self, parent):
        """Create the main content area"""
        main_content = Container(classes="bg-gray-900 p-6")
        main_content.set_position(250, 70)
        main_content.set_size(1150, 780)
        
        # Content grid
        content_grid = Grid(columns=2, gap=20)
        content_grid.set_position(0, 0)
        content_grid.set_size(1150, 780)
        
        # Dashboard cards
        self.create_dashboard_cards(content_grid)
        
        # Charts section
        self.create_charts_section(content_grid)
        
        # Real-time monitoring
        self.create_realtime_section(content_grid)
        
        # Data management
        self.create_data_section(content_grid)
        
        main_content.add_child(content_grid)
        parent.add_child(main_content)
        
    def create_dashboard_cards(self, parent):
        """Create dashboard overview cards"""
        cards_container = Container()
        cards_container.set_size(550, 200)
        
        card_grid = Grid(columns=2, gap=15)
        card_grid.set_size(550, 200)
        
        # Metrics cards
        metrics = [
            {"title": "Total Users", "value": "12,345", "change": "+12%", "color": (0.23, 0.45, 1.0, 1.0)},
            {"title": "Revenue", "value": "$98,765", "change": "+8%", "color": (0.23, 1.0, 0.24, 1.0)},
            {"title": "Orders", "value": "1,234", "change": "-2%", "color": (1.0, 0.8, 0.2, 1.0)},
            {"title": "Performance", "value": "94%", "change": "+5%", "color": (0.45, 0.24, 1.0, 1.0)}
        ]
        
        for metric in metrics:
            card = self.create_metric_card(metric)
            card_grid.add_child(card)
            
        cards_container.add_child(card_grid)
        parent.add_child(cards_container)
        
    def create_metric_card(self, metric):
        """Create a single metric card"""
        card = Card(border_radius=8, padding=16)
        card.set_size(260, 90)
        
        # Title
        title = Text(metric["title"], classes="text-gray-300 text-sm")
        title.set_size(200, 20)
        title.set_position(16, 16)
        
        # Value
        value = Text(metric["value"], classes="text-white text-2xl font-bold")
        value.set_size(200, 30)
        value.set_position(16, 40)
        
        # Change indicator
        change_text = Text(metric["change"], classes="text-sm font-medium")
        change_text.set_size(60, 20)
        change_text.set_position(180, 16)
        
        # Accent color bar
        accent_bar = Container()
        accent_bar.set_position(0, 0)
        accent_bar.set_size(4, 90)
        # Set accent bar color based on metric color
        
        card.add_child(accent_bar)
        card.add_child(title)
        card.add_child(value)
        card.add_child(change_text)
        
        return card
        
    def create_charts_section(self, parent):
        """Create charts visualization section"""
        charts_container = Card(border_radius=8, padding=20)
        charts_container.set_size(550, 360)
        
        # Section title
        section_title = Text("Analytics Overview", classes="text-white text-lg font-bold mb-4")
        section_title.set_size(500, 30)
        section_title.set_position(20, 20)
        
        # Charts grid
        charts_grid = Grid(columns=1, gap=20)
        charts_grid.set_position(20, 60)
        charts_grid.set_size(510, 280)
        
        # Sales chart
        sales_chart = BarChart(
            data=self.sales_data,
            title="Monthly Sales",
            bar_color=(0.23, 0.45, 1.0, 1.0)
        )
        sales_chart.set_size(510, 130)
        
        # Performance chart
        performance_chart = LineChart(
            data=self.performance_data,
            title="Performance Trend",
            line_color=(0.23, 1.0, 0.24, 1.0)
        )
        performance_chart.set_size(510, 130)
        
        charts_grid.add_child(sales_chart)
        charts_grid.add_child(performance_chart)
        
        charts_container.add_child(section_title)
        charts_container.add_child(charts_grid)
        
        parent.add_child(charts_container)
        
    def create_realtime_section(self, parent):
        """Create real-time monitoring section"""
        realtime_container = Card(border_radius=8, padding=20)
        realtime_container.set_size(550, 200)
        
        # Section title
        section_title = Text("Real-time Monitoring", classes="text-white text-lg font-bold")
        section_title.set_size(400, 30)
        section_title.set_position(20, 20)
        
        # Real-time plot
        realtime_plot = RealTimePlot(
            max_points=50,
            update_interval=0.5,
            data_callback=self.get_realtime_data
        )
        realtime_plot.add_real_time_series("CPU Usage", (1.0, 0.24, 0.24, 1.0))
        realtime_plot.add_real_time_series("Memory Usage", (0.23, 0.45, 1.0, 1.0))
        realtime_plot.set_position(20, 60)
        realtime_plot.set_size(510, 120)
        
        realtime_container.add_child(section_title)
        realtime_container.add_child(realtime_plot)
        
        parent.add_child(realtime_container)
        
    def create_data_section(self, parent):
        """Create data management section"""
        data_container = Card(border_radius=8, padding=20)
        data_container.set_size(550, 200)
        
        # Section title with actions
        header_row = Row(gap=10, justify_content='space-between', align_items='center')
        header_row.set_position(20, 20)
        header_row.set_size(510, 40)
        
        section_title = Text("Data Management", classes="text-white text-lg font-bold")
        section_title.set_size(300, 30)
        
        # Action buttons
        actions_row = Row(gap=8, align_items='center')
        actions_row.set_size(200, 30)
        
        refresh_btn = Button("Refresh", classes="bg-blue-600 hover:bg-blue-700 text-white text-sm rounded px-3 py-1")
        refresh_btn.set_size(60, 25)
        
        export_btn = Button("Export", classes="bg-green-600 hover:bg-green-700 text-white text-sm rounded px-3 py-1")
        export_btn.set_size(60, 25)
        
        actions_row.add_child(refresh_btn)
        actions_row.add_child(export_btn)
        
        header_row.add_child(section_title)
        header_row.add_child(actions_row)
        
        # Progress indicators
        progress_section = Column(gap=10, align_items='start')
        progress_section.set_position(20, 80)
        progress_section.set_size(510, 100)
        
        # Different progress items
        progress_items = [
            {"label": "Data Processing", "value": 75},
            {"label": "File Upload", "value": 100},
            {"label": "Analysis", "value": 45}
        ]
        
        for item in progress_items:
            progress_row = Row(gap=10, align_items='center')
            progress_row.set_size(510, 25)
            
            label = Text(item["label"], classes="text-gray-300 text-sm")
            label.set_size(120, 20)
            
            progress = Progress(value=item["value"], show_text=True)
            progress.set_size(300, 15)
            
            progress_row.add_child(label)
            progress_row.add_child(progress)
            progress_section.add_child(progress_row)
            
        data_container.add_child(header_row)
        data_container.add_child(progress_section)
        
        parent.add_child(data_container)
        
    def create_footer(self, parent):
        """Create the application footer"""
        footer = Container(classes="bg-gray-800 border-t border-gray-700")
        footer.set_position(0, 850)
        footer.set_size(1400, 50)
        
        footer_content = Row(gap=20, justify_content='space-between', align_items='center')
        footer_content.set_position(20, 10)
        footer_content.set_size(1360, 30)
        
        # Left side - version info
        version_info = Text("ModernGUI v0.1.0 - Python GUI Framework", classes="text-gray-400 text-sm")
        version_info.set_size(400, 20)
        
        # Right side - status indicators
        status_row = Row(gap=15, align_items='center')
        status_row.set_size(300, 20)
        
        # Status indicators
        statuses = [
            {"label": "Server", "status": "online", "color": (0.23, 1.0, 0.24, 1.0)},
            {"label": "Database", "status": "online", "color": (0.23, 1.0, 0.24, 1.0)},
            {"label": "Cache", "status": "warning", "color": (1.0, 0.8, 0.2, 1.0)}
        ]
        
        for status in statuses:
            status_item = Row(gap=5, align_items='center')
            status_item.set_size(80, 20)
            
            indicator = Container()
            indicator.set_size(8, 8)
            # Set indicator color based on status
            
            status_text = Text(status["label"], classes="text-gray-400 text-xs")
            status_text.set_size(60, 15)
            
            status_item.add_child(indicator)
            status_item.add_child(status_text)
            status_row.add_child(status_item)
            
        footer_content.add_child(version_info)
        footer_content.add_child(status_row)
        
        footer.add_child(footer_content)
        parent.add_child(footer)
        
    def get_realtime_data(self):
        """Generate real-time data for monitoring"""
        current_time = time.time()
        
        # Simulate CPU and memory usage
        cpu_usage = 30 + 20 * math.sin(current_time * 0.5) + random.uniform(-5, 5)
        memory_usage = 50 + 15 * math.cos(current_time * 0.3) + random.uniform(-3, 3)
        
        return {
            "CPU Usage": (current_time, max(0, min(100, cpu_usage))),
            "Memory Usage": (current_time, max(0, min(100, memory_usage)))
        }
        
    def run(self):
        """Run the application"""
        # Start with entrance animations
        self.animate_entrance()
        
        # Run the application loop
        self.app.run()
        
    def animate_entrance(self):
        """Animate the entrance of UI elements"""
        # This would animate the entrance of components
        # In a full implementation, you would use the animator
        pass


if __name__ == "__main__":
    example = CompleteExample()
    example.run()