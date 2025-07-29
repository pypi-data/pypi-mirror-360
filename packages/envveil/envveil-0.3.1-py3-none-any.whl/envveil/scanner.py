import re
import os
import logging
from pathlib import Path
from typing import Set, Dict, Any, Union
import fnmatch

logger = logging.getLogger("envveil.scanner")

# Try to use importlib.resources for pattern file loading if available
try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources  # type: ignore

def load_secret_patterns(pattern_file: str = "envveil/secret_patterns.txt") -> Set[str]:
    """Load secret patterns from file with fallback to defaults."""
    patterns = set()
    # Try to load from package resources first
    try:
        if pkg_resources.is_resource(__package__ or "envveil", "secret_patterns.txt"):
            with pkg_resources.open_text(__package__ or "envveil", "secret_patterns.txt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    patterns.add(line.upper())
            logger.info(f"Loaded %d patterns from package resource", len(patterns))
            logger.debug(f"Patterns loaded: {patterns}")
            return patterns
    except Exception as e:
        logger.warning(f"Could not load patterns from package resource: {e}")
    # Try local file paths
    pattern_paths = [pattern_file, os.path.join(os.getcwd(), pattern_file)]
    for path in pattern_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        patterns.add(line.upper())
                logger.info(f"Loaded %d patterns from %s", len(patterns), path)
                logger.debug(f"Patterns loaded: {patterns}")
                return patterns
            except Exception as e:
                logger.warning(f"Error loading patterns from {path}: {e}")
    # Fallback: default patterns
    patterns = {
        "SECRET", "KEY", "TOKEN", "PASSWORD", "PRIVATE", "API", "ACCESS",
        "AUTH", "CREDENTIAL", "CERT", "CERTIFICATE", "SIGNATURE", "HASH",
        "SALT", "SEED", "NONCE", "SESSION", "BEARER", "OAUTH", "JWT",
        "ENCRYPTION", "DECRYPT", "CIPHER", "KEYSTORE", "PASSPHRASE",
        "LICENSE", "ACTIVATION", "WEBHOOK", "ENDPOINT", "URL", "URI",
        "CLIENT", "CONSUMER", "PRODUCER", "SUBSCRIBER", "PUBLISHER"
    }
    logger.info(f"Using %d default patterns", len(patterns))
    logger.debug(f"Patterns loaded: {patterns}")
    return patterns

def is_sensitive_key(key: str, secret_patterns: Set[str]) -> bool:
    """Check if a key matches sensitive patterns."""
    key_upper = key.upper()
    if key_upper in secret_patterns:
        return True
    prefix_re = r"(?:DEV_|PROD_|TEST_|STAGING_|LOCAL_)?"
    suffix_re = r"(?:_TOKEN|_SECRET|_KEY|_PASSWORD|_HASH|_SALT|_AUTH|_API|_ID|_URL|_URI|_ENDPOINT)?"
    for pattern in secret_patterns:
        pattern_regex = re.compile(
            r"^" + prefix_re + re.escape(pattern) + suffix_re + r"$",
            re.IGNORECASE
        )
        if pattern_regex.match(key):
            return True
    return False

def scan_env_file(env_path: str, secret_patterns: Set[str] = None) -> Union[Dict[str, Any], str]:
    """
    Scan a .env or source file for sensitive keys and return them as a dictionary.
    Supports various formats: KEY=VALUE, KEY="VALUE", KEY='VALUE', export KEY=VALUE
    """
    if secret_patterns is None:
        secret_patterns = load_secret_patterns()
    secrets = {}
    try:
        logger.info(f"Scanning: {env_path}")
        if not os.path.exists(env_path):
            return f"File not found: {env_path}"
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            line_number = 0
            for line in f:
                line_number += 1
                original_line = line
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key = value = None
                if line.startswith('export '):
                    line = line[7:].strip()
                if '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if len(value) >= 2:
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                if key and is_sensitive_key(key, secret_patterns):
                    secrets[key] = {
                        'value': value,
                        'line': line_number,
                        'file': env_path
                    }
                    logger.warning(f"Found sensitive key: {key} (line {line_number})")
        if not secrets:
            logger.info(f"No sensitive keys found in {env_path}")
            return "No sensitive keys found."
        logger.info(f"Found {len(secrets)} sensitive keys in {env_path}")
        return secrets
    except FileNotFoundError:
        return f"File not found: {env_path}"
    except PermissionError:
        return f"Permission denied: {env_path}"
    except Exception as e:
        return f"Error scanning file {env_path}: {e}"

def scan_directory(directory_path: str, file_patterns: list = None, skip_dirs: set = None) -> Dict[str, Any]:
    """
    Recursively scan a directory for files containing sensitive keys.
    Returns a dict mapping file paths to found secrets.
    """
    if file_patterns is None:
        file_patterns = [
            '*.env*', '*.py', '*.js', '*.jsx', '*.ts', '*.tsx', '*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.cfg', '*.conf',
            'config.*', 'settings.*'
        ]
    if skip_dirs is None:
        skip_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.venv', 'env', 'venv'}
    secret_patterns = load_secret_patterns()
    all_secrets = {}
    scanned_files = set()
    logger.info(f"Scanning directory: {directory_path}")
    for root, dirs, files in os.walk(directory_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            file_path = os.path.join(root, file)
            # Use fnmatch for filename matching
            if any(fnmatch.fnmatch(file, pattern) for pattern in file_patterns):
                if file_path in scanned_files:
                    continue
                scanned_files.add(file_path)
                result = scan_env_file(file_path, secret_patterns)
                if isinstance(result, dict) and result:
                    all_secrets[file_path] = result
    logger.info(f"Scan complete. Files scanned: {len(scanned_files)}. Files with secrets: {len(all_secrets)}.")
    return all_secrets

def scan_project_repository(repo_path: str = None) -> Dict[str, Any]:
    """
    Scan an entire project repository for sensitive keys.
    Returns a dict mapping file paths to found secrets.
    """
    if repo_path is None:
        repo_path = os.getcwd()
    logger.info(f"Starting repository scan at: {repo_path}")
    if not os.path.exists(repo_path):
        logger.error(f"Repository path does not exist: {repo_path}")
        return {}
    results = scan_directory(repo_path)
    if results:
        logger.info(f"Sensitive keys found in {len(results)} files.")
    else:
        logger.info("No sensitive keys found in repository.")
    return results 