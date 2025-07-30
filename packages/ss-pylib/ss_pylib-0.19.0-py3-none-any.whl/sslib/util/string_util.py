import re
import base64
from datetime import datetime
from stringcase import camelcase
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class StringUtil:
    ASSOCIATED = b'header'

    @staticmethod
    def to_int(src: str) -> int:
        try:
            return int(src)
        except ValueError:
            return 0

    @staticmethod
    def to_bool(source: str) -> bool:
        return source.lower() in ('true', '1', 'yes', 'y')

    @staticmethod
    def camel_case(source: str) -> str:
        return camelcase(source)

    @staticmethod
    def datetime_or_none(source: datetime) -> str | None:
        return source.strftime('%Y-%m-%d %H:%M:%S') if source is not None else None

    @staticmethod
    def camel_to_snake(name: str) -> str:
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def encrypt(src: str, key: str) -> str:
        '''key: 32byte'''
        nonce, cipher = StringUtil.__make_key(key=key)
        encrypted = cipher.encrypt(nonce=nonce, data=src.encode(), associated_data=StringUtil.ASSOCIATED)
        encrypted = base64.urlsafe_b64encode(encrypted).decode().replace('=', '')
        return encrypted

    @staticmethod
    def decrypt(src: str, key: str) -> str | None:
        encrypted = StringUtil.__b64decode_padded(src)
        nonce, cipher = StringUtil.__make_key(key=key)
        decrypted = cipher.decrypt(nonce=nonce, data=encrypted, associated_data=StringUtil.ASSOCIATED)
        return decrypted.decode()

    @staticmethod
    def __make_key(key: str):
        nonce = base64.b64encode(key.encode())
        return nonce, AESGCM(key=nonce)

    @staticmethod
    def __b64decode_padded(data_b64: str) -> bytes:
        '''Base64 문자열을 디코딩할 때, 패딩(=)이 모자라면 채워주고 디코딩'''
        s = data_b64.strip()
        # 길이를 4의 배수로 만들어 줄 패딩 개수 계산
        pad_len = (-len(s)) % 4
        if pad_len:
            s += "=" * pad_len
        return base64.urlsafe_b64decode(s)


if __name__ == '__main__':
    KEY = '123456789012345678901234'
    encrypted = StringUtil.encrypt('암호화', KEY)
    print(f'암호화: {encrypted}')
    decrypted = StringUtil.decrypt(encrypted, KEY)
    print(f'복호화: {decrypted}')
