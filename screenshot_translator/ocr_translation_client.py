import sys
import os
import base64
import requests
import cv2


def libre_translate(text, from_lang='en', to_lang='zh', 
                   endpoint="https://libretranslate.com/translate"):
    """使用 LibreTranslate（免费开源）"""
    try:
        data = {
            'q': text,
            'source': from_lang,
            'target': to_lang,
            'format': 'text'
        }
        
        response = requests.post(endpoint, data=data, timeout=10)
        print(f"状态码: {response.status_code}",  file=sys.stderr)
        print(f"响应头: {response.headers}",  file=sys.stderr)
        print(f"原始响应: {response.text}",  file=sys.stderr)

        if response.status_code == 200:
            rst_text = ""
            result = response.json()
            result.get('translatedText', rst_text)
            return f"Libre翻译内容：\n{rst_text}"
        else:
            return f"Libre返回code：\n{response.status_code}"
    except Exception as e:
        return f"LibreTranslate 失败: {e}"
    
def image_to_base64(image_path):
    """图片转base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def main(image_path):
    if not os.path.exists(image_path):
        print("识别失败：图片文件不存在")
        return
    
    try:
        # 1. OCR识别
        print("正在OCR识别...", file=sys.stderr)
        ocr_data = {
            "image": image_to_base64(image_path)
        }
        ocr_response = requests.post("http://127.0.0.1:5000/ocr", json=ocr_data)
        ocr_result = ocr_response.json()
        
        if not ocr_result["success"]:
            print(f"OCR识别失败：{ocr_result['error']}")
            return
        
        ocr_text = ocr_result["text"]
        
        if not ocr_text.strip():
            print("识别失败：未识别到任何文字")
            return
        
        print(f"识别内容：\n{ocr_text}")
        
        # 2. 翻译
        print("正在翻译...", file=sys.stderr)
        translate_data = {
            "text": ocr_text
        }
        translate_response = requests.post("http://127.0.0.1:5000/translate", json=translate_data)
        translate_result = translate_response.json()
        
        if not translate_result["success"]:
            print(f"翻译失败：{translate_result['error']}")
            return
        
        translated_text = translate_result["translated"]
        print(f"翻译内容：\n{translated_text}")

        print("正在LibreTranslate ...", file=sys.stderr)
        libre_translated_text = libre_translate(ocr_text)
        print(libre_translated_text)
        
    except Exception as e:
        print(f"处理失败：{str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("错误：请提供图片路径")