"""
Basic example demonstrating ModernGUI usage
"""
import sys
import os

# Add the pulse_ui package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from pulse_ui.core.application import Application
from pulse_ui.core.window import Window
from pulse_ui.components.basic import Container, Button, Text


class BasicExample:
    """基本的なサンプルアプリケーション"""
    
    def __init__(self):
        self.app = Application("Basic PulseUI Example")
        self.window = self.app.create_window("Basic Example", 800, 600)
        
        # UI コンポーネントを作成
        self.create_ui()
        
    def create_ui(self):
        """ユーザーインターフェースを作成"""
        # メインコンテナを作成
        main_container = Container(
            classes="bg-gray-800 p-8 flex flex-col items-center justify-center"
        )
        main_container.set_size(800, 600)
        
        # タイトルを作成
        title = Text(
            "PulseUIへようこそ！",
            classes="text-white text-3xl font-bold mb-4"
        )
        title.set_position(50, 50)
        title.set_size(700, 50)
        
        # 説明文を作成
        description = Text(
            "Reactライクなコンポーネントを持つモダンなPython GUIライブラリ",
            classes="text-gray-300 text-lg mb-8"
        )
        description.set_position(50, 120)
        description.set_size(700, 30)
        
        # ボタンを作成
        primary_button = Button(
            "プライマリボタン",
            classes="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-4",
            on_click=self.on_primary_click
        )
        primary_button.set_position(200, 200)
        primary_button.set_size(150, 40)
        
        secondary_button = Button(
            "セカンダリボタン",
            classes="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded",
            on_click=self.on_secondary_click
        )
        secondary_button.set_position(370, 200)
        secondary_button.set_size(150, 40)
        
        # コンテナにコンポーネントを追加
        main_container.add_child(title)
        main_container.add_child(description)
        main_container.add_child(primary_button)
        main_container.add_child(secondary_button)
        
        # コンテナをルートに設定
        self.window.set_root_component(main_container)
        
    def on_primary_click(self, button):
        """プライマリボタンクリックの処理"""
        print("プライマリボタンがクリックされました！")
        
    def on_secondary_click(self, button):
        """セカンダリボタンクリックの処理"""
        print("セカンダリボタンがクリックされました！")
        
    def run(self):
        """アプリケーションを実行"""
        self.app.run()


if __name__ == "__main__":
    example = BasicExample()
    example.run()