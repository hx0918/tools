# coding: utf-8

import sys
import subprocess
import threading
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QTimer, Qt
from pynput import mouse
import time

class ScreenshotTranslatorTray:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 脚本路径
        self.script_path = Path("C:/MY_SPACE/Sources/tools/screenshot_translator/combine.py")
        self.last_click_time = 0
        self.click_delay = 1.0
        
        # 鼠标监听器
        self.mouse_listener = None
        self.listening = False
        
        self.setup_tray()
    
    def setup_tray(self):
        """设置系统托盘"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon()
        
        # 加载图标
        icon_path = Path(__file__).parent / "icon.png"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.tray_icon.setIcon(icon)

            # 检查图标是否有效
            if icon.isNull():
                print("警告: 图标加载失败，可能格式不支持")
            else:
                print("图标加载成功")

            # 同时设置应用程序图标
            self.app.setWindowIcon(icon)
            print(f"使用自定义图标: {icon_path}")
        else:
            # 备用方案
            print("未找到 icon.png，使用默认图标")
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.blue)
            icon = QIcon(pixmap)
            self.tray_icon.setIcon(icon)
            self.app.setWindowIcon(icon)
        
        self.tray_icon.setToolTip("截图翻译工具 - 按鼠标中键截图翻译")
        
        # 创建右键菜单
        self.setup_context_menu()
        
        # 连接信号
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def setup_context_menu(self):
        """设置右键菜单"""
        menu = QMenu()
        
        # 手动启动翻译
        start_action = QAction("手动截图翻译", self.app)
        start_action.triggered.connect(self.start_translation_manual)
        menu.addAction(start_action)
        
        menu.addSeparator()
        
        # 监听状态
        self.listen_action = QAction("监听已启动", self.app)
        self.listen_action.setCheckable(True)
        self.listen_action.setChecked(True)
        self.listen_action.triggered.connect(self.toggle_listening)
        menu.addAction(self.listen_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def on_tray_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.start_translation_manual()
    
    def start_mouse_listener(self):
        """启动鼠标监听"""
        def on_click(x, y, button, pressed):
            if button == mouse.Button.middle and pressed:  # 鼠标中键按下
                current_time = time.time()
                if current_time - self.last_click_time < self.click_delay:
                    return
                
                self.last_click_time = current_time
                print("检测到鼠标中键，启动截图翻译...")
                self.start_translation()
        
        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()
        self.listening = True
        self.update_listen_status()
    
    def stop_mouse_listener(self):
        """停止鼠标监听"""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        self.listening = False
        self.update_listen_status()
    
    def toggle_listening(self):
        """切换监听状态"""
        if self.listening:
            self.stop_mouse_listener()
        else:
            self.start_mouse_listener()
    
    def update_listen_status(self):
        """更新监听状态显示"""
        if self.listening:
            self.listen_action.setText("监听已启动")
            self.tray_icon.setToolTip("截图翻译工具 - 按鼠标中键截图翻译")
            # self.tray_icon.showMessage("监听启动", "鼠标中键监听已启动", QSystemTrayIcon.Information, 2000)
        else:
            self.listen_action.setText("监听已停止")
            self.tray_icon.setToolTip("截图翻译工具 - 监听已停止")
    
    def start_translation(self):
        """启动翻译流程（在后台线程中）"""
        def run_translation():
            try:
                result = subprocess.run([
                    sys.executable, str(self.script_path)
                ], capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode == 0:
                    self.tray_icon.showMessage("翻译完成", "截图翻译成功完成", QSystemTrayIcon.Information, 1000)
                else:
                    self.tray_icon.showMessage("翻译失败", "截图翻译失败", QSystemTrayIcon.Critical, 1000)
                    
            except subprocess.TimeoutExpired:
                self.tray_icon.showMessage("翻译超时", "截图翻译流程超时", QSystemTrayIcon.Warning, 1000)
            except Exception as e:
                self.tray_icon.showMessage("错误", f"启动失败: {str(e)}", QSystemTrayIcon.Critical, 1000)
        
        thread = threading.Thread(target=run_translation)
        thread.daemon = True
        thread.start()
    
    def start_translation_manual(self):
        """手动启动翻译"""
        self.tray_icon.showMessage("启动翻译", "开始截图翻译流程...", QSystemTrayIcon.Information, 1000)
        self.start_translation()
    
    def quit_app(self):
        """退出应用程序"""
        self.stop_mouse_listener()
        self.tray_icon.hide()
        self.app.quit()
    
    def run(self):
        """运行应用程序"""
        # 显示托盘图标
        self.tray_icon.show()
        
        # 启动鼠标监听
        self.start_mouse_listener()
        
        # 显示启动消息
        # self.tray_icon.showMessage(
        #     "截图翻译工具", 
        #     "程序已启动到系统托盘，按鼠标中键截图翻译", 
        #     QSystemTrayIcon.Information, 
        #     1000
        # )
        
        print("截图翻译工具已启动到系统托盘")
        print("按鼠标中键即可截图翻译")
        print("右键点击托盘图标查看更多选项")
        
        # 运行应用
        sys.exit(self.app.exec_())

def main():
    """主函数"""
    # 检查依赖
    try:
        from pynput import mouse
    except ImportError:
        print("错误：缺少 pynput 库，请安装:")
        print("pip install pynput")
        sys.exit(1)
    
    # 检查主脚本
    script_path = Path("C:/MY_SPACE/Sources/tools/screenshot_translator/screenshot_translator.py")
    if not script_path.exists():
        print(f"错误：主脚本不存在: {script_path}")
        sys.exit(1)
    
    # 创建并运行托盘应用
    tray_app = ScreenshotTranslatorTray()
    tray_app.run()

if __name__ == "__main__":
    main()