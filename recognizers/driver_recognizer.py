from paddleocr import PaddleOCR
import cv2
import re

def recognize_driver_license(image_path):
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, layout=True)
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法加载图像: {image_path}")

    result = ocr.ocr(img, cls=True)
    full_text = "\n".join([word_info[1][0] for line in result for word_info in line])

    # 结构化字段提取
    structured_data = {
        "姓名": "",
        "性别": "",
        "出生日期": "",
        "驾驶证号": "",
        "准驾车型": "",
        "有效期限": ""
    }

    # 1. 姓名（独立行匹配）
    name_match = re.search(r"^[\u4e00-\u9fa5]{2,4}$", full_text, re.MULTILINE)
    structured_data["姓名"] = name_match.group(0) if name_match else ""

    # 2. 性别（标签匹配）
    gender_match = re.search(r"性别[:：]?\s*([\u4e00-\u9fa5])", full_text)
    structured_data["性别"] = gender_match.group(1) if gender_match else ""

    # 3. 出生日期（标准日期格式）
    birth_date = re.search(r"出生日期[:：]?\s*(\d{4}-\d{2}-\d{2})", full_text)
    structured_data["出生日期"] = birth_date.group(1) if birth_date else ""

    # 4. 驾驶证号（完整18位数字）
    license_number = re.search(r"证号[:：]?\s*(\d{18})", full_text)
    structured_data["驾驶证号"] = license_number.group(1) if license_number else ""

    # 5. 准驾车型（字母+数字）
    vehicle_type = re.search(r"准驾车型[:：]?\s*([A-Z]\d?)", full_text)
    structured_data["准驾车型"] = vehicle_type.group(1) if vehicle_type else ""

    # 6. 有效期限（日期范围）
    validity = re.search(r"有效期限[:：]?\s*(\d{4}-\d{2}-\d{2}至\d{4}-\d{2}-\d{2})", full_text)
    structured_data["有效期限"] = validity.group(1) if validity else ""

    return structured_data
