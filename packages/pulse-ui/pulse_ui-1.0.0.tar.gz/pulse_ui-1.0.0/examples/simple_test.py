"""
PulseUIの基本機能を確認するためのシンプルなテスト
"""
import sys
import os

# Add the pulse_ui package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pulse_ui.core.application import Application
    from pulse_ui.core.window import Window
    from pulse_ui.components.basic import Container, Button, Text
    print("✓ すべてのインポートが成功しました！")
    
    class SimpleTest:
        """シンプルなテストアプリケーション"""
        
        def __init__(self):
            print("アプリケーションを作成中...")
            self.app = Application("Simple Test")
            
            print("ウィンドウを作成中...")
            self.window = self.app.create_window("テストウィンドウ", 600, 400)
            
            print("コンポーネントを作成中...")
            self.create_ui()
            
        def create_ui(self):
            """シンプルなUIを作成"""
            # メインコンテナ
            container = Container()
            container.set_size(600, 400)
            container.set_position(0, 0)
            
            # ウェルカムテキスト
            welcome_text = Text("PulseUIへようこそ！")
            welcome_text.set_position(200, 150)
            welcome_text.set_size(200, 30)
            
            # テストボタン
            test_button = Button("クリックしてください！", on_click=self.on_button_click)
            test_button.set_position(250, 200)
            test_button.set_size(100, 40)
            
            # コンテナに追加
            container.add_child(welcome_text)
            container.add_child(test_button)
            
            # ルートに設定
            self.window.set_root_component(container)
            print("✓ UIが正常に作成されました！")
            
        def on_button_click(self, button):
            """ボタンクリックの処理"""
            print("ボタンがクリックされました！PulseUIが動作しています！")
            
        def run(self):
            """テストを実行"""
            print("アプリケーションを開始中...")
            try:
                self.app.run()
            except KeyboardInterrupt:
                print("ユーザーによってアプリケーションが停止されました")
            except Exception as e:
                print(f"アプリケーション実行時エラー: {e}")
                
    if __name__ == "__main__":
        print("=== PulseUI シンプルテスト ===")
        test = SimpleTest()
        test.run()
        
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("すべての依存関係がインストールされていることを確認してください。")
except Exception as e:
    print(f"エラー: {e}")
    print("インストールと依存関係を確認してください。")