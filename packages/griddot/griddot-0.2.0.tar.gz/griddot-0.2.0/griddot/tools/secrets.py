import base64
import json
import os
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key


def get_repository_path():
    """Get the repository root path"""
    current_path = Path(__file__).resolve()

    while current_path.parent != current_path:
        if (current_path / '.git').exists():
            return current_path
        current_path = current_path.parent
    return Path.cwd()


def rsa_generate():
    """Generate RSA key pair and return as PEM strings"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_pem, public_pem


def rsa_encrypt(public_key_pem, plaintext):
    """Encrypt plaintext using RSA public key"""
    public_key = load_pem_public_key(public_key_pem.encode('utf-8'))

    encrypted = public_key.encrypt(
        plaintext.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Convert to base64 for storage
    import base64
    return base64.b64encode(encrypted).decode('utf-8')


def hybrid_encrypt(public_key_pem: str, plaintext: str) -> str:
    """Encrypt plaintext using AES, then encrypt AES key with RSA"""
    public_key = load_pem_public_key(public_key_pem.encode('utf-8'))

    # Generate AES key and nonce
    aes_key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)

    # Encrypt plaintext with AES
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)

    # Encrypt AES key with RSA
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Return combined encrypted data as JSON
    payload = {
        "key": base64.b64encode(encrypted_key).decode('utf-8'),
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "data": base64.b64encode(ciphertext).decode('utf-8')
    }
    return json.dumps(payload)


def hybrid_decrypt(private_key_pem: str, encrypted_payload: str) -> str:
    """Decrypt AES key using RSA, then decrypt data using AES"""
    private_key = load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
    payload = json.loads(encrypted_payload)

    aes_key = private_key.decrypt(
        base64.b64decode(payload["key"]),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    aesgcm = AESGCM(aes_key)
    nonce = base64.b64decode(payload["nonce"])
    ciphertext = base64.b64decode(payload["data"])

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')


def rsa_decrypt(private_key_pem, encrypted_text):
    """Decrypt ciphertext using RSA private key"""
    private_key = load_pem_private_key(private_key_pem.encode('utf-8'), password=None)

    # Decode from base64
    import base64
    encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))

    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted.decode('utf-8')


def decrypt_secrets(files: list[str]):
    """Decrypt the encrypted secrets file using the private key"""
    repo_path = get_repository_path()
    print(f"🔍  Found repo at: {repo_path}")

    private_key_path = repo_path / ".secrets" / "key.pem"

    if not private_key_path.exists():
        print(f"❌ Cannot decrypt files because you don't have private key {private_key_path}, check passwork.me")
        return

    if len(files) == 0:
        files = list(repo_path.rglob('*.encrypted'))
        if len(files) == 0:
            print("❌ No .encrypted files found in the repository")
            return

    full_paths = [Path(file).resolve() for file in files]
    for file in full_paths:
        if not file.exists():
            print(f"❌ File {file} does not exist, skipping")
            continue

        private_pem = private_key_path.read_text(encoding='utf-8')
        encrypted_content = file.read_text(encoding='utf-8')

        decrypted = hybrid_decrypt(private_pem, encrypted_content)

        # Remove the ".encrypted" suffix
        secret_file_path = file.with_suffix('')
        if secret_file_path.exists():
            old_content = secret_file_path.read_text(encoding='utf-8')
            if old_content != decrypted:
                print(f"Overwriting old content with new one, old content:\n{old_content}")
            else:
                print(f"✅  Decrypted content is the same as existing content, skipping write to {secret_file_path}")
                continue

        secret_file_path.write_text(decrypted)
        print(f"✅  Generated file {secret_file_path} from {file}")


def create_new_key():
    """Create a new RSA key pair for secret encryption"""
    repo_path = get_repository_path()
    print(f"🔍 Found repo at: {repo_path}")

    private_key_path = repo_path / ".secrets" / "key.pem"
    public_key_path = repo_path / "key.pub"

    if private_key_path.exists():
        print(f"❌ Cannot create new key because you already have a private key {private_key_path}")
        return

    private_key_path.parent.mkdir(parents=True, exist_ok=True)
    pem_private, pem_public = rsa_generate()

    private_key_path.write_text(pem_private)
    public_key_path.write_text(pem_public)

    print(f"✅  Generated private key: {private_key_path}")
    print(f"✅  Generated public key: {public_key_path}")


def encrypt_secrets(files: list[str]):
    """Encrypt secrets files using the public key"""
    repo_path = get_repository_path()
    print(f"🔍 Found repo at: {repo_path}")

    public_key_path = repo_path / "key.pub"

    if not public_key_path.exists():
        print(f"❌ Cannot encrypt secrets file because you don't have public key {public_key_path}, check passwork.me")
        return

    if len(files) == 0:
        files = list(repo_path.rglob('*.encrypted'))
        files = [str(file).replace('.encrypted', '') for file in files if file.is_file()]
        if len(files) == 0:
            print("❌ No files found in the repository")
            return

    full_paths = [Path(file).resolve() for file in files]
    for file in full_paths:
        if not file.exists():
            print(f"❌ File {file} does not exist, skipping")
            continue

        public_pem = public_key_path.read_text(encoding='utf-8')
        plaintext = file.read_text(encoding='utf-8')

        encrypted = hybrid_encrypt(public_pem, plaintext)

        encrypted_file_path = file.with_suffix(file.suffix + '.encrypted')
        encrypted_file_path.write_text(encrypted)
        print(f"✅  Encrypted file created: {encrypted_file_path}")
