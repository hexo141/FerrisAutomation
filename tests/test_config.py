import sys
import os

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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import load_config

def test_load_config():
    config = load_config()
    assert hasattr(config, 'OPENAI_API_KEY')
    assert hasattr(config, 'OPENAI_BASE_URL')
    assert hasattr(config, 'OMNIPARSER_URL')
    assert hasattr(config, 'DEFAULT_MODEL')
    print("✓ load_config test passed")

def test_config_update_methods():
    config = load_config()
    
    # 测试更新API密钥
    config.update_api_key("sk-test123456")
    assert config.OPENAI_API_KEY == "sk-test123456"
    assert config.is_configured() == True
    print("✓ update_api_key test passed")
    
    # 测试更新API地址
    config.update_base_url("https://api.example.com/v1")
    assert config.OPENAI_BASE_URL == "https://api.example.com/v1"
    print("✓ update_base_url test passed")
    
    # 测试更新模型
    config.update_model("claude-3-opus")
    assert config.DEFAULT_MODEL == "claude-3-opus"
    print("✓ update_model test passed")
    
    # 测试更新OmniParser地址
    config.update_omniparser_url("localhost:9000")
    assert config.OMNIPARSER_URL == "http://localhost:9000"
    print("✓ update_omniparser_url test passed")

def test_config_save():
    config = load_config()
    config.update_api_key("sk-testkey123")
    config.update_base_url("https://api.openai.com/v1")
    config.update_model("gpt-4o")
    config.update_omniparser_url("http://localhost:8000")
    
    config.save_to_env()
    
    import os
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    assert os.path.exists(env_path)
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "sk-testkey123" in content
    assert "gpt-4o" in content
    print("✓ config save test passed")

if __name__ == "__main__":
    test_load_config()
    test_config_update_methods()
    test_config_save()
    print("\nAll config tests passed! ✓")
