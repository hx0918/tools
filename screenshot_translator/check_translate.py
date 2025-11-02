def check_translation_setup():
    """检查翻译环境"""
    import argostranslate.package
    import argostranslate.translate
    
    # 检查已安装的语言包
    installed_packages = argostranslate.package.get_installed_packages()
    print("已安装的语言包:")
    for pkg in installed_packages:
        print(f"  {pkg.from_code} -> {pkg.to_code}")
    
    # 检查英译中包是否存在
    en_to_zh = any(pkg.from_code == "en" and pkg.to_code == "zh" for pkg in installed_packages)
    print(f"英译中语言包: {'已安装' if en_to_zh else '未安装'}")
    
    return en_to_zh

# 在代码开头添加检查
print("检查翻译环境...")
translation_ready = check_translation_setup()