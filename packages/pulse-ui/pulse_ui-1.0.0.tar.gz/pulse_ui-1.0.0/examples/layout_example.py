"""
Layout example demonstrating different layout components
"""
import sys
import os

# Add the pulse_ui package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pulse_ui.core.application import Application
from pulse_ui.core.window import Window
from pulse_ui.components.basic import Container, Button, Text
from pulse_ui.components.layout import Row, Column, Grid, Stack
from pulse_ui.components.display import Card, Badge, Progress, Divider


class LayoutExample:
    """Layout example application"""
    
    def __init__(self):
        self.app = Application("Layout ModernGUI Example")
        self.window = self.app.create_window("Layout Example", 1000, 700)
        
        # Create UI components
        self.create_ui()
        
    def create_ui(self):
        """Create the user interface"""
        # Create main container
        main_container = Container(
            classes="bg-gray-900 p-4"
        )
        main_container.set_size(1000, 700)
        
        # Create title
        title = Text(
            "Layout Components Demo",
            classes="text-white text-2xl font-bold mb-4"
        )
        title.set_position(20, 20)
        title.set_size(960, 40)
        
        # Create row layout example
        row_title = Text("Row Layout (Horizontal)", classes="text-white text-lg font-bold")
        row_title.set_position(20, 80)
        row_title.set_size(300, 30)
        
        row_container = Row(gap=10, justify_content='start', align_items='center')
        row_container.set_position(20, 120)
        row_container.set_size(460, 60)
        
        # Add buttons to row
        for i in range(3):
            btn = Button(f"Button {i+1}", classes=f"bg-blue-{500+i*100} text-white font-bold py-2 px-4 rounded")
            btn.set_size(140, 40)
            row_container.add_child(btn)
            
        # Create column layout example
        col_title = Text("Column Layout (Vertical)", classes="text-white text-lg font-bold")
        col_title.set_position(500, 80)
        col_title.set_size(300, 30)
        
        col_container = Column(gap=10, justify_content='start', align_items='start')
        col_container.set_position(500, 120)
        col_container.set_size(200, 200)
        
        # Add items to column
        col_items = ["Item 1", "Item 2", "Item 3"]
        for i, item_text in enumerate(col_items):
            item = Text(item_text, classes="text-gray-300 bg-gray-700 p-2 rounded")
            item.set_size(180, 30)
            col_container.add_child(item)
            
        # Create grid layout example
        grid_title = Text("Grid Layout", classes="text-white text-lg font-bold")
        grid_title.set_position(20, 200)
        grid_title.set_size(300, 30)
        
        grid_container = Grid(columns=3, gap=8)
        grid_container.set_position(20, 240)
        grid_container.set_size(460, 180)
        
        # Add items to grid
        for i in range(9):
            grid_item = Card(background_color=(0.1 + i*0.05, 0.2 + i*0.02, 0.3 + i*0.01, 1.0))
            grid_item_text = Text(f"Grid {i+1}", classes="text-white text-center")
            grid_item_text.set_size(140, 50)
            grid_item.add_child(grid_item_text)
            grid_container.add_child(grid_item)
            
        # Create stack layout example
        stack_title = Text("Stack Layout (Overlapping)", classes="text-white text-lg font-bold")
        stack_title.set_position(500, 200)
        stack_title.set_size(300, 30)
        
        stack_container = Stack(align_items='center')
        stack_container.set_position(500, 240)
        stack_container.set_size(200, 120)
        
        # Add items to stack
        base_card = Card(background_color=(0.2, 0.2, 0.2, 1.0))
        base_card.set_size(180, 100)
        
        overlay_text = Text("Overlay Text", classes="text-white text-center font-bold")
        overlay_text.set_size(160, 30)
        
        badge = Badge("NEW", background_color=(1.0, 0.2, 0.2, 1.0))
        badge.set_size(40, 20)
        badge.set_position(520, 250)  # Top-right corner
        
        stack_container.add_child(base_card)
        stack_container.add_child(overlay_text)
        stack_container.add_child(badge)
        
        # Create progress bars example
        progress_title = Text("Progress Bars", classes="text-white text-lg font-bold")
        progress_title.set_position(20, 450)
        progress_title.set_size(300, 30)
        
        # Different progress values
        progress_values = [25, 50, 75, 100]
        progress_colors = [
            (1.0, 0.2, 0.2, 1.0),  # Red
            (1.0, 0.8, 0.2, 1.0),  # Yellow
            (0.2, 0.6, 1.0, 1.0),  # Blue
            (0.2, 1.0, 0.2, 1.0)   # Green
        ]
        
        for i, (value, color) in enumerate(zip(progress_values, progress_colors)):
            progress = Progress(value=value, fill_color=color, show_text=True)
            progress.set_position(20, 490 + i * 40)
            progress.set_size(300, 20)
            main_container.add_child(progress)
            
        # Create dividers
        divider1 = Divider(orientation='horizontal', thickness=2)
        divider1.set_position(20, 430)
        divider1.set_size(960, 10)
        
        divider2 = Divider(orientation='vertical', thickness=2)
        divider2.set_position(480, 80)
        divider2.set_size(10, 340)
        
        # Create cards with content
        card_title = Text("Card Components", classes="text-white text-lg font-bold")
        card_title.set_position(520, 450)
        card_title.set_size(300, 30)
        
        # Feature cards
        feature_cards_data = [
            {"title": "Fast Performance", "desc": "GPU-accelerated rendering"},
            {"title": "Easy to Use", "desc": "React-like components"},
            {"title": "Customizable", "desc": "TailwindCSS styling"}
        ]
        
        for i, card_data in enumerate(feature_cards_data):
            card = Card(border_radius=8, padding=12)
            card.set_position(520 + i * 150, 490)
            card.set_size(140, 80)
            
            card_title_text = Text(card_data["title"], classes="text-white text-sm font-bold")
            card_title_text.set_size(116, 20)
            card_title_text.set_position(532, 500)
            
            card_desc = Text(card_data["desc"], classes="text-gray-300 text-xs")
            card_desc.set_size(116, 30)
            card_desc.set_position(532, 525)
            
            card.add_child(card_title_text)
            card.add_child(card_desc)
            main_container.add_child(card)
            
        # Add all components to main container
        main_container.add_child(title)
        main_container.add_child(row_title)
        main_container.add_child(row_container)
        main_container.add_child(col_title)
        main_container.add_child(col_container)
        main_container.add_child(grid_title)
        main_container.add_child(grid_container)
        main_container.add_child(stack_title)
        main_container.add_child(stack_container)
        main_container.add_child(progress_title)
        main_container.add_child(divider1)
        main_container.add_child(divider2)
        main_container.add_child(card_title)
        
        # Set container as root
        self.window.set_root_component(main_container)
        
    def run(self):
        """Run the application"""
        self.app.run()


if __name__ == "__main__":
    example = LayoutExample()
    example.run()