import os
import tempfile
import pytest
from envveil.scanner import scan_env_file, load_secret_patterns, scan_project_repository

# Test: Ensure secret patterns are loaded and contain API_KEY
def test_patterns_load():
    """Test that secret patterns are loaded and contain API_KEY."""
    patterns = load_secret_patterns()
    assert isinstance(patterns, set)
    assert "API_KEY" in patterns  # Updated to match secret_patterns.txt

# Test: Detect a sensitive key in a .env file
def test_env_sensitive():
    """Test that a .env file with a sensitive key is detected."""
    content = "OPENAI_API_KEY=sk-123456\nNORMAL_VAR=foo"
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tf:
        tf.write(content)
        tf.flush()
        result = scan_env_file(tf.name)
    os.unlink(tf.name)
    assert isinstance(result, dict)
    assert "OPENAI_API_KEY" in result
    assert "NORMAL_VAR" not in result

# Test: No sensitive key in a .env file
def test_env_no_sensitive():
    """Test that a .env file with no sensitive keys returns the correct message."""
    content = "NORMAL_VAR=foo\nANOTHER=bar"
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tf:
        tf.write(content)
        tf.flush()
        result = scan_env_file(tf.name)
    os.unlink(tf.name)
    assert isinstance(result, str)
    assert "No sensitive keys found" in result

def test_scan_env_file_openai_api_key():
    content = "OPENAI_API_KEY=sk-testkey1234567890"
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tf:
        tf.write(content)
        tf.flush()
        result = scan_env_file(tf.name)
    os.unlink(tf.name)
    assert isinstance(result, dict)
    assert "OPENAI_API_KEY" in result
    assert result["OPENAI_API_KEY"]["value"] == "sk-testkey1234567890"

# Test 1: Scan a demo directory for a .env file containing a CSRF_TOKEN
def test_demo_scan_1(tmp_path):
    """Scan a demo directory for a .env file containing a CSRF_TOKEN secret."""
    demo_dir = tmp_path / "demo"
    demo_dir.mkdir()
    env_file = demo_dir / ".env"
    env_file.write_text("CSRF_TOKEN=ZGVtby1hcGkta2V5LWZvci10ZXN0aW5nLW9ubHk\nNORMAL_VAR=foo")
    results = scan_project_repository(str(demo_dir))
    found = False
    for file, secrets in results.items():
        if os.path.basename(file) == ".env" and "CSRF_TOKEN" in secrets:
            found = True
    assert found, "CSRF_TOKEN should be detected in demo/.env"

# Test 2: Scan a demo directory for a .env file containing an OPENAI_API_KEY
def test_demo_scan_2(tmp_path):
    """Scan a demo directory for a .env file containing an OPENAI_API_KEY secret."""
    demo_dir = tmp_path / "demo2"
    demo_dir.mkdir()
    env_file = demo_dir / ".env"
    env_file.write_text("OPENAI_API_KEY=sk-testkey1234567890\nNORMAL_VAR=foo")
    results = scan_project_repository(str(demo_dir))
    found = False
    for file, secrets in results.items():
        if os.path.basename(file) == ".env" and "OPENAI_API_KEY" in secrets:
            found = True
    assert found, "OPENAI_API_KEY should be detected in demo2/.env" 