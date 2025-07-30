"""
Data table component for displaying tabular data
"""
from typing import List, Dict, Any, Optional, Callable
from ..core.component import Component
from ..styling.parser import StyleParser


class DataTable(Component):
    """Data table component for displaying tabular data"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.data = props.get('data', [])
        self.columns = props.get('columns', [])
        self.headers = props.get('headers', [])
        
        # Table styling
        self.header_background = (0.3, 0.3, 0.3, 1.0)
        self.row_background = (0.2, 0.2, 0.2, 1.0)
        self.alternate_row_background = (0.25, 0.25, 0.25, 1.0)
        self.border_color = (0.5, 0.5, 0.5, 1.0)
        self.text_color = (1.0, 1.0, 1.0, 1.0)
        self.selected_row_background = (0.23, 0.45, 1.0, 0.3)
        
        # Table properties
        self.row_height = props.get('row_height', 30)
        self.header_height = props.get('header_height', 35)
        self.cell_padding = props.get('cell_padding', 8)
        self.sortable = props.get('sortable', True)
        self.selectable = props.get('selectable', True)
        
        # State
        self.selected_row = -1
        self.sort_column = -1
        self.sort_ascending = True
        self.scroll_y = 0
        
        # Events
        self.on_row_select: Optional[Callable] = props.get('on_row_select')
        self.on_sort: Optional[Callable] = props.get('on_sort')
        
    def set_data(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None):
        """Set table data"""
        self.data = data
        if columns:
            self.columns = columns
        elif data and isinstance(data[0], dict):
            self.columns = list(data[0].keys())
            
    def set_headers(self, headers: List[str]):
        """Set column headers"""
        self.headers = headers
        
    def get_column_width(self, column_index: int) -> int:
        """Calculate column width"""
        if not self.columns:
            return 100
            
        # Simple equal width distribution
        available_width = self.width - 2  # Account for borders
        column_count = len(self.columns)
        return available_width // column_count if column_count > 0 else 100
        
    def get_visible_rows(self) -> range:
        """Get the range of visible rows based on scroll position"""
        if not self.data:
            return range(0, 0)
            
        table_height = self.height - self.header_height
        visible_row_count = table_height // self.row_height
        
        start_row = max(0, self.scroll_y // self.row_height)
        end_row = min(len(self.data), start_row + visible_row_count + 1)
        
        return range(start_row, end_row)
        
    def handle_mouse_event(self, event_type: str, event_data):
        """Handle mouse events"""
        if not self.selectable:
            return
            
        if event_type == 'mouse_down':
            # Check if click is in table area
            mouse_x, mouse_y = event_data.pos
            
            if (self.x <= mouse_x <= self.x + self.width and
                self.y + self.header_height <= mouse_y <= self.y + self.height):
                
                # Calculate clicked row
                relative_y = mouse_y - self.y - self.header_height + self.scroll_y
                clicked_row = int(relative_y // self.row_height)
                
                if 0 <= clicked_row < len(self.data):
                    self.selected_row = clicked_row
                    if self.on_row_select:
                        self.on_row_select(clicked_row, self.data[clicked_row])
                        
        elif event_type == 'mouse_wheel':
            # Scroll table
            scroll_amount = -event_data.y * self.row_height
            max_scroll = max(0, len(self.data) * self.row_height - (self.height - self.header_height))
            self.scroll_y = max(0, min(max_scroll, self.scroll_y + scroll_amount))
            
    def sort_by_column(self, column_index: int):
        """Sort table by column"""
        if not self.sortable or not self.data or column_index >= len(self.columns):
            return
            
        column_key = self.columns[column_index]
        
        # Toggle sort direction if same column
        if self.sort_column == column_index:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_ascending = True
            
        self.sort_column = column_index
        
        # Sort data
        try:
            self.data.sort(
                key=lambda row: row.get(column_key, ''),
                reverse=not self.sort_ascending
            )
        except TypeError:
            # Handle mixed types by converting to string
            self.data.sort(
                key=lambda row: str(row.get(column_key, '')),
                reverse=not self.sort_ascending
            )
            
        if self.on_sort:
            self.on_sort(column_index, self.sort_ascending)
            
    def render(self, renderer):
        """Render the data table"""
        # Render table background
        renderer.render_rectangle(self.x, self.y, self.width, self.height, self.row_background)
        
        # Render header
        self.render_header(renderer)
        
        # Render data rows
        self.render_rows(renderer)
        
        # Render borders
        self.render_borders(renderer)
        
    def render_header(self, renderer):
        """Render table header"""
        header_y = self.y
        
        # Render header background
        renderer.render_rectangle(self.x, header_y, self.width, self.header_height, self.header_background)
        
        # Render column headers
        current_x = self.x
        headers = self.headers if self.headers else self.columns
        
        for i, header in enumerate(headers):
            column_width = self.get_column_width(i)
            
            # Render header text
            text_x = current_x + self.cell_padding
            text_y = header_y + self.cell_padding
            # renderer.render_text(str(header), text_x, text_y, self.text_color)
            
            # Render sort indicator if this column is sorted
            if self.sort_column == i:
                indicator = "↑" if self.sort_ascending else "↓"
                indicator_x = current_x + column_width - 20
                # renderer.render_text(indicator, indicator_x, text_y, self.text_color)
                
            current_x += column_width
            
    def render_rows(self, renderer):
        """Render table rows"""
        visible_rows = self.get_visible_rows()
        
        for row_index in visible_rows:
            row_data = self.data[row_index]
            row_y = self.y + self.header_height + (row_index * self.row_height) - self.scroll_y
            
            # Skip rows that are not visible
            if row_y + self.row_height < self.y or row_y > self.y + self.height:
                continue
                
            # Determine row background color
            if row_index == self.selected_row:
                bg_color = self.selected_row_background
            elif row_index % 2 == 0:
                bg_color = self.row_background
            else:
                bg_color = self.alternate_row_background
                
            # Render row background
            renderer.render_rectangle(self.x, row_y, self.width, self.row_height, bg_color)
            
            # Render cells
            current_x = self.x
            for i, column in enumerate(self.columns):
                column_width = self.get_column_width(i)
                
                # Get cell value
                cell_value = row_data.get(column, '')
                
                # Render cell text
                text_x = current_x + self.cell_padding
                text_y = row_y + self.cell_padding
                # renderer.render_text(str(cell_value), text_x, text_y, self.text_color)
                
                current_x += column_width
                
    def render_borders(self, renderer):
        """Render table borders"""
        # Outer border
        renderer.render_rectangle(self.x, self.y, self.width, 1, self.border_color)
        renderer.render_rectangle(self.x, self.y + self.height - 1, self.width, 1, self.border_color)
        renderer.render_rectangle(self.x, self.y, 1, self.height, self.border_color)
        renderer.render_rectangle(self.x + self.width - 1, self.y, 1, self.height, self.border_color)
        
        # Header separator
        renderer.render_rectangle(self.x, self.y + self.header_height, self.width, 1, self.border_color)
        
        # Column separators
        current_x = self.x
        for i in range(len(self.columns)):
            current_x += self.get_column_width(i)
            if current_x < self.x + self.width:
                renderer.render_rectangle(current_x, self.y, 1, self.height, self.border_color)