import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """配置类，支持环境变量和运行时修改"""
    
    def __init__(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.OMNIPARSER_URL = os.getenv("OMNIPARSER_URL", "http://localhost:8000")
        self.DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")
        # OmniParser自启动配置
        self.OMNIPARSER_AUTO_START = os.getenv("OMNIPARSER_AUTO_START", "true").lower() in ("true", "1", "yes")
        self.OMNIPARSER_PATH = os.getenv("OMNIPARSER_PATH", "")
        self.OMNIPARSER_DEVICE = os.getenv("OMNIPARSER_DEVICE", "cpu")
    
    def is_configured(self):
        """检查API密钥是否已配置"""
        return bool(self.OPENAI_API_KEY.strip())
    
    def save_to_env(self):
        """将当前配置保存到.env文件"""
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        env_content = (
            f"# LLM API Configuration\n"
            f"OPENAI_API_KEY={self.OPENAI_API_KEY}\n"
            f"OPENAI_BASE_URL={self.OPENAI_BASE_URL}\n"
            f"DEFAULT_MODEL={self.DEFAULT_MODEL}\n"
            f"\n"
            f"# OmniParser Configuration\n"
            f"OMNIPARSER_URL={self.OMNIPARSER_URL}\n"
            f"OMNIPARSER_AUTO_START={str(self.OMNIPARSER_AUTO_START).lower()}\n"
            f"OMNIPARSER_PATH={self.OMNIPARSER_PATH}\n"
            f"OMNIPARSER_DEVICE={self.OMNIPARSER_DEVICE}\n"
        )
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
    
    def update_api_key(self, api_key):
        """更新API密钥"""
        self.OPENAI_API_KEY = api_key.strip()
    
    def update_base_url(self, base_url):
        """更新API基础地址"""
        url = base_url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.OPENAI_BASE_URL = url
    
    def update_model(self, model):
        """更新模型名称"""
        self.DEFAULT_MODEL = model.strip()
    
    def update_omniparser_url(self, url):
        """更新OmniParser地址"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.OMNIPARSER_URL = url
    
    def update_omniparser_path(self, path):
        """更新OmniParser安装路径"""
        self.OMNIPARSER_PATH = path.strip()
    
    def set_omniparser_auto_start(self, enabled):
        """设置是否自动启动OmniParser"""
        self.OMNIPARSER_AUTO_START = bool(enabled)


def load_config():
    """加载配置"""
    return Config()
