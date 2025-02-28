from paddleocr import PaddleOCR
import cv2
import re

def recognize_social_security(image_path):
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, layout=True)
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法加载图像: {image_path}")

    result = ocr.ocr(img, cls=True)
    full_text = "\n".join([word_info[1][0] for line in result for word_info in line])

    # 结构化字段提取
    structured_data = {
        "姓名": "",
        "社会保障号码": "",
        "卡号": "",
        "发卡日期": "",
        "服务电话": ""
    }

    # 1. 姓名（匹配独立行或标签）
    name_match = re.search(r"^姓名[:：]?\s*([\u4e00-\u9fa5]{2,4})$", full_text, re.MULTILINE)
    structured_data["姓名"] = name_match.group(1) if name_match else ""

    # 2. 社会保障号码（匹配15-20位连续数字）
    social_number = re.search(r"社会保障号码[:：]?\s*(\d{15,20})", full_text)
    structured_data["社会保障号码"] = social_number.group(1) if social_number else ""

    # 3. 卡号（字母+数字组合）
    card_number = re.search(r"卡号[:：]?\s*([A-Za-z]+\d+)", full_text)
    structured_data["卡号"] = card_number.group(1) if card_number else ""

    # 4. 发卡日期（年月格式）
    issue_date = re.search(r"发卡日期[:：]?\s*(\d{4}年\d{1,2}月)", full_text)
    structured_data["发卡日期"] = issue_date.group(1) if issue_date else ""

    # 5. 服务电话（匹配第一个有效电话）
    service_phone = re.search(r"服务电话[:：]?.*?(\d{5,})", full_text)
    structured_data["服务电话"] = service_phone.group(1) if service_phone else ""

    return structured_data