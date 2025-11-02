# install_translation_package.py
import argostranslate.package
import argostranslate.translate

def install_english_chinese_package():
    """单独安装英译中语言包"""
    print("开始安装英译中翻译语言包...")
    print("=" * 50)
    
    # 检查当前已安装的包
    installed_packages = argostranslate.package.get_installed_packages()
    print("当前已安装的语言包:")
    for pkg in installed_packages:
        print(f"  {pkg.from_code} -> {pkg.to_code}")
    
    # 检查是否已安装英译中
    en_to_zh = any(pkg.from_code == "en" and pkg.to_code == "zh" for pkg in installed_packages)
    if en_to_zh:
        print("✓ 英译中语言包已安装，无需重复安装")
        return True
    
    # 获取可用的语言包
    print("\n正在获取可用的语言包...")
    available_packages = argostranslate.package.get_available_packages()
    
    # 查找英译中包
    package_to_install = None
    for pkg in available_packages:
        if pkg.from_code == "en" and pkg.to_code == "zh":
            package_to_install = pkg
            break
    
    if not package_to_install:
        print("✗ 错误：未找到英译中语言包")
        return False
    
    print(f"找到语言包: {package_to_install.from_code} -> {package_to_install.to_code}")
    print("开始下载和安装...")
    print("注意：这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 下载语言包
        download_path = package_to_install.download()
        print(f"✓ 下载完成: {download_path}")
        
        # 安装语言包
        argostranslate.package.install_from_path(download_path)
        print("✓ 安装完成")
        
        # 验证安装
        installed_packages = argostranslate.package.get_installed_packages()
        en_to_zh = any(pkg.from_code == "en" and pkg.to_code == "zh" for pkg in installed_packages)
        
        if en_to_zh:
            print("✓ 英译中语言包安装验证成功")
            
            # 测试翻译
            test_text = "Hello, how are you?"
            translated = argostranslate.translate.translate(test_text, "en", "zh")
            print(f"测试翻译: '{test_text}' -> '{translated}'")
            
            return True
        else:
            print("✗ 安装后验证失败")
            return False
            
    except Exception as e:
        print(f"✗ 安装过程中出错: {e}")
        return False

if __name__ == "__main__":
    print("Argos Translate 语言包安装工具")
    print("=" * 50)
    
    success = install_english_chinese_package()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 语言包安装成功！现在可以运行截图翻译工具了。")
    else:
        print("❌ 语言包安装失败，请检查网络连接或错误信息。")