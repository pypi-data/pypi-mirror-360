"""
Easing functions for animations
"""
import math
from typing import Callable


class Easing:
    """Collection of easing functions for smooth animations"""
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear easing function"""
        return t
        
    @staticmethod
    def ease_in_sine(t: float) -> float:
        """Sine ease-in"""
        return 1 - math.cos((t * math.pi) / 2)
        
    @staticmethod
    def ease_out_sine(t: float) -> float:
        """Sine ease-out"""
        return math.sin((t * math.pi) / 2)
        
    @staticmethod
    def ease_in_out_sine(t: float) -> float:
        """Sine ease-in-out"""
        return -(math.cos(math.pi * t) - 1) / 2
        
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in"""
        return t * t
        
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out"""
        return 1 - (1 - t) * (1 - t)
        
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out"""
        return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
        
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """Cubic ease-in"""
        return t * t * t
        
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out"""
        return 1 - pow(1 - t, 3)
        
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """Cubic ease-in-out"""
        return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
        
    @staticmethod
    def ease_in_quart(t: float) -> float:
        """Quartic ease-in"""
        return t * t * t * t
        
    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic ease-out"""
        return 1 - pow(1 - t, 4)
        
    @staticmethod
    def ease_in_out_quart(t: float) -> float:
        """Quartic ease-in-out"""
        return 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2
        
    @staticmethod
    def ease_in_expo(t: float) -> float:
        """Exponential ease-in"""
        return 0 if t == 0 else pow(2, 10 * (t - 1))
        
    @staticmethod
    def ease_out_expo(t: float) -> float:
        """Exponential ease-out"""
        return 1 if t == 1 else 1 - pow(2, -10 * t)
        
    @staticmethod
    def ease_in_out_expo(t: float) -> float:
        """Exponential ease-in-out"""
        if t == 0:
            return 0
        elif t == 1:
            return 1
        elif t < 0.5:
            return pow(2, 20 * t - 10) / 2
        else:
            return (2 - pow(2, -20 * t + 10)) / 2
            
    @staticmethod
    def ease_in_back(t: float) -> float:
        """Back ease-in"""
        c1 = 1.70158
        c3 = c1 + 1
        return c3 * t * t * t - c1 * t * t
        
    @staticmethod
    def ease_out_back(t: float) -> float:
        """Back ease-out"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)
        
    @staticmethod
    def ease_in_out_back(t: float) -> float:
        """Back ease-in-out"""
        c1 = 1.70158
        c2 = c1 * 1.525
        
        if t < 0.5:
            return (pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
        else:
            return (pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
            
    @staticmethod
    def bounce_out(t: float) -> float:
        """Bounce ease-out"""
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
            
    @staticmethod
    def bounce_in(t: float) -> float:
        """Bounce ease-in"""
        return 1 - Easing.bounce_out(1 - t)
        
    @staticmethod
    def bounce_in_out(t: float) -> float:
        """Bounce ease-in-out"""
        if t < 0.5:
            return (1 - Easing.bounce_out(1 - 2 * t)) / 2
        else:
            return (1 + Easing.bounce_out(2 * t - 1)) / 2
            
    # Mapping of easing names to functions
    FUNCTIONS = {
        'linear': linear.__func__,
        'ease_in': ease_in_cubic.__func__,
        'ease_out': ease_out_cubic.__func__,
        'ease_in_out': ease_in_out_cubic.__func__,
        'ease_in_sine': ease_in_sine.__func__,
        'ease_out_sine': ease_out_sine.__func__,
        'ease_in_out_sine': ease_in_out_sine.__func__,
        'ease_in_quad': ease_in_quad.__func__,
        'ease_out_quad': ease_out_quad.__func__,
        'ease_in_out_quad': ease_in_out_quad.__func__,
        'ease_in_cubic': ease_in_cubic.__func__,
        'ease_out_cubic': ease_out_cubic.__func__,
        'ease_in_out_cubic': ease_in_out_cubic.__func__,
        'ease_in_quart': ease_in_quart.__func__,
        'ease_out_quart': ease_out_quart.__func__,
        'ease_in_out_quart': ease_in_out_quart.__func__,
        'ease_in_expo': ease_in_expo.__func__,
        'ease_out_expo': ease_out_expo.__func__,
        'ease_in_out_expo': ease_in_out_expo.__func__,
        'ease_in_back': ease_in_back.__func__,
        'ease_out_back': ease_out_back.__func__,
        'ease_in_out_back': ease_in_out_back.__func__,
        'bounce': bounce_out.__func__,
        'bounce_in': bounce_in.__func__,
        'bounce_out': bounce_out.__func__,
        'bounce_in_out': bounce_in_out.__func__
    }
    
    @classmethod
    def apply(cls, easing_name: str, t: float) -> float:
        """Apply an easing function by name"""
        easing_func = cls.FUNCTIONS.get(easing_name, cls.linear)
        return easing_func(t)
        
    @classmethod
    def get_function(cls, easing_name: str) -> Callable[[float], float]:
        """Get an easing function by name"""
        return cls.FUNCTIONS.get(easing_name, cls.linear)