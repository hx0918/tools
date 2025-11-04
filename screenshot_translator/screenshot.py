import os
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyautogui
from datetime import datetime

class SimpleRectangleScreenshot:
    def __init__(self):
        # 初始化变量
        self.root = None
        self.canvas = None
        self.screenshot_image = None
        self.overlay_image = None
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.rect = None
        self.drawing = False
        self.tracking = True
        
        # 截图保存路径
        self.save_path = os.path.expanduser("~/Pictures/Screenshots")
        os.makedirs(self.save_path, exist_ok=True)
        
        # 启动截图流程
        self.start_screenshot()
    
    def get_screen_info(self):
        """获取所有屏幕信息"""
        screens = []
        try:
            import screeninfo
            monitors = screeninfo.get_monitors()
            
            for monitor in monitors:
                screens.append({
                    'bbox': (monitor.x, monitor.y, monitor.x + monitor.width, monitor.y + monitor.height),
                    'width': monitor.width,
                    'height': monitor.height,
                    'x': monitor.x,
                    'y': monitor.y
                })
        except ImportError:
            # 备用方案
            screens.append({
                'bbox': (0, 0, pyautogui.size().width, pyautogui.size().height),
                'width': pyautogui.size().width,
                'height': pyautogui.size().height,
                'x': 0,
                'y': 0
            })
        except Exception as e:
            print(f"获取屏幕信息失败: {e}")
            screens.append({
                'bbox': (0, 0, 1920, 1080),
                'width': 1920,
                'height': 1080,
                'x': 0,
                'y': 0
            })
        
        return screens

    def get_current_screen(self, x, y):
        """根据坐标获取当前所在屏幕"""
        screens = self.get_screen_info()
        
        for screen in screens:
            x1, y1, x2, y2 = screen['bbox']
            if x1 <= x < x2 and y1 <= y < y2:
                return screen
        
        # 默认返回第一个屏幕
        return screens[0]
    
    def create_overlay_image(self, width, height, alpha=0.7):
        """创建半透明覆盖层"""
        return Image.new('RGBA', (width, height), (0, 0, 0, int(255 * alpha)))
    
    def take_screen_screenshot(self, screen_info):
        """截取指定屏幕的截图"""
        bbox = screen_info['bbox']
        try:
            x, y, x2, y2 = bbox
            width = x2 - x
            height = y2 - y
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            return screenshot.convert('RGBA')
        except Exception as e:
            print(f"截图失败: {e}")
            return pyautogui.screenshot().convert('RGBA')
    
    def start_screenshot(self):
        """启动截图流程"""
        time.sleep(0.3)
        
        # 创建主窗口
        self.create_main_window()
        
        # 初始显示当前屏幕
        self.switch_to_current_screen()
        
        # 开始鼠标跟踪
        self.start_mouse_tracking()
    
    def create_main_window(self):
        """创建主窗口"""
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.01)  # 初始几乎透明
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.root, 
            width=100,  # 初始小尺寸，后面会调整
            height=100,
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack()
        
        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", self.cancel_screenshot)
        
        print("截图工具已启动 - 拖动鼠标选择区域，按ESC取消")
    
    def switch_to_current_screen(self):
        """切换到当前鼠标所在屏幕"""
        current_x, current_y = pyautogui.position()
        screen_info = self.get_current_screen(current_x, current_y)
        
        # 截取屏幕截图
        self.screenshot_image = self.take_screen_screenshot(screen_info)
        
        # 创建半透明覆盖层
        self.overlay_image = self.create_overlay_image(screen_info['width'], screen_info['height'])
        
        # 移动窗口到目标屏幕并调整大小
        self.root.geometry(f"{screen_info['width']}x{screen_info['height']}+{screen_info['x']}+{screen_info['y']}")
        print(self.root.geometry())
        self.canvas.config(width=screen_info['width'], height=screen_info['height'])
        
        # 显示内容
        self.root.attributes('-alpha', 0.7)  # 变为半透明
        self.update_display()
        
        print(f"已切换到屏幕 ({screen_info['x']}, {screen_info['y']}) - {screen_info['width']}x{screen_info['height']}")
    
    def start_mouse_tracking(self):
        """开始实时监控鼠标移动"""
        def check_mouse_position():
            if not self.tracking or not self.root:
                return
                
            try:
                current_x, current_y = pyautogui.position()
                current_screen = self.get_current_screen(current_x, current_y)
                
                # 获取当前窗口位置
                window_geometry = self.root.geometry()
                window_x = int(window_geometry.split('+')[1])
                window_y = int(window_geometry.split('+')[2])
                
                # 如果鼠标在不同屏幕，且不在绘制过程中
                if (current_screen['x'] != window_x or current_screen['y'] != window_y) and not self.drawing:
                    self.switch_to_current_screen()
                
                # 继续监控
                if self.tracking:
                    self.root.after(100, check_mouse_position)
                    
            except Exception as e:
                print(f"鼠标监控错误: {e}")
                if self.tracking:
                    self.root.after(100, check_mouse_position)
        
        # 开始监控循环
        self.root.after(100, check_mouse_position)
    
    def update_display(self, rect_coords=None):
        """更新显示"""
        if not self.canvas:
            return
            
        self.canvas.delete("all")
        
        # 显示屏幕截图
        if self.screenshot_image:
            screenshot_photo = ImageTk.PhotoImage(self.screenshot_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=screenshot_photo)
            self.canvas.screenshot_photo = screenshot_photo  # 保持引用
        
        # 显示半透明覆盖层
        if self.overlay_image:
            overlay_photo = ImageTk.PhotoImage(self.overlay_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=overlay_photo)
            self.canvas.overlay_photo = overlay_photo  # 保持引用
        
        # 如果有矩形区域，清除该区域的覆盖层
        if rect_coords and self.screenshot_image:
            x1, y1, x2, y2 = rect_coords
            
            # 在矩形区域显示原图
            cropped_image = self.screenshot_image.crop((x1, y1, x2, y2))
            cropped_photo = ImageTk.PhotoImage(cropped_image)
            self.canvas.create_image(x1, y1, anchor=tk.NW, image=cropped_photo)
            self.canvas.cropped_photo = cropped_photo
            
            # 绘制矩形边框
            self.rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='#FF0000', width=3,
                tags="selection_rect"
            )
    
    def on_button_press(self, event):
        """鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        self.drawing = True
        
        if self.rect:
            self.canvas.delete(self.rect)
    
    def on_mouse_drag(self, event):
        """鼠标拖动事件"""
        if not self.drawing:
            return
            
        self.end_x = event.x
        self.end_y = event.y
        
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        self.update_display((x1, y1, x2, y2))
    
    def on_button_release(self, event):
        """鼠标释放事件"""
        if not self.drawing:
            return
            
        self.drawing = False
        self.end_x = event.x
        self.end_y = event.y
        
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        # 确保区域有效
        if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
            # 获取当前窗口位置（即当前屏幕位置）
            window_geometry = self.root.geometry()
            screen_x = int(window_geometry.split('+')[1])
            screen_y = int(window_geometry.split('+')[2])
            
            # 计算实际截图区域
            bbox = (
                screen_x + x1,
                screen_y + y1,
                x2 - x1,
                y2 - y1
            )
            
            try:
                # 截取选中区域
                region_screenshot = pyautogui.screenshot(region=bbox)
                filepath = self.save_screenshot(region_screenshot)
                
                # 显示成功消息
                self.show_success_message(x1, y1)
                
                # 延迟后关闭
                self.root.after(800, self.cleanup_and_exit)
                return
            except Exception as e:
                print(f"截图失败: {e}")
                self.show_error_message(x1, y1, str(e))
        
        # 如果区域无效，重新开始
        self.update_display()
    
    def show_success_message(self, x, y):
        """显示截图成功消息"""
        self.canvas.create_text(
            x + 60, y + 20,
            text="✓ 截图已保存",
            fill="#00FF00",
            font=("Arial", 12, "bold")
        )
    
    def show_error_message(self, x, y, error_msg):
        """显示错误消息"""
        self.canvas.create_text(
            x + 80, y + 20,
            text=f"✗ {error_msg[:15]}...",
            fill="#FF0000",
            font=("Arial", 10)
        )
    
    def save_screenshot(self, image):
        """保存截图"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.save_path, filename)
        image.save(filepath, "PNG")
        print(f"截图已保存: {filepath}")
        return filepath
    
    def cancel_screenshot(self, event=None):
        """取消截图"""
        self.tracking = False
        self.cleanup_and_exit()
    
    def cleanup_and_exit(self):
        """清理并退出"""
        self.tracking = False
        if self.root:
            self.root.quit()
            self.root.destroy()

def main():
    """主函数"""
    try:
        print("启动简单矩形截图工具...")
        print("使用方法: 拖动鼠标选择区域，按ESC取消")
        print("支持多屏幕 - 鼠标移动到其他屏幕自动切换")
        
        app = SimpleRectangleScreenshot()
        app.root.mainloop()
        
    except ImportError as e:
        print("缺少依赖库，请安装: pip install pyautogui pillow screeninfo")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()