import sys
import subprocess
from pathlib import Path
from pynput import mouse
import threading
import time

class MouseWheelListener:
    def __init__(self):
        self.running = False
        self.listener = None
        self.script_path = Path("C:/MY_SPACE/Sources/tools/screenshot_translator/combine.py")
        self.last_click_time = 0
        self.click_delay = 1.0  # 防止连续点击的最小间隔（秒）
    
    def on_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if button == mouse.Button.middle and pressed:  # 鼠标中键按下
            current_time = time.time()
            if current_time - self.last_click_time < self.click_delay:
                return  # 防止连续点击
            
            self.last_click_time = current_time
            print(f"\n🎯 鼠标滚轮按下，启动截图翻译...")
            
            # 在新线程中启动翻译流程，避免阻塞监听
            thread = threading.Thread(target=self.start_translation)
            thread.daemon = True
            thread.start()
    
    def start_translation(self):
        """启动翻译流程"""
        try:
            print("🚀 启动截图翻译流程...")
            result = subprocess.run([
                sys.executable, str(self.script_path)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ 截图翻译完成!")
            else:
                print(f"❌ 翻译失败，退出码: {result.returncode}")
                if result.stderr:
                    print(f"错误信息: {result.stderr.strip()}")
                    
        except subprocess.TimeoutExpired:
            print("❌ 翻译流程超时")
        except Exception as e:
            print(f"❌ 启动翻译失败: {e}")
    
    def start_listening(self):
        """开始监听鼠标事件"""
        print("=" * 50)
        print("🖱️  鼠标滚轮监听器已启动")
        print("📌 使用说明:")
        print("   - 按下鼠标滚轮（中键）开始截图翻译")
        print("   - 确保已启动 ocr_translate_server.py")
        print("   - 按 Ctrl+C 停止监听")
        print("=" * 50)
        
        self.running = True
        
        # 创建鼠标监听器
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        
        try:
            # 保持主线程运行
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 用户中断，停止监听...")
        finally:
            self.stop_listening()
    
    def stop_listening(self):
        """停止监听"""
        self.running = False
        if self.listener:
            self.listener.stop()
        print("🎯 鼠标监听器已停止")

def check_dependencies():
    """检查依赖"""
    try:
        import pynput
        return True
    except ImportError:
        print("❌ 缺少 pynput 库，请安装:")
        print("pip install pynput")
        return False

def main():
    """主函数"""
    if not check_dependencies():
        sys.exit(1)
    
    # 检查主脚本是否存在
    script_path = Path("C:/MY_SPACE/Sources/tools/screenshot_translator/combine.py")
    if not script_path.exists():
        print(f"❌ 主脚本不存在: {script_path}")
        print("请确保 combine.py 在正确的位置")
        sys.exit(1)
    
    print("🔍 检查服务器状态...")
    # 这里可以添加服务器状态检查逻辑
    print("⚠️  请确保已手动启动: python ocr_translate_server.py")
    
    listener = MouseWheelListener()
    listener.start_listening()

if __name__ == "__main__":
    main()