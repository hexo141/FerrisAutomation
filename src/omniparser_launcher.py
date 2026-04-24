"""
OmniParser Launcher Module
Auto-detects, downloads, installs and launches OmniParser service.
"""

import os
import sys
import subprocess
import socket
import time
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class OmniParserLauncher:
    """OmniParser自动检测、下载、安装和启动器"""
    
    OMNIPARSER_GIT_URL = "https://github.com/microsoft/OmniParser.git"
    OMNIPARSER_GIT_URL_MIRROR = "https://hf-mirror.com/api/models/microsoft/OmniParser.git"
    MODEL_REPO = "microsoft/OmniParser-v2.0"
    HF_ENDPOINT = "https://huggingface.co"
    HF_MIRROR_ENDPOINT = "https://hf-mirror.com"
    
    WEIGHT_FILES = [
        "icon_detect/train_args.yaml",
        "icon_detect/model.pt",
        "icon_detect/model.yaml",
        "icon_caption/config.json",
        "icon_caption/generation_config.json",
        "icon_caption/model.safetensors",
    ]
    
    def __init__(self, base_url="http://localhost:8000", timeout=30, install_dir=None, is_china=None):
        self.base_url = base_url
        self.timeout = timeout
        self.host = self._extract_host(base_url)
        self.port = self._extract_port(base_url)
        self.process = None
        self.install_dir = install_dir or Path(os.path.expanduser("~/OmniParser"))
        self.is_china = is_china if is_china is not None else self._detect_china()
    
    def _detect_china(self):
        """检测是否为中华地区（大陆）"""
        try:
            resp = requests.get("http://ip-api.com/json/", timeout=5)
            data = resp.json()
            country = data.get("country", "").lower()
            is_china = country in ("china", "cn")
            logger.info(f"Region detected: {data.get('country', 'Unknown')} (China: {is_china})")
            return is_china
        except Exception as e:
            logger.warning(f"Failed to detect region, assuming not China: {e}")
            return False
    
    def _extract_host(self, url):
        """从URL提取主机地址"""
        url = url.replace("http://", "").replace("https://", "").rstrip("/")
        return url.split(":")[0] if ":" in url else "localhost"
    
    def _extract_port(self, url):
        """从URL提取端口"""
        url = url.replace("http://", "").replace("https://", "").rstrip("/")
        parts = url.split(":")
        return int(parts[1]) if len(parts) > 1 else 8000
    
    def is_running(self):
        """检测OmniParser是否正在运行"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def find_omniparser_path(self):
        """查找OmniParser安装路径"""
        cwd = Path.cwd()
        
        search_paths = [
            self.install_dir,
            cwd / "OmniParser",
            cwd / "omniparser",
            Path(os.path.expanduser("~/OmniParser")),
            Path(os.path.expanduser("~/omniparser")),
            Path("C:/OmniParser"),
            Path("D:/OmniParser"),
            Path(os.path.expanduser("~/projects/OmniParser")),
            Path(os.path.expanduser("~/code/OmniParser")),
            Path(os.path.expanduser("~/Desktop/OmniParser")),
        ]
        
        # 也搜索当前目录下匹配OmniParser*的目录
        if cwd.exists():
            for d in cwd.iterdir():
                if d.is_dir() and d.name.lower().startswith("omniparser"):
                    if d not in search_paths:
                        search_paths.insert(1, d)
        
        for path in search_paths:
            if path.exists():
                for name in ["app.py", "server.py", "main.py", "gradio_demo.py", "demo.py"]:
                    candidate = path / name
                    if candidate.exists():
                        return candidate
                    candidate = path / "src" / name
                    if candidate.exists():
                        return candidate
        
        return None
    
    def clone_omniparser(self, target_dir=None):
        """克隆OmniParser仓库"""
        if target_dir is None:
            target_dir = self.install_dir
        
        if target_dir.exists() and (target_dir / ".git").exists():
            logger.info(f"OmniParser already cloned at {target_dir}")
            return True
        
        repo_url = self.OMNIPARSER_GIT_URL_MIRROR if self.is_china else self.OMNIPARSER_GIT_URL
        logger.info(f"Cloning OmniParser to {target_dir}...")
        cmd = ["git", "clone", repo_url, str(target_dir)]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("OmniParser cloned successfully")
                return True
            else:
                logger.error(f"Failed to clone OmniParser: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception while cloning: {e}")
            return False
    
    def download_weights(self, target_dir=None):
        """下载OmniParser模型权重"""
        if target_dir is None:
            target_dir = self.install_dir
        
        hf_endpoint = self.HF_MIRROR_ENDPOINT if self.is_china else self.HF_ENDPOINT
        
        logger.info(f"Downloading OmniParser weights from {self.MODEL_REPO}...")
        
        weights_dir = target_dir / "weights"
        weights_dir.mkdir(parents=True, exist_ok=True)
        
        env = os.environ.copy()
        env["HF_ENDPOINT"] = hf_endpoint
        
        success = True
        for weight_file in self.WEIGHT_FILES:
            file_path = weights_dir / weight_file
            if file_path.exists():
                logger.info(f"  [OK] {weight_file}")
                continue
            
            logger.info(f"  Downloading {weight_file}...")
            cmd = [
                "huggingface-cli", "download",
                self.MODEL_REPO,
                weight_file,
                "--local-dir", str(weights_dir),
                "--resume-download"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
                if result.returncode == 0:
                    logger.info(f"  [OK] {weight_file}")
                else:
                    logger.error(f"  [FAIL] {weight_file}: {result.stderr}")
                    success = False
            except subprocess.TimeoutExpired:
                logger.error(f"  [TIMEOUT] {weight_file}")
                success = False
            except Exception as e:
                logger.error(f"  [ERROR] {weight_file}: {e}")
                success = False
        
        return success
    
    def _check_uv_installed(self):
        """检查uv是否已安装"""
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _install_uv(self):
        """安装uv工具"""
        logger.info("Installing uv package manager...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "uv"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info("uv installed successfully")
                return True
            else:
                logger.error(f"Failed to install uv: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception while installing uv: {e}")
            return False
    
    def install_dependencies(self, target_dir=None):
        """使用uv安装OmniParser依赖"""
        if target_dir is None:
            target_dir = self.install_dir
        
        requirements_file = target_dir / "requirements.txt"
        if not requirements_file.exists():
            logger.warning(f"requirements.txt not found at {target_dir}")
            return False
        
        # 检查并安装uv
        if not self._check_uv_installed():
            if not self._install_uv():
                logger.warning("Failed to install uv, falling back to pip")
                return self._install_dependencies_pip(requirements_file)
        
        logger.info("Installing OmniParser dependencies using uv...")
        
        cmd = ["uv", "pip", "install", "-r", str(requirements_file), "--system"]
        
        # 中国地区使用阿里云pip镜像
        if self.is_china:
            cmd.extend([
                "--index-url", "https://mirrors.aliyun.com/pypi/simple",
                "--trusted-host", "mirrors.aliyun.com"
            ])
            logger.info("Using Aliyun pip mirror for China region")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                logger.info("Dependencies installed successfully with uv")
                return True
            else:
                logger.error(f"Failed to install dependencies with uv: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception while installing dependencies with uv: {e}")
            return False
    
    def _install_dependencies_pip(self, requirements_file):
        """使用pip安装依赖（降级方案）"""
        logger.info("Installing dependencies using pip...")
        
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
        
        if self.is_china:
            cmd.extend(["-i", "https://mirrors.aliyun.com/pypi/simple"])
            logger.info("Using Aliyun pip mirror for China region")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                logger.info("Dependencies installed successfully with pip")
                return True
            else:
                logger.error(f"Failed to install dependencies with pip: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception while installing dependencies with pip: {e}")
            return False
    
    def setup(self, target_dir=None):
        """
        完整设置OmniParser：克隆、下载权重、安装依赖
        
        Returns:
            bool: 是否设置成功
        """
        if target_dir is None:
            target_dir = self.install_dir
        
        logger.info("=" * 50)
        logger.info("Setting up OmniParser...")
        if self.is_china:
            logger.info("China region detected - using mirrors for faster download")
        logger.info("=" * 50)
        
        # 1. 克隆仓库
        if not self.clone_omniparser(target_dir):
            logger.error("Failed to clone OmniParser")
            return False
        
        # 2. 下载权重
        if not self.download_weights(target_dir):
            logger.warning("Some weights failed to download, but continuing...")
        
        # 3. 安装依赖
        if not self.install_dependencies(target_dir):
            logger.warning("Failed to install dependencies, but continuing...")
        
        logger.info("OmniParser setup completed!")
        return True
    
    def launch(self, omniparser_path=None, device="cpu"):
        """
        启动OmniParser服务
        
        Args:
            omniparser_path: OmniParser项目路径，为None时自动检测
            device: 运行设备 (cpu/cuda)
        
        Returns:
            bool: 是否成功启动
        """
        if self.is_running():
            logger.info(f"OmniParser is already running at {self.base_url}")
            return True
        
        # 查找OmniParser路径
        if omniparser_path is None:
            omniparser_path = self.find_omniparser_path()
            if omniparser_path is None:
                logger.warning("OmniParser installation not found")
                return False
        
        omniparser_path = Path(omniparser_path)
        
        if not omniparser_path.exists():
            logger.error(f"OmniParser path not found: {omniparser_path}")
            return False
        
        # 确定项目目录
        project_dir = omniparser_path.parent if omniparser_path.name.endswith(('.py',)) else omniparser_path
        
        # 使用OmniParser标准启动命令: python -m omnitool.omniparserserver.omniparserserver
        cmd = [
            sys.executable, "-m",
            "omnitool.omniparserserver.omniparserserver",
            "--device", device,
            "--port", str(self.port)
        ]
        
        logger.info(f"Starting OmniParser from {project_dir}")
        logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=str(project_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            # 等待服务启动
            logger.info("Waiting for OmniParser to start...")
            for i in range(self.timeout):
                time.sleep(1)
                if self.is_running():
                    logger.info(f"OmniParser started successfully at {self.base_url}")
                    return True
                
                # 检查进程是否仍在运行
                if self.process.poll() is not None:
                    logger.error(f"OmniParser process exited with code {self.process.returncode}")
                    return False
                
                if (i + 1) % 5 == 0:
                    logger.info(f"Still waiting... ({i + 1}/{self.timeout}s)")
            
            logger.error(f"OmniParser did not start within {self.timeout} seconds")
            return False
            
        except Exception as e:
            logger.error(f"Failed to start OmniParser: {e}")
            return False
    
    def stop(self):
        """停止OmniParser进程"""
        if self.process and self.process.poll() is None:
            logger.info("Stopping OmniParser...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            logger.info("OmniParser stopped")
    
    def get_status(self):
        """获取OmniParser状态"""
        if self.is_running():
            return {
                "status": "running",
                "url": self.base_url,
                "port": self.port
            }
        else:
            status_info = {
                "status": "stopped",
                "url": self.base_url,
                "port": self.port
            }
            if self.process:
                status_info["exit_code"] = self.process.poll()
            return status_info
