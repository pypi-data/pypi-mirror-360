import argparse
from .scanner import scan_env_file, scan_project_repository
from .encryptor import encrypt_secrets, ensure_gitignore_entries, decrypt_secrets, rotate_key
from .patterns import find_files_by_patterns
import os
import requests

def main():
    parser = argparse.ArgumentParser(description="envveil: Scan and encrypt sensitive keys in your project.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan .env for sensitive keys.")
    scan_parser.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    encrypt_parser = subparsers.add_parser("encrypt", help="Scan and encrypt sensitive keys from .env.")
    encrypt_parser.add_argument("--env", default=".env", help="Path to .env file (default: .env)")
    encrypt_parser.add_argument("--passphrase", default=None, help="Passphrase for encryption (optional)")

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt and print secrets from .env.encrypted.")
    decrypt_parser.add_argument("--key", default=None, help="Path to key file (default: .envveil.key)")
    decrypt_parser.add_argument("--passphrase", default=None, help="Passphrase for decryption (if used)")
    decrypt_parser.add_argument("--encrypted", default=None, help="Path to encrypted file (default: .env.encrypted)")

    rotate_parser = subparsers.add_parser("rotate-key", help="Rotate the encryption key or passphrase and re-encrypt secrets.")
    rotate_parser.add_argument("--old-key", default=None, help="Path to old key file (default: .envveil.key)")
    rotate_parser.add_argument("--old-passphrase", default=None, help="Old passphrase (if used)")
    rotate_parser.add_argument("--new-key", default=None, help="Path to new key file (optional)")
    rotate_parser.add_argument("--new-passphrase", default=None, help="New passphrase (if used)")
    rotate_parser.add_argument("--encrypted", default=None, help="Path to encrypted file (default: .env.encrypted)")

    gitignore_parser = subparsers.add_parser("gitignore", help="Fetch and update .gitignore for a language.")
    gitignore_parser.add_argument("language", help="Programming language (e.g. python, node, java)")
    gitignore_parser.add_argument("--replace", action="store_true", help="Replace .gitignore with the selected template")

    retrofit_parser = subparsers.add_parser("retrofit", help="Retroactively protect secrets in an already-pushed repo.")
    retrofit_parser.add_argument("--env", default=".env", help="Path to .env file (default: .env)")
    retrofit_parser.add_argument("--passphrase", default=None, help="Passphrase for encryption (optional)")

    scanall_parser = subparsers.add_parser("scanall", help="Scan multiple files for sensitive keys.")
    scanall_parser.add_argument("--pattern", action="append", help="Glob pattern for files to scan (can be used multiple times)")

    scanrepo_parser = subparsers.add_parser("scanrepo", help="Scan the entire project directory for sensitive keys.")
    scanrepo_parser.add_argument("--dir", default=".", help="Directory to scan (default: current directory)")

    storeenv_parser = subparsers.add_parser("storeenv", help="Add the .env file to .gitignore without encrypting it.")
    storeenv_parser.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    args = parser.parse_args()

    if args.command == "scan":
        result = scan_env_file(args.env)
        print("Scan result:")
        print(result)
    elif args.command == "encrypt":
        secrets = scan_env_file(args.env)
        if isinstance(secrets, dict) and secrets:
            path = encrypt_secrets(secrets, passphrase=args.passphrase)
            print(f"Secrets encrypted and saved to {path}.")
        else:
            print("No secrets found to encrypt.")
    elif args.command == "decrypt":
        encrypted_path = args.encrypted if args.encrypted else None
        try:
            from getpass import getpass
            passphrase = args.passphrase
            if passphrase is None and args.key is None:
                resp = input("Decrypt with passphrase? (y/n): ").strip().lower()
                if resp == 'y':
                    passphrase = getpass("Enter passphrase: ")
            if passphrase:
                secrets = decrypt_secrets(encrypted_path or ".env.encrypted", passphrase=passphrase)
            else:
                secrets = decrypt_secrets(encrypted_path or ".env.encrypted", key_path=args.key or ".envveil.key")
            print("Decrypted secrets:")
            for k, v in secrets.items():
                print(f"{k}={v}")
        except Exception as e:
            print(f"Error: {e}")
    elif args.command == "rotate-key":
        encrypted_path = args.encrypted if args.encrypted else None
        try:
            from getpass import getpass
            old_passphrase = args.old_passphrase
            new_passphrase = args.new_passphrase
            if old_passphrase is None and args.old_key is None:
                resp = input("Decrypt with old passphrase? (y/n): ").strip().lower()
                if resp == 'y':
                    old_passphrase = getpass("Enter old passphrase: ")
            if new_passphrase is None and args.new_key is None:
                resp = input("Encrypt with new passphrase? (y/n): ").strip().lower()
                if resp == 'y':
                    new_passphrase = getpass("Enter new passphrase: ")
            new_encrypted, new_key = rotate_key(
                encrypted_path=encrypted_path or ".env.encrypted",
                old_key_path=args.old_key or ".envveil.key",
                old_passphrase=old_passphrase,
                new_key_path=args.new_key,
                new_passphrase=new_passphrase
            )
            print(f"Secrets re-encrypted and saved to {new_encrypted}.")
            if new_key:
                print(f"New key saved to {new_key}.")
        except Exception as e:
            print(f"Error: {e}")
    elif args.command == "gitignore":
        template = fetch_gitignore_template(args.language)
        if template:
            if getattr(args, "replace", False):
                with open(".gitignore", "w", encoding="utf-8") as f:
                    f.write(template + "\n")
                ensure_gitignore_entries()
                print(f".gitignore replaced with {args.language} template.")
            else:
                updated = update_gitignore_with_template(template)
                ensure_gitignore_entries()
                if updated:
                    print(f".gitignore updated with {args.language} template.")
                else:
                    print(f".gitignore already contains most {args.language} rules. Ensured secret files are ignored.")
        else:
            print(f"Could not fetch .gitignore template for language: {args.language}")
    elif args.command == "retrofit":
        secrets = scan_env_file(args.env)
        if isinstance(secrets, dict) and secrets:
            path = encrypt_secrets(secrets, passphrase=args.passphrase)
            print(f"Secrets encrypted and saved to {path}.")
            print("Ensured .env.encrypted and .envveil.key are in .gitignore.")
        elif isinstance(secrets, dict) and not secrets:
            print("No secrets found in the .env file.")
        else:
            print(secrets)
    elif args.command == "scanall":
        patterns = args.pattern if args.pattern else [".env", "settings.py", "config/*.json"]
        files = find_files_by_patterns(patterns)
        if not files:
            print(f"No files found for patterns: {patterns}")
        for file in files:
            print(f"\nScanning {file}:")
            result = scan_env_file(file)
            print(result)
    elif args.command == "scanrepo":
        results = scan_project_repository(args.dir)
        if not results:
            print("No sensitive keys found in the repository.")
        else:
            print("Sensitive keys found in the following files:")
            for file, secrets in results.items():
                print(f"\nFile: {file}")
                for key, info in secrets.items():
                    value = info['value']
                    value_display = value[:20] + ('...' if len(value) > 20 else '') if value else ''
                    print(f"  {key}: {value_display} (line {info['line']})")
    elif args.command == "storeenv":
        env_file = args.env
        gitignore_path = ".gitignore"
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines()]
        else:
            lines = []
        if env_file not in lines:
            lines.append(env_file)
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            print(f"Added {env_file} to .gitignore.")
        else:
            print(f"{env_file} is already in .gitignore.")

def fetch_gitignore_template(language):
    lang_map = {
        'python': 'Python',
        'node': 'Node',
        'nodejs': 'Node',
        'java': 'Java',
        'go': 'Go',
        'c++': 'C++',
        'cpp': 'C++',
        'c#': 'CSharp',
        'csharp': 'CSharp',
    }
    template_name = lang_map.get(language.lower(), language.capitalize())
    url = f"https://raw.githubusercontent.com/github/gitignore/main/{template_name}.gitignore"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.text
    else:
        return None

def update_gitignore_with_template(template_text, gitignore_path=".gitignore"):
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            existing = f.read()
        new_lines = [line for line in template_text.splitlines() if line.strip() and line not in existing]
        if new_lines:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write("\n" + "\n".join(new_lines) + "\n")
            return True
        return False
    else:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(template_text + "\n")
        return True

if __name__ == "__main__":
    main() 