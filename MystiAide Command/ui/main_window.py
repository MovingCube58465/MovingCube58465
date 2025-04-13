import urllib.parse
import webbrowser
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
                            QMessageBox, QProgressBar, QApplication, QFrame, QDialog)
from PyQt5.QtCore import Qt, QUrl, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QDesktopServices, QPalette, QColor
import requests

from utils.styles import GLOBAL_STYLE
from ui.upload_dialog import UploadDialog
from ui.command_detail_dialog import CommandDetailDialog
from ui.floating_window import FloatingCommandWindow
from ui.login_dialog import LoginDialog  # 导入登录对话框
from ui.register_dialog import RegisterDialog  # 导入注册对话框
# 在文件顶部添加
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class MystiAideApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MystiAide 命令库浏览器")
        self.setGeometry(100, 100, 1000, 700)
        
        # 用户信息
        self.user_name = ""
        self.user_id = ""
        self.is_logged_in = False
        
        # 设置应用整体样式
        self.setStyleSheet(GLOBAL_STYLE + """
            QMainWindow {
                background-color: #f8f9fa;
            }
            QWidget {
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
            QPushButton:pressed {
                background-color: #2a56c6;
            }
            QLineEdit {
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4285f4;
            }
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #e0e0e0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4285f4;
                border-radius: 3px;
            }
        """)
        
        # 悬浮窗
        self.floating_window = FloatingCommandWindow(self)
        
        self.init_ui()
        
        # 尝试加载保存的登录状态
        self.load_login_state()
        
        # 加载初始列表
        self.original_items = []
        self.load_main_list()
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建主部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # 创建顶部栏，包含标题和登录按钮
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建卡片式容器
        self.main_card = QFrame()
        self.main_card.setObjectName("mainCard")
        self.main_card.setStyleSheet("""
            #mainCard {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.card_layout = QVBoxLayout(self.main_card)
        self.card_layout.setContentsMargins(15, 15, 15, 15)
        self.card_layout.setSpacing(15)
        
        # 创建标题区域
        title_area = QWidget()
        title_layout = QHBoxLayout(title_area)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题部分
        title_widget = QWidget()
        title_widget_layout = QVBoxLayout(title_widget)
        title_widget_layout.setContentsMargins(0, 0, 0, 0)
        title_widget_layout.setSpacing(5)
        
        # 创建标题
        title = QLabel("MystiAide 命令库")
        title.setFont(QFont("Microsoft YaHei UI", 18, QFont.Bold))
        title.setStyleSheet("color: #202124; margin-bottom: 5px;")
        title_widget_layout.addWidget(title)
        
        # 添加副标题
        subtitle = QLabel("高效管理和使用您的命令集合")
        subtitle.setFont(QFont("Microsoft YaHei UI", 10))
        subtitle.setStyleSheet("color: #5f6368; margin-bottom: 10px;")
        title_widget_layout.addWidget(subtitle)
        
        title_layout.addWidget(title_widget)
        
        # 登录部分
        login_widget = QWidget()
        login_layout = QHBoxLayout(login_widget)
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # 用户信息标签（初始隐藏）
        self.user_info_label = QLabel("")
        self.user_info_label.setStyleSheet("color: #4285f4; font-weight: bold;")
        self.user_info_label.setVisible(False)
        login_layout.addWidget(self.user_info_label)
        
        # 注册按钮
        self.register_button = QPushButton("注册")
        self.register_button.setFixedWidth(80)
        self.register_button.clicked.connect(self.show_register_dialog)
        login_layout.addWidget(self.register_button)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setFixedWidth(80)
        self.login_button.clicked.connect(self.show_login_dialog)
        login_layout.addWidget(self.login_button)
        
        title_layout.addWidget(login_widget)
        
        self.card_layout.addWidget(title_area)
        
        # 创建搜索框
        self.create_search_box()
        
        # 创建列表显示区域
        self.create_list_widget()
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.card_layout.addWidget(self.progress_bar)
        self.progress_bar.setVisible(False)
        
        # 将卡片添加到主布局
        self.main_layout.addWidget(self.main_card)
        
        # 创建状态栏
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("color: #5f6368;")
        self.status_bar.showMessage("准备就绪")
    
    def show_login_dialog(self):
        """显示登录对话框"""
        if self.is_logged_in:
            # 如果已登录，则显示退出登录选项
            reply = QMessageBox.question(self, "用户操作", 
                                        f"当前登录: {self.user_name}\n是否退出登录?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.logout()
        else:
            # 显示登录对话框
            dialog = LoginDialog(self)
            self.animate_dialog_open(dialog)
            if dialog.exec_() == QDialog.Accepted:
                self.user_name = dialog.username
                self.user_id = dialog.user_id
                self.is_logged_in = True
                self.update_login_status()
                self.status_bar.showMessage(f"欢迎, {self.user_name}!")
    
    def show_register_dialog(self):
        """显示注册对话框"""
        if self.is_logged_in:
            QMessageBox.information(self, "已登录", "您已经登录，无需注册")
            return
            
        dialog = RegisterDialog(self)
        self.animate_dialog_open(dialog)
        if dialog.exec_() == QDialog.Accepted:
            # 注册成功后自动登录
            self.user_name = dialog.username
            self.user_id = dialog.user_id
            self.is_logged_in = True
            self.update_login_status()
            self.status_bar.showMessage(f"注册成功并已登录，欢迎 {self.user_name}!")
    
    def logout(self):
        """退出登录"""
        self.user_name = ""
        self.user_id = ""
        self.is_logged_in = False
        self.update_login_status()
        self.status_bar.showMessage("已退出登录")
    
    def update_login_status(self):
        """更新登录状态显示"""
        if self.is_logged_in:
            self.login_button.setText("退出")
            self.user_info_label.setText(f"用户: {self.user_name}")
            self.user_info_label.setVisible(True)
            self.register_button.setVisible(False)  # 登录后隐藏注册按钮
        else:
            self.login_button.setText("登录")
            self.user_info_label.setVisible(False)
            self.register_button.setVisible(True)  # 未登录时显示注册按钮
    
    def show_upload_dialog(self):
        """显示上传对话框"""
        # 检查是否已登录
        if not self.is_logged_in:
            QMessageBox.warning(self, "需要登录", "上传命令库需要先登录账号")
            self.show_login_dialog()
            if not self.is_logged_in:
                return
        
        dialog = UploadDialog(self)
        # 传递用户ID
        dialog.set_user_id(self.user_id)
        # 添加动画效果
        self.animate_dialog_open(dialog)
        dialog.exec_()
    
    def animate_dialog_open(self, dialog):
        """为对话框添加打开动画"""
        dialog.setWindowOpacity(0)
        dialog.show()
        
        # 创建透明度动画
        self.animation = QPropertyAnimation(dialog, b"windowOpacity")
        self.animation.setDuration(250)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
    
    def create_list_widget(self):
        """创建列表显示部件"""
        # 创建列表容器
        list_container = QFrame()
        list_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
        """)
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(2)
        self.tree_widget.setHeaderLabels(["名称", "描述"])
        
        self.tree_widget.setColumnWidth(0, 250)  # 名称列宽度
        self.tree_widget.setColumnWidth(1, 600)  # 描述列宽度
        self.tree_widget.setIndentation(0)
        
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: white;
                alternate-background-color: #f8f9fa;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #4285f4;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTreeWidget::item {
                padding: 8px 4px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTreeWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
            }
            QTreeWidget::item:hover {
                background-color: #f1f3f4;
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
        
        # 设置交替行颜色
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        list_layout.addWidget(self.tree_widget)
        self.card_layout.addWidget(list_container)
    
    def load_main_list(self):
        """加载主列表"""
        self.status_bar.showMessage("正在加载列表...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        QApplication.processEvents()  
        
        try:
            self.tree_widget.clear()
            self.progress_bar.setValue(30)
            QApplication.processEvents()
            
            response = requests.get("https://www.viqu.com/MystiAide/cls/dir.php")
            
            self.progress_bar.setValue(70)
            QApplication.processEvents()
            
            if response.status_code == 200:
                response.encoding = 'utf-8'
                items = response.text.split('\n')
                self.original_items = []
                
                for item in items:
                    if item.strip():
                        parts = item.split('≈')
                        name = parts[0].strip()
                        desc = parts[1].strip() if len(parts) > 1 else ""
                        full_name = f"{name}≈{desc}" if desc else name
                        
                        self.original_items.append((name, desc, full_name))
                        
                        item = QTreeWidgetItem(self.tree_widget)
                        item.setText(0, name)
                        item.setText(1, desc)
                        item.setData(0, Qt.UserRole, full_name)
                
                self.status_bar.showMessage(f"加载完成，共 {len(self.original_items)} 个项目")
            else:
                QMessageBox.critical(self, "错误", f"无法获取列表，HTTP状态码: {response.status_code}")
                self.status_bar.showMessage("加载失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误: {str(e)}")
            self.status_bar.showMessage("加载出错")
        finally:
            self.progress_bar.setValue(100)
            QApplication.processEvents()
            self.progress_bar.setVisible(False)
    
    def search_lists(self):
        """搜索列表"""
        search_term = self.search_input.text().lower()
        if not search_term:
            self.clear_search()
            return
        
        self.tree_widget.clear()
        found_count = 0
        
        for name, desc, full_name in self.original_items:
            if search_term in name.lower() or search_term in desc.lower():
                item = QTreeWidgetItem(self.tree_widget)
                item.setText(0, name)
                item.setText(1, desc)
                item.setData(0, Qt.UserRole, full_name)
                found_count += 1
        
        self.status_bar.showMessage(f"找到 {found_count} 个匹配项" if found_count > 0 else "没有找到匹配项")
    
    def clear_search(self):
        """清除搜索"""
        self.search_input.clear()
        self.tree_widget.clear()
        
        for name, desc, full_name in self.original_items:
            item = QTreeWidgetItem(self.tree_widget)
            item.setText(0, name)
            item.setText(1, desc)
            item.setData(0, Qt.UserRole, full_name)
        
        self.status_bar.showMessage(f"显示全部 {len(self.original_items)} 个项目")
    
    def setup_url_monitoring(self):
        """设置URL监控，用于检测需要退出登录的链接"""
        # 创建QNetworkAccessManager来监控网络请求
        from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.check_redirect_url)
    
    def check_redirect_url(self, reply):
        """检查重定向URL是否包含需要退出登录的标记"""
        redirect_url = reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
        if redirect_url:
            url_string = redirect_url.toString()
            if "account" in url_string:
                print(f"检测到账号相关链接: {url_string}，执行退出登录")
                self.logout()

    def on_item_double_clicked(self, item, column):
        full_name = item.data(0, Qt.UserRole)
        # 检查链接是否包含account
        if "account" in full_name:
            self.logout()
            return
        self.show_list_details(full_name)
    
    def show_list_details(self, list_name):
        # 检查链接是否包含account
        if "account" in list_name:
            self.logout()
            return
            
        detail_dialog = CommandDetailDialog(list_name, self)
        # 添加动画效果
        self.animate_dialog_open(detail_dialog)
        # 将对话框设置为非模态
        detail_dialog.setModal(False)
        detail_dialog.show()  # 使用show()而不是exec_()
        # 保存对话框引用，防止被垃圾回收
    
    def create_search_box(self):
        """创建搜索框区域"""
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f3f4;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)
        search_layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: transparent;
                font-size: 14px;
                padding: 5px;
            }
        """)
        self.search_input.returnPressed.connect(self.search_lists)
        
        search_button = QPushButton("搜索")
        search_button.setFixedWidth(80)
        search_button.clicked.connect(self.search_lists)
        
        clear_button = QPushButton("清除")
        clear_button.setFixedWidth(80)
        clear_button.clicked.connect(self.clear_search)
        
        refresh_button = QPushButton("刷新")
        refresh_button.setFixedWidth(80)
        refresh_button.clicked.connect(self.load_main_list)
        
        upload_button = QPushButton("上传")
        upload_button.setFixedWidth(80)
        upload_button.setStyleSheet("""
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
        upload_button.clicked.connect(self.show_upload_dialog)
        
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_button)
        search_layout.addWidget(refresh_button)
        search_layout.addWidget(upload_button)
        
        self.card_layout.addWidget(search_frame)

    def load_login_state(self):
        """加载并解密保存的登录状态"""
        import os
        import json
        import time
        import requests
        from utils.aes_crypto import AESCrypto
        
        try:
            # 使用更隐蔽的文件位置和名称
            config_dir = self.get_secure_config_dir()
            login_file = self.get_secure_login_file_path(config_dir)
            
            if not os.path.exists(login_file):
                return
            
            # 先解密整个文件
            temp_file = os.path.join(config_dir, f".tmp_{int(time.time())}.dat")
            if not AESCrypto.decrypt_file(login_file, temp_file):
                print("解密登录文件失败")
                return
            
            try:
                # 读取解密后的JSON文件
                with open(temp_file, "r", encoding="utf-8") as f:
                    encrypted_data = json.load(f)
                
                # 解密内部数据
                login_data = AESCrypto.decrypt_login_data(encrypted_data)
                
                # 删除临时文件
                os.remove(temp_file)
                
                if not login_data:
                    self.clear_login_state()
                    return
                
                # 检查数据是否完整
                if "username" in login_data and "user_id" in login_data:
                    # 检查是否过期
                    if "timestamp" in login_data:
                        current_time = time.time()
                        login_time = login_data["timestamp"]
                        # 7天 = 604800秒
                        if current_time - login_time > 604800:
                            print("登录状态已过期")
                            self.clear_login_state()
                            return
                    
                    # 恢复登录状态
                    self.user_name = login_data["username"]
                    self.user_id = login_data["user_id"]
                    
                    # 验证登录状态
                    self.verify_login(self.user_name, self.user_id)
                else:
                    print("登录数据不完整")
                    self.clear_login_state()
            except Exception as e:
                print(f"处理解密后的数据时出错: {str(e)}")
                # 确保删除临时文件
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        except Exception as e:
            print(f"加载登录状态时出错: {str(e)}")
        
        def clear_login_state(self):
            """清除保存的登录状态"""
            import os
            
            try:
                config_dir = self.get_secure_config_dir()
                login_file = self.get_secure_login_file_path(config_dir)
                
                if os.path.exists(login_file):
                    os.remove(login_file)
                    print("已清除登录状态")
            except Exception as e:
                print(f"清除登录状态时出错: {str(e)}")
        
        def logout(self):
            """退出登录"""
            self.user_name = ""
            self.user_id = ""
            self.is_logged_in = False
            self.update_login_status()
            self.status_bar.showMessage("已退出登录")
            
            # 清除保存的登录状态
            self.clear_login_state()

    def get_machine_info(self):
        """获取机器特定信息作为加密密钥的种子"""
        import platform
        import uuid
        
        # 获取系统信息和硬件标识
        system_info = platform.system() + platform.version()
        try:
            machine_id = str(uuid.getnode())  # MAC地址的数字表示
        except:
            machine_id = "fallback_id"
            
        # 组合并返回
        return f"{system_info}:{machine_id}:MystiAide_Secret_Key"

    def verify_login(self, username, user_id):
        """验证保存的登录信息是否有效"""
        try:
            # 向服务器验证用户信息
            verify_url = f"https://www.viqu.com/MystiAide/normal_user/getid.php?name={username}"
            response = requests.get(verify_url)
            
            if response.status_code == 200:
                server_user_id = response.text.strip()
                if server_user_id and server_user_id == user_id:
                    # 登录信息有效
                    self.is_logged_in = True
                    self.update_login_status()
                    self.status_bar.showMessage(f"欢迎回来, {self.user_name}!")
                    print(f"已验证并恢复登录状态: {self.user_name}")
                else:
                    print(f"用户ID验证失败: 本地={user_id}, 服务器={server_user_id}")
                    self.clear_login_state()
            else:
                print(f"验证登录状态失败: {response.status_code}")
                # 如果服务器不可用，仍然使用本地数据
                self.is_logged_in = True
                self.update_login_status()
                self.status_bar.showMessage(f"欢迎回来, {self.user_name}! (离线模式)")
        except Exception as e:
            print(f"验证登录状态时出错: {str(e)}")
            # 如果网络错误，仍然使用本地数据
            self.is_logged_in = True
            self.update_login_status()
            self.status_bar.showMessage(f"欢迎回来, {self.user_name}! (离线模式)")

    def get_secure_config_dir(self):
        """获取安全的配置目录"""
        import os
        
        # 使用AppData目录下的隐藏文件夹
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        # 创建一个看起来像系统目录的路径
        config_dir = os.path.join(app_data, "Microsoft", "Credentials", "SystemData")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_secure_login_file_path(self, config_dir):
        """获取安全的登录文件路径，使用不明显的文件名"""
        import os
        import hashlib
        
        # 使用机器信息的哈希作为文件名的一部分
        machine_hash = hashlib.md5(self.get_machine_info().encode()).hexdigest()[:12]
        # 使用看起来像系统文件的名称
        filename = f"CredentialCache_{machine_hash}.dat"
        return os.path.join(config_dir, filename)