from paddleocr import PaddleOCR
import cv2


def recognize_document(image_path):
    # 初始化OCR引擎
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="ch",
        use_gpu=False,
        layout=True
    )

    # 图像预处理
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法加载图像: {image_path}")

    # OCR识别
    result = ocr.ocr(img, cls=True)

    # 提取文本
    recognized_text = ""
    for line in result:
        for word_info in line:
            text = word_info[1][0]
            recognized_text += f"{text}\n"

    return recognized_text