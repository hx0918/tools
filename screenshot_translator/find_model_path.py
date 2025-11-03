# find_all_models.py
import os
import sys
from pathlib import Path
import paddle
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False

def find_all_models():
    print("=" * 60)
    print("正在查找所有模型文件...")
    print("=" * 60)
    
    # 1. PaddlePaddle 相关路径
    print("\n🔍 PaddlePaddle 模型路径:")
    try:
        paddle_home = Path(paddle.utils.get_home_dir())
        print(f"PaddlePaddle 主目录: {paddle_home}")
        
        # 检查常见的缓存路径
        paddle_cache_paths = [
            paddle_home,
            Path("~/.cache/paddle").expanduser(),
            Path("~/.paddleclas").expanduser(),
            Path("~/.paddledet").expanduser(),
        ]
        
        for path in paddle_cache_paths:
            if path.exists():
                print(f"📁 找到: {path}")
                # 显示目录大小
                total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                print(f"   大小: {total_size / (1024**3):.2f} GB")
                # 显示前几个文件
                model_files = list(path.rglob('*.pdparams')) + list(path.rglob('*.pdmodel'))
                for i, file_path in enumerate(model_files[:5]):
                    print(f"   📄 {file_path.relative_to(path)}")
                if len(model_files) > 5:
                    print(f"   ... 还有 {len(model_files) - 5} 个模型文件")
    except Exception as e:
        print(f"❌ PaddlePaddle 路径查找失败: {e}")
    
    # 2. PaddleOCR 特定路径
    print("\n🔍 PaddleOCR 模型路径:")
    if PADDLEOCR_AVAILABLE:
        try:
            # PaddleOCR 的默认模型路径
            paddleocr_paths = [
                Path("~/.paddleocr").expanduser(),
                Path("./inference"),  # 当前目录下的 inference 文件夹
                Path("./models"),     # 当前目录下的 models 文件夹
            ]
            
            for path in paddleocr_paths:
                if path.exists():
                    print(f"📁 找到: {path}")
                    total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                    print(f"   大小: {total_size / (1024**3):.2f} GB")
                    for file_path in path.rglob('*'):
                        if file_path.is_file():
                            print(f"   📄 {file_path.relative_to(path)}")
        except Exception as e:
            print(f"❌ PaddleOCR 路径查找失败: {e}")
    else:
        print("❌ PaddleOCR 未安装")
    
    # 3. ArgosTranslate 模型路径
    print("\n🔍 ArgosTranslate 模型路径:")
    if ARGOS_AVAILABLE:
        try:
            argos_path = Path("~/.argos-translate").expanduser()
            if argos_path.exists():
                print(f"📁 找到: {argos_path}")
                total_size = sum(f.stat().st_size for f in argos_path.rglob('*') if f.is_file())
                print(f"   大小: {total_size / (1024**3):.2f} GB")
                
                # 显示所有模型包
                for package_dir in argos_path.iterdir():
                    if package_dir.is_dir():
                        print(f"   📦 语言包: {package_dir.name}")
                        for model_file in package_dir.rglob('*'):
                            if model_file.is_file():
                                size_mb = model_file.stat().st_size / (1024**2)
                                print(f"      📄 {model_file.name} ({size_mb:.1f} MB)")
            else:
                print("❌ ArgosTranslate 模型目录不存在")
        except Exception as e:
            print(f"❌ ArgosTranslate 路径查找失败: {e}")
    else:
        print("❌ ArgosTranslate 未安装")
    
    # 4. 检查环境变量中的路径
    print("\n🔍 环境变量相关路径:")
    env_vars = ['HOMEPATH', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA']
    for var in env_vars:
        if var in os.environ:
            path = Path(os.environ[var])
            if path.exists():
                # 检查是否有相关的模型文件
                model_dirs = list(path.rglob('.paddle*')) + list(path.rglob('*argos*'))
                if model_dirs:
                    print(f"📍 {var}: {path}")
                    for model_dir in model_dirs[:3]:
                        print(f"   📁 {model_dir.relative_to(path)}")

if __name__ == "__main__":
    find_all_models()