from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, 
                            QPushButton, QProgressBar, QMessageBox, QApplication, 
                            QFrame, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QWidget)  # 添加 QWidget
from PyQt5.QtCore import QRegExp, QPropertyAnimation, QEasingCurve, Qt  # 添加 Qt 到这里
from PyQt5.QtGui import QRegExpValidator, QFont, QColor
import requests
from utils.styles import GLOBAL_STYLE

class UploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("上传命令库")
        self.setGeometry(300, 300, 550, 550)
        
        # 初始化用户ID
        self.user_id = ""
        
        # 设置样式
        # 在样式表中设置的边框属性
        self.setStyleSheet(GLOBAL_STYLE + """
            QDialog {
                background-color: #f8f9fa;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: none;  # 移除边框
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);  # 添加阴影代替边框
            }
            QLineEdit, QTextEdit {
                border: 1px solid #e8e8e8;  # 使用更浅的颜色
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #202124;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #4285f4;
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
    
    # 删除这里的错误导入语句
    def init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("上传新命令库")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Bold))
        title.setStyleSheet("color: #202124; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("创建并分享您的命令集合")
        subtitle.setFont(QFont("Microsoft YaHei UI", 10))
        subtitle.setStyleSheet("color: #5f6368; margin-bottom: 10px;")
        layout.addWidget(subtitle)
        
        # 表单容器
        form_container = QFrame()
        self.add_shadow_effect(form_container)
        form_container_layout = QVBoxLayout(form_container)
        form_container_layout.setContentsMargins(15, 15, 15, 15)
        form_container_layout.setSpacing(15)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # 命令库名称
        name_label = QLabel("命令库名称")
        name_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("不超过15个字符，不支持特殊字符")
        name_validator = QRegExpValidator(QRegExp("[^&?#\\[\\]]{1,15}"))
        self.name_input.setValidator(name_validator)
        form_layout.addRow(name_label, self.name_input)
        
        # 作者
        author_label = QLabel("作者")
        author_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("不超过15个字符，不支持特殊字符")
        author_validator = QRegExpValidator(QRegExp("[^&?#\\[\\]]{1,15}"))
        self.author_input.setValidator(author_validator)
        form_layout.addRow(author_label, self.author_input)
        
        # 命令库介绍
        desc_label = QLabel("命令库介绍")
        desc_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("不超过150个字符，不支持特殊字符")
        desc_validator = QRegExpValidator(QRegExp("[^&?#\\[\\]]{1,150}"))
        self.desc_input.setValidator(desc_validator)
        form_layout.addRow(desc_label, self.desc_input)
        
        form_container_layout.addLayout(form_layout)
        
        # 命令列表
        cmd_label = QLabel("命令列表")
        cmd_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        form_container_layout.addWidget(cmd_label)
        
        self.commands_input = QTextEdit()
        self.commands_input.setPlaceholderText("每行一个命令，格式: 命令 - - -(#) 描述")
        self.commands_input.setMinimumHeight(150)
        form_container_layout.addWidget(self.commands_input)
        
        layout.addWidget(form_container)
        
        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f4;
                color: #5f6368;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
            QPushButton:pressed {
                background-color: #dadce0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # 上传按钮
        upload_btn = QPushButton("上传")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f9d58;
            }
            QPushButton:hover {
                background-color: #0b8043;
            }
            QPushButton:pressed {
                background-color: #096536;
            }
        """)
        upload_btn.clicked.connect(self.upload_data)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(upload_btn)
        
        layout.addWidget(button_container, 0, Qt.AlignRight)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)
        self.progress_bar.setVisible(False)
    
    def add_shadow_effect(self, widget):
        """为控件添加阴影效果"""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        widget.setGraphicsEffect(shadow)
    
    # 在UploadDialog类中添加设置用户ID的方法
    
    def set_user_id(self, user_id):
        """设置用户ID"""
        self.user_id = user_id
    
    # 修改upload_data方法，添加用户ID
    def upload_data(self):
        """处理上传逻辑"""
        # 获取输入数据
        name = self.name_input.text().strip()
        desc = self.desc_input.text().strip()
        author = self.author_input.text().strip()
        commands = self.commands_input.toPlainText().strip()
        
        # 验证输入
        if not all([name, desc, author, commands]):
            QMessageBox.warning(self, "错误", "所有字段都必须填写!")
            return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(50)
        QApplication.processEvents()  # 更新UI
        
        # 处理命令列表
        # 替换#为---，换行符为∅
        processed_commands = commands.replace("#", " --- ").replace("\n", "∅")
        
        # 构建表单数据 - 修改name字段格式为"命令组名称≈作者@id"
        formatted_name = f"{name}≈{author}"
        if hasattr(self, 'user_id') and self.user_id:
            formatted_name += f"@{self.user_id}"
            
        data = {
            "name": formatted_name,
            "fn": f"<des>{desc}</des><r>{author}</r><at></at><ut>true</ut>",
            "doc": "PC端上传",
            "des": processed_commands
        }
        
        # 如果有用户ID，添加到请求中
        if hasattr(self, 'user_id') and self.user_id:
            data["uid"] = self.user_id
        
        # 发送POST请求
        try:
            response = requests.post(
                "https://www.viqu.com/MystiAide/wi/upload.php",
                data=data
            )
            
            self.progress_bar.setValue(100)
            
            if response.status_code == 200:
                QMessageBox.information(self, "系统", f"{response.text}")
                if "成功" in response.text:
                    self.close()
            else:
                QMessageBox.critical(self, "上传失败", f"HTTP状态码: {response.status_code}\n返回内容: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"上传过程中发生错误: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)