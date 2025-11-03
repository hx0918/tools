import sys
import os
import base64
import requests

def image_to_base64(image_path):
    """图片转base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def main(image_path):
    if not os.path.exists(image_path):
        print("识别失败：图片文件不存在", file=sys.stderr)
        return
    
    try:
        # OCR识别
        print("正在OCR识别...", file=sys.stderr)
        ocr_data = {
            "image": image_to_base64(image_path)
        }
        ocr_response = requests.post("http://127.0.0.1:5000/ocr", json=ocr_data)
        ocr_result = ocr_response.json()
        
        if not ocr_result["success"]:
            print(f"OCR识别失败：{ocr_result['error']}", file=sys.stderr)
            return
        
        ocr_text = ocr_result["text"]
        
        if not ocr_text.strip():
            print("识别失败：未识别到任何文字", file=sys.stderr)
            return
        
        # 输出OCR结果到stdout
        print(ocr_text)
        
    except Exception as e:
        print(f"OCR处理失败：{str(e)}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("错误：请提供图片路径", file=sys.stderr)