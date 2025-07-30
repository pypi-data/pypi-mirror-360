"""
Pre-defined transitions for common UI animations
"""
from typing import Any, Callable, Optional, List
from .animator import Animator


class Transition:
    """Pre-defined transitions for common UI animations"""
    
    def __init__(self, animator: Animator):
        self.animator = animator
        
    def slide_in_from_left(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Slide element in from the left"""
        original_x = getattr(target, 'x', 0)
        setattr(target, 'x', original_x - getattr(target, 'width', 100))
        
        return self.animator.animate(target, 'x', original_x, duration, 'ease_out', on_complete)
        
    def slide_in_from_right(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Slide element in from the right"""
        original_x = getattr(target, 'x', 0)
        setattr(target, 'x', original_x + getattr(target, 'width', 100))
        
        return self.animator.animate(target, 'x', original_x, duration, 'ease_out', on_complete)
        
    def slide_in_from_top(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Slide element in from the top"""
        original_y = getattr(target, 'y', 0)
        setattr(target, 'y', original_y - getattr(target, 'height', 100))
        
        return self.animator.animate(target, 'y', original_y, duration, 'ease_out', on_complete)
        
    def slide_in_from_bottom(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Slide element in from the bottom"""
        original_y = getattr(target, 'y', 0)
        setattr(target, 'y', original_y + getattr(target, 'height', 100))
        
        return self.animator.animate(target, 'y', original_y, duration, 'ease_out', on_complete)
        
    def slide_out_to_left(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Slide element out to the left"""
        final_x = getattr(target, 'x', 0) - getattr(target, 'width', 100)
        return self.animator.animate(target, 'x', final_x, duration, 'ease_in', on_complete)
        
    def slide_out_to_right(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Slide element out to the right"""
        final_x = getattr(target, 'x', 0) + getattr(target, 'width', 100)
        return self.animator.animate(target, 'x', final_x, duration, 'ease_in', on_complete)
        
    def fade_in(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Fade element in"""
        setattr(target, 'opacity', 0.0)
        return self.animator.animate(target, 'opacity', 1.0, duration, 'ease_out', on_complete)
        
    def fade_out(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Fade element out"""
        return self.animator.animate(target, 'opacity', 0.0, duration, 'ease_in', on_complete)
        
    def scale_in(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Scale element in from 0"""
        setattr(target, 'scale_x', 0.0)
        setattr(target, 'scale_y', 0.0)
        
        animations = self.animator.animate_multiple(
            target, 
            {'scale_x': 1.0, 'scale_y': 1.0}, 
            duration, 
            'ease_out', 
            on_complete
        )
        return animations
        
    def scale_out(self, target: Any, duration: float = 0.3, on_complete: Optional[Callable] = None):
        """Scale element out to 0"""
        animations = self.animator.animate_multiple(
            target, 
            {'scale_x': 0.0, 'scale_y': 0.0}, 
            duration, 
            'ease_in', 
            on_complete
        )
        return animations
        
    def pop_in(self, target: Any, duration: float = 0.4, on_complete: Optional[Callable] = None):
        """Pop in with bounce effect"""
        setattr(target, 'scale_x', 0.0)
        setattr(target, 'scale_y', 0.0)
        setattr(target, 'opacity', 0.0)
        
        # First animate scale with bounce
        def fade_in_after_scale():
            self.animator.animate(target, 'opacity', 1.0, 0.1, 'ease_out', on_complete)
            
        animations = self.animator.animate_multiple(
            target,
            {'scale_x': 1.0, 'scale_y': 1.0},
            duration,
            'bounce_out',
            fade_in_after_scale
        )
        return animations
        
    def flip_in_x(self, target: Any, duration: float = 0.5, on_complete: Optional[Callable] = None):
        """Flip in around X axis"""
        setattr(target, 'rotation_x', 90.0)
        return self.animator.animate(target, 'rotation_x', 0.0, duration, 'ease_out', on_complete)
        
    def flip_in_y(self, target: Any, duration: float = 0.5, on_complete: Optional[Callable] = None):
        """Flip in around Y axis"""
        setattr(target, 'rotation_y', 90.0)
        return self.animator.animate(target, 'rotation_y', 0.0, duration, 'ease_out', on_complete)
        
    def rotate_in(self, target: Any, angle: float = 180.0, duration: float = 0.5, on_complete: Optional[Callable] = None):
        """Rotate in from specified angle"""
        setattr(target, 'rotation', angle)
        return self.animator.animate(target, 'rotation', 0.0, duration, 'ease_out', on_complete)
        
    def shake(self, target: Any, intensity: float = 10.0, duration: float = 0.5, on_complete: Optional[Callable] = None):
        """Shake animation"""
        original_x = getattr(target, 'x', 0)
        
        def shake_right():
            def shake_left():
                def shake_center():
                    self.animator.animate(target, 'x', original_x, 0.1, 'ease_out', on_complete)
                self.animator.animate(target, 'x', original_x - intensity, 0.1, 'ease_in_out', shake_center)
            self.animator.animate(target, 'x', original_x + intensity, 0.1, 'ease_in_out', shake_left)
            
        return self.animator.animate(target, 'x', original_x + intensity, 0.1, 'ease_in_out', shake_right)
        
    def pulse(self, target: Any, scale: float = 1.2, duration: float = 0.6, on_complete: Optional[Callable] = None):
        """Pulse animation"""
        def scale_back():
            self.animator.animate_multiple(
                target,
                {'scale_x': 1.0, 'scale_y': 1.0},
                duration * 0.5,
                'ease_out',
                on_complete
            )
            
        return self.animator.animate_multiple(
            target,
            {'scale_x': scale, 'scale_y': scale},
            duration * 0.5,
            'ease_in',
            scale_back
        )
        
    def rubber_band(self, target: Any, duration: float = 1.0, on_complete: Optional[Callable] = None):
        """Rubber band animation"""
        def step2():
            def step3():
                def step4():
                    self.animator.animate_multiple(
                        target,
                        {'scale_x': 1.0, 'scale_y': 1.0},
                        duration * 0.1,
                        'ease_out',
                        on_complete
                    )
                self.animator.animate_multiple(
                    target,
                    {'scale_x': 1.05, 'scale_y': 0.95},
                    duration * 0.1,
                    'ease_in_out',
                    step4
                )
            self.animator.animate_multiple(
                target,
                {'scale_x': 0.95, 'scale_y': 1.05},
                duration * 0.2,
                'ease_in_out',
                step3
            )
        self.animator.animate_multiple(
            target,
            {'scale_x': 1.25, 'scale_y': 0.75},
            duration * 0.3,
            'ease_in_out',
            step2
        )