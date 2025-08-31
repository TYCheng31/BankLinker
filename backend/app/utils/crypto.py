# app/utils/crypto.py
import os
from cryptography.fernet import Fernet

# 環境變數載入金鑰（請事先放到 .env：ENCRYPTION_KEY=...）
# 產生金鑰指令：python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
_FERNET_KEY = os.getenv("ENCRYPTION_KEY")
if not _FERNET_KEY:
    raise RuntimeError("ENCRYPTION_KEY not set")
fernet = Fernet(_FERNET_KEY.encode() if isinstance(_FERNET_KEY, str) else _FERNET_KEY)

def encrypt_to_bytes(plaintext: str) -> bytes:
    return fernet.encrypt(plaintext.encode("utf-8"))

def decrypt_to_str(cipher_bytes: bytes) -> str:
    return fernet.decrypt(cipher_bytes).decode("utf-8")
