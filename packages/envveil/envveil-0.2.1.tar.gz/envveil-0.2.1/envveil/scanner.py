import re
import os

def load_secret_patterns(pattern_file="envveil/secret_patterns.txt"):
    patterns = set()
    try:
        with open(pattern_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                patterns.add(line.upper())
    except Exception:
        # fallback: use default patterns
        patterns = {
            "SECRET", "KEY", "TOKEN", "PASSWORD", "PRIVATE", "API", "ACCESS"
        }
    return patterns

def scan_env_file(env_path):
    """
    Scan a .env or source file for sensitive keys and return them as a dictionary.
    Supports both KEY=VALUE and KEY = "VALUE"/KEY = 'VALUE' formats.
    Sensitive keys are loaded from secret_patterns.txt (case-insensitive, exact or with common prefixes/suffixes).
    """
    secret_patterns = load_secret_patterns()
    # Accept common prefixes/suffixes
    prefix_re = r"(?:DEV_|PROD_|TEST_)?"
    suffix_re = r"(?:_TOKEN|_SECRET|_KEY|_PASSWORD)?"
    # Build a regex that matches any of the patterns, with optional prefix/suffix
    pattern_re = re.compile(
        r"^" + prefix_re + r"(" + "|".join(re.escape(p) for p in secret_patterns) + r")" + suffix_re + r"$",
        re.IGNORECASE
    )
    # Also support Python assignment: KEY = "VALUE" or KEY = 'VALUE'
    py_assign_re = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*(['\"])(.*?)\2$")
    secrets = {}
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key = value = None
                # .env style: KEY=VALUE
                if '=' in line and not line.startswith('export '):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key, value = parts[0].strip(), parts[1].strip()
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                # Python assignment style: KEY = "VALUE" or KEY = 'VALUE'
                if key is None:
                    m = py_assign_re.match(line)
                    if m:
                        key, value = m.group(1), m.group(3)
                if key and pattern_re.match(key):
                    secrets[key] = value
        if not secrets:
            return "No sensitive keys found."
        return secrets
    except FileNotFoundError:
        return f"File not found: {env_path}"
    except Exception as e:
        return f"Error scanning file: {e}" 