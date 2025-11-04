import sys
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QComboBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

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
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.finished.emit(result.stdout.strip(), True)
            else:
                error_msg = result.stderr.strip() if result.stderr else "翻译失败"
                self.finished.emit(error_msg, False)
                
        except subprocess.TimeoutExpired:
            self.finished.emit("翻译超时", False)
        except Exception as e:
            self.finished.emit(f"翻译错误: {str(e)}", False)

class TranslationApp(QMainWindow):
    def __init__(self, initial_text=""):
        super().__init__()
        self.initial_text = initial_text
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
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 源语言选择
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("源语言:"))
        self.source_combo = QComboBox()
        self.source_combo.addItems(["英文", "中文", "日文"])
        self.source_combo.setCurrentText("英文")
        source_layout.addWidget(self.source_combo)
        source_layout.addStretch()
        main_layout.addLayout(source_layout)
        
        # 原文文本框
        main_layout.addWidget(QLabel("原文:"))
        self.source_text = QTextEdit()
        self.source_text.setPlainText(self.initial_text)
        self.source_text.setFont(QFont("Arial", 11))
        main_layout.addWidget(self.source_text)
        
        # 翻译按钮和目标语言选择
        button_layout = QHBoxLayout()
        
        # 目标语言选择
        button_layout.addWidget(QLabel("目标语言:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(["中文", "英文", "日文"])
        self.target_combo.setCurrentText("中文")
        button_layout.addWidget(self.target_combo)
        
        button_layout.addStretch()
        
        # 翻译按钮
        self.translate_btn = QPushButton("翻译")
        self.translate_btn.setFixedSize(100, 40)
        self.translate_btn.clicked.connect(self.start_translation)
        button_layout.addWidget(self.translate_btn)
        
        main_layout.addLayout(button_layout)
        
        # 译文文本框
        main_layout.addWidget(QLabel("译文:"))
        self.target_text = QTextEdit()
        self.target_text.setFont(QFont("微软雅黑", 11))
        self.target_text.setReadOnly(True)
        main_layout.addWidget(self.target_text)
        
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
    """主函数"""
    # 获取命令行参数
    initial_text = ""
    if len(sys.argv) > 1:
        initial_text = " ".join(sys.argv[1:])
    
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = TranslationApp(initial_text)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()