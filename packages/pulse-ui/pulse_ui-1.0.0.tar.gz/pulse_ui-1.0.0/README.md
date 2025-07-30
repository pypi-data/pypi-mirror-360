# PulseUI 🚀

> **未来のPython GUIライブラリ** - Reactの直感性、TailwindCSSの柔軟性、科学的可視化の強力さを統合

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

PulseUIは、Reactライクなコンポーネントアーキテクチャとユーティリティファーストスタイリングを備えたモダンなPython GUIライブラリです。GPU加速レンダリングと科学的可視化機能により、美しく高性能なデスクトップアプリケーションを簡単に構築できます。

## ✨ 特徴

### 🎯 **学習コストが非常に低い**
```python
# Reactライクな直感的なAPI
container = Container(classes="flex flex-col items-center p-8")
title = Text("こんにちは、PulseUI！", classes="text-2xl font-bold text-blue-600")
button = Button("クリック！", on_click=handle_click)
```

### 🎨 **TailwindCSS風スタイリング**
```python
# ユーティリティファーストCSSアプローチ
card = Container(classes="bg-white rounded-lg shadow-lg p-6 m-4")
header = Text("タイトル", classes="text-xl font-bold text-gray-800 mb-4")
button = Button("送信", classes="bg-blue-500 hover:bg-blue-700 text-white rounded px-4 py-2")
```

### ⚡ **GPU加速レンダリング**
- OpenGL/Vulkanベースの高性能グラフィックス
- スムーズな60FPSアニメーション
- 軽量で高速な描画エンジン

### 📊 **科学的可視化**
```python
# リアルタイムデータ可視化
chart = LineChart(data=data_points, classes="w-full h-64")
plot = RealTimePlot(max_points=1000, update_interval=0.1)
table = DataTable(data=dataset, sortable=True, filterable=True)
```

### 🔄 **強力なアニメーションシステム**
```python
# 30種類以上のイージング関数
animator.fade_in(component, duration=0.5)
animator.slide_in_left(panel, duration=0.3, easing='bounce_out')
animator.pulse(button, scale=1.2)
```

## 📦 インストール

```bash
# PyPIからインストール
pip install pulse-ui

## 🚀 クイックスタート

### 基本的なアプリケーション

```python
from pulse_ui import Application, Container, Text, Button

class HelloApp:
    def __init__(self):
        # アプリケーションを作成
        self.app = Application("PulseUI デモ")
        self.window = self.app.create_window("Hello World", 600, 400)
        
        # UIを構築
        self.create_ui()
        
    def create_ui(self):
        # メインコンテナ
        container = Container(classes="bg-gradient-to-br from-blue-500 to-purple-600 p-8")
        container.set_size(600, 400)
        
        # タイトル
        title = Text(
            "PulseUIへようこそ！", 
            classes="text-white text-3xl font-bold text-center mb-6"
        )
        title.set_position(50, 100)
        title.set_size(500, 50)
        
        # ボタン
        button = Button(
            "今すぐ体験", 
            classes="bg-white text-blue-600 font-bold py-3 px-8 rounded-full hover:shadow-lg transition-all",
            on_click=self.on_click
        )
        button.set_position(225, 200)
        button.set_size(150, 50)
        
        # コンポーネントを追加
        container.add_child(title)
        container.add_child(button)
        
        # ルートコンポーネントを設定
        self.window.set_root_component(container)
        
    def on_click(self, button):
        print("🎉 PulseUIが動作しています！")
        
    def run(self):
        self.app.run()

# アプリケーションを実行
if __name__ == "__main__":
    app = HelloApp()
    app.run()
```

### 科学的可視化の例

```python
from pulse_ui import Application, Container, LineChart, BarChart, RealTimePlot
import math
import random
import time

class DataVisualizationApp:
    def __init__(self):
        self.app = Application("データ可視化デモ")
        self.window = self.app.create_window("科学的可視化", 1200, 800)
        self.create_dashboard()
        
    def create_dashboard(self):
        # ダッシュボードコンテナ
        dashboard = Container(classes="bg-gray-900 p-6")
        dashboard.set_size(1200, 800)
        
        # 線グラフ
        line_data = [(i, 50 + 30 * math.sin(i * 0.3)) for i in range(50)]
        line_chart = LineChart(
            data=line_data,
            title="サインウェーブデータ",
            line_color=(0.2, 0.8, 0.2, 1.0)
        )
        line_chart.set_position(50, 50)
        line_chart.set_size(500, 300)
        
        # 棒グラフ
        bar_data = [("月", 65), ("火", 78), ("水", 92), ("木", 81), ("金", 95)]
        bar_chart = BarChart(
            data=bar_data,
            title="週間売上",
            bar_color=(0.2, 0.6, 1.0, 1.0)
        )
        bar_chart.set_position(650, 50)
        bar_chart.set_size(500, 300)
        
        # リアルタイムプロット
        realtime_plot = RealTimePlot(
            max_points=100,
            update_interval=0.1,
            data_callback=self.get_realtime_data
        )
        realtime_plot.add_real_time_series("CPU使用率", (1.0, 0.3, 0.3, 1.0))
        realtime_plot.add_real_time_series("メモリ使用率", (0.3, 0.6, 1.0, 1.0))
        realtime_plot.set_position(50, 400)
        realtime_plot.set_size(1100, 300)
        
        # コンポーネントを追加
        dashboard.add_child(line_chart)
        dashboard.add_child(bar_chart)
        dashboard.add_child(realtime_plot)
        
        self.window.set_root_component(dashboard)
        
    def get_realtime_data(self):
        """リアルタイムデータを生成"""
        current_time = time.time()
        cpu_usage = 30 + 20 * math.sin(current_time * 0.5) + random.uniform(-5, 5)
        memory_usage = 50 + 15 * math.cos(current_time * 0.3) + random.uniform(-3, 3)
        
        return {
            "CPU使用率": (current_time, max(0, min(100, cpu_usage))),
            "メモリ使用率": (current_time, max(0, min(100, memory_usage)))
        }
        
    def run(self):
        self.app.run()

if __name__ == "__main__":
    app = DataVisualizationApp()
    app.run()
```

## 🏗️ コンポーネントライブラリ

### 基本コンポーネント
- `Container` - レイアウトコンテナ
- `Text` - テキスト表示
- `Button` - クリック可能なボタン
- `Input` - テキスト入力フィールド
- `Image` - 画像表示

### レイアウトコンポーネント
- `Row` - 水平レイアウト
- `Column` - 垂直レイアウト
- `Grid` - グリッドレイアウト
- `Stack` - 重ねレイアウト

### 表示コンポーネント
- `Card` - カードコンテナ
- `Badge` - バッジ表示
- `Progress` - プログレスバー
- `Divider` - 区切り線
- `Icon` - アイコン表示

### データ可視化
- `LineChart` - 線グラフ
- `BarChart` - 棒グラフ
- `PieChart` - 円グラフ
- `ScatterChart` - 散布図
- `RealTimePlot` - リアルタイムプロット
- `DataTable` - データテーブル

## 🎨 スタイリングシステム

PulseUIは、TailwindCSSと同様のユーティリティファーストアプローチを採用しています。

### カラーシステム
```python
# 背景色
"bg-blue-500"     # 青色背景
"bg-red-600"      # 赤色背景
"bg-gray-100"     # グレー背景

# テキスト色
"text-white"      # 白文字
"text-gray-800"   # 濃いグレー文字
"text-blue-600"   # 青文字
```

### スペーシング
```python
# パディング
"p-4"             # 全方向16px
"px-6"            # 水平24px
"py-2"            # 垂直8px

# マージン
"m-4"             # 全方向16px
"mx-auto"         # 水平中央揃え
"mt-8"            # 上32px
```

### レイアウト
```python
# Flexbox
"flex"            # flex表示
"flex-col"        # 縦方向
"items-center"    # 中央揃え
"justify-between" # 両端揃え

# グリッド
"grid"            # grid表示
"grid-cols-3"     # 3列グリッド
"gap-4"           # 16pxギャップ
```

### タイポグラフィ
```python
# フォントサイズ
"text-sm"         # 14px
"text-lg"         # 18px
"text-2xl"        # 24px
"text-4xl"        # 36px

# フォントウェイト
"font-normal"     # 標準
"font-bold"       # 太字
"font-light"      # 細字
```

## 🔄 アニメーションシステム

### 基本アニメーション
```python
from pulse_ui.animation import Animator, Transition

animator = Animator()

# フェード効果
animator.fade_in(component, duration=0.5)
animator.fade_out(component, duration=0.3)

# スライド効果
animator.slide_in_left(panel, duration=0.4)
animator.slide_in_right(sidebar, duration=0.3)

# スケール効果
animator.scale_in(modal, duration=0.2)
animator.scale_out(popup, duration=0.15)
```

### 高度なアニメーション
```python
# カスタムプロパティアニメーション
animator.animate(component, 'x', 100, duration=1.0, easing='bounce_out')

# 複数プロパティの同時アニメーション
animator.animate_multiple(component, {
    'x': 200,
    'y': 150,
    'opacity': 0.8
}, duration=0.5, easing='ease_in_out')

# アニメーションチェーン
def on_complete():
    animator.pulse(component, scale=1.2, duration=0.3)
    
animator.slide_in_left(component, duration=0.5, on_complete=on_complete)
```

### イージング関数
```python
# 基本的なイージング
'linear'          # 一定速度
'ease_in'         # 加速
'ease_out'        # 減速
'ease_in_out'     # 加速→減速

# 高度なイージング
'bounce_out'      # バウンス効果
'elastic_out'     # 弾性効果
'back_out'        # バック効果
'sine_in_out'     # サイン波
```

## 📊 データ可視化の例

### リアルタイムモニタリング
```python
import time
import random
import math

class SystemMonitor:
    def __init__(self):
        self.app = Application("システムモニター")
        self.window = self.app.create_window("リアルタイムモニタリング", 1000, 600)
        self.setup_monitoring()
        
    def setup_monitoring(self):
        container = Container(classes="bg-black p-6")
        container.set_size(1000, 600)
        
        # CPU使用率グラフ
        self.cpu_plot = RealTimePlot(
            max_points=60,
            update_interval=1.0,
            data_callback=self.get_system_data
        )
        self.cpu_plot.add_real_time_series("CPU", (1.0, 0.2, 0.2, 1.0))
        self.cpu_plot.add_real_time_series("メモリ", (0.2, 0.8, 0.2, 1.0))
        self.cpu_plot.add_real_time_series("ディスク", (0.2, 0.2, 1.0, 1.0))
        self.cpu_plot.set_position(50, 50)
        self.cpu_plot.set_size(900, 500)
        
        container.add_child(self.cpu_plot)
        self.window.set_root_component(container)
        
    def get_system_data(self):
        """システムデータをシミュレート"""
        timestamp = time.time()
        
        return {
            "CPU": (timestamp, 20 + 30 * math.sin(timestamp * 0.1) + random.uniform(-5, 5)),
            "メモリ": (timestamp, 40 + 20 * math.cos(timestamp * 0.15) + random.uniform(-3, 3)),
            "ディスク": (timestamp, 60 + 10 * math.sin(timestamp * 0.2) + random.uniform(-2, 2))
        }
        
    def run(self):
        self.app.run()
```

## 🏢 企業レベルのアプリケーション例

```python
from pulse_ui import *
from pulse_ui.components.layout import Row, Column, Grid
from pulse_ui.components.display import Card, Progress, Badge
from pulse_ui.visualization import LineChart, BarChart, DataTable

class EnterpriseDashboard:
    def __init__(self):
        self.app = Application("企業ダッシュボード")
        self.window = self.app.create_window("営業ダッシュボード", 1400, 900)
        self.create_enterprise_ui()
        
    def create_enterprise_ui(self):
        # メインレイアウト
        main_layout = Column(classes="bg-gray-50 min-h-screen")
        main_layout.set_size(1400, 900)
        
        # ヘッダー
        header = self.create_header()
        
        # コンテンツエリア
        content = Row(classes="flex-1")
        content.set_size(1400, 800)
        
        # サイドバー
        sidebar = self.create_sidebar()
        
        # メインコンテンツ
        main_content = self.create_main_content()
        
        # レイアウトを構築
        content.add_child(sidebar)
        content.add_child(main_content)
        
        main_layout.add_child(header)
        main_layout.add_child(content)
        
        self.window.set_root_component(main_layout)
        
    def create_header(self):
        """ヘッダーを作成"""
        header = Container(classes="bg-white shadow-lg p-4 border-b")
        header.set_size(1400, 80)
        
        header_content = Row(classes="justify-between items-center")
        header_content.set_size(1400, 60)
        
        # ロゴとタイトル
        logo_section = Row(classes="items-center gap-4")
        logo_section.set_size(400, 60)
        
        logo = Icon("pulse", size=32, color=(0.2, 0.6, 1.0, 1.0))
        logo.set_size(40, 40)
        
        title = Text("PulseUI Enterprise", classes="text-2xl font-bold text-gray-800")
        title.set_size(300, 40)
        
        logo_section.add_child(logo)
        logo_section.add_child(title)
        
        # ユーザー情報
        user_section = Row(classes="items-center gap-3")
        user_section.set_size(200, 60)
        
        notifications = Badge("3", classes="bg-red-500 text-white")
        notifications.set_size(20, 20)
        
        user_name = Text("田中太郎", classes="text-gray-700 font-medium")
        user_name.set_size(80, 30)
        
        user_section.add_child(notifications)
        user_section.add_child(user_name)
        
        header_content.add_child(logo_section)
        header_content.add_child(user_section)
        
        header.add_child(header_content)
        return header
        
    def create_sidebar(self):
        """サイドバーを作成"""
        sidebar = Container(classes="bg-gray-800 text-white p-6")
        sidebar.set_size(250, 800)
        
        nav_items = [
            {"icon": "dashboard", "label": "ダッシュボード", "active": True},
            {"icon": "analytics", "label": "分析", "active": False},
            {"icon": "reports", "label": "レポート", "active": False},
            {"icon": "settings", "label": "設定", "active": False},
        ]
        
        nav_menu = Column(classes="gap-2")
        nav_menu.set_size(220, 400)
        
        for item in nav_items:
            nav_item = self.create_nav_item(item)
            nav_menu.add_child(nav_item)
            
        sidebar.add_child(nav_menu)
        return sidebar
        
    def create_nav_item(self, item):
        """ナビゲーションアイテムを作成"""
        bg_class = "bg-blue-600" if item["active"] else "hover:bg-gray-700"
        nav_item = Container(classes=f"{bg_class} rounded p-3 cursor-pointer")
        nav_item.set_size(220, 45)
        
        content = Row(classes="items-center gap-3")
        content.set_size(200, 35)
        
        icon = Icon(item["icon"], size=20, color=(1.0, 1.0, 1.0, 1.0))
        icon.set_size(25, 25)
        
        label = Text(item["label"], classes="text-white font-medium")
        label.set_size(150, 25)
        
        content.add_child(icon)
        content.add_child(label)
        nav_item.add_child(content)
        
        return nav_item
        
    def create_main_content(self):
        """メインコンテンツを作成"""
        main = Container(classes="bg-gray-50 p-6")
        main.set_size(1150, 800)
        
        # KPIカード
        kpi_section = self.create_kpi_cards()
        
        # チャートエリア
        charts_section = self.create_charts_section()
        
        # データテーブル
        table_section = self.create_data_table()
        
        main_content = Column(classes="gap-6")
        main_content.set_size(1150, 800)
        
        main_content.add_child(kpi_section)
        main_content.add_child(charts_section)
        main_content.add_child(table_section)
        
        main.add_child(main_content)
        return main
        
    def create_kpi_cards(self):
        """KPIカードを作成"""
        kpi_container = Grid(columns=4, gap=20)
        kpi_container.set_size(1150, 120)
        
        kpis = [
            {"title": "総売上", "value": "¥12,345,678", "change": "+12.5%", "color": "green"},
            {"title": "新規顧客", "value": "1,234", "change": "+8.2%", "color": "blue"},
            {"title": "成約率", "value": "23.4%", "change": "-2.1%", "color": "red"},
            {"title": "平均単価", "value": "¥45,678", "change": "+5.7%", "color": "purple"}
        ]
        
        for kpi in kpis:
            card = self.create_kpi_card(kpi)
            kpi_container.add_child(card)
            
        return kpi_container
        
    def create_kpi_card(self, kpi):
        """個別のKPIカードを作成"""
        card = Card(classes="bg-white rounded-lg shadow p-6")
        card.set_size(260, 120)
        
        content = Column(classes="gap-2")
        content.set_size(220, 80)
        
        title = Text(kpi["title"], classes="text-gray-600 text-sm font-medium")
        title.set_size(220, 20)
        
        value = Text(kpi["value"], classes="text-2xl font-bold text-gray-900")
        value.set_size(220, 35)
        
        change_color = {"green": "text-green-600", "blue": "text-blue-600", 
                       "red": "text-red-600", "purple": "text-purple-600"}[kpi["color"]]
        change = Text(kpi["change"], classes=f"{change_color} text-sm font-medium")
        change.set_size(220, 20)
        
        content.add_child(title)
        content.add_child(value)
        content.add_child(change)
        
        card.add_child(content)
        return card
        
    def create_charts_section(self):
        """チャートセクションを作成"""
        charts_container = Row(gap=20)
        charts_container.set_size(1150, 350)
        
        # 売上推移グラフ
        sales_data = [(i, 100 + 50 * math.sin(i * 0.3) + random.uniform(-10, 10)) for i in range(30)]
        sales_chart = LineChart(
            data=sales_data,
            title="月間売上推移",
            line_color=(0.2, 0.6, 1.0, 1.0)
        )
        sales_chart.set_size(565, 350)
        
        # 商品別売上
        product_data = [
            ("商品A", 450), ("商品B", 380), ("商品C", 290), 
            ("商品D", 220), ("商品E", 180)
        ]
        product_chart = BarChart(
            data=product_data,
            title="商品別売上",
            bar_color=(0.8, 0.4, 0.1, 1.0)
        )
        product_chart.set_size(565, 350)
        
        charts_container.add_child(sales_chart)
        charts_container.add_child(product_chart)
        
        return charts_container
        
    def create_data_table(self):
        """データテーブルを作成"""
        table_container = Card(classes="bg-white rounded-lg shadow")
        table_container.set_size(1150, 300)
        
        # サンプルデータ
        table_data = [
            {"顧客名": "株式会社A", "担当者": "山田太郎", "売上": "¥1,200,000", "状況": "進行中"},
            {"顧客名": "B商事", "担当者": "佐藤花子", "売上": "¥850,000", "状況": "完了"},
            {"顧客名": "C工業", "担当者": "田中次郎", "売上": "¥2,100,000", "状況": "提案中"},
            {"顧客名": "D物産", "担当者": "鈴木一郎", "売上": "¥670,000", "状況": "完了"},
            {"顧客名": "E商店", "担当者": "高橋美咲", "売上": "¥950,000", "状況": "進行中"},
        ]
        
        data_table = DataTable(
            data=table_data,
            columns=["顧客名", "担当者", "売上", "状況"],
            headers=["顧客名", "担当者", "売上金額", "進捗状況"],
            sortable=True,
            selectable=True,
            on_row_select=self.on_row_select
        )
        data_table.set_size(1110, 260)
        data_table.set_position(20, 20)
        
        table_container.add_child(data_table)
        return table_container
        
    def on_row_select(self, row_index, row_data):
        """テーブル行選択時の処理"""
        print(f"選択された行: {row_data}")
        
    def run(self):
        self.app.run()

# エンタープライズアプリケーションを実行
if __name__ == "__main__":
    app = EnterpriseDashboard()
    app.run()
```

## 🔧 必要環境

### 最小要件
- **Python**: 3.10以上
- **OpenGL**: 3.3以上
- **RAM**: 512MB以上
- **ストレージ**: 100MB以上

### 推奨環境
- **Python**: 3.11以上
- **OpenGL**: 4.0以上
- **RAM**: 2GB以上
- **GPU**: 専用グラフィックカード

### 対応プラットフォーム
- ✅ **Windows** 10/11
- ✅ **macOS** 10.15以上
- ✅ **Linux** Ubuntu 20.04以上、CentOS 8以上

## 📄 ライセンス

PulseUIは[MITライセンス](LICENSE)の下で公開されています。商用・非商用問わず自由にご利用いただけます。

## 🌟 スターをお願いします！

PulseUIが役に立った場合は、ぜひ⭐をお願いします！

[![GitHub stars](https://img.shields.io/github/stars/pulseui/pulse-ui.svg?style=social&label=Star)](https://github.com/tikipiya/PulseUI)


<div align="center">

**PulseUI** で未来のPython GUIアプリケーションを今すぐ構築しましょう！

</div>