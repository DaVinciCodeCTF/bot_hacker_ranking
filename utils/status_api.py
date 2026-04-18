import base64
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any

import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)


@dataclass
class ServiceStatus:
    service_name: str
    status: str
    latency: str | int | float
    message: str
    timestamp: str


def decrypt_status_payload(payload: Dict[str, Any], key_b64: str) -> Dict[str, Any]:
    nonce_b64 = payload.get("nonce")
    ciphertext_b64 = payload.get("ciphertext")
    algorithm = payload.get("algorithm")

    if not nonce_b64 or not ciphertext_b64:
        raise ValueError("Invalid encrypted payload: missing nonce/ciphertext")
    if algorithm != "AES-256-GCM":
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    key = base64.b64decode(key_b64)
    if len(key) != 32:
        raise ValueError("STATUS_API_KEY must decode to 32 bytes")

    nonce = base64.b64decode(nonce_b64)
    ciphertext = base64.b64decode(ciphertext_b64)

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))


def fetch_and_decrypt_status(url: str, key_b64: str, timeout: int = 8) -> Dict[str, Any]:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    encrypted_payload = resp.json()
    return decrypt_status_payload(encrypted_payload, key_b64)
