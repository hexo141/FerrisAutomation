import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置标准输出编码为UTF-8（支持Unicode字符）
if sys.platform == 'win32':
    import io
    # Reconfigure stdout to use UTF-8 encoding
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from src.safety import is_dangerous_action, DANGEROUS_ACTION_TYPES, DANGEROUS_EXTENSIONS

def test_dangerous_action_types():
    for action in DANGEROUS_ACTION_TYPES:
        assert is_dangerous_action(action) == True
    print("✓ Dangerous action types test passed")

def test_safe_action_types():
    assert is_dangerous_action("click") == False
    assert is_dangerous_action("type") == False
    assert is_dangerous_action("move") == False
    assert is_dangerous_action("scroll") == False
    print("✓ Safe action types test passed")

def test_dangerous_file_extensions():
    for ext in DANGEROUS_EXTENSIONS:
        assert is_dangerous_action("write_file", {"path": f"test{ext}", "content": ""}) == True
    print("✓ Dangerous file extensions test passed")

def test_dangerous_content():
    assert is_dangerous_action("write_file", {"path": "test.txt", "content": "rm -rf /"}) == True
    assert is_dangerous_action("write_file", {"path": "test.txt", "content": "format C:"}) == True
    print("✓ Dangerous content test passed")

def test_safe_file_operations():
    assert is_dangerous_action("write_file", {"path": "test.txt", "content": "hello world"}) == False
    assert is_dangerous_action("read_file", {"path": "test.txt"}) == False
    print("✓ Safe file operations test passed")

if __name__ == "__main__":
    test_dangerous_action_types()
    test_safe_action_types()
    test_dangerous_file_extensions()
    test_dangerous_content()
    test_safe_file_operations()
    print("\nAll safety tests passed! ✓")
