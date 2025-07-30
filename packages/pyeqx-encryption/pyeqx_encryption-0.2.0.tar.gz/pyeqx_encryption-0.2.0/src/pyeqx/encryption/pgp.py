import os
from typing import Optional
from pgpy import PGPKey, PGPMessage, PGPUID
from pgpy.constants import PubKeyAlgorithm, SymmetricKeyAlgorithm, HashAlgorithm
from datetime import timedelta


def pgp_encrypt_file(
    file_path: str, key_file_path: str, output_file_path: Optional[str] = None
) -> str:
    """
    Encrypt a file using PGP with the provided public key.

    Args:
        file_path (str): Path to the file to be encrypted.
        key_file_path (str): Path to the PGP public key file.
        output_file_path (Optional[str]): Path to save the encrypted file.
            If not provided, the encrypted file will be saved with a '.encrypted' extension.

    Returns:
        str: Path to the encrypted file.
    """
    if output_file_path is None:
        output_file_path = f"{file_path}.encrypted"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File to encrypt not found: {file_path}")

    if not os.path.exists(key_file_path):
        raise FileNotFoundError(f"Key file not found: {key_file_path}")

    key, _ = PGPKey.from_file(key_file_path)
    key._require_usage_flags = False
    message = PGPMessage.new(file_path, file=True)

    encrypted_message = key.encrypt(message)

    return encrypted_message


def pgp_decrypt_file(
    file_path: str,
    key_file_path: str,
    passphrase: Optional[str] = None,
    output_file_path: Optional[str] = None,
):
    """
    Decrypt a PGP encrypted file.

    Args:
        file_path (str): Path to the encrypted file.
        key_file_path (str): Path to the PGP private key file.
        passphrase (Optional[str]): Passphrase for the private key, if it is protected.
    """
    if output_file_path is None:
        output_file_path = f"{file_path}.decrypted"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File to decrypt not found: {file_path}")

    if not os.path.exists(key_file_path):
        raise FileNotFoundError(f"Key file not found: {key_file_path}")

    key, _ = PGPKey.from_file(key_file_path)

    if passphrase:
        key.unlock(passphrase)

    encrypted_message = PGPMessage.from_file(file_path)
    decrypted_message = key.decrypt(encrypted_message)

    return decrypted_message


def pgp_generate_key_pair(pn: bytearray, email: str, passphrase: Optional[str] = None):
    """
    Generate a PGP key pair.
    This function uses the PGP implementation to generate a public-private key pair.

    Returns:
        tuple: (private_key, public_key)
            - private_key: The private key in bytes.
            - public_key: The public key in bytes.
    """
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    uid = PGPUID.new(pn=pn, email=email)

    key.add_uid(uid, key_expiration=timedelta(days=365))

    if passphrase:
        key.protect(passphrase, SymmetricKeyAlgorithm.AES256, HashAlgorithm.SHA256)

    private_key = key
    public_key = key.pubkey

    return private_key, public_key
