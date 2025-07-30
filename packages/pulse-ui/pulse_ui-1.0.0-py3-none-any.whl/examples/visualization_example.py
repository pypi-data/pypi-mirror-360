"""
Visualization example demonstrating charts and plots
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
from pulse_ui.components.basic import Container, Button, Text
from pulse_ui.visualization.charts import LineChart, BarChart, PieChart
from pulse_ui.visualization.plots import RealTimePlot
from pulse_ui.visualization.data_table import DataTable


class VisualizationExample:
    """Visualization example application"""
    
    def __init__(self):
        self.app = Application("Visualization ModernGUI Example")
        self.window = self.app.create_window("Visualization Example", 1200, 800)
        
        # Generate sample data
        self.generate_sample_data()
        
        # Create UI components
        self.create_ui()
        
    def generate_sample_data(self):
        """Generate sample data for charts"""
        # Line chart data
        self.line_data = [(i, math.sin(i * 0.5) * 50 + 100) for i in range(20)]
        
        # Bar chart data
        self.bar_data = [
            ("Jan", 50),
            ("Feb", 75),
            ("Mar", 100),
            ("Apr", 85),
            ("May", 110),
            ("Jun", 95)
        ]
        
        # Pie chart data
        self.pie_data = [
            ("Desktop", 45),
            ("Mobile", 35),
            ("Tablet", 20)
        ]
        
        # Table data
        self.table_data = [
            {"Name": "Alice", "Age": 25, "City": "New York", "Salary": 50000},
            {"Name": "Bob", "Age": 30, "City": "San Francisco", "Salary": 75000},
            {"Name": "Charlie", "Age": 35, "City": "Chicago", "Salary": 60000},
            {"Name": "Diana", "Age": 28, "City": "Boston", "Salary": 55000},
            {"Name": "Eve", "Age": 32, "City": "Seattle", "Salary": 70000}
        ]
        
    def create_ui(self):
        """Create the user interface"""
        # Create main container
        main_container = Container(
            classes="bg-gray-900 p-4"
        )
        main_container.set_size(1200, 800)
        
        # Create title
        title = Text(
            "Data Visualization Examples",
            classes="text-white text-2xl font-bold mb-4"
        )
        title.set_position(20, 20)
        title.set_size(1160, 40)
        
        # Create line chart
        line_chart = LineChart(
            data=self.line_data,
            title="Sample Line Chart",
            line_color=(0.23, 0.45, 1.0, 1.0)
        )
        line_chart.set_position(20, 80)
        line_chart.set_size(380, 250)
        
        # Create bar chart
        bar_chart = BarChart(
            data=self.bar_data,
            title="Sample Bar Chart",
            bar_color=(0.23, 1.0, 0.24, 1.0)
        )
        bar_chart.set_position(420, 80)
        bar_chart.set_size(380, 250)
        
        # Create pie chart
        pie_chart = PieChart(
            data=self.pie_data,
            title="Sample Pie Chart"
        )
        pie_chart.set_position(820, 80)
        pie_chart.set_size(360, 250)
        
        # Create real-time plot
        real_time_plot = RealTimePlot(
            max_points=100,
            update_interval=0.1,
            data_callback=self.get_real_time_data
        )
        real_time_plot.add_real_time_series("Sine Wave", (1.0, 0.24, 0.24, 1.0))
        real_time_plot.add_real_time_series("Cosine Wave", (0.23, 0.45, 1.0, 1.0))
        real_time_plot.set_position(20, 350)
        real_time_plot.set_size(580, 200)
        
        # Create data table
        data_table = DataTable(
            data=self.table_data,
            columns=["Name", "Age", "City", "Salary"],
            headers=["Name", "Age", "City", "Salary ($)"],
            row_height=25,
            on_row_select=self.on_table_row_select
        )
        data_table.set_position(620, 350)
        data_table.set_size(560, 200)
        
        # Create control buttons
        refresh_button = Button(
            "Refresh Data",
            classes="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-4",
            on_click=self.refresh_data
        )
        refresh_button.set_position(20, 570)
        refresh_button.set_size(120, 40)
        
        export_button = Button(
            "Export Data",
            classes="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded",
            on_click=self.export_data
        )
        export_button.set_position(160, 570)
        export_button.set_size(120, 40)
        
        # Add components to container
        main_container.add_child(title)
        main_container.add_child(line_chart)
        main_container.add_child(bar_chart)
        main_container.add_child(pie_chart)
        main_container.add_child(real_time_plot)
        main_container.add_child(data_table)
        main_container.add_child(refresh_button)
        main_container.add_child(export_button)
        
        # Set container as root
        self.window.set_root_component(main_container)
        
        # Store references for updates
        self.real_time_plot = real_time_plot
        self.data_table = data_table
        
    def get_real_time_data(self):
        """Generate real-time data for the plot"""
        current_time = time.time()
        
        return {
            "Sine Wave": (current_time, math.sin(current_time) * 50),
            "Cosine Wave": (current_time, math.cos(current_time) * 30)
        }
        
    def refresh_data(self, button):
        """Refresh all data"""
        print("Refreshing data...")
        
        # Generate new random data
        self.line_data = [(i, random.uniform(50, 150)) for i in range(20)]
        self.bar_data = [(month, random.randint(40, 120)) for month, _ in self.bar_data]
        
        # Update charts would go here in a full implementation
        
    def export_data(self, button):
        """Export data"""
        print("Exporting data...")
        
    def on_table_row_select(self, row_index, row_data):
        """Handle table row selection"""
        print(f"Selected row {row_index}: {row_data}")
        
    def run(self):
        """Run the application"""
        self.app.run()


if __name__ == "__main__":
    example = VisualizationExample()
    example.run()