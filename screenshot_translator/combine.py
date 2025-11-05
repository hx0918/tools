# coding: utf-8

import sys
import os
import subprocess
import time
from pathlib import Path
import io

if sys.stdout.encoding != 'utf-8':
    print(sys.stdout.encoding, file=sys.stderr)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class ScreenshotTranslator:
    def __init__(self):
        self.base_dir = Path("C:/MY_SPACE/Sources/tools/screenshot_translator")
        self.temp_dir = self.base_dir / "temp"
        self.screenshot_path = self.temp_dir / "screenshot.png"
        self.ocr_result_path = self.temp_dir / "ocr.txt"
        self.pre_result = None
        
        # 确保目录存在
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def run_command(self, command, description=""):
        """运行命令并返回退出码和输出"""
        if description:
            # print(f"\n{description}", file=sys.stderr)
            print(f"执行命令: {' '.join(command)}", file=sys.stderr)
            pass
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=30)
            
            # if result.stdout:
            #     print(f"输出:\n{result.stdout.strip()}", file=sys.stderr)
            # if result.stderr:
            #     print(f"log:\n{result.stderr.strip()}", file=sys.stderr)
            
            # print(f"退出码: {result.returncode}", file=sys.stderr)
            return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
            
        except subprocess.TimeoutExpired:
            print("命令执行超时", file=sys.stderr)
            return -1
        except Exception as e:
            print(f"执行命令失败: {e}", file=sys.stderr)
            return -1
    
    def run_command_no_timeout(self, command, description=""):
        """运行命令并返回退出码和输出"""
        if description:
            # print(f"\n{description}", file=sys.stderr)
            print(f"执行命令: {' '.join(command)}", file=sys.stderr)
            pass
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            
            # if result.stdout:
            #     print(f"输出:\n{result.stdout.strip()}", file=sys.stderr)
            # if result.stderr:
            #     print(f"log:\n{result.stderr.strip()}", file=sys.stderr)
            
            # print(f"退出码: {result.returncode}", file=sys.stderr)
            return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
            
        except subprocess.TimeoutExpired:
            print("命令执行超时", file=sys.stderr)
            return -1
        except Exception as e:
            print(f"执行命令失败: {e}", file=sys.stderr)
            return -1
    
    def step1_screenshot(self):
        """步骤1: 截图"""
        print("=" * 50)
        print("步骤1: 开始截图")
        print("=" * 50)
        
        qtshot_script = self.base_dir / "qtshot.py"
        if not qtshot_script.exists():
            print(f"截图脚本不存在: {qtshot_script}", file=sys.stderr)
            return -1
        
        result = self.run_command(
            [sys.executable, str(qtshot_script)],
            "启动截图工具"
        )
        self.pre_result = result
        
        if result["returncode"] == 0:
            if self.screenshot_path.exists():
                file_size = self.screenshot_path.stat().st_size
                print(f"截图成功: {self.screenshot_path} ({file_size} 字节)", file=sys.stderr)
                return 0
            else:
                print("截图文件不存在", file=sys.stderr)
                return -1
        else:
            print("截图失败或用户取消", file=sys.stderr)
            return -1
    
    def step2_ocr(self):
        """步骤2: OCR识别"""
        print("=" * 50)
        print("步骤2: OCR文字识别", file=sys.stderr)
        print("=" * 50)
        
        ocr_client_script = self.base_dir / "ocr_client.py"
        if not ocr_client_script.exists():
            print(f"OCR客户端脚本不存在: {ocr_client_script}", file=sys.stderr)
            return -1
        
        if not self.screenshot_path.exists():
            print("截图文件不存在，无法进行OCR", file=sys.stderr)
            return -1
        
        result = self.run_command(
            [sys.executable, str(ocr_client_script), str(self.screenshot_path)],
            "执行OCR识别"
        )
        self.pre_result = result
        
        if result["returncode"] == 0:
            ocr_text = result["stdout"].strip()
            print(f"OCR成功: 识别到 {len(ocr_text)} 个字符", file=sys.stderr)
            print(f"识别结果: {ocr_text[:100]}{'...' if len(ocr_text) > 100 else ''}", file=sys.stderr)
            return 0
        else:
            print("OCR识别失败", file=sys.stderr)
            return -1
    
    def step3_translate(self, ocr_text):
        """步骤3: 翻译"""
        print("=" * 50, file=sys.stderr)
        print("步骤3: 文本翻译", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        
        translate_client_script = self.base_dir / "translate_client.py"
        if not translate_client_script.exists():
            print(f"翻译客户端脚本不存在: {translate_client_script}", file=sys.stderr)
            return -1
               
        result = self.run_command(
            [sys.executable, str(translate_client_script), ocr_text],
            "执行翻译"
        )
        self.pre_result = result
        
        if result["returncode"] == 0:
            print("翻译成功", file=sys.stderr)
            print(result["stdout"].strip(), file=sys.stderr)
            return 0
        else:
            print("翻译失败", file=sys.stderr)
            return -1
    
    def step4_show(self):
        """步骤4: 显示结果"""
        print("=" * 50, file=sys.stderr)
        print("步骤4: 显示翻译结果", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        
        gui_script = self.base_dir / "translate_gui.py"
        result = self.run_command_no_timeout(
            [sys.executable, str(gui_script)],
            "执行显示结果"
        )
        self.pre_result = result
        
        if result["returncode"] == 0:
            print("显示成功", file=sys.stderr)
            print(result["stdout"].strip(), file=sys.stderr)
            return 0
        else:
            print("显示失败", file=sys.stderr)
            return -1
        return 0

    def cleanup(self):
        """清理临时文件"""
        try:
            if self.screenshot_path.exists():
                # self.screenshot_path.unlink()
                print("清理截图文件", file=sys.stderr)
            if self.ocr_result_path.exists():
                # self.ocr_result_path.unlink()
                print("清理OCR结果文件", file=sys.stderr)
        except Exception as e:
            print(f"清理文件时出错: {e}", file=sys.stderr)
    

    def write_translation_files(self, src_txt, rst_txt):
        """将原文和译文写入临时文件"""
        from pathlib import Path
        
        temp_dir = Path("C:/MY_SPACE/Sources/tools/screenshot_translator/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        source_file = temp_dir / "translation_source.txt"
        target_file = temp_dir / "translation_target.txt"
        
        try:
            # 写入原文
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(src_txt)
            print(f"原文已写入: {source_file}", file=sys.stderr)
            
            # 写入译文
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(rst_txt)
            print(f"译文已写入: {target_file}", file=sys.stderr)
            
        except Exception as e:
            print(f"写入文件失败: {e}", file=sys.stderr)
            
    def run(self):
        """运行完整的截图翻译流程"""
        print(f"启动截图翻译工具", file=sys.stderr)
        print(f"工作目录: {self.base_dir}", file=sys.stderr)
        
        # 步骤1: 截图
        if self.step1_screenshot() != 0:
            print("截图步骤失败，终止流程", file=sys.stderr)
            return -1
        
        # 步骤2: OCR
        if self.step2_ocr() != 0:
            print("OCR步骤失败，终止流程", file=sys.stderr)
            return -1
        ocr_text = self.pre_result["stdout"].strip()
        
        # 步骤3: 翻译
        if self.step3_translate(self.pre_result["stdout"]) != 0:
            print("翻译步骤失败", file=sys.stderr)
            return -1
        translated_text = self.pre_result["stdout"].strip()

        self.write_translation_files(ocr_text, translated_text)
        # 步骤4: 显示
        if self.step4_show() != 0:
            print("显示步骤失败", file=sys.stderr)
            return -1
        
        print("=" * 50)
        print("截图翻译流程完成!", file=sys.stderr)
        print("=" * 50)
        
        # 清理临时文件
        # self.cleanup()
        return 0

def main():
    """主函数"""
    try:
        translator = ScreenshotTranslator()
        result = translator.run()
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n用户中断", file=sys.stderr)
        sys.exit(-1)
    except Exception as e:
        print(f"程序异常: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(-1)

if __name__ == "__main__":
    main()