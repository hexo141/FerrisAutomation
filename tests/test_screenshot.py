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

from src.screenshot import image_to_base64

def test_image_to_base64():
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    b64 = image_to_base64(img)
    assert isinstance(b64, str)
    assert len(b64) > 0
    print("✓ image_to_base64 test passed")

if __name__ == "__main__":
    test_image_to_base64()
    print("\nAll screenshot tests passed! ✓")
