import easyocr
import cv2  # OpenCV 用于加载图像

def recognize_document(image_path):
    # 使用 OpenCV 检查图片是否正确加载
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Failed to load image at path: {image_path}")

    # 创建 EasyOCR 读取器
    reader = easyocr.Reader(['ch_sim', 'en'])  # 支持中文和英文识别，你可以根据需要调整语言
    # 识别图片
    result = reader.readtext(image_path)

    # 提取识别的文本（不包含 Confidence 信息）
    recognized_text = ""
    for (bbox, text, prob) in result:
        recognized_text += f"{text}\n"  # 去掉 Confidence 信息，只保留文本

    return recognized_text
