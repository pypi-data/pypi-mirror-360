"""
PulseUIアニメーション機能のデモンストレーション
"""
import sys
import os
import math
import time

# Add the pulse_ui package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pulse_ui.core.application import Application
from pulse_ui.core.window import Window
from pulse_ui.components.basic import Container, Button, Text


class AnimatedCircle(Container):
    """A simple animated circle component"""
    
    def __init__(self, **props):
        super().__init__(**props)
        self.start_time = time.time()
        self.radius = 50
        self.center_x = 400
        self.center_y = 300
        self.speed = 2.0
        
    def update(self):
        """Update animation"""
        super().update()
        
        # Calculate animated position
        elapsed = time.time() - self.start_time
        angle = elapsed * self.speed
        
        # Circular motion
        offset_x = math.cos(angle) * 100
        offset_y = math.sin(angle) * 50
        
        self.set_position(
            int(self.center_x + offset_x - self.radius),
            int(self.center_y + offset_y - self.radius)
        )
        
    def render(self, renderer):
        """Render the animated circle"""
        # Render as a colored circle
        renderer.render_circle(
            self.x + self.radius,
            self.y + self.radius,
            self.radius,
            (0.23, 0.45, 1.0, 1.0)  # Blue color
        )


class AnimationExample:
    """アニメーション例アプリケーション"""
    
    def __init__(self):
        self.app = Application("Animation PulseUI Example")
        self.window = self.app.create_window("アニメーション例", 800, 600)
        
        # UI コンポーネントを作成
        self.create_ui()
        
    def create_ui(self):
        """ユーザーインターフェースを作成"""
        # メインコンテナを作成
        main_container = Container(
            classes="bg-gray-900 p-8"
        )
        main_container.set_size(800, 600)
        
        # タイトルを作成
        title = Text(
            "アニメーション例",
            classes="text-white text-2xl font-bold mb-4"
        )
        title.set_position(50, 50)
        title.set_size(700, 40)
        
        # アニメーション円を作成
        animated_circle = AnimatedCircle()
        animated_circle.set_size(100, 100)
        
        # コントロールボタンを作成
        start_button = Button(
            "アニメーション開始",
            classes="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mr-4",
            on_click=self.on_start_click
        )
        start_button.set_position(50, 500)
        start_button.set_size(120, 40)
        
        stop_button = Button(
            "アニメーション停止",
            classes="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded",
            on_click=self.on_stop_click
        )
        stop_button.set_position(180, 500)
        stop_button.set_size(120, 40)
        
        # Add components to container
        main_container.add_child(title)
        main_container.add_child(animated_circle)
        main_container.add_child(start_button)
        main_container.add_child(stop_button)
        
        # Set container as root
        self.window.set_root_component(main_container)
        
    def on_start_click(self, button):
        """Handle start animation click"""
        print("Animation started!")
        
    def on_stop_click(self, button):
        """Handle stop animation click"""
        print("Animation stopped!")
        
    def run(self):
        """Run the application"""
        self.app.run()


if __name__ == "__main__":
    example = AnimationExample()
    example.run()