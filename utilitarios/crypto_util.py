# utils/crypto_util.py
"""Utilitário profissional para criptografia de backups (AES-GCM + PBKDF2-HMAC-SHA256).

Formato de arquivo (JSON):
{
  "version": 1,
  "encrypted": true,
  "salt": "<base64>",
  "nonce": "<base64>",
  "ciphertext": "<base64>"
}

Requisitos: package `cryptography`. Se não estiver instalado, as funções de
encrypt/decrypt lançarão CryptoError (não existe fallback inseguro).
"""
from __future__ import annotations

import os
import json
import base64
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Segurança: parâmetros recomendados
_KDF_ITERATIONS = 250_000
_SALT_BYTES = 16
_NONCE_BYTES = 12
_KEY_LEN = 32  # bytes -> AES-256

# Tentativa de importar cryptography (requerido)
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.backends import default_backend

    HAVE_CRYPTO = True
except Exception:
    HAVE_CRYPTO = False


class CryptoError(Exception):
    """Exceção customizada para erros do módulo de criptografia."""
    pass


def _b64(u: bytes) -> str:
    return base64.b64encode(u).decode("ascii")


def _unb64(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def derive_key(password: str, salt: bytes = None, iterations: int = _KDF_ITERATIONS) -> Tuple[bytes, bytes]:
    """
    Deriva uma chave a partir da senha usando PBKDF2-HMAC-SHA256.
    Retorna (key_bytes, salt_used).
    """
    if not HAVE_CRYPTO:
        raise CryptoError("cryptography library is required for secure key derivation.")
    if not password:
        raise CryptoError("password must be provided")

    if salt is None:
        salt = os.urandom(_SALT_BYTES)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_KEY_LEN,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(password.encode("utf-8"))
    return key, salt


def encrypt_bytes(plaintext: bytes, password: str) -> Dict[str, Any]:
    """
    Criptografa os bytes usando AES-GCM. Retorna dict pronto para serialização:
    {
      "version": 1,
      "encrypted": True,
      "salt": base64,
      "nonce": base64,
      "ciphertext": base64
    }
    """
    if not HAVE_CRYPTO:
        raise CryptoError("cryptography library is required for encryption.")

    if not isinstance(plaintext, (bytes, bytearray)):
        raise CryptoError("plaintext must be bytes")

    if not password:
        raise CryptoError("password required for encryption")

    key, salt = derive_key(password, None, _KDF_ITERATIONS)
    aesgcm = AESGCM(key)
    nonce = os.urandom(_NONCE_BYTES)

    # AESGCM.encrypt returns ciphertext||tag (tag appended). That's OK.
    ct = aesgcm.encrypt(nonce, plaintext, None)

    payload = {
        "version": 1,
        "encrypted": True,
        "salt": _b64(salt),
        "nonce": _b64(nonce),
        "ciphertext": _b64(ct)
    }
    return payload


def decrypt_bytes(payload: Dict[str, Any], password: str) -> bytes:
    """
    Descriptografa o payload gerado por encrypt_bytes.
    Espera o dict com keys: version, encrypted, salt, nonce, ciphertext.
    Retorna os bytes originais.
    """
    if not HAVE_CRYPTO:
        raise CryptoError("cryptography library is required for decryption.")

    if not isinstance(payload, dict):
        raise CryptoError("payload must be a dict")

    version = int(payload.get("version", 0))
    if version != 1:
        raise CryptoError(f"unsupported payload version: {version}")

    if not payload.get("encrypted", False):
        # Por decisão de segurança deste utilitário, não aceitamos payloads não-encriptados.
        raise CryptoError("payload is not encrypted (refuse to process plaintext payloads)")

    try:
        salt = _unb64(payload["salt"])
        nonce = _unb64(payload["nonce"])
        ct = _unb64(payload["ciphertext"])
    except KeyError as e:
        raise CryptoError(f"malformed payload, missing key: {e}") from e
    except Exception as e:
        raise CryptoError("failed to decode base64 payload") from e

    key, _ = derive_key(password, salt, _KDF_ITERATIONS)
    aesgcm = AESGCM(key)
    try:
        plain = aesgcm.decrypt(nonce, ct, None)
        return plain
    except Exception as e:
        # Não vazar detalhes sensíveis, apenas informar que a decriptação falhou.
        raise CryptoError("decryption failed (invalid password or corrupted payload)") from e


def encrypt_to_file(path: str, data: bytes, password: str, *, overwrite: bool = False) -> None:
    """
    Cripta `data` e salva em `path` no formato JSON descrito.
    - path: caminho do arquivo a ser gravado (string)
    - data: bytes a serem criptografados
    - password: senha (str)
    - overwrite: se False e arquivo existir -> CryptoError
    """
    if not HAVE_CRYPTO:
        raise CryptoError("cryptography library is required for encryption to file.")

    if os.path.exists(path) and not overwrite:
        raise CryptoError(f"file exists and overwrite is False: {path}")

    payload = encrypt_bytes(data, password)

    # grava JSON com indent pequeno (não inclui dados sensíveis em logs)
    tmp_path = f"{path}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, separators=(",", ":"), ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    except Exception as e:
        # cleanup tmp
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise CryptoError(f"failed to write encrypted file: {e}") from e


def decrypt_from_file(path: str, password: str) -> bytes:
    """
    Lê o arquivo JSON em `path`, valida e descriptografa, retornando os bytes originais.
    """
    if not HAVE_CRYPTO:
        raise CryptoError("cryptography library is required for decryption from file.")

    if not os.path.exists(path):
        raise CryptoError("file not found")

    try:
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except Exception as e:
        raise CryptoError(f"failed to read payload file: {e}") from e

    # delegate to decrypt_bytes (aqui validamos versão e integridade)
    return decrypt_bytes(payload, password)


# --- Optional convenience helpers -------------------------------------------------
def encrypt_file_from_source_file(src_path: str, dest_path: str, password: str, *, overwrite: bool = False) -> None:
    """
    Lê bytes de um arquivo fonte (binário/texto), criptografa e salva em dest_path.
    """
    if not os.path.exists(src_path):
        raise CryptoError("source file not found")
    with open(src_path, "rb") as f:
        data = f.read()
    encrypt_to_file(dest_path, data, password, overwrite=overwrite)


def decrypt_to_dest_file(encrypted_path: str, dest_path: str, password: str, *, overwrite: bool = False) -> None:
    """
    Descriptografa o arquivo `encrypted_path` e grava os bytes em `dest_path`.
    """
    if os.path.exists(dest_path) and not overwrite:
        raise CryptoError("destination file exists and overwrite is False")
    data = decrypt_from_file(encrypted_path, password)
    tmp = f"{dest_path}.tmp"
    try:
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, dest_path)
    except Exception as e:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        raise CryptoError(f"failed to write decrypted output file: {e}") from e