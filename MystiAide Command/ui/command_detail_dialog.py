import re
import urllib.parse
import requests
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QTextBrowser, QFrame, QScrollArea, 
                            QProgressBar, QMessageBox, QApplication, QWidget, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QCursor, QFont, QColor
from utils.styles import GLOBAL_STYLE

class CommandDetailDialog(QDialog):
    def __init__(self, list_name, parent=None):
        super().__init__(parent)
        self.list_name = list_name
        self.parent = parent
        self.setWindowTitle(f"{list_name.split('≈')[0]} - 详情")
        self.setGeometry(200, 200, 850, 650)
        
        # 设置主题色
        self.primary_color = "#1976D2"  # 蓝色主题
        self.accent_color = "#FF4081"   # 粉色强调色
        self.bg_color = "#F5F5F5"       # 浅灰色背景
        self.text_color = "#212121"     # 深灰色文本
        
        # 设置样式
        self.setStyleSheet(GLOBAL_STYLE + """
            QDialog {
                background-color: #f8f9fa;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: none;  /* 移除边框 */
            }
            QLabel {
                color: #202124;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QTextBrowser, QLineEdit {
                border: none;  /* 移除边框 */
                border-radius: 4px;
                padding: 8px;
                background-color: #f8f9fa;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
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
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #e0e0e0;
                text-align: center;
                max-height: 6px;
            }
            QProgressBar::chunk {
                background-color: #4285f4;
                border-radius: 3px;
            }
        """)
        
        self.init_ui()
        self.load_details()
    
    def init_ui(self):
        """初始化UI组件"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # 标题
        title = QLabel(f"{self.list_name.split('≈')[0]}")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Bold))
        title.setStyleSheet("color: #202124; margin-bottom: 5px;")
        self.layout.addWidget(title)
        
        # 详情框架
        self.detail_frame = QFrame()
        self.add_shadow_effect(self.detail_frame)
        self.detail_layout = QVBoxLayout(self.detail_frame)
        self.detail_layout.setContentsMargins(15, 15, 15, 15)
        self.detail_layout.setSpacing(10)
        
        # 描述
        self.desc_label = QLabel("描述")
        self.desc_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        self.desc_browser = QTextBrowser()
        self.desc_browser.setReadOnly(True)
        self.desc_browser.setMinimumHeight(80)
        self.desc_browser.setStyleSheet("background-color: #f8f9fa;")
        
        self.detail_layout.addWidget(self.desc_label)
        self.detail_layout.addWidget(self.desc_browser)
        
        # 作者
        self.author_label = QLabel("作者")
        self.author_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        self.author_display = QLineEdit()
        self.author_display.setReadOnly(True)
        self.author_display.setStyleSheet("background-color: #f8f9fa;")
        
        self.detail_layout.addWidget(self.author_label)
        self.detail_layout.addWidget(self.author_display)
        
        self.layout.addWidget(self.detail_frame)
        
        # 命令列表框架
        self.cmd_frame = QFrame()
        self.add_shadow_effect(self.cmd_frame)
        self.cmd_layout = QVBoxLayout(self.cmd_frame)
        self.cmd_layout.setContentsMargins(15, 15, 15, 15)
        self.cmd_layout.setSpacing(10)
        
        # 命令列表标题和悬浮窗按钮
        cmd_header = QWidget()
        cmd_header_layout = QHBoxLayout(cmd_header)
        cmd_header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cmd_label = QLabel("命令列表")
        self.cmd_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        cmd_header_layout.addWidget(self.cmd_label)
        
        # 添加悬浮窗按钮
        self.float_btn = QPushButton("打开悬浮窗")
        self.float_btn.setIcon(self.style().standardIcon(self.style().SP_TitleBarMaxButton))
        self.float_btn.clicked.connect(self.show_floating_window)
        cmd_header_layout.addWidget(self.float_btn, 0, Qt.AlignRight)
        
        self.cmd_layout.addWidget(cmd_header)
        
        # 创建可滚动的命令列表区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
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
        
        self.cmd_content = QWidget()
        self.cmd_content.setStyleSheet("background-color: #f8f9fa; border-radius: 4px;")
        self.cmd_content_layout = QVBoxLayout(self.cmd_content)
        self.cmd_content_layout.setAlignment(Qt.AlignTop)
        self.cmd_content_layout.setContentsMargins(10, 10, 10, 10)
        self.cmd_content_layout.setSpacing(8)
        
        self.scroll_area.setWidget(self.cmd_content)
        self.cmd_layout.addWidget(self.scroll_area)
        
        self.layout.addWidget(self.cmd_frame)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.layout.addWidget(self.progress_bar)
        self.progress_bar.setVisible(False)
        
        # 存储命令列表
        self.command_list = []
    
    def add_shadow_effect(self, widget):
        """为控件添加阴影效果"""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        widget.setGraphicsEffect(shadow)
    
    def show_floating_window(self):
        """显示悬浮窗"""
        if self.parent and hasattr(self.parent, 'floating_window'):
            # 设置悬浮窗位置在当前对话框旁边
            dialog_pos = self.pos()
            self.parent.floating_window.move(dialog_pos.x() + self.width() + 10, dialog_pos.y())
            
            self.parent.floating_window.set_commands(self.command_list)
            self.parent.floating_window.show()
            self.parent.floating_window.raise_()
            self.parent.floating_window.activateWindow()
    
    def load_details(self):
        """加载命令库详情"""
        try:
            self.progress_bar.setValue(10)
            QApplication.processEvents()
            
            encoded_list_name = urllib.parse.quote(self.list_name)
            main_xml_url = f"https://www.viqu.com/MystiAide/cls/{encoded_list_name}/main.xml"
            
            self.progress_bar.setValue(30)
            QApplication.processEvents()
            
            response = requests.get(main_xml_url)
            
            if response.status_code == 200:
                response.encoding = 'utf-8'
                content = response.text
                
                # 解析XML
                des_match = re.search(r'<des>(.*?)</des>', content)
                r_match = re.search(r'<r>(.*?)</r>', content)
                
                # 设置描述和作者
                if des_match:
                    desc_text = des_match.group(1)
                    self.desc_browser.setPlainText(desc_text)
                
                if r_match:
                    author_text = r_match.group(1)
                    self.author_display.setText(author_text)
                
                self.progress_bar.setValue(50)
                QApplication.processEvents()
                
                # 获取list.xml内容
                list_xml_url = f"https://www.viqu.com/MystiAide/cls/{encoded_list_name}/list.xml"
                response = requests.get(list_xml_url)
                
                self.progress_bar.setValue(70)
                QApplication.processEvents()
                
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    list_items = [item.strip() for item in response.text.split('∅') if item.strip()]
                    
                    # 清空命令列表
                    self.command_list = []
                    
                    # 添加命令列表
                    for item in list_items:
                        parts = item.split('---')
                        command = parts[0].strip()
                        description = parts[1].strip() if len(parts) > 1 else ""
                        
                        # 添加到命令列表
                        self.command_list.append({
                            'command': command,
                            'description': description
                        })
                        
                        # 创建命令项
                        cmd_item = QLabel()
                        cmd_item.setTextFormat(Qt.RichText)
                        cmd_item.setTextInteractionFlags(Qt.TextBrowserInteraction)
                        cmd_item.setCursor(QCursor(Qt.PointingHandCursor))
                        cmd_item.setStyleSheet("QLabel { margin-bottom: 10px; }")
                        
                        html = f"""
                        <div style="margin-bottom: 8px; padding: 8px; border-left: 3px solid #2196F3; background-color: #f8f9fa; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                            <a href='command://{command}' style="color: #2196F3; text-decoration: none; font-weight: bold; font-size: 14px; word-wrap: break-word; word-break: break-all;">{command}</a>
                        """
                        if description:
                            html += f"""
                            <div style="color: #555; margin-top: 5px; padding-left: 5px; font-size: 13px; word-wrap: break-word; word-break: break-all; border-top: 1px solid #f0f0f0; padding-top: 5px;">
                                {description}
                            </div>
                            """
                        html += "</div>"
                        
                        cmd_item.setText(html)
                        cmd_item.setWordWrap(True)  # 启用文本自动换行
                        cmd_item.linkActivated.connect(self.copy_command)
                        
                        self.cmd_content_layout.addWidget(cmd_item)
                    
                    self.progress_bar.setValue(100)
                    QApplication.processEvents()
                else:
                    error_label = QLabel(f"无法获取命令列表，HTTP状态码: {response.status_code}")
                    self.cmd_content_layout.addWidget(error_label)
            else:
                error_label = QLabel(f"无法获取详情，HTTP状态码: {response.status_code}")
                self.layout.addWidget(error_label)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误: {str(e)}")
        finally:
            # 隐藏进度条
            self.progress_bar.setVisible(False)
    
    def copy_command(self, link):
        """复制命令到剪贴板"""
        if link.startswith("command://"):
            command = link[9:]  # 去掉 command:// 前缀
            clipboard = QApplication.clipboard()
            clipboard.setText(command)
            
            if self.parent:
                self.parent.status_bar.showMessage(f"已复制命令: {command}")