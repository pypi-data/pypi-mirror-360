import base64
import binascii
import hashlib
import urllib.parse
import codecs
import asyncio
from typing import Union


class EncodingUtils:
    # ----- Base64 -----
    @staticmethod
    async def base64_encode(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return base64.b64encode(data).decode()

    @staticmethod
    async def base64_decode(data: str) -> str:
        try:
            return base64.b64decode(data).decode()
        except Exception:
            return ""

    # ----- Base32 -----
    @staticmethod
    async def base32_encode(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return base64.b32encode(data).decode()

    @staticmethod
    async def base32_decode(data: str) -> str:
        try:
            return base64.b32decode(data).decode()
        except Exception:
            return ""

    # ----- Hex -----
    @staticmethod
    async def hex_encode(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return binascii.hexlify(data).decode()

    @staticmethod
    async def hex_decode(data: str) -> str:
        try:
            return binascii.unhexlify(data).decode()
        except Exception:
            return ""

    # ----- URL Encoding -----
    @staticmethod
    async def url_encode(data: str) -> str:
        return urllib.parse.quote_plus(data)

    @staticmethod
    async def url_decode(data: str) -> str:
        return urllib.parse.unquote_plus(data)

    # ----- ROT13 -----
    @staticmethod
    async def rot13(data: str) -> str:
        return codecs.encode(data, 'rot_13')

    # ----- XOR Encoding -----
    @staticmethod
    async def xor_encode(data: str, key: str) -> str:
        return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

    @staticmethod
    async def xor_bytes(data: bytes, key: bytes) -> bytes:
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

    # ----- Hashing (async via to_thread for scalability) -----
    @staticmethod
    async def hash_md5(data: Union[str, bytes]) -> str:
        return await asyncio.to_thread(lambda: hashlib.md5(data.encode() if isinstance(data, str) else data).hexdigest())

    @staticmethod
    async def hash_sha1(data: Union[str, bytes]) -> str:
        return await asyncio.to_thread(lambda: hashlib.sha1(data.encode() if isinstance(data, str) else data).hexdigest())

    @staticmethod
    async def hash_sha256(data: Union[str, bytes]) -> str:
        return await asyncio.to_thread(lambda: hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest())

    @staticmethod
    async def hash_sha512(data: Union[str, bytes]) -> str:
        return await asyncio.to_thread(lambda: hashlib.sha512(data.encode() if isinstance(data, str) else data).hexdigest())

    # ----- Padding Helper -----
    @staticmethod
    async def pad_string(data: str, block_size: int = 16, padding_char: str = ' ') -> str:
        return data + (padding_char * ((block_size - len(data) % block_size) % block_size))

    # ----- String <-> Binary -----
    @staticmethod
    async def string_to_binary(data: str) -> str:
        return ' '.join(format(ord(char), '08b') for char in data)

    @staticmethod
    async def binary_to_string(binary_str: str) -> str:
        try:
            chars = binary_str.split()
            return ''.join(chr(int(char, 2)) for char in chars)
        except Exception:
            return ""

    # ----- Morse Code -----
    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
        'E': '.',  'F': '..-.', 'G': '--.',  'H': '....',
        'I': '..', 'J': '.---', 'K': '-.-',  'L': '.-..',
        'M': '--', 'N': '-.',   'O': '---',  'P': '.--.',
        'Q': '--.-','R': '.-.', 'S': '...',  'T': '-',
        'U': '..-','V': '...-', 'W': '.--',  'X': '-..-',
        'Y': '-.--','Z': '--..',
        '0': '-----', '1': '.----', '2': '..---',
        '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..',
        '9': '----.'
    }

    @staticmethod
    async def to_morse(text: str) -> str:
        return ' '.join(EncodingUtils.MORSE_CODE_DICT.get(c.upper(), '') for c in text)

    @staticmethod
    async def from_morse(morse: str) -> str:
        reverse = {v: k for k, v in EncodingUtils.MORSE_CODE_DICT.items()}
        return ''.join(reverse.get(code, '') for code in morse.strip().split())

