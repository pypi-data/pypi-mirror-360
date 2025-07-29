import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import base64
import json
import getpass
from datetime import datetime

KEY_FILE = ".envveil.key"
ENCRYPTED_FILE = ".env.encrypted"
AUDIT_LOG = "envveil_audit.log"

def generate_key(key_path=KEY_FILE):
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)
    else:
        with open(key_path, "rb") as f:
            key = f.read()
    return key

def get_fernet(key_path=KEY_FILE):
    key = generate_key(key_path)
    return Fernet(key)

def derive_key_from_passphrase(passphrase: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(passphrase.encode())
    return base64.urlsafe_b64encode(key), salt

def ensure_gitignore_entries(entries=None, gitignore_path=".gitignore"):
    if entries is None:
        entries = [ENCRYPTED_FILE, KEY_FILE]
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
    else:
        lines = []
    updated = False
    for entry in entries:
        if entry not in lines:
            lines.append(entry)
            updated = True
    if updated:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    return updated

def warn_if_key_not_ignored(key_path=KEY_FILE, gitignore_path=".gitignore"):
    if not os.path.exists(gitignore_path):
        print(f"[envveil WARNING] {gitignore_path} does not exist. Please add {key_path} to it to avoid leaking your encryption key.")
        return
    with open(gitignore_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    if key_path not in lines:
        print(f"[envveil WARNING] {key_path} is not in {gitignore_path}. Please add it to avoid leaking your encryption key.")

def log_audit_event(action, file_path):
    user = getpass.getuser()
    timestamp = datetime.utcnow().isoformat()
    with open(AUDIT_LOG, "a", encoding="utf-8") as log:
        log.write(f"{timestamp} | {user} | {action} | {file_path}\n")

def encrypt_secrets(secrets: dict, encrypted_path=ENCRYPTED_FILE, key_path=KEY_FILE, passphrase: str = None):
    if passphrase:
        key, salt = derive_key_from_passphrase(passphrase)
        f = Fernet(key)
    else:
        f = get_fernet(key_path)
        salt = None
        warn_if_key_not_ignored(key_path)
    lines = [f"{k}={v}" for k, v in secrets.items()]
    data = "\n".join(lines).encode()
    encrypted = f.encrypt(data)
    if passphrase:
        with open(encrypted_path, "w", encoding="utf-8") as ef:
            json.dump({"salt": base64.b64encode(salt).decode(), "data": base64.b64encode(encrypted).decode()}, ef)
    else:
        with open(encrypted_path, "wb") as ef:
            ef.write(encrypted)
    ensure_gitignore_entries()
    return encrypted_path

def decrypt_secrets(encrypted_path=ENCRYPTED_FILE, key_path=KEY_FILE, passphrase: str = None):
    if passphrase:
        with open(encrypted_path, "r", encoding="utf-8") as ef:
            obj = json.load(ef)
            salt = base64.b64decode(obj["salt"])
            encrypted = base64.b64decode(obj["data"])
        key, _ = derive_key_from_passphrase(passphrase, salt)
        f = Fernet(key)
    else:
        f = get_fernet(key_path)
        with open(encrypted_path, "rb") as ef:
            encrypted = ef.read()
    decrypted = f.decrypt(encrypted).decode()
    secrets = {}
    for line in decrypted.splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            secrets[k] = v
    log_audit_event("decrypt", encrypted_path)
    return secrets

def rotate_key(encrypted_path=ENCRYPTED_FILE, old_key_path=KEY_FILE, old_passphrase=None, new_key_path=None, new_passphrase=None):
    if old_passphrase:
        secrets = decrypt_secrets(encrypted_path, passphrase=old_passphrase)
    else:
        secrets = decrypt_secrets(encrypted_path, key_path=old_key_path)
    if new_passphrase:
        encrypt_secrets(secrets, encrypted_path=encrypted_path, passphrase=new_passphrase)
        log_audit_event("rotate_key (passphrase)", encrypted_path)
        return encrypted_path, None
    else:
        if new_key_path:
            key = Fernet.generate_key()
            with open(new_key_path, "wb") as f:
                f.write(key)
            fernet = Fernet(key)
            lines = [f"{k}={v}" for k, v in secrets.items()]
            data = "\n".join(lines).encode()
            encrypted = fernet.encrypt(data)
            with open(encrypted_path, "wb") as ef:
                ef.write(encrypted)
            ensure_gitignore_entries(entries=[encrypted_path, new_key_path])
            log_audit_event("rotate_key (new_key)", encrypted_path)
            warn_if_key_not_ignored(new_key_path)
            return encrypted_path, new_key_path
        else:
            encrypt_secrets(secrets, encrypted_path=encrypted_path, key_path=KEY_FILE)
            log_audit_event("rotate_key (default_key)", encrypted_path)
            warn_if_key_not_ignored(KEY_FILE)
            return encrypted_path, KEY_FILE 