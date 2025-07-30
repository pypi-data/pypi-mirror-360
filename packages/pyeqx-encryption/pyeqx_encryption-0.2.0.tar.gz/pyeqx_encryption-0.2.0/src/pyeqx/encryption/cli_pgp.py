from argparse import ArgumentParser


def add_pgp_commands(parser: ArgumentParser):
    """
    Add PGP specific commands to the parser.
    """
    subparsers = parser.add_subparsers(
        title="commands",
        description="Available commands for PGP encryption and decryption.",
        dest="command",
        required=True,
        help="Available commands",
    )

    __add_keygen_command(
        subparsers.add_parser(
            "keygen",
            help="Generate a PGP public/private key pair (for one party).",
        )
    )

    __add_encrypt_file_command(
        subparsers.add_parser(
            "encrypt-file",
            help="Encrypt a file using a PGP public key.",
        )
    )

    __add_decrypt_file_command(
        subparsers.add_parser(
            "decrypt-file",
            help="Decrypt a PGP encrypted file using a private key.",
        )
    )


def __add_encrypt_file_command(parser: ArgumentParser):
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the file to be encrypted.",
    )
    parser.add_argument(
        "-k",
        "--key",
        type=str,
        required=True,
        help="Path to the PGP public key file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to save the encrypted file. If not provided, the file will be saved with a '.encrypted' extension.",
    )


def __add_decrypt_file_command(parser: ArgumentParser):
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the encrypted file.",
    )
    parser.add_argument(
        "-k",
        "--key",
        type=str,
        required=True,
        help="Path to the PGP private key file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to save the decrypted file. If not provided, the file will be saved with a '.decrypted' extension.",
    )


def __add_keygen_command(parser: ArgumentParser):
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="Name for the key pair.",
    )
    parser.add_argument(
        "-e",
        "--email",
        type=str,
        required=True,
        help="Email address associated with the key pair.",
    )
    parser.add_argument(
        "-p",
        "--passphrase",
        type=str,
        default=None,
        help="Optional passphrase for the private key.",
    )
    parser.add_argument(
        "--public-out",
        type=str,
        required=True,
        help="Path to save the generated public key.",
    )
    parser.add_argument(
        "--private-out",
        type=str,
        required=True,
        help="Path to save the generated private key.",
    )
