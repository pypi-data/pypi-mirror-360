"""
Component - Base class for all UI components with React-like architecture
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from .context import Context


class Component(ABC):
    """Base class for all UI components with React-like architecture"""
    
    def __init__(self, **props):
        self.props = props
        self.state = {}
        self.children: List[Component] = []
        self.parent: Optional[Component] = None
        self.context: Optional[Context] = None
        
        # Layout properties
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        
        # Style properties
        self.classes = props.get('classes', '')
        self.style = props.get('style', {})
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Component lifecycle
        self.mounted = False
        self.needs_update = True
        
        # Call constructor hook
        self.constructor()
        
    def constructor(self):
        """Constructor hook - override in subclasses"""
        pass
        
    def set_parent(self, parent: Optional['Component']):
        """Set the parent component"""
        self.parent = parent
        
    def set_context(self, context: Context):
        """Set the context and propagate to children"""
        self.context = context
        for child in self.children:
            child.set_context(context)
            
    def add_child(self, child: 'Component'):
        """Add a child component"""
        child.set_parent(self)
        if self.context:
            child.set_context(self.context)
        self.children.append(child)
        self.needs_update = True
        
    def remove_child(self, child: 'Component'):
        """Remove a child component"""
        if child in self.children:
            child.set_parent(None)
            self.children.remove(child)
            self.needs_update = True
            
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from component state"""
        return self.state.get(key, default)
        
    def set_state(self, key: str, value: Any):
        """Set a value in component state and trigger update"""
        self.state[key] = value
        self.needs_update = True
        
    def get_prop(self, key: str, default: Any = None) -> Any:
        """Get a property value"""
        return self.props.get(key, default)
        
    def set_prop(self, key: str, value: Any):
        """Set a property value"""
        self.props[key] = value
        self.needs_update = True
        
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def remove_event_handler(self, event_type: str, handler: Callable):
        """Remove an event handler"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].remove(handler)
            
    def trigger_event(self, event_type: str, event_data: Any = None):
        """Trigger an event"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(self, event_data)
                
    def component_did_mount(self):
        """Called after component is mounted"""
        pass
        
    def component_will_unmount(self):
        """Called before component is unmounted"""
        pass
        
    def component_did_update(self):
        """Called after component is updated"""
        pass
        
    def should_component_update(self) -> bool:
        """Determine if component should update"""
        return self.needs_update
        
    def update(self):
        """Update the component and its children"""
        if not self.mounted:
            self.component_did_mount()
            self.mounted = True
            
        if self.should_component_update():
            self.component_did_update()
            self.needs_update = False
            
        # Update children
        for child in self.children:
            child.update()
            
    def set_position(self, x: int, y: int):
        """Set the position of the component"""
        self.x = x
        self.y = y
        
    def set_size(self, width: int, height: int):
        """Set the size of the component"""
        self.width = width
        self.height = height
        
    def get_bounds(self) -> tuple:
        """Get the bounding box of the component"""
        return (self.x, self.y, self.width, self.height)
        
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is within the component's bounds"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
                
    @abstractmethod
    def render(self, renderer) -> None:
        """Render the component - must be implemented by subclasses"""
        pass
        
    def __repr__(self):
        return f"{self.__class__.__name__}(props={self.props})"