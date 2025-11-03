# test_cpu_gpu.py
from paddleocr import PaddleOCR
import time

def test_ocr(device_type):
    print(f"\n测试 {device_type.upper()} 版本:")
    print("-" * 30)
    
    try:
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang='en',
            device=device_type,
            text_det_thresh=0.1,      # 降低阈值提高检测率
            text_det_box_thresh=0.3,
        )
        
        # 测试图片路径 - 替换为你的实际图片路径
        test_image = r"C:\MY_SPACE\Sources\tools\screenshot_translator\temp\screenshot.png"
        
        start_time = time.time()
        result = ocr.predict(input=test_image)
        end_time = time.time()
        
        print(f"处理时间: {end_time - start_time:.2f}秒")
        
        # 解析结果
        all_text = []
        for res in result:
            if "rec_texts" in res and res["rec_texts"]:
                all_text.extend(res["rec_texts"])
        
        if all_text:
            print(f"✅ 识别成功: {all_text}")
        else:
            print("❌ 未识别到文本")
            
        return all_text
        
    except Exception as e:
        print(f"❌ {device_type} 版本失败: {e}")
        return []

# 分别测试CPU和GPU
cpu_result = test_ocr('cpu')
gpu_result = test_ocr('gpu')

print("\n" + "=" * 50)
print("测试结果对比:")
print(f"CPU识别: {'成功' if cpu_result else '失败'}")
print(f"GPU识别: {'成功' if gpu_result else '失败'}")