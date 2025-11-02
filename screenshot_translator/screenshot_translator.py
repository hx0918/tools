import sys
import os
from paddleocr import PaddleOCR
import argostranslate.translate

# 保存原始stdout和stderr
original_stdout = sys.stdout
original_stderr = sys.stderr

def log(*args, **kwargs):
    """输出运行时日志到 stderr"""
    print(*args, file=original_stderr, **kwargs)
    original_stderr.flush()

def output_result(*args, **kwargs):
    """输出最终结果到 stdout"""
    print(*args, file=original_stdout, **kwargs)
    original_stdout.flush()

def check_gpu_availability():
    try:
        import paddle
        return paddle.device.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
    except Exception as e:
        log(f"GPU检查失败: {e}")
        return False

def main(image_path):
    log("开始截图翻译流程")
    
    if not os.path.exists(image_path):
        output_result("识别失败：图片文件不存在")
        return
    
    try:
        log("初始化OCR引擎...")
        device = 'gpu' if check_gpu_availability() else 'cpu'
        log(f"使用设备: {device}")
        
        # 重定向第三方库的输出到stderr
        sys.stdout = original_stderr
        sys.stderr = original_stderr
        
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            device=device,
            lang='en',
        )
        
        # 恢复stdout用于我们的结果输出
        sys.stdout = original_stdout
        
        log("OCR引擎初始化完成")
        
        log("开始OCR识别...")
        # 再次重定向第三方库输出
        sys.stdout = original_stderr
        result_data = ocr.predict(input=image_path)
        sys.stdout = original_stdout  # 恢复
        
        log("OCR识别完成")
        
        log("解析识别结果...")
        all_text_lines = []
        for res in result_data:
            if "rec_texts" in res and res["rec_texts"]:
                # output_result(f"{res["rec_texts"]}")
                all_text_lines.extend(res["rec_texts"])
        
        if all_text_lines:
            all_text = " ".join(all_text_lines)
            log(f"识别到 {len(all_text_lines)} 行文本，共 {len(all_text)} 字符")
            
            # 输出识别结果到 stdout
            output_result(f"识别内容：{all_text}")
            
            log("开始翻译...")
            try:
                # 重定向翻译库的输出
                sys.stdout = original_stderr
                translated_text = argostranslate.translate.translate(all_text, "en", "zh")
                sys.stdout = original_stdout  # 恢复
                
                log("翻译完成")
                
                # 输出翻译结果到 stdout
                output_result(f"翻译内容：{translated_text}")
                
            except Exception as e:
                error_msg = f"翻译失败：{str(e)}"
                log(error_msg)
                output_result(error_msg)
            
        else:
            output_result("识别失败：未识别到任何文字")
            
    except Exception as e:
        error_msg = f"处理失败：{str(e)}"
        log(error_msg)
        output_result(error_msg)
    finally:
        # 确保恢复原始输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        output_result("错误：请提供图片路径作为参数")