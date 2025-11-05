from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import argostranslate.translate
import base64
import cv2
import numpy as np
import io
from PIL import Image
import sqlite3
import os
from typing import List, Dict, Optional
from contextlib import contextmanager

app = Flask(__name__)

# 字典查询类 - 线程安全版本
class StarDictSQLite:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """使用上下文管理器自动管理连接"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def lookup_word(self, word: str) -> Optional[Dict]:
        """查询单词的完整信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, word, sw, phonetic, definition, translation, pos, collins, oxford, tag, bnc, frq, exchange, detail, audio FROM stardict WHERE word = ? OR sw = ?",
                (word.lower(), word.lower())
            )
            result = cursor.fetchone()
            if result:
                fields = ['id', 'word', 'sw', 'phonetic', 'definition', 'translation', 
                         'pos', 'collins', 'oxford', 'tag', 'bnc', 'frq', 'exchange', 'detail', 'audio']
                return dict(zip(fields, result))
        return None
    
    def _parse_pos_distribution(self, pos_str: str) -> Dict[str, int]:
        """解析词性分布字符串"""
        pos_dist = {}
        if pos_str:
            parts = pos_str.split('/')
            for part in parts:
                if ':' in part:
                    pos, percent = part.split(':')
                    pos_dist[pos.strip()] = int(percent)
        return pos_dist
    
    def get_detailed_translations(self, word: str) -> Dict:
        """获取单词的详细翻译信息"""
        result = self.lookup_word(word)
        if not result:
            return {}
        
        # 解析词性分布
        pos_dist = self._parse_pos_distribution(result.get('pos', ''))
        
        # 构建返回结果
        detailed_info = {
            'word': result.get('word'),
            'phonetic': result.get('phonetic'),
            'pos_distribution': pos_dist,
            'definition': result.get('definition', ''),
            'translation': result.get('translation', ''),
            'collins_star': result.get('collins'),
            'is_oxford_core': bool(result.get('oxford')),
            'frequency': result.get('frq')
        }
        
        return detailed_info
    
    def format_dictionary_output(self, word: str) -> str:
        """格式化字典查询输出"""
        detailed_info = self.get_detailed_translations(word)
        if not detailed_info:
            return f"未找到单词: {word}"
        
        output_parts = []
        
        # 中文翻译
        if detailed_info['translation']:
            translation = detailed_info['translation']
            # 清理翻译文本，取主要部分
            lines = translation.split('\n')
            clean_translations = []
            for line in lines[:3]:  # 取前3行
                line = line.strip()
                if line and '。' not in line and len(line) < 100:
                    clean_translations.append(line)
            
            if clean_translations:
                output_parts.append(f"中文释义: {'; '.join(clean_translations)}")
        
        # 词性分布
        if detailed_info['pos_distribution']:
            pos_str = "，".join([f"{pos}({percent}%)" for pos, percent in detailed_info['pos_distribution'].items()])
            output_parts.append(f"词性: {pos_str}")
        
        # 基本信息
        if detailed_info['phonetic']:
            output_parts.append(f"音标: {detailed_info['phonetic']}")
        
        # 英文释义（限制长度）
        if detailed_info['definition']:
            definition = detailed_info['definition']
            if len(definition) > 200:
                definition = definition[:200] + "..."
            output_parts.append(f"英文释义: {definition}")
        
        return "\n".join(output_parts)

# 初始化字典
print("正在初始化本地词典...")
dict_db_path = r"C:\MY_SPACE\Sources\tools\screenshot_translator\dict_rsrc\ecdict-sqlite-28\stardict.db"
dictionary = StarDictSQLite(dict_db_path)
print("本地词典初始化完成！")

# 启动时一次性加载OCR模型
print("正在加载OCR模型...")
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    device='cpu',
    lang='en',
)
print("OCR模型加载完成！")

# 启动时预加载翻译模型
print("正在加载翻译模型...")
installed_languages = argostranslate.translate.get_installed_languages()
print("翻译模型加载完成！")

def is_single_word(text: str) -> bool:
    """判断文本是否为单个单词"""
    cleaned_text = text.strip()
    # 单个单词：没有空格，只包含字母和可能的连字符、撇号
    if ' ' in cleaned_text:
        return False
    # 允许字母、连字符、撇号（如 don't, well-known）
    cleaned = cleaned_text.replace('-', '').replace("'", "")
    return cleaned.isalpha()

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    """OCR识别接口"""
    try:
        # 接收base64图片
        data = request.json
        image_path = data['image']
        
        # OCR识别
        result = ocr.predict(input=image_path)
        
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
    """翻译接口 - 集成字典查询功能"""
    try:
        data = request.json
        text = data['text'].strip()
        
        print(f"收到翻译请求: '{text}'")
        
        # 判断是否为单个单词
        if is_single_word(text):
            # 使用字典查询
            # print(f"使用字典查询单词: {text}")
            dict_result = dictionary.format_dictionary_output(text)
            # print(f"字典查询结果:\n{dict_result}")
            return jsonify({
                "success": True,
                "translated": dict_result,
                "source": "dictionary"
            })
        else:
            # 使用argostranslate翻译
            # print(f"使用机器翻译文本: {text}")
            translated = argostranslate.translate.translate(text, "en", "zh")
            # print(f"机器翻译结果: {translated}")
            return jsonify({
                "success": True,
                "translated": translated,
                "source": "argostranslate"
            })
        
    except Exception as e:
        print(f"翻译出错: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/dict_lookup', methods=['POST'])
def dict_lookup_endpoint():
    """专门的字典查询接口"""
    try:
        data = request.json
        word = data['word'].strip()
        
        print(f"字典查询请求: {word}")
        dict_result = dictionary.format_dictionary_output(word)
        print(f"字典查询结果:\n{dict_result}")
        
        return jsonify({
            "success": True,
            "result": dict_result
        })
        
    except Exception as e:
        print(f"字典查询出错: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "services": {
            "dictionary": "available",
            "ocr": "available", 
            "translation": "available"
        }
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)