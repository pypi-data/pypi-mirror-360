from argparse import ArgumentParser


def add_kyber512_commands(parser: ArgumentParser):
    subparsers = parser.add_subparsers(
        title="commands",
        description="Available commands for encryption and key management.",
        dest="command",
        required=True,
        help="Available commands",
    )

    __add_keygen_command(
        subparsers.add_parser(
            "keygen",
            help="Generate a Kyber512 public/private key pair (for one party).",
        )
    )
    __add_encapsulate_command(
        subparsers.add_parser(
            "encapsulate",
            help="Encapsulate a shared secret using a recipient's Kyber public key. "
            "Outputs Kyber ciphertext, ephemeral shared secret, and derived AES key/salt.",
        )
    )
    __add_decapsulate_command(
        subparsers.add_parser(
            "decapsulate",
            help="Decapsulate the shared secret using a sender's Kyber private key and the Kyber ciphertext from recipient. "
            "Outputs recovered shared secret and derived AES key.",
        )
    )
    __add_encrypt_file_command(
        subparsers.add_parser(
            "encrypt-file", help="Encrypt a file using a pre-derived AES-256-GCM key."
        )
    )
    __add_decrypt_file_command(
        subparsers.add_parser(
            "decrypt-file", help="Decrypt a file using a pre-derived AES-256-GCM key."
        )
    )

    return parser


def __add_keygen_command(parser: ArgumentParser):
    parser.add_argument(
        "--public-out", required=True, help="Output file for the Kyber public key."
    )
    parser.add_argument(
        "--private-out", required=True, help="Output file for the Kyber private key."
    )


def __add_encapsulate_command(parser: ArgumentParser):
    parser.add_argument(
        "--public-in",
        required=True,
        help="Input file for the recipient's Kyber public key.",
    )
    parser.add_argument(
        "--ciphertext-out",
        required=True,
        help="Output file for the Kyber ciphertext (to be sent to sender).",
    )
    parser.add_argument(
        "--shared-secret-out",
        required=True,
        help="Output file for the ephemeral shared secret (for the recipient).",
    )
    parser.add_argument(
        "--aes-key-out",
        required=True,
        help="Output file for the derived AES key (for the recipient).",
    )
    parser.add_argument(
        "--salt-out",
        required=True,
        help="Output file for the HKDF salt (to be sent to sender).",
    )


def __add_decapsulate_command(parser: ArgumentParser):
    parser.add_argument(
        "--private-in",
        required=True,
        help="Input file for the sender's Kyber private key.",
    )
    parser.add_argument(
        "--ciphertext-in",
        required=True,
        help="Input file for the Kyber ciphertext (received from recipient).",
    )
    parser.add_argument(
        "--salt-in",
        required=True,
        help="Input file for the HKDF salt (received from recipient).",
    )
    parser.add_argument(
        "--shared-secret-out",
        required=True,
        help="Output file for the recovered shared secret (for the sender).",
    )
    parser.add_argument(
        "--aes-key-out",
        required=True,
        help="Output file for the derived AES key (for the sender).",
    )


def __add_encrypt_file_command(parser: ArgumentParser):
    parser.add_argument(
        "--aes-key-in", required=True, help="Input file for the derived AES key."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input file containing plaintext data to encrypt.",
    )
    parser.add_argument(
        "--output-ciphertext",
        required=True,
        help="Output file for the encrypted ciphertext.",
    )
    parser.add_argument(
        "--output-nonce", required=True, help="Output file for the AES GCM nonce."
    )
    parser.add_argument(
        "--output-tag",
        required=True,
        help="Output file for the AES GCM authentication tag.",
    )
    parser.add_argument(
        "--associated-data",
        help="Optional associated data (string) to bind to the ciphertext for integrity protection.",
    )


def __add_decrypt_file_command(parser: ArgumentParser):
    parser.add_argument(
        "--aes-key-in", required=True, help="Input file for the derived AES key."
    )
    parser.add_argument(
        "--input", required=True, help="Input file containing ciphertext."
    )
    parser.add_argument(
        "--input-nonce", required=True, help="Input file for the AES GCM nonce."
    )
    parser.add_argument(
        "--input-tag",
        required=True,
        help="Input file for the AES GCM authentication tag.",
    )
    parser.add_argument(
        "--output", required=True, help="Output file for the decrypted plaintext data."
    )
    parser.add_argument(
        "--associated-data",
        help="Optional associated data (string) used during encryption. Must match exactly.",
    )
