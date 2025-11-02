from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import argostranslate.translate
import base64
import cv2
import numpy as np
import io
from PIL import Image

app = Flask(__name__)

# 启动时一次性加载模型
print("正在加载OCR模型...")
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    device='gpu',
    lang='en',
)
print("OCR模型加载完成！")

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    """OCR识别接口"""
    try:
        # 接收base64图片
        data = request.json
        image_data = base64.b64decode(data['image'])
        
        # 转换为OpenCV格式
        image = Image.open(io.BytesIO(image_data))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 临时保存图片
        temp_path = r"D:\Source\ai_tools\screenshot_translator\temp\screenshot_server.png"
        cv2.imwrite(temp_path, image)
        
        # OCR识别
        result = ocr.predict(input=temp_path)
        
        # 解析结果
        all_text_lines = []
        for res in result:
            if "rec_texts" in res and res["rec_texts"]:
                all_text_lines.extend(res["rec_texts"])
        
        all_text = " ".join(all_text_lines) if all_text_lines else ""
        
        return jsonify({
            "success": True,
            "text": all_text
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/translate', methods=['POST'])
def translate_endpoint():
    """翻译接口"""
    try:
        data = request.json
        text = data['text']
        
        translated = argostranslate.translate.translate(text, "en", "zh")
        
        return jsonify({
            "success": True,
            "translated": translated
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)