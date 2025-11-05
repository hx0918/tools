# coding: utf-8

import sys
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import io

if sys.stdout.encoding != 'utf-8':
    print(sys.stdout.encoding, file=sys.stderr)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class TranslationThread(QThread):
    """翻译线程，避免界面卡顿"""
    finished = pyqtSignal(str, bool)  # 信号：翻译结果, 是否成功
    
    def __init__(self, text, source_lang, target_lang):
        super().__init__()
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang
    
    def run(self):
        try:
            # 调用 translate_client.py
            script_path = Path("C:/MY_SPACE/Sources/tools/screenshot_translator/translate_client.py")
            
            result = subprocess.run([
                sys.executable, str(script_path), self.text
            ], capture_output=True, text=True, encoding='utf-8') #, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout.strip())
                self.finished.emit(result.stdout.strip(), True)
            else:
                error_msg = result.stderr.strip() if result.stderr else "翻译失败"
                self.finished.emit(error_msg, False)
                
        except subprocess.TimeoutExpired:
            self.finished.emit("翻译超时", False)
        except Exception as e:
            self.finished.emit(f"翻译错误: {str(e)}", False)

class TranslationApp(QMainWindow):
    def __init__(self, initial_src_text="", initial_rst_text=""):
        super().__init__()
        self.initial_src_text = initial_src_text
        self.initial_rst_text = initial_rst_text
        self.translation_thread = None
        self.init_ui()
            
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("翻译工具")
        self.setFixedSize(800, 600)
        
        # 居中显示
        self.center_window()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 左右两列
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 左列 - 文本框区域
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        
        # 原文文本框
        self.source_text = QTextEdit()
        self.source_text.setPlainText(self.initial_src_text)
        self.source_text.setFont(QFont("Arial", 11))
        self.source_text.setPlaceholderText("请输入要翻译的文本...")
        left_layout.addWidget(self.source_text)
        
        # 译文文本框
        self.target_text = QTextEdit()
        self.target_text.setPlainText(self.initial_rst_text)
        self.target_text.setFont(QFont("微软雅黑", 11))
        self.target_text.setReadOnly(True)
        self.target_text.setPlaceholderText("翻译结果将显示在这里...")
        left_layout.addWidget(self.target_text)
        
        # 右列 - 控制区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加弹性空间来定位控件
        # 源语言下拉菜单 - 在竖直高度1/4处
        right_width = 80
        right_layout.addStretch(1)  # 上部1/4空间
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(["英文", "中文", "日文"])
        self.source_combo.setCurrentText("英文")
        self.source_combo.setFixedWidth(right_width)
        right_layout.addWidget(self.source_combo)
        
        # 翻译按钮 - 在竖直方向中间
        right_layout.addStretch(1)  # 中间1/2空间
        
        self.translate_btn = QPushButton("翻译")
        self.translate_btn.setFixedSize(right_width, 40)
        self.translate_btn.clicked.connect(self.start_translation)
        right_layout.addWidget(self.translate_btn)
        
        # 目标语言下拉菜单 - 在竖直高度3/4处
        right_layout.addStretch(1)  # 下部1/4空间
        
        self.target_combo = QComboBox()
        self.target_combo.addItems(["中文", "英文", "日文"])
        self.target_combo.setCurrentText("中文")
        self.target_combo.setFixedWidth(right_width)
        right_layout.addWidget(self.target_combo)
        
        right_layout.addStretch(1)  # 底部空间
        
        # 将左右布局添加到主布局
        main_layout.addLayout(left_layout, 6)  # 左列占4份
        main_layout.addWidget(right_widget, 1)  # 右列占1份
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def center_window(self):
        """窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def start_translation(self):
        """开始翻译"""
        text = self.source_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "警告", "请输入要翻译的文本")
            return
        
        # 获取语言选择
        source_lang = self.source_combo.currentText()
        target_lang = self.target_combo.currentText()
        
        if source_lang == target_lang:
            QMessageBox.warning(self, "警告", "源语言和目标语言不能相同")
            return
        
        # 禁用按钮，避免重复点击
        self.translate_btn.setEnabled(False)
        self.statusBar().showMessage("翻译中...")
        
        # 启动翻译线程
        self.translation_thread = TranslationThread(text, source_lang, target_lang)
        self.translation_thread.finished.connect(self.on_translation_finished)
        self.translation_thread.start()
    
    def on_translation_finished(self, result, success):
        """翻译完成回调"""
        self.translate_btn.setEnabled(True)
        
        if success:
            self.target_text.setPlainText(result)
            self.statusBar().showMessage("翻译完成")
        else:
            self.target_text.setPlainText("")
            QMessageBox.critical(self, "错误", result)
            self.statusBar().showMessage("翻译失败")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.translation_thread and self.translation_thread.isRunning():
            self.translation_thread.terminate()
            self.translation_thread.wait()
        event.accept()

def main():
    """主函数 - 从固定临时文件读取"""
    temp_dir = Path("C:/MY_SPACE/Sources/tools/screenshot_translator/temp")
    source_file = temp_dir / "translation_source.txt"
    target_file = temp_dir / "translation_target.txt"
    
    source_text = ""
    target_text = ""
    
    # 读取原文
    if source_file.exists():
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                source_text = f.read().strip()
        except Exception as e:
            print(f"读取原文文件失败: {e}")
    
    # 读取译文
    if target_file.exists():
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                target_text = f.read().strip()
        except Exception as e:
            print(f"读取译文文件失败: {e}")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TranslationApp(source_text, target_text)
    window.show()
    
    # 存储应用实例以便获取结果
    result = app.exec_()
    
    # 检查是否有翻译结果
    # if window.target_text.toPlainText().strip():
    #     print("翻译完成")
    #     return 0
    # else:
    #     print("翻译未完成或用户取消")
    #     return -1
    return 0

if __name__ == "__main__":
    main()