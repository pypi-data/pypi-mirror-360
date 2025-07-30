# esbm-pyeqx-encryption

An encryption library for using in `pyeqx` ecosystem.

Currently support encryption features:

- `Kyber512` - Key Encapsulation Mechanism - KEM
- `HKDF-SHA256` - HKDF-SHA256 (HMAC-based Key Derivation Function)
- `AES 256 GCM` - AES-256-GCM (Advanced Encryption Standard with Galois/Counter Mode)

status: `in development`

## Installation

This is an instruction to prepare your local machine to use and/or develop this library.

### Pre-requisites

To setup virtual environment to execute unit tests, it has to setup virtual env and install dependencies

```bash
# setup virtual env
python3.12 -m venv .venv

# activate virtual env
source .venv/bin/activate
```

To setup `vscode`, run `yarn install` which will setup and configure the `vscode` to support formatting, linting, and etc.

```bash
#
yarn install
```

## Project Structure

```markdown
pyeqx-encryption-cli/
├── src/
│ └── pyeqx/
│ └── encryption/ # The actual Python package
│ ├── **init**.py # Defines the package and exposes core functions
│ ├── cli.py # Command-line interface logic
│ └── core.py # Core cryptographic functions (Kyber, HKDF, AES)
├── test/ # Unit tests for the core logic
│ └── pyeqx/
│ └── encryption/ # The actual Python package
│ ├── test_core.py
│ └── test_cli_keygen.py
├── .gitignore # Specifies files/directories to ignore by Git
├── LICENSE # Licensing information (e.g., MIT)
├── pyproject.toml # Modern project metadata, dependencies, and build configuration
├── README.md # Project overview, installation, and usage instructions
└── requirements.txt # Development dependencies
```

## Usage

### Development

to execute unit test run this command at root of the project

```bash
pytest -s
```

#### Build

to build the package run this command at root of the project

```bash
python3 -m pip install --upgrade build
python3 -m build
```

### CLI

First, execute this command `pip3 install -e .` to install current as python binary.

To generate key-pair, execute following command

```bash
pyeqx-encryption-cli keygen --public-out .tmp/alice_public.key --private-out .tmp/alice_private.key
```

To encapsulate `Alice` public key for `Bob` to send `cipher_text` and `salt` to `Alice`

```bash
pyeqx-encryption-cli encapsulate \
  --public-in .tmp/alice_public.key \
  --ciphertext-out .tmp/bob_kyber_ciphertext.bin \
  --shared-secret-out .tmp/bob_secret.bin \
  --aes-key-out .tmp/bob_aes_key.bin \
  --salt-out .tmp/bob_aes_salt.bin
```

To decapsulate `cipher_text` and `salt` from `Bob`

```bash
pyeqx-encryption-cli decapsulate --private-in .tmp/alice_private.key \
  --ciphertext-in .tmp/bob_kyber_ciphertext.bin \
  --salt-in .tmp/bob_aes_salt.bin \
  --shared-secret-out .tmp/alice_recovered_secret.bin \
  --aes-key-out .tmp/alice_aes_key.bin
```

To verify both aes key are identical, just `hexdump`, it should be identical

```bash
hexdump -C alice_aes_key.bin
hexdump -C bob_aes_key.bin
```

To encrypt the file

```bash
pyeqx-encryption-cli encrypt-file --aes-key-in .tmp/alice_aes_key.bin \
  --input .tmp/secret_document.txt \
  --output-ciphertext .tmp/encrypted_message.bin \
  --output-nonce .tmp/message_nonce.bin \
  --output-tag .tmp/message_tag.bin \
  --associated-data "Project_Alpha_Report"
```

To decrypt the file

```bash
pyeqx-encryption-cli decrypt-file --aes-key-in .tmp/bob_aes_key.bin \
  --input .tmp/encrypted_message.bin \
  --input-nonce .tmp/message_nonce.bin \
  --input-tag .tmp/message_tag.bin \
  --output .tmp/decrypted_document.txt \
  --associated-data "Project_Alpha_Report"
```

### Scenario

The usage scenario for a 2-party secure file exchange. The scenario is `Alice` send a secret file to `Bob`

Please see [docs/scenario.md](docs/scenario.md)
