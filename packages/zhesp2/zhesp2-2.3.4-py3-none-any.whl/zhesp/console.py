#!/usr/bin/env python3
"""
Z-HESP2 — Zero’s Hash Encryption Secure Protocol 2.4
Self-contained CLI script with: encrypt · decrypt · genkey · update · exit
Clipboard integration removed. Clean output. Update via PyPI.
"""

import os
import base64
import getpass
import shlex
import zlib
import json
import time
import secrets
import subprocess
import sys
from datetime import datetime, timezone

from Crypto.Cipher import AES
from argon2.low_level import hash_secret_raw, Type

# ─────────────────────────────── Constants ─────────────────────────────── #
VERSION = 2
INTEGRITY_FLAG_FILE = os.path.expanduser("~/.zhesp2_verified")

# ─────────────────────────────── Banner ─────────────────────────────── #
def banner() -> None:
    print(r"""
 ███████╗██╗  ██╗███████╗███████╗███████╗██████╗
 ██╔════╝██║  ██║██╔════╝██╔════╝██╔════╝██╔══██╗
 ███████╗███████║█████╗  █████╗  █████╗  ██████╔╝
 ╚════██║██╔══██║██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗
 ███████║██║  ██║██║     ██║     ███████╗██║  ██║
 ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
        Zero's Hash Encryption Secure Protocol
                  Version 2.4 (Z-HESP2)
    """)

# ─────────────────────────────── KDF ─────────────────────────────── #
def derive_key(password: str, salt: bytes, length: int = 32, time_cost=3, memory_cost=65536, parallelism=2) -> bytes:
    return hash_secret_raw(
        password.encode(),
        salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=length,
        type=Type.ID,
    )

# ─────────────────────────────── Encrypt V2 ─────────────────────────────── #
def encrypt(message: str, password: str, metadata: dict | None = None) -> str:
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(password, salt)

    if metadata is None:
        metadata = {}
    metadata["timestamp"] = datetime.now(timezone.utc).isoformat()
    metadata["version"] = VERSION

    meta_json = json.dumps(metadata).encode()
    meta_nonce = os.urandom(12)
    meta_cipher = AES.new(key, AES.MODE_GCM, nonce=meta_nonce)
    meta_ct, meta_tag = meta_cipher.encrypt_and_digest(meta_json)

    compressed_msg = zlib.compress(message.encode())
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(compressed_msg)

    meta_ct_len = len(meta_ct).to_bytes(4, "big")
    ct_len = len(ciphertext).to_bytes(4, "big")

    payload = (
        VERSION.to_bytes(1, "big") +
        salt +
        iv +
        meta_nonce +
        meta_tag +
        meta_ct_len +
        meta_ct +
        ct_len +
        ciphertext +
        tag
    )
    return "ZH2:" + base64.urlsafe_b64encode(payload).decode()

# ─────────────────────────────── Decrypt ─────────────────────────────── #
def decrypt(token: str, password: str) -> str:
    try:
        if not token.startswith("ZH2:"):
            return "[!] Invalid ZHESP2 header."
        raw = base64.urlsafe_b64decode(token[4:])
        version = raw[0]
        payload = raw[1:]

        if version == 1:
            return decrypt_v1(payload, password)
        elif version == 2:
            return decrypt_v2(payload, password)
        else:
            return f"[!] Unknown ZHESP2 version: {version}"
    except Exception as e:
        return f"[!] Decryption error: {e}"

def decrypt_v1(payload: bytes, password: str) -> str:
    try:
        salt = payload[:16]
        iv = payload[16:28]
        tag = payload[28:44]
        aad = payload[44:48]
        ciphertext = payload[48:]

        key = derive_key(password, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        cipher.update(aad)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        meta_len = int.from_bytes(aad, "big")
        meta_blob = zlib.decompress(plaintext[:meta_len])
        metadata = json.loads(meta_blob.decode())
        message = zlib.decompress(plaintext[meta_len:]).decode()

        return f"[+] Metadata: {json.dumps(metadata, indent=2)}\n[+] Decrypted: {message}"
    except Exception as e:
        return f"[!] Decryption error (v1): {e}"

def decrypt_v2(payload: bytes, password: str) -> str:
    try:
        salt = payload[:16]
        iv = payload[16:28]
        meta_nonce = payload[28:40]
        meta_tag = payload[40:56]
        meta_len = int.from_bytes(payload[56:60], "big")
        meta_ct = payload[60:60 + meta_len]
        offset = 60 + meta_len

        ct_len = int.from_bytes(payload[offset:offset + 4], "big")
        offset += 4
        ciphertext = payload[offset:offset + ct_len]
        tag = payload[offset + ct_len:offset + ct_len + 16]

        key = derive_key(password, salt)

        meta_cipher = AES.new(key, AES.MODE_GCM, nonce=meta_nonce)
        metadata_json = meta_cipher.decrypt_and_verify(meta_ct, meta_tag)
        metadata = json.loads(metadata_json.decode())

        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        message = zlib.decompress(plaintext).decode()

        return f"[+] Metadata: {json.dumps(metadata, indent=2)}\n[+] Decrypted: {message}"
    except Exception as e:
        return f"[!] Decryption error (v2): {e}"

# ─────────────────────────────── One-Time Integrity Check ─────────────────────────────── #
def safe_encrypt_flow(message: str, password: str) -> str:
    if not os.path.exists(INTEGRITY_FLAG_FILE):
        print("[*] Running first-time encryption integrity check...")
        try:
            test_token = encrypt("test123", password)
            output = decrypt(test_token, password)
            if "test123" not in output:
                raise RuntimeError("[!] Integrity test failed. Got: " + output)
            with open(INTEGRITY_FLAG_FILE, "w") as f:
                f.write("verified")
            print("[✓] Z-HESP2 encryption system verified.")
        except Exception as e:
            raise RuntimeError(f"[!] Integrity test failed: {e}")
    return encrypt(message, password)

# ─────────────────────────────── Generate Key ─────────────────────────────── #
def generate_key(length: int = 32) -> str:
    raw = secrets.token_bytes(length)
    b64 = base64.urlsafe_b64encode(raw).decode()
    print(f"[+] Generated Key ({length * 8} bits):\nBase64: {b64}\nHex:    {raw.hex()}\n")
    return b64

# ─────────────────────────────── Update from PyPI ─────────────────────────────── #
def update_self():
    print("[*] Updating Z-HESP2 from PyPI...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "zhesp2"])
        print("[✓] Update complete. You may need to restart your terminal or shell.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Update failed: {e}")

# ─────────────────────────────── CLI ─────────────────────────────── #
def main() -> None:
    banner()
    print("Z-HESP2 ready. Commands: encrypt, decrypt, genkey, update, exit.")
    failures = 0

    while True:
        try:
            cmd = input("zhesp2 > ").strip()
            if not cmd:
                continue
            args = shlex.split(cmd)

            match args[0]:
                case "exit" | "quit":
                    print("[*] Goodbye.")
                    break
                case "encrypt":
                    msg = " ".join(args[1:]) or input("Message: ")
                    pwd = getpass.getpass("Passphrase: ")
                    token = safe_encrypt_flow(msg, pwd)
                    print("[+] Encrypted token:\n" + token)
                case "decrypt":
                    token = args[1] if len(args) > 1 else input("Ciphertext: ")
                    pwd = getpass.getpass("Passphrase: ")

                    if failures >= 3:
                        delay = min(2 ** (failures - 2), 60)
                        print(f"[!] Too many failed attempts. Sleeping {delay}s...")
                        time.sleep(delay)

                    result = decrypt(token, pwd)
                    print(result)
                    failures = failures + 1 if result.startswith("[!]") else 0
                case "genkey":
                    generate_key()
                case "update":
                    update_self()
                case _:
                    print("[!] Unknown command.")
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Exiting Z-HESP2.")
            break
        except Exception as err:
            print(f"[!] Error: {err}")

# ─────────────────────────────── Entrypoint ─────────────────────────────── #
if __name__ == "__main__":
    main()
