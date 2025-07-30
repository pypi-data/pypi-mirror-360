"""
Animator - Handles animations and transitions
"""
import time
from typing import Dict, List, Callable, Any, Optional
from .easing import Easing


class Animation:
    """Represents a single animation"""
    
    def __init__(self, 
                 target: Any,
                 property_name: str,
                 start_value: float,
                 end_value: float,
                 duration: float,
                 easing: str = 'ease_in_out',
                 on_complete: Optional[Callable] = None):
        self.target = target
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing = easing
        self.on_complete = on_complete
        
        self.start_time = time.time()
        self.is_complete = False
        
    def update(self) -> bool:
        """Update the animation and return True if still running"""
        if self.is_complete:
            return False
            
        current_time = time.time()
        elapsed = current_time - self.start_time
        progress = min(elapsed / self.duration, 1.0)
        
        # Apply easing
        eased_progress = Easing.apply(self.easing, progress)
        
        # Calculate current value
        current_value = self.start_value + (self.end_value - self.start_value) * eased_progress
        
        # Set the property value
        if hasattr(self.target, self.property_name):
            setattr(self.target, self.property_name, current_value)
        
        # Check if animation is complete
        if progress >= 1.0:
            self.is_complete = True
            if self.on_complete:
                self.on_complete()
                
        return not self.is_complete


class Animator:
    """Manages multiple animations and provides animation utilities"""
    
    def __init__(self):
        self.animations: List[Animation] = []
        self.running = True
        
    def animate(self,
                target: Any,
                property_name: str,
                to_value: float,
                duration: float = 1.0,
                easing: str = 'ease_in_out',
                on_complete: Optional[Callable] = None) -> Animation:
        """Start an animation"""
        # Get current value
        current_value = getattr(target, property_name, 0.0)
        
        # Create animation
        animation = Animation(
            target, property_name, current_value, to_value,
            duration, easing, on_complete
        )
        
        self.animations.append(animation)
        return animation
        
    def animate_multiple(self,
                        target: Any,
                        properties: Dict[str, float],
                        duration: float = 1.0,
                        easing: str = 'ease_in_out',
                        on_complete: Optional[Callable] = None) -> List[Animation]:
        """Animate multiple properties simultaneously"""
        animations = []
        
        for prop_name, to_value in properties.items():
            animation = self.animate(target, prop_name, to_value, duration, easing)
            animations.append(animation)
            
        # Set callback on last animation
        if animations and on_complete:
            animations[-1].on_complete = on_complete
            
        return animations
        
    def fade_in(self, target: Any, duration: float = 0.5) -> Animation:
        """Fade in animation"""
        return self.animate(target, 'opacity', 1.0, duration, 'ease_out')
        
    def fade_out(self, target: Any, duration: float = 0.5) -> Animation:
        """Fade out animation"""
        return self.animate(target, 'opacity', 0.0, duration, 'ease_in')
        
    def slide_in_left(self, target: Any, distance: float = 100, duration: float = 0.5) -> Animation:
        """Slide in from left animation"""
        original_x = getattr(target, 'x', 0)
        setattr(target, 'x', original_x - distance)
        return self.animate(target, 'x', original_x, duration, 'ease_out')
        
    def slide_in_right(self, target: Any, distance: float = 100, duration: float = 0.5) -> Animation:
        """Slide in from right animation"""
        original_x = getattr(target, 'x', 0)
        setattr(target, 'x', original_x + distance)
        return self.animate(target, 'x', original_x, duration, 'ease_out')
        
    def scale_in(self, target: Any, duration: float = 0.3) -> List[Animation]:
        """Scale in animation"""
        return self.animate_multiple(target, {'scale_x': 1.0, 'scale_y': 1.0}, duration, 'ease_out')
        
    def scale_out(self, target: Any, duration: float = 0.3) -> List[Animation]:
        """Scale out animation"""
        return self.animate_multiple(target, {'scale_x': 0.0, 'scale_y': 0.0}, duration, 'ease_in')
        
    def bounce(self, target: Any, duration: float = 0.6) -> Animation:
        """Bounce animation"""
        return self.animate(target, 'y', getattr(target, 'y', 0), duration, 'bounce')
        
    def pulse(self, target: Any, scale: float = 1.1, duration: float = 0.5) -> List[Animation]:
        """Pulse animation"""
        def pulse_back():
            self.animate_multiple(target, {'scale_x': 1.0, 'scale_y': 1.0}, duration * 0.5, 'ease_out')
            
        return self.animate_multiple(target, {'scale_x': scale, 'scale_y': scale}, duration * 0.5, 'ease_in', pulse_back)
        
    def update(self):
        """Update all active animations"""
        if not self.running:
            return
            
        # Update animations and remove completed ones
        self.animations = [anim for anim in self.animations if anim.update()]
        
    def stop_all(self):
        """Stop all animations"""
        self.animations.clear()
        
    def stop_animations_for_target(self, target: Any):
        """Stop all animations for a specific target"""
        self.animations = [anim for anim in self.animations if anim.target != target]
        
    def get_active_animation_count(self) -> int:
        """Get the number of active animations"""
        return len(self.animations)
        
    def is_animating(self, target: Any, property_name: str = None) -> bool:
        """Check if target or specific property is being animated"""
        for anim in self.animations:
            if anim.target == target:
                if property_name is None or anim.property_name == property_name:
                    return True
        return False
        
    def pause(self):
        """Pause all animations"""
        self.running = False
        
    def resume(self):
        """Resume all animations"""
        self.running = True
        # Adjust start times to account for pause
        current_time = time.time()
        for anim in self.animations:
            elapsed = current_time - anim.start_time
            anim.start_time = current_time - min(elapsed, anim.duration)