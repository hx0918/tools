import sys
import requests

def main(text):
    if not text.strip():
        print("翻译失败：输入文本为空", file=sys.stderr)
        return
    
    try:
        # 翻译
        print("正在翻译...", file=sys.stderr)
        translate_data = {
            "text": text
        }
        translate_response = requests.post("http://127.0.0.1:5000/translate", json=translate_data)
        translate_result = translate_response.json()
        
        if not translate_result["success"]:
            print(f"翻译失败：{translate_result['error']}", file=sys.stderr)
            return
        
        translated_text = translate_result["translated"]
        
        # 输出翻译结果到stdout
        print(translated_text)
        
    except Exception as e:
        print(f"翻译处理失败：{str(e)}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 从命令行参数获取文本
        text = sys.argv[1]
        main(text)
    else:
        # 从stdin读取文本（支持管道操作）
        text = sys.stdin.read().strip()
        if text:
            main(text)
        else:
            print("错误：请提供要翻译的文本", file=sys.stderr)
            print("用法1: python translate_client.py \"要翻译的文本\"", file=sys.stderr)
            print("用法2: echo \"要翻译的文本\" | python translate_client.py", file=sys.stderr)