import os
from typing import Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import pqcrypto.kem.ml_kem_512 as Kyber512


def generate_kyber_key_pair():
    """
    Generate a key pair using the Kyber512 algorithm.
    This function uses the Kyber512 implementation from the pqcrypto library to generate a public-private key pair.

    Returns:
        tuple: (private_key, public_key)
            - private_key: The private key in bytes.
            - public_key: The public key in bytes.
    """
    public_key, private_key = Kyber512.generate_keypair()
    return private_key, public_key


def encapsulate_kyber_shared_secret(public_key: bytes):
    """
    Encapsulate a shared secret using the provided public key.
    This function uses the Kyber512 implementation from the pqcrypto library to encapsulate a shared secret.

    Args:
        public_key (bytes): The public key to use for encapsulation in bytes.

    Returns:
        tuple: (cipher_text, shared_secret)
            - cipher_text: The encapsulated cipher text, in bytes.
            - shared_secret: The ephemeral shared secret, in bytes.
    """
    cipher_text, shared_secret = Kyber512.encrypt(public_key)
    return cipher_text, shared_secret


def decapsulate_kyber_shared_secret(private_key: bytes, cipher_text: bytes):
    """
    Decapsulate a shared secret using the provided private key and cipher text.
    This function uses the Kyber512 implementation from the pqcrypto library to decapsulate a shared secret.

    Args:
        private_key (bytes): The private key to use for decapsulation in bytes.
        cipher_text (bytes): The cipher text to decapsulate in bytes.

    Returns:
        shared_secret (bytes): The decapsulated shared secret, in bytes.
    """
    shared_secret = Kyber512.decrypt(private_key, cipher_text)
    return shared_secret


def derive_aes_key(
    shared_secret: bytes, salt: Optional[bytes] = None, info: bytes = b"aes-256-gcm-key"
):
    """
    Derives a 256-bit (32-byte) AES key using HKDF-SHA256 from the shared secret.

    Args:
        shared_secret: The shared secret to derive the AES key from, in bytes.
        salt: Optional salt for HKDF. If None, a new random salt will be generated.
        info: Optional context information for HKDF. Defaults to b"aes-256-gcm-key".


    Returns:
        tuple: (key, salt)
            - key (bytes): The derived AES key, in bytes.
            - salt (bytes): The salt used for HKDF, in bytes.
    """
    if salt is None:
        salt = os.urandom(16)

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes (256 bits) for AES-256
        salt=salt,
        info=info,
        backend=default_backend(),
    )
    key = hkdf.derive(shared_secret)
    return key, salt


def encrypt_data_aes_gcm(key: bytes, plain_text: bytes, associated_data: bytes = None):
    """
    Encrypts data using AES-256-GCM.

    Args:
        key (bytes): The AES key to use for encryption, in bytes.
        plaintext (bytes): The plaintext data to encrypt, in bytes.
        associated_data (bytes): Optional associated data for GCM authentication, in bytes.

    Returns:
        tuple: (nonce, cipher_text, tag)
            - nonce (bytes): The nonce used for encryption, in bytes.
            - cipher_text (bytes): The encrypted data, in bytes.
            - tag (bytes): The GCM authentication tag, in bytes.
    """
    nonce = os.urandom(12)

    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()

    if associated_data:
        encryptor.authenticate_additional_data(associated_data)

    cipher_text = encryptor.update(plain_text) + encryptor.finalize()
    tag = encryptor.tag
    return nonce, cipher_text, tag


def decrypt_data_aes_gcm(
    key: bytes,
    nonce: bytes,
    cipher_text: bytes,
    tag: bytes,
    associated_data: Optional[bytes] = None,
):
    """
    Decrypts data using AES-256-GCM.

    Args:
        key (bytes): The AES key to use for decryption, in bytes.
        nonce (bytes): The nonce used for encryption, in bytes.
        cipher_text (bytes): The encrypted data to decrypt, in bytes.
        tag (bytes): The GCM authentication tag, in bytes.
        associated_data (bytes, optional): Optional associated data for GCM authentication, in bytes.

    Returns:
        plain_text (bytes): The decrypted plaintext data, in bytes.

    Raises:
        cryptography.exceptions.InvalidTag: If the GCM authentication tag does not match, indicating tampering or incorrect key/nonce.
    """

    cipher = Cipher(
        algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend()
    )
    decryptor = cipher.decryptor()

    if associated_data:
        decryptor.authenticate_additional_data(associated_data)

    plain_text = decryptor.update(cipher_text) + decryptor.finalize()
    return plain_text
