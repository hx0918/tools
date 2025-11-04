import sys
import shlex

def test_args():
    print("原始 sys.argv:", sys.argv)
    
    if len(sys.argv) > 1:
        full_cmd = ' '.join(sys.argv[1:])
        print("合并后的命令行:", full_cmd)
        
        parsed_args = shlex.split(full_cmd)
        print("shlex 解析结果:", parsed_args)
        
        source_text = parsed_args[0] if len(parsed_args) > 0 else ""
        target_text = parsed_args[1] if len(parsed_args) > 1 else ""
        
        print("原文:", repr(source_text))
        print("译文:", repr(target_text))

def main():
    """主函数"""
    # 手动处理引号
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        source_text = args[0]
        target_text = ""
        
        # 如果第一个参数以引号开始，找到匹配的结束引号
        if args[0].startswith(('"', "'")):
            quote_char = args[0][0]
            combined = args[0]
            i = 1
            while i < len(args) and not combined.endswith(quote_char):
                combined += " " + args[i]
                i += 1
            source_text = combined[1:-1]  # 去掉引号
            if i < len(args):
                target_text = ' '.join(args[i:])
        elif len(args) > 1:
            target_text = args[1]
    
    print("手动解析结果:")
    print("原文:", repr(source_text))
    print("译文:", repr(target_text))

if __name__ == "__main__":
    # test_args()
    main()