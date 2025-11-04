import sys
import os
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel)
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import (QPixmap, QPainter, QPen, QColor, QCursor, QScreen)
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
import pyautogui

class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化变量
        self.start_pos = None
        self.end_pos = None
        self.drawing = False
        self.selection_rect = None
        self.current_screen = None
        self.screenshot_pixmap = None
        self.overlay_color = QColor(0, 0, 0, 100)
            
        # 初始化退出码为-1（默认失败）
        self.exit_code = -1

        # 截图保存路径
        self.save_path = r"C:/MY_SPACE/Sources/tools/screenshot_translator/temp"
        os.makedirs(self.save_path, exist_ok=True)
        
        print("截图工具初始化...")
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始设置
        self.label = QLabel(self)
        self.switch_to_current_screen()
        
        print("截图工具已启动 - 拖动选择区域，ESC取消")
        
        # 启动鼠标跟踪
        self.start_mouse_tracking()
        
        # 强制激活窗口和设置焦点
        QTimer.singleShot(100, self.force_focus)

    def force_focus(self):
        """强制获取焦点"""
        self.activateWindow()
        self.raise_()
        self.setFocus()
        print("窗口已激活并获取焦点")

    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_Escape:
            print("ESC pressed - 截图取消")
            self.safe_exit(-1)
            event.accept()
        else:
            super().keyPressEvent(event)

    def get_current_screen(self):
        """获取当前鼠标所在的屏幕"""
        cursor_pos = QCursor.pos()
        return QApplication.screenAt(cursor_pos) or QApplication.primaryScreen()
    
    def switch_to_current_screen(self):
        new_screen = self.get_current_screen()
        
        if new_screen != self.current_screen:
            # 只需要清空显示即可
            self.label.clear()
            self.current_screen = new_screen
            
            # 短暂延迟后执行切换
            QTimer.singleShot(50, lambda: self.delayed_screen_switch(new_screen))

    def delayed_screen_switch(self, new_screen):
        screen_geometry = new_screen.geometry()
        self.setGeometry(screen_geometry)
        self.capture_screen()
        # print(f"🖥️ 切换到屏幕: {screen_geometry.x()}, {screen_geometry.y()}")
        self.update_display()
        # 切换屏幕后重新获取焦点
        self.setFocus()
        
    def capture_screen(self):
        """截取当前屏幕"""
        if self.current_screen:
            self.screenshot_pixmap = self.current_screen.grabWindow(0)
    
    def start_mouse_tracking(self):
        """开始鼠标位置跟踪"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_mouse_position)
        self.timer.start(100)
    
    def check_mouse_position(self):
        """检查鼠标位置，处理屏幕切换"""
        if not self.drawing:
            self.switch_to_current_screen()
    
    def update_display(self, selection_rect=None):
        """更新显示"""
        if not self.screenshot_pixmap:
            return
            
        display_pixmap = self.screenshot_pixmap.copy()
        painter = QPainter(display_pixmap)
        painter.fillRect(display_pixmap.rect(), self.overlay_color)
        
        if selection_rect:
            painter.drawPixmap(selection_rect, self.screenshot_pixmap, selection_rect)
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawRect(selection_rect)
        
        painter.end()
        self.label.setPixmap(display_pixmap)
        self.label.setGeometry(self.rect())
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.drawing = True
            self.selection_rect = QRect(self.start_pos, self.end_pos)
            self.update_display(self.selection_rect)
    
    def mouseMoveEvent(self, event):
        if self.drawing and self.start_pos:
            self.end_pos = event.pos()
            x1 = min(self.start_pos.x(), self.end_pos.x())
            y1 = min(self.start_pos.y(), self.end_pos.y())
            x2 = max(self.start_pos.x(), self.end_pos.x())
            y2 = max(self.start_pos.y(), self.end_pos.y())
            self.selection_rect = QRect(QPoint(x1, y1), QPoint(x2, y2))
            self.update_display(self.selection_rect)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            self.end_pos = event.pos()
            
            x1 = min(self.start_pos.x(), self.end_pos.x())
            y1 = min(self.start_pos.y(), self.end_pos.y())
            x2 = max(self.start_pos.x(), self.end_pos.x())
            y2 = max(self.start_pos.y(), self.end_pos.y())
            selection_rect = QRect(QPoint(x1, y1), QPoint(x2, y2))
            
            if selection_rect.width() > 10 and selection_rect.height() > 10:
                self.capture_selected_area(selection_rect)
            else:
                self.update_display()
    
    def capture_selected_area(self, selection_rect):
        """从全屏截图中截取选定区域"""
        try:
            
            # 将 QPixmap 转换为 QImage，然后截取区域
            screenshot_image = self.screenshot_pixmap.toImage()
            
            # 截取选定区域
            cropped_image = screenshot_image.copy(
                selection_rect.x(),
                selection_rect.y(), 
                selection_rect.width(),
                selection_rect.height()
            )
            
            # 转换为 PIL Image 用于保存
            cropped_pixmap = QPixmap.fromImage(cropped_image)
            
            # 保存截图
            filepath = self.save_screenshot(cropped_pixmap)
            self.safe_exit(0)
            
        except Exception as e:
            print(f"截图失败: {e}")
            # 失败返回-1
            self.safe_exit(-1)

    def safe_exit(self, exit_code=0):
        """安全退出程序"""
        print("安全退出程序")
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        # 设置退出码
        self.exit_code = exit_code
        
        self.close()
        QApplication.quit()
    
    def save_screenshot(self, image):
        """保存截图"""
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"screenshot_{timestamp}.png"
        # filepath = os.path.join(self.save_path, filename)
        filepath = r"C:\MY_SPACE\Sources\tools\screenshot_translator\temp\screenshot.png"
        image.save(filepath, "PNG")
        print(f"截图已保存: {filepath}")
        return filepath
    
    def show_success_message(self, position):
        success_pixmap = self.screenshot_pixmap.copy()
        painter = QPainter(success_pixmap)
        painter.fillRect(success_pixmap.rect(), QColor(0, 0, 0, 100))
        painter.setPen(QColor(0, 255, 0))
        painter.drawText(position + QPoint(60, 30), "截图已保存")
        painter.end()
        self.label.setPixmap(success_pixmap)
    
    def show_error_message(self, position, error_msg):
        error_pixmap = self.screenshot_pixmap.copy()
        painter = QPainter(error_pixmap)
        painter.fillRect(error_pixmap.rect(), QColor(0, 0, 0, 100))
        painter.setPen(QColor(255, 0, 0))
        painter.drawText(position + QPoint(80, 30), f"✗ {error_msg[:20]}...")
        painter.end()
        self.label.setPixmap(error_pixmap)

def main():
    """主函数 - 简化版本"""
    try:
        print("启动截图工具...")
        app = QApplication(sys.argv)
        
        # 创建并显示窗口
        tool = ScreenshotTool()
        tool.show()
        
        # 运行应用
        result = app.exec_()
        
        # 获取退出码
        exit_code = getattr(tool, 'exit_code', -1)
        print(f"应用退出代码: {exit_code}")
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(-1)

if __name__ == "__main__":
    main()