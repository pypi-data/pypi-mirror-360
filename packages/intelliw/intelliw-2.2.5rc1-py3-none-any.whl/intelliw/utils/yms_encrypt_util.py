import base64
import hashlib
import hmac
import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class YmsEncryptUtil:
    _log = logging.getLogger("YmsEncryptUtil")
    _aes_key_bytes = bytearray(base64.b64decode("g/A/0jw92C1Ki7toxpL6hzAqpYaGd3oUo9OLengo1Ck="))
    _aes_key_iv = bytearray(base64.b64decode("s6jg4fmrG/46NvIx9nb3i7MKUZ0rIebFMMDu6Ou0pdA="))
    _aes_key_aad = bytearray(base64.b64decode("NanjgbGidWdUm1+Kb3g8Fn6/gJ8cTWqeNnJASE2M4oE="))
    _initialized = False

    DEFAULT_FACTORS = ("123", "456", "789")

    CIPHER_TEXT_PREFIX = "YMS("
    CIPHER_TEXT_SUFFIX = ")"
    YMS_BASE64_PREFIX = "BAS("
    YMS_BASE64_SUFFIX = ")"

    @classmethod
    def __init__(cls, factor1: str = None, factor2: str = None, factor3: str = None):
        if not cls._initialized:
            cls._initialized = True
            factors = []
            for f in (factor1, factor2, factor3):
                if not f:
                    factors.extend(cls.DEFAULT_FACTORS)
                    break
                factors.append(cls._decode_encrypt_factor(f))
            else:
                cls._gen_aes_keys(*factors)

    @classmethod
    def _decode_encrypt_factor(cls, factor: str) -> str:
        if factor.startswith(cls.YMS_BASE64_PREFIX) and factor.endswith(cls.YMS_BASE64_SUFFIX):
            decoded = base64.b64decode(factor[len(cls.YMS_BASE64_PREFIX):-len(cls.YMS_BASE64_SUFFIX)])
            return decoded.decode('utf-8')
        return factor

    @classmethod
    def _gen_aes_keys(cls, fact1: str, fact2: str, fact3: str):
        cls._aes_key_bytes = cls._gen_config_file_key(fact1, fact2, fact3)
        try:
            cls._aes_key_iv = hashlib.sha256(fact2.encode()).digest()
            cls._aes_key_aad = hashlib.sha256(fact3.encode()).digest()
        except Exception as e:
            cls._log.warning(f"生成Iv和附加字符失败: {e}")

    @classmethod
    def _gen_config_file_key(cls, str1: str, str2: str, str3: str) -> bytes:
        try:
            data = hashlib.sha256(str3.encode()).digest()
            password = hmac.new(str2.encode(), str1.encode(), hashlib.sha256).digest()

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=data,
                iterations=10000,
                backend=default_backend()
            )
            return kdf.derive(password)
        except Exception as e:
            cls._log.error(f"生成配置文件密钥失败: {e}")
            return b''

    @classmethod
    def encrypt(cls, s: str) -> str:
        if s == "" or (s.startswith(cls.CIPHER_TEXT_PREFIX) and s.endswith(cls.CIPHER_TEXT_SUFFIX)):
            return s
        return cls._enc_config_file_item(s)

    @classmethod
    def decrypt(cls, s: str) -> str:
        if s == "" or not (s.startswith(cls.CIPHER_TEXT_PREFIX) and s.endswith(cls.CIPHER_TEXT_SUFFIX)):
            return s
        return cls._dec_config_file_item(s)

    @classmethod
    def _enc_config_file_item(cls, plain_text: str) -> str:
        try:
            encryptor = Cipher(
                algorithms.AES(cls._aes_key_bytes),
                modes.GCM(cls._aes_key_iv, min_tag_length=8),
                backend=default_backend()
            ).encryptor()
            encryptor.authenticate_additional_data(cls._aes_key_aad)
            ciphertext = encryptor.update(plain_text.encode()) + encryptor.finalize()
            add_tag = encryptor.tag[:-8]
            return cls.CIPHER_TEXT_PREFIX + (ciphertext + add_tag).hex().upper() + cls.CIPHER_TEXT_SUFFIX
        except Exception as e:
            cls._log.error(f"加密失败: {e}")
            return ""

    @classmethod
    def _dec_config_file_item(cls, cipher_hex: str) -> str:
        cipher_hex = cipher_hex[len(cls.CIPHER_TEXT_PREFIX):-len(cls.CIPHER_TEXT_SUFFIX)]
        try:
            data = bytes.fromhex(cipher_hex)
            tag, ciphertext = data[-8:], data[:-8]

            decryptor = Cipher(
                algorithms.AES(cls._aes_key_bytes),
                modes.GCM(cls._aes_key_iv, tag, min_tag_length=8),
                backend=default_backend()
            ).decryptor()
            decryptor.authenticate_additional_data(cls._aes_key_aad)
            return (decryptor.update(ciphertext) + decryptor.finalize()).decode()
        except Exception as e:
            cls._log.error(f"解密失败: {cipher_hex[:8]}...: {e}")
            return f"{cls.CIPHER_TEXT_PREFIX}{cipher_hex}{cls.CIPHER_TEXT_SUFFIX}"
