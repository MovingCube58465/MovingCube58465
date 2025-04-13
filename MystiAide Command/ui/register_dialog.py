from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                            QPushButton, QLabel, QFrame, QHBoxLayout, 
                            QMessageBox, QApplication, QGraphicsDropShadowEffect, QWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor
import requests
from utils.styles import GLOBAL_STYLE

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户注册")
        self.setFixedSize(400, 350)  # 稍微高一点，因为有确认密码字段
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 用户信息
        self.username = ""
        self.user_id = ""
        
        # 设置样式
        self.setStyleSheet(GLOBAL_STYLE + """
            QDialog {
                background-color: #f8f9fa;
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: none;
            }
            QLabel {
                color: #202124;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QLineEdit {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QLineEdit:focus {
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
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("用户注册")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Bold))
        title.setStyleSheet("color: #202124; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("注册账号以使用更多功能")
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
        
        # 用户名
        username_label = QLabel("用户名")
        username_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        form_layout.addRow(username_label, self.username_input)
        
        # 密码
        password_label = QLabel("密码")
        password_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow(password_label, self.password_input)
        
        # 确认密码
        confirm_password_label = QLabel("确认密码")
        confirm_password_label.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("请再次输入密码")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow(confirm_password_label, self.confirm_password_input)
        
        form_container_layout.addLayout(form_layout)
        
        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
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
        
        # 注册按钮
        register_btn = QPushButton("注册")
        register_btn.clicked.connect(self.register)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(register_btn)
        
        form_container_layout.addWidget(button_container)
        layout.addWidget(form_container)
    
    def add_shadow_effect(self, widget):
        """为控件添加阴影效果"""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        widget.setGraphicsEffect(shadow)
    
    def register(self):
        """处理注册逻辑"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # 验证输入
        if not username or not password:
            QMessageBox.warning(self, "错误", "用户名和密码不能为空!")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "错误", "两次输入的密码不一致!")
            return
        
        try:
            # 注册请求
            register_url = f"https://www.viqu.com/MystiAide/normal_user/sign.php?type=create&name={username}&data={password}&id=1"
            response = requests.get(register_url)
            
            if response.status_code == 200:
                response_text = response.text.strip()
                
                if "true" in response_text.lower():
                    # 注册成功，获取用户ID
                    self.username = username
                    if self.get_user_id(username):
                        QMessageBox.information(self, "注册成功", "账号注册成功!")
                        self.accept()
                    else:
                        QMessageBox.warning(self, "注册问题", "注册成功但无法获取用户ID，部分功能可能受限")
                        self.accept()  # 仍然接受注册，但可能有功能限制
                else:
                    QMessageBox.warning(self, "注册失败", response_text)
            else:
                QMessageBox.critical(self, "错误", f"服务器响应错误: {response.status_code}")
        
        except Exception as e:
            QMessageBox.critical(self, "错误", f"注册过程中发生错误: {str(e)}")
    
    def get_user_id(self, username):
        """获取用户ID"""
        try:
            # 获取用户ID请求
            id_url = f"https://www.viqu.com/MystiAide/normal_user/getid.php?name={username}"
            response = requests.get(id_url)
            
            if response.status_code == 200:
                user_id = response.text.strip()
                if user_id and user_id != "null" and user_id != "false":
                    self.user_id = user_id
                    print(f"获取到用户ID: {self.user_id}")  # 调试信息
                    # 保存登录状态
                    self.save_login_state(username, self.user_id)
                    return True
                else:
                    print(f"获取用户ID返回无效值: {user_id}")  # 调试信息
                    return False
            else:
                QMessageBox.warning(self, "警告", f"获取用户ID失败: {response.status_code}")
                return False
        
        except Exception as e:
            QMessageBox.warning(self, "警告", f"获取用户ID时发生错误: {str(e)}")
            return False
    
    def save_login_state(self, username, user_id):
        """保存加密的登录状态到文件"""
        import os
        import json
        import time
        from utils.aes_crypto import AESCrypto
        
        try:
            # 使用主窗口中的方法获取安全的配置目录和文件路径
            config_dir = self.parent().get_secure_config_dir()
            login_file = self.parent().get_secure_login_file_path(config_dir)
            
            # 准备登录数据
            login_data = {
                "username": username,
                "user_id": user_id,
                "timestamp": time.time()
            }
            
            # 加密数据
            encrypted_data = AESCrypto.encrypt_login_data(login_data)
            if not encrypted_data:
                print("加密登录数据失败")
                return
            
            # 保存加密数据到临时JSON文件
            temp_file = os.path.join(config_dir, f".tmp_{int(time.time())}.dat")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(encrypted_data, f)
            
            # 对整个JSON文件再次加密
            AESCrypto.encrypt_file(temp_file, login_file)
            
            # 删除临时文件
            os.remove(temp_file)
                
            print(f"双重加密的登录状态已保存")
        except Exception as e:
            print(f"保存登录状态时出错: {str(e)}")