from paddleocr import PaddleOCR


# img_path = r"D:\Source\ai_tools\screenshot_translator\temp\Snipaste_2025-11-02_21-12-10.png"
# img_path = r"C:\MY_SPACE\Sources\tools\screenshot_translator\temp\screenshot.png"
img_path = "https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/general_ocr_002.png"

# 初始化 PaddleOCR 实例
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    device='cpu',
    lang='en')

# 对示例图像执行 OCR 推理 
result = ocr.predict(
    input=img_path)
    
# 可视化结果并保存 json 结果
for res in result:
    res.print()
    # res.save_to_img("output")
    res.save_to_json("output")
    print(res["rec_texts"])