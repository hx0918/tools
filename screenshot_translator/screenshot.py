import os
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyautogui
from datetime import datetime

class RectangleScreenshot:
    def __init__(self):
        # 初始化变量
        self.root = None
        self.canvas = None
        self.screenshot_image = None
        self.screenshot_photo = None
        self.overlay_image = None
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.rect = None
        self.current_screen = None
        self.screen_info = None
        self.drawing = False
        
        # 截图保存路径
        self.save_path = os.path.expanduser("~/Pictures/Screenshots")
        os.makedirs(self.save_path, exist_ok=True)
        
        # 启动截图流程
        self.start_screenshot()
    
    def get_screen_info(self):
        """获取所有屏幕信息（修复多屏幕支持）"""
        screens = []
        try:
            # 使用tkinter获取多屏幕信息
            temp_root = tk.Tk()
            temp_root.withdraw()
            
            # 获取所有屏幕信息
            for i in range(temp_root.winfo_screenwidth()):
                try:
                    width = temp_root.winfo_screenwidth()
                    height = temp_root.winfo_screenheight()
                    # 简单的多屏幕检测 - 实际应该使用更复杂的方法
                    screens.append({
                        'bbox': (0, 0, width, height),
                        'width': width,
                        'height': height
                    })
                    break
                except:
                    break
            
            temp_root.destroy()
            
            # 如果没有检测到屏幕，使用pyautogui的默认方法
            if not screens:
                screens.append({
                    'bbox': (0, 0, pyautogui.size().width, pyautogui.size().height),
                    'width': pyautogui.size().width,
                    'height': pyautogui.size().height
                })
                
        except Exception as e:
            print(f"获取屏幕信息失败: {e}")
            # 备用方案
            screens.append({
                'bbox': (0, 0, 1920, 1080),  # 默认分辨率
                'width': 1920,
                'height': 1080
            })
        return screens
    
    def get_screen_info2(self):
        """使用screeninfo获取所有屏幕信息"""
        screens = []
        try:
            import screeninfo
            monitors = screeninfo.get_monitors()
            
            for i, monitor in enumerate(monitors):
                screens.append({
                    'bbox': (monitor.x, monitor.y, monitor.x + monitor.width, monitor.y + monitor.height),
                    'width': monitor.width,
                    'height': monitor.height,
                    'x': monitor.x,
                    'y': monitor.y
                })
            
            # 如果没有检测到屏幕，使用备用方案
            if not screens:
                screens.append({
                    'bbox': (0, 0, pyautogui.size().width, pyautogui.size().height),
                    'width': pyautogui.size().width,
                    'height': pyautogui.size().height,
                    'x': 0,
                    'y': 0
                })
                
        except ImportError:
            print("未安装screeninfo库，使用备用屏幕检测方法")
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
            # 最终备用方案
            screens.append({
                'bbox': (0, 0, 1920, 1080),
                'width': 1920,
                'height': 1080,
                'x': 0,
                'y': 0
            })
        
        return screens

    def get_current_screen(self, x, y):
        """根据坐标获取当前所在屏幕（使用screeninfo）"""

        print(f"获取当前屏幕，坐标: ({x}, {y})")
        screens = self.get_screen_info()
        print("1")
        print(screens)
        screens = self.get_screen_info2()
        print("2")
        print(screens)
        
        for i, screen in enumerate(screens):
            x1, y1, x2, y2 = screen['bbox']
            # 检查坐标是否在当前屏幕范围内
            if x1 <= x < x2 and y1 <= y < y2:
                return i, screen
        
        # 如果没有找到匹配的屏幕，返回第一个屏幕
        return 0, screens[0]

    def create_overlay_image(self, width, height, alpha=0.8):
        """创建半透明覆盖层"""
        # 创建深色半透明图像
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, int(255 * alpha)))
        return overlay
    
    def take_screen_screenshot(self, screen_info):
        """截取指定屏幕的截图"""
        bbox = screen_info['bbox']
        try:
            screenshot = pyautogui.screenshot(region=bbox)
            return screenshot.convert('RGBA')
        except Exception as e:
            print(f"截图失败: {e}")
            # 备用方案：截取整个屏幕
            return pyautogui.screenshot().convert('RGBA')
    
    def start_screenshot(self):
        """启动截图流程"""
        # 短暂延迟，确保之前的UI操作完成
        time.sleep(0.3)
        
        # 获取当前鼠标位置和所在屏幕
        current_x, current_y = pyautogui.position()
        screen_index, screen_info = self.get_current_screen(current_x, current_y)
        self.current_screen = screen_index
        self.screen_info = screen_info
        
        # 创建GUI界面
        self.create_gui()
    
    def create_gui(self):
        """创建截图界面"""
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.3)  # 初始半透明
        
        # 获取屏幕尺寸
        screen_width = self.screen_info['width']
        screen_height = self.screen_info['height']
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.root, 
            width=screen_width, 
            height=screen_height,
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack()
        
        # 截取屏幕截图
        self.screenshot_image = self.take_screen_screenshot(self.screen_info)
        
        # 创建半透明覆盖层
        self.overlay_image = self.create_overlay_image(screen_width, screen_height)
        
        # 显示截图和覆盖层
        self.update_display()
        
        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", self.cancel_screenshot)
        self.root.bind("<KeyPress>", self.on_key_press)
        
        # 设置窗口位置
        x, y, _, _ = self.screen_info['bbox']
        self.root.geometry(f"{screen_width}x{screen_height}+{x}+{y}")
        
        # 显示窗口并获取焦点
        self.root.focus_force()
        self.canvas.focus_set()
    
    def update_display(self, rect_coords=None):
        """更新显示，包括矩形选择区域"""
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
            
            # 在矩形区域显示原图（通过创建一个"窗口"来实现）
            cropped_image = self.screenshot_image.crop((x1, y1, x2, y2))
            cropped_photo = ImageTk.PhotoImage(cropped_image)
            
            self.canvas.create_image(x1, y1, anchor=tk.NW, image=cropped_photo)
            self.canvas.cropped_photo = cropped_photo  # 保持引用
            
            # 绘制矩形边框
            self.rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='#FF0000', width=2,
                tags="selection_rect"
            )
    
    def on_button_press(self, event):
        """鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        self.drawing = True
        
        # 移除之前的矩形
        if self.rect:
            self.canvas.delete(self.rect)
    
    def on_mouse_drag(self, event):
        """鼠标拖动事件"""
        if not self.drawing:
            return
            
        self.end_x = max(0, min(event.x, self.screen_info['width']))
        self.end_y = max(0, min(event.y, self.screen_info['height']))
        
        # 确保坐标正确
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        # 更新显示
        self.update_display((x1, y1, x2, y2))
    
    def on_button_release(self, event):
        """鼠标释放事件"""
        if not self.drawing:
            return
            
        self.drawing = False
        self.end_x = max(0, min(event.x, self.screen_info['width']))
        self.end_y = max(0, min(event.y, self.screen_info['height']))
        
        # 确保坐标正确
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        # 确保区域有效
        if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
            # 截取矩形区域
            screen_x, screen_y, _, _ = self.screen_info['bbox']
            bbox = (
                screen_x + x1,
                screen_y + y1,
                x2 - x1,  # 宽度
                y2 - y1   # 高度
            )
            
            try:
                # 截取选中区域
                region_screenshot = pyautogui.screenshot(region=bbox)
                self.save_screenshot(region_screenshot)
                
                # 显示成功消息
                self.show_success_message(x1, y1)
                
                # 延迟后关闭
                self.root.after(800, self.root.destroy)
                return
            except Exception as e:
                print(f"截图失败: {e}")
                self.show_error_message(x1, y1, str(e))
        
        # 如果区域无效，重新开始
        self.update_display()
    
    def show_success_message(self, x, y):
        """显示截图成功消息"""
        success_text = "✓ 截图已保存"
        self.canvas.create_text(
            x + 60, y + 20,
            text=success_text,
            fill="#00FF00",
            font=("Arial", 12, "bold"),
            tags="success_msg"
        )
    
    def show_error_message(self, x, y, error_msg):
        """显示错误消息"""
        error_text = f"✗ 失败: {error_msg}"
        self.canvas.create_text(
            x + 80, y + 20,
            text=error_text,
            fill="#FF0000",
            font=("Arial", 10),
            tags="error_msg"
        )
    
    def save_screenshot(self, image):
        """保存截图"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.save_path, filename)
        image.save(filepath, "PNG")
        print(f"截图已保存: {filepath}")
        return filepath
    
    def on_key_press(self, event):
        """键盘事件处理"""
        if event.keysym == 'Escape':
            self.cancel_screenshot()
    
    def cancel_screenshot(self, event=None):
        """取消截图"""
        if self.root:
            self.root.destroy()

def main():
    """主函数"""
    try:
        # 检查依赖
        import pyautogui
        from PIL import Image, ImageTk
        
        print("启动矩形截图工具...")
        print("使用方法:")
        print("1. 鼠标拖动选择区域")
        print("2. 释放鼠标完成截图")
        print("3. 按ESC取消截图")
        
        # 启动截图工具
        app = RectangleScreenshot()
        
        # 运行主循环
        if app.root:
            app.root.mainloop()
            
    except ImportError as e:
        print("缺少必要的依赖库，请安装：")
        print("pip install pyautogui pillow")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()