from paddleocr import PaddleOCR
import cv2
import re

def recognize_id_card(image_path):
    """身份证识别模块，返回结构化字典数据"""
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, layout=True)
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法加载图像: {image_path}")

    result = ocr.ocr(img, cls=True)
    full_text = "\n".join([word_info[1][0] for line in result for word_info in line])

    structured_data = {
        "姓名": "",
        "性别": "",
        "民族": "",
        "出生": "",
        "住址": "",
        "公民身份号码": ""
    }

    # 1. 姓名提取
    name_match = re.search(r"姓名[:：]?\s*([\u4e00-\u9fa5]{2,4})", full_text)
    if not name_match:
        name_match = re.search(r"^\s*([\u4e00-\u9fa5]{2,4})\s*$", full_text, re.MULTILINE)
    if name_match:
        structured_data["姓名"] = name_match.group(1)

    # 2. 性别提取
    gender_match = re.search(r"性别[:：]?\s*([\u4e00-\u9fa5])", full_text)
    if gender_match:
        structured_data["性别"] = gender_match.group(1)

    # 3. 民族提取
    ethnic_match = re.search(r"民族[:：]?\s*([\u4e00-\u9fa5]{1,3})", full_text)
    if ethnic_match:
        structured_data["民族"] = ethnic_match.group(1)

    # 4. 出生日期提取
    birth_match = re.search(r"(出生|出生日期)[:：]?\s*(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2})", full_text)
    if birth_match:
        structured_data["出生"] = birth_match.group(2).replace("年", "-").replace("月", "-").replace("日", "")

    # 5. 住址提取（排除末尾的身份证号）
    address_match = re.search(r"住址[:：]?([\s\S]*?)(?=\n(公民身份号码|身份证号)|$)", full_text)
    if address_match:
        structured_data["住址"] = address_match.group(1).replace("\n", "").strip()

    # 6. 身份证号提取（严格匹配独立行）
    id_number_match = re.search(
        r"^\s*(公民身份号码|身份证号)[:：]?\s*([\dX]{18})\s*$",
        full_text,
        re.IGNORECASE | re.MULTILINE
    )
    if id_number_match:
        structured_data["公民身份号码"] = id_number_match.group(2).upper()

    return structured_data