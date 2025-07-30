import os
import unittest

from loguru import logger

from poocr.api.ocr import IDCardOCR, PassportOCR, VatInvoiceOCR, social_security_card


class TestOCR(unittest.TestCase):
    """
    ocr.py测试用的代码
    """

    def setUp(self):
        self.SecretId = os.getenv("SecretId", None)
        self.SecretKey = os.getenv("SecretKey", None)

        self.ak = os.getenv('ak', None)
        self.sk = os.getenv('sk', None)

        self.baidu_id = os.getenv('baidu_id', None)
        self.baidu_key = os.getenv('baidu_key', None)

    def test_IDCardOCR(self):
        r = IDCardOCR(img_path=r'../test_files/IDCard/idcard_bak.png', id=self.SecretId, key=self.SecretKey)
        logger.info(r)

    def test_PassportOCR(self):
        r = PassportOCR(
            img_path=r'.\passport.png',
            id=self.SecretId, key=self.SecretKey)
        logger.info(r)

    def test_VatInvoiceOCR(self):
        v_r = VatInvoiceOCR(img_path=r'../test_files/VatInvoiceOCR/img.png', id=self.SecretId, key=self.SecretKey)
        logger.info(v_r)

    def test_social_security_card(self):
        r = social_security_card(img_path=r'D:\workplace\code\gitcode\pobd\tests\test_files\ocr\Social\img.png',
                                 id=self.baidu_id, key=self.baidu_key)
        logger.info(r)
