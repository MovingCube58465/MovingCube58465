# 全局样式定义 - SIUI风格
import os
from PyQt5.QtGui import QFontDatabase, QFont

def load_custom_font():
    """加载自定义字体并返回字体名称"""
    font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'fonts', 'main.ttf')
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                return font_families[0]
    # 如果字体加载失败，返回系统默认字体
    return 'Microsoft YaHei'

GLOBAL_STYLE = """
QMainWindow, QDialog {
    background-color: #f0f0f0;
}
QLabel {
    color: #333333;
    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
}
QLineEdit, QTextEdit {
    padding: 6px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: #ffffff;
    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
}
QPushButton {
    padding: 6px 12px;
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1976D2;
}
QPushButton:pressed {
    background-color: #0D47A1;
}
QTreeWidget {
    border: 1px solid #cccccc;
    background-color: white;
    alternate-background-color: #f5f5f5;
    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
}
QTextBrowser {
    border: 1px solid #cccccc;
    background-color: white;
    font-family: 'Microsoft YaHei', 'SimHei', sans-serif;
}
QScrollArea {
    border: none;
}
QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: #f0f0f0;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #2196F3;
    border-radius: 3px;
}
/* 悬浮窗样式 */
#floatingWindow {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid #cccccc;
    border-radius: 6px;
}
QSlider::groove:horizontal {
    border: 1px solid #cccccc;
    height: 8px;
    background: #f0f0f0;
    margin: 2px 0;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #2196F3;
    border: 1px solid #1976D2;
    width: 18px;
    margin: -2px 0;
    border-radius: 9px;
}
QSlider::handle:horizontal:hover {
    background: #1976D2;
}
QHeaderView::section {
    background-color: #2196F3;
    color: white;
    padding: 6px;
    border: none;
    font-family: 'Microsoft YaHei UI', 'SimHei', sans-serif;
    font-weight: bold;
}
"""