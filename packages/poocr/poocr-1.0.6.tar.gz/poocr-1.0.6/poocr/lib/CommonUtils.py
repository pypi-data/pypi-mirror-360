# -*- coding: UTF-8 -*-


import base64

import pymupdf


def get_error_info(error_info):
    """
    检查接口返回数据是否错误
    :param error_info: 调用接口的返回数据
    :return:
    """
    error_url = 'http://python4office.cn/pobaidu/pobaidu-error/'
    if error_info.get('error_code', False):
        return f"接口调用错误，错误信息是{error_info}，原因和解决方法请查看官方文档：{error_url}"
    return False


def img2base64(imgPath):
    with open(imgPath, "rb") as f:
        data = f.read()
        encodestr = base64.b64encode(data)  # 得到 byte 编码的数据
        picbase = str(encodestr, 'utf-8')
        return picbase


def pdf2base64(pdf_path):
    base64_encoded_pdf = []
    pdf = pymupdf.open(pdf_path)
    for i in range(len(pdf)):
        pdf_bytes = pdf.convert_to_pdf(i, i + 1)
        # 灏嗗浘鐗囪浆鎹负Base64缂栫爜鐨勫瓧绗︿覆
        base64_encoded_pdf.append(base64.b64encode(pdf_bytes).decode('utf-8'))
    # 鍏抽棴PDF鏂囨。
    pdf.close()
    return base64_encoded_pdf



def extract_all_fields(data, invoice_info, prefix=""):
    """
    递归提取所有字段，包括嵌套的列表和字典。

    :param data: 要提取的数据，可以是 dict 或 list
    :param invoice_info: 最终输出的字典，用于存储提取的字段
    :param prefix: 当前处理的字段前缀，用于生成唯一键名
    """
    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)):
                extract_all_fields(value, invoice_info, new_prefix)
            else:
                invoice_info[new_prefix] = value
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            new_prefix = f"{prefix}[{idx}]"
            if isinstance(item, (dict, list)):
                extract_all_fields(item, invoice_info, new_prefix)
            else:
                invoice_info[new_prefix] = item