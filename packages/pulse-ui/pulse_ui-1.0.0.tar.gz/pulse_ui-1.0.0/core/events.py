"""
EventManager - Handles all input events and routing
"""
import pygame
from typing import Dict, List, Callable, Any


class EventManager:
    """Manages all input events and routing"""
    
    def __init__(self):
        self.callbacks: Dict[str, List[Callable]] = {}
        self.mouse_position = (0, 0)
        self.mouse_buttons = [False, False, False]
        self.keys_pressed = set()
        
    def register_callback(self, event_type: str, callback: Callable):
        """Register a callback for a specific event type"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
        
    def unregister_callback(self, event_type: str, callback: Callable):
        """Unregister a callback for a specific event type"""
        if event_type in self.callbacks:
            self.callbacks[event_type].remove(callback)
            
    def handle_event(self, event):
        """Handle a pygame event"""
        event_type = self._get_event_type(event)
        
        if event_type:
            # Update internal state
            self._update_state(event)
            
            # Call registered callbacks
            if event_type in self.callbacks:
                for callback in self.callbacks[event_type]:
                    callback(event)
                    
    def _get_event_type(self, event) -> str:
        """Convert pygame event to string type"""
        event_map = {
            pygame.MOUSEBUTTONDOWN: 'mouse_down',
            pygame.MOUSEBUTTONUP: 'mouse_up',
            pygame.MOUSEMOTION: 'mouse_move',
            pygame.KEYDOWN: 'key_down',
            pygame.KEYUP: 'key_up',
            pygame.QUIT: 'quit',
            pygame.VIDEORESIZE: 'resize'
        }
        return event_map.get(event.type, '')
        
    def _update_state(self, event):
        """Update internal state based on event"""
        if event.type == pygame.MOUSEMOTION:
            self.mouse_position = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button <= 3:
                self.mouse_buttons[event.button - 1] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button <= 3:
                self.mouse_buttons[event.button - 1] = False
        elif event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed"""
        return key in self.keys_pressed
        
    def get_mouse_position(self) -> tuple:
        """Get current mouse position"""
        return self.mouse_position
        
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is currently pressed"""
        return self.mouse_buttons[button - 1] if button <= 3 else False