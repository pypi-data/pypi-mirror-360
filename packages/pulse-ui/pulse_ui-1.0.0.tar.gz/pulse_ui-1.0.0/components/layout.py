"""
Layout components - Row, Column, Stack, Grid for organizing UI elements
"""
from typing import List, Dict, Any, Optional
from ..core.component import Component
from ..styling.parser import StyleParser


class Row(Component):
    """Horizontal layout component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.gap = props.get('gap', 0)
        self.align_items = props.get('align_items', 'start')  # start, center, end, stretch
        self.justify_content = props.get('justify_content', 'start')  # start, center, end, space-between, space-around
        
    def component_did_mount(self):
        """Layout children when component mounts"""
        self.layout_children()
        
    def layout_children(self):
        """Layout children horizontally"""
        if not self.children:
            return
            
        available_width = self.width - (len(self.children) - 1) * self.gap
        
        # Calculate child widths based on justify_content
        if self.justify_content == 'start':
            child_x = self.x
            for child in self.children:
                child.set_position(child_x, self.calculate_child_y(child))
                child_x += child.width + self.gap
                
        elif self.justify_content == 'center':
            total_child_width = sum(child.width for child in self.children)
            start_x = self.x + (available_width - total_child_width) // 2
            child_x = start_x
            for child in self.children:
                child.set_position(child_x, self.calculate_child_y(child))
                child_x += child.width + self.gap
                
        elif self.justify_content == 'end':
            total_child_width = sum(child.width for child in self.children)
            start_x = self.x + available_width - total_child_width
            child_x = start_x
            for child in self.children:
                child.set_position(child_x, self.calculate_child_y(child))
                child_x += child.width + self.gap
                
        elif self.justify_content == 'space-between':
            if len(self.children) == 1:
                self.children[0].set_position(self.x, self.calculate_child_y(self.children[0]))
            else:
                total_child_width = sum(child.width for child in self.children)
                remaining_space = available_width - total_child_width
                gap_size = remaining_space / (len(self.children) - 1)
                
                child_x = self.x
                for child in self.children:
                    child.set_position(child_x, self.calculate_child_y(child))
                    child_x += child.width + gap_size
                    
    def calculate_child_y(self, child):
        """Calculate Y position based on align_items"""
        if self.align_items == 'start':
            return self.y
        elif self.align_items == 'center':
            return self.y + (self.height - child.height) // 2
        elif self.align_items == 'end':
            return self.y + self.height - child.height
        elif self.align_items == 'stretch':
            child.set_size(child.width, self.height)
            return self.y
        else:
            return self.y
            
    def render(self, renderer):
        """Render the row (layout only, no visual representation)"""
        pass


class Column(Component):
    """Vertical layout component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.gap = props.get('gap', 0)
        self.align_items = props.get('align_items', 'start')  # start, center, end, stretch
        self.justify_content = props.get('justify_content', 'start')  # start, center, end, space-between, space-around
        
    def component_did_mount(self):
        """Layout children when component mounts"""
        self.layout_children()
        
    def layout_children(self):
        """Layout children vertically"""
        if not self.children:
            return
            
        available_height = self.height - (len(self.children) - 1) * self.gap
        
        # Calculate child positions based on justify_content
        if self.justify_content == 'start':
            child_y = self.y
            for child in self.children:
                child.set_position(self.calculate_child_x(child), child_y)
                child_y += child.height + self.gap
                
        elif self.justify_content == 'center':
            total_child_height = sum(child.height for child in self.children)
            start_y = self.y + (available_height - total_child_height) // 2
            child_y = start_y
            for child in self.children:
                child.set_position(self.calculate_child_x(child), child_y)
                child_y += child.height + self.gap
                
        elif self.justify_content == 'end':
            total_child_height = sum(child.height for child in self.children)
            start_y = self.y + available_height - total_child_height
            child_y = start_y
            for child in self.children:
                child.set_position(self.calculate_child_x(child), child_y)
                child_y += child.height + self.gap
                
        elif self.justify_content == 'space-between':
            if len(self.children) == 1:
                self.children[0].set_position(self.calculate_child_x(self.children[0]), self.y)
            else:
                total_child_height = sum(child.height for child in self.children)
                remaining_space = available_height - total_child_height
                gap_size = remaining_space / (len(self.children) - 1)
                
                child_y = self.y
                for child in self.children:
                    child.set_position(self.calculate_child_x(child), child_y)
                    child_y += child.height + gap_size
                    
    def calculate_child_x(self, child):
        """Calculate X position based on align_items"""
        if self.align_items == 'start':
            return self.x
        elif self.align_items == 'center':
            return self.x + (self.width - child.width) // 2
        elif self.align_items == 'end':
            return self.x + self.width - child.width
        elif self.align_items == 'stretch':
            child.set_size(self.width, child.height)
            return self.x
        else:
            return self.x
            
    def render(self, renderer):
        """Render the column (layout only, no visual representation)"""
        pass


class Stack(Component):
    """Stack layout component (children stacked on top of each other)"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.align_items = props.get('align_items', 'center')  # start, center, end, stretch
        
    def component_did_mount(self):
        """Layout children when component mounts"""
        self.layout_children()
        
    def layout_children(self):
        """Stack children on top of each other"""
        for child in self.children:
            if self.align_items == 'start':
                child.set_position(self.x, self.y)
            elif self.align_items == 'center':
                child_x = self.x + (self.width - child.width) // 2
                child_y = self.y + (self.height - child.height) // 2
                child.set_position(child_x, child_y)
            elif self.align_items == 'end':
                child_x = self.x + self.width - child.width
                child_y = self.y + self.height - child.height
                child.set_position(child_x, child_y)
            elif self.align_items == 'stretch':
                child.set_position(self.x, self.y)
                child.set_size(self.width, self.height)
                
    def render(self, renderer):
        """Render the stack (layout only, no visual representation)"""
        pass


class Grid(Component):
    """Grid layout component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.columns = props.get('columns', 2)
        self.rows = props.get('rows', None)  # Auto-calculate if not specified
        self.gap = props.get('gap', 0)
        self.column_gap = props.get('column_gap', self.gap)
        self.row_gap = props.get('row_gap', self.gap)
        
    def component_did_mount(self):
        """Layout children when component mounts"""
        self.layout_children()
        
    def layout_children(self):
        """Layout children in a grid"""
        if not self.children:
            return
            
        # Calculate grid dimensions
        total_columns = self.columns
        total_rows = self.rows or ((len(self.children) + total_columns - 1) // total_columns)
        
        # Calculate cell dimensions
        available_width = self.width - (total_columns - 1) * self.column_gap
        available_height = self.height - (total_rows - 1) * self.row_gap
        
        cell_width = available_width // total_columns
        cell_height = available_height // total_rows
        
        # Position children
        for i, child in enumerate(self.children):
            col = i % total_columns
            row = i // total_columns
            
            child_x = self.x + col * (cell_width + self.column_gap)
            child_y = self.y + row * (cell_height + self.row_gap)
            
            child.set_position(child_x, child_y)
            child.set_size(cell_width, cell_height)
            
    def render(self, renderer):
        """Render the grid (layout only, no visual representation)"""
        pass