import sys
import os
import shutil
import winreg
import ctypes
from PyQt5.QtWidgets import QApplication
from ui.main_window import MystiAideApp


if __name__ == "__main__":

    # 启动主应用程序
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MystiAideApp()
    window.show()
    sys.exit(app.exec_())