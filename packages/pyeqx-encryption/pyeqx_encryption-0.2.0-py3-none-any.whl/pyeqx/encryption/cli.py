from argparse import ArgumentParser, Namespace
import logging
import os
import stat
from sys import stderr

from cryptography.exceptions import InvalidTag

from pyeqx.encryption.cli_kyber512 import add_kyber512_commands
from pyeqx.encryption.cli_pgp import add_pgp_commands
from pyeqx.encryption.kyber512 import (
    decapsulate_kyber_shared_secret,
    decrypt_data_aes_gcm,
    derive_aes_key,
    encapsulate_kyber_shared_secret,
    encrypt_data_aes_gcm,
    generate_kyber_key_pair,
)
from pyeqx.encryption.pgp import (
    pgp_decrypt_file,
    pgp_encrypt_file,
    pgp_generate_key_pair,
)

logger = logging.getLogger("pyeqx.encryption.cli")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stderr))


def __parse_arguments():
    parser = ArgumentParser(
        description="A command-line tool for multiple encryption algorithms including Kyber512 + HKDF-SHA256 + AES-256-GCM, GPG, and more."
    )

    # add subparsers for different encryption algorithms
    subparsers = parser.add_subparsers(
        dest="algorithm", help="Available encryption algorithms"
    )
    subparsers.required = True

    # create Kyber512 parser
    kyber512_parser = subparsers.add_parser(
        "kyber512",
        description="A command-line tool for Kyber512 + HKDF-SHA256 + AES-256-GCM encryption.",
        aliases=["kyber"],
        help="Kyber512 + HKDF-SHA256 + AES-256-GCM encryption.",
    )

    # add Kyber512 specific commands
    add_kyber512_commands(kyber512_parser)

    # create PGP parser
    pgp_parser = subparsers.add_parser(
        "pgp",
        description="A command-line tool for PGP encryption and decryption.",
        help="PGP encryption and decryption.",
    )

    # add PGP specific commands
    add_pgp_commands(pgp_parser)

    return parser.parse_args()


def save_to_file(data: bytes, filename: str):
    """
    Save binary data to a file.
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(data)

        os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR)
        logger.info(f"Saved {len(data)} bytes to {filename}")
    except IOError as e:
        logger.error(f"Could not write to file {filename}: {e}", exc_info=True)
        exit(1)


def load_from_file(filename: str) -> bytes:
    """
    Load binary data from a file.
    """
    try:
        with open(filename, "rb") as f:
            data = f.read()
        logger.info(f"Loaded {len(data)} bytes from {filename}")
        return data
    except FileNotFoundError:
        logger.error(f"File {filename} not found.", exc_info=True)
        exit(1)
    except IOError as e:
        logger.error(f"Could not read from file {filename}: {e}", exc_info=True)
        exit(1)


def execute_kyber512_command(args: Namespace):
    if args.command == "keygen":
        logger.info("Generating Kyber512 key pair...")
        private_key, public_key = generate_kyber_key_pair()
        save_to_file(public_key, args.public_out)
        save_to_file(private_key, args.private_out)
        logger.info("Kyber key pair generation complete.")
    elif args.command == "encapsulate":
        logger.info("Encapsulating shared secret using Kyber512 public key...")
        public_key = load_from_file(args.public_in)

        # Encapsulate shared secret using Kyber512 public key
        cipher_text, ephemeral_shared_secret = encapsulate_kyber_shared_secret(
            public_key
        )
        save_to_file(cipher_text, args.ciphertext_out)
        save_to_file(ephemeral_shared_secret, args.shared_secret_out)

        aes_key, salt = derive_aes_key(ephemeral_shared_secret)
        save_to_file(aes_key, args.aes_key_out)
        save_to_file(salt, args.salt_out)
        logger.info("Encapsulation complete. AES key and salt derived.")
    elif args.command == "decapsulate":
        logger.info(
            "Decapsulating shared secret using Kyber512 private key and ciphertext..."
        )
        private_key = load_from_file(args.private_in)
        cipher_text = load_from_file(args.ciphertext_in)
        aes_salt = load_from_file(args.salt_in)

        recovered_shared_secret = decapsulate_kyber_shared_secret(
            private_key, cipher_text
        )
        save_to_file(recovered_shared_secret, args.shared_secret_out)

        aes_key, _ = derive_aes_key(recovered_shared_secret, salt=aes_salt)
        save_to_file(aes_key, args.aes_key_out)
        logger.info("Decapsulation complete. AES key derived.")
    elif args.command == "encrypt-file":
        logger.info("Encrypting file using AES-256-GCM with derived key...")
        aes_key = load_from_file(args.aes_key_in)
        plaintext = load_from_file(args.input)
        associated_data = (
            args.associated_data.encode("utf-8") if args.associated_data else None
        )

        nonce, cipher_text, tag = encrypt_data_aes_gcm(
            aes_key, plaintext, associated_data
        )
        save_to_file(cipher_text, args.output_ciphertext)
        save_to_file(nonce, args.output_nonce)
        save_to_file(tag, args.output_tag)
        logger.info("File encryption complete. Ciphertext, nonce, and tag saved.")
    elif args.command == "decrypt-file":
        logger.info("Decrypting file using AES-256-GCM with derived key...")
        aes_key = load_from_file(args.aes_key_in)
        cipher_text = load_from_file(args.input)
        nonce = load_from_file(args.input_nonce)
        tag = load_from_file(args.input_tag)
        associated_data = (
            args.associated_data.encode("utf-8") if args.associated_data else None
        )

        decrypted_data = decrypt_data_aes_gcm(
            aes_key, nonce, cipher_text, tag, associated_data
        )
        save_to_file(decrypted_data, args.output)
        logger.info("File decryption complete. Decrypted data saved.")


def execute_pgp_command(args: Namespace):
    if args.command == "keygen":
        logger.info("Generating PGP key pair...")

        private_key, public_key = pgp_generate_key_pair(
            pn=args.name, email=args.email, passphrase=args.passphrase
        )

        save_to_file(f"{public_key}".encode(), args.public_out)
        save_to_file(f"{private_key}".encode(encoding="utf-8"), args.private_out)
        logger.info("Kyber key pair generation complete.")

    elif args.command == "encrypt-file":
        logger.info("Encrypting file using PGP public key...")

        encrypted = pgp_encrypt_file(
            file_path=args.input,
            key_file_path=args.key,
            output_file_path=args.output,
        )

        save_to_file(f"{encrypted}".encode(encoding="utf-8"), args.output)

        logger.info(f"File encrypted successfully, saved to {args.output}")
    elif args.command == "decrypt-file":
        logger.info("Decrypting PGP encrypted file using private key...")

        print(args)

        decrypted = pgp_decrypt_file(
            file_path=args.input,
            key_file_path=args.key,
            passphrase=args.passphrase if "passphrase" in args else None,
            output_file_path=args.output,
        )

        save_to_file(f"{decrypted}".encode(encoding="utf-8"), args.output)
        logger.info(f"File decrypted successfully, saved to {args.output}")
    else:
        logger.error(f"Unsupported command: {args.command}")
        exit(1)


def main():
    try:
        args = __parse_arguments()

        if args.algorithm == "kyber" or args.algorithm == "kyber512":
            execute_kyber512_command(args)
        elif args.algorithm == "pgp":
            execute_pgp_command(args)
        else:
            logger.error(f"Unsupported algorithm: {args.algorithm}")
            exit(1)
    except InvalidTag:
        logger.error(
            "Decryption failed: Invalid authentication tag. The ciphertext may have been tampered with or the wrong key was used."
        )
        exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
