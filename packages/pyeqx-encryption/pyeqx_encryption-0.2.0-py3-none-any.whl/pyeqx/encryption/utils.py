from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2


def random_passphrase(password: str, iterations: int = 100000):
    """
    Generate a random passphrase from a base password using PBKDF2.

    Args:
        password (str): The base password to derive the passphrase from.
        iterations (int): The number of iterations for PBKDF2. Default is 100000.

    Returns:
        str: A derived passphrase in hexadecimal format.

    Raises:
        ValueError: If the base password is less than 8 characters long.
    """

    if len(password) < 8:
        raise ValueError("Base password must be at least 8 characters long")

    # Use cryptographically secure random salt
    salt = get_random_bytes(32)

    # Use higher iteration count for better security
    return PBKDF2(password, salt, dkLen=32, count=iterations).hex()
