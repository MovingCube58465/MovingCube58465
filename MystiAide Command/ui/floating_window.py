from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QScrollArea, QFrame, QSlider, QGraphicsOpacityEffect, QApplication)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QCursor, QPainter, QBrush, QColor


class FloatingCommandWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setObjectName("floatingWindow")
        self.setMinimumSize(300, 400)
        self.setMaximumSize(400, 600)
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_TranslucentBackground)  # 允许背景透明
        self.setWindowFlag(Qt.X11BypassWindowManagerHint, True)
        
        # 设置初始透明度
        self.opacity = 1.0  # 将透明度设置为1.0，避免字体锯齿
        self.background_opacity_effect = QGraphicsOpacityEffect(self)
        self.background_opacity_effect.setOpacity(self.opacity)
        self.setGraphicsEffect(self.background_opacity_effect)
        
        # 设置样式
        self.setStyleSheet("""
            #floatingWindow {
                background-color: transparent;
            }
            QWidget {
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #202124;
            }
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QPushButton:pressed {
                background-color: #2a56c6;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #e0e0e0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #4285f4;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #3367d6;
            }
        """)
        
        self.init_ui()
        self.old_pos = self.pos()
        self.commands = []
        self.main_app = parent
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 主内容框
        self.content_frame = QFrame(self)
        self.content_frame.setObjectName("contentFrame")
        self.content_frame.setStyleSheet("""
            #contentFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # 标题栏
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        title_label = QLabel("命令列表")
        title_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        title_label.setStyleSheet("color: #202124;")
        
        opacity_btn = QPushButton("透明度")
        opacity_btn.setFixedSize(70, 24)
        opacity_btn.setFont(QFont("Microsoft YaHei UI", 9))
        opacity_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                padding: 4px 8px;
            }
        """)
        opacity_btn.clicked.connect(self.toggle_opacity_slider)
        
        close_btn = QPushButton("")
        close_btn.setFixedSize(24, 24)
        close_btn.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ea4335;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #d93025;
            }
        """)
        close_btn.clicked.connect(self.hide)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(opacity_btn)
        title_layout.addWidget(close_btn)
        
        content_layout.addWidget(title_bar)
        
        # 透明度滑块（初始隐藏）
        self.opacity_slider_container = QWidget()
        self.opacity_slider_container.setVisible(False)
        self.opacity_slider_container.setFixedHeight(40)  # 设置固定高度而不是最大高度
        opacity_slider_layout = QHBoxLayout(self.opacity_slider_container)
        opacity_slider_layout.setContentsMargins(0, 0, 0, 0)
        
        opacity_label = QLabel("透明度:")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(int(self.opacity * 100))
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        
        opacity_slider_layout.addWidget(opacity_label)
        opacity_slider_layout.addWidget(self.opacity_slider, 1)
        
        content_layout.addWidget(self.opacity_slider_container)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        separator.setFixedHeight(1)
        content_layout.addWidget(separator)
        
        # 命令列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f3f4;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c2c2c2;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a6a6a6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.command_widget = QWidget()
        self.command_layout = QVBoxLayout(self.command_widget)
        self.command_layout.setAlignment(Qt.AlignTop)
        self.command_layout.setContentsMargins(5, 5, 5, 5)
        self.command_layout.setSpacing(10)
        
        scroll_area.setWidget(self.command_widget)
        content_layout.addWidget(scroll_area)
        
        layout.addWidget(self.content_frame)
    
    def toggle_opacity_slider(self):
        """切换透明度滑块的可见性"""
        # 添加动画效果
        visible = not self.opacity_slider_container.isVisible()
        self.opacity_slider_container.setVisible(visible)
        
        if visible:
            # 显示时设置固定高度
            self.opacity_slider_container.setFixedHeight(40)
        else:
            # 隐藏时设置高度为0
            self.opacity_slider_container.setFixedHeight(0)
    
        # 创建高度动画
        height = 40 if visible else 0
        animation = QPropertyAnimation(self.opacity_slider_container, b"maximumHeight")
        animation.setDuration(200)
        animation.setStartValue(0 if visible else 40)
        animation.setEndValue(height)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
    
    def change_opacity(self, value):
        """改变窗口透明度"""
        self.opacity = value / 100.0
        self.background_opacity_effect.setOpacity(self.opacity)
    
    def paintEvent(self, event):
        """自定义绘制事件，添加圆角和阴影"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        
        # 设置半透明背景
        painter.setBrush(QBrush(QColor(255, 255, 255, 240)))
        painter.drawRoundedRect(self.rect(), 10, 10)
    
    def mousePressEvent(self, event):
        """鼠标按下事件，记录拖动起始位置"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，实现窗口拖动"""
        if event.buttons() & Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    
    def set_commands(self, commands):
        """设置命令列表"""
        self.commands = commands
        self.update_command_display()
    
    def update_command_display(self):
        """更新命令显示"""
        # 清除现有内容
        while self.command_layout.count():
            item = self.command_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
        # 添加新命令
        for command_data in self.commands:
            command = command_data.get('command', 'command')
            description = command_data.get('description', 'description')
        
            cmd_item = QLabel()
            cmd_item.setTextFormat(Qt.RichText)
            cmd_item.setTextInteractionFlags(Qt.TextBrowserInteraction)
            cmd_item.setCursor(QCursor(Qt.PointingHandCursor))
            cmd_item.setFont(QFont("Microsoft YaHei", 10))  # 使用高质量字体
            cmd_item.setStyleSheet("""
            QLabel {
                margin-bottom: 10px;
                color: #34495e;
                font-size: 12px;
            }
            QLabel:hover {
                color: #2c3e50;
            }
            """)
            
            # 设置宽度以确保自动换行
            cmd_item.setFixedWidth(300)  # 设置固定宽度
            cmd_item.setWordWrap(True)   # 启用自动换行
        
            html = f"""
            <div style="margin-bottom: 5px;">
                <a href='command://{command}' style="color: #3498db; text-decoration: none; font-weight: bold; word-wrap: break-word; word-break: break-all;">{command}</a>
            </div>
            """
            if description:
                html += f"""
                <div style="color: #7f8c8d; margin-left: 10px; margin-bottom: 15px; word-wrap: break-word; word-break: break-all;">
                    {description}
                </div>
                """
            
            cmd_item.setText(html)
            cmd_item.linkActivated.connect(self.copy_command)
            self.command_layout.addWidget(cmd_item)
    def copy_command(self, link):
        """复制命令到剪贴板"""
        if link.startswith("command://"):
            command = link[9:]
            clipboard = QApplication.clipboard()
            clipboard.setText(command)
            
            # 使用保存的主应用引用
            if self.main_app and hasattr(self.main_app, 'status_bar'):
                self.main_app.status_bar.showMessage(f"已复制命令: {command}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = FloatingCommandWindow()
    window.set_commands([
        {"command": "command1", "description": "这是命令1的描述"},
        {"command": "command2", "description": "这是命令2的描述"},
        {"command": "command3", "description": "这是命令3的描述"}
    ])
    window.show()
    sys.exit(app.exec_())