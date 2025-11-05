import sqlite3
import os
from typing import List, Dict, Optional

class StarDictSQLite:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._connect()
    
    def _connect(self):
        """连接数据库"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        print(f"成功连接数据库: {self.db_path}")
    
    def lookup_word(self, word: str) -> Optional[Dict]:
        """查询单词的完整信息"""
        cursor = self.conn.cursor()
        
        cursor.execute(
            "SELECT id, word, sw, phonetic, definition, translation, pos, collins, oxford, tag, bnc, frq, exchange, detail, audio FROM stardict WHERE word = ? OR sw = ?",
            (word.lower(), word.lower())
        )
        
        result = cursor.fetchone()
        if result:
            fields = ['id', 'word', 'sw', 'phonetic', 'definition', 'translation', 
                     'pos', 'collins', 'oxford', 'tag', 'bnc', 'frq', 'exchange', 'detail', 'audio']
            return dict(zip(fields, result))
        return None
    
    def _parse_pos_distribution(self, pos_str: str) -> Dict[str, int]:
        """解析词性分布字符串，如 'u:97/n:3'"""
        pos_dist = {}
        if pos_str:
            parts = pos_str.split('/')
            for part in parts:
                if ':' in part:
                    pos, percent = part.split(':')
                    pos_dist[pos.strip()] = int(percent)
        return pos_dist
    
    def _parse_definition(self, definition: str) -> List[str]:
        """解析definition字段，提取清晰的释义"""
        definitions = []
        if definition:
            # 按句号分割，但保留缩写
            lines = definition.split('n. ')
            for i, line in enumerate(lines):
                line = line.strip()
                if line:
                    if i == 0 and not line.startswith('n. '):
                        definitions.append(line)
                    else:
                        definitions.append(f"n. {line}")
        return definitions
    
    def _parse_translation(self, translation: str) -> List[str]:
        """解析translation字段，提取中文释义"""
        translations = []
        if translation:
            # 按词性分割
            lines = translation.split('\n')
            for line in lines:
                line = line.strip()
                if line and '。' not in line:  # 过滤掉长句子解释
                    translations.append(line)
        return translations
    
    def get_detailed_translations(self, word: str) -> Dict:
        """获取单词的详细翻译信息"""
        result = self.lookup_word(word)
        if not result:
            return {}
        
        detailed_info = {
            'word': result.get('word'),
            'phonetic': result.get('phonetic'),
            'pos_distribution': self._parse_pos_distribution(result.get('pos', '')),
            'definitions': self._parse_definition(result.get('definition', '')),
            'translations': self._parse_translation(result.get('translation', '')),
            'collins_star': result.get('collins'),
            'is_oxford_core': bool(result.get('oxford')),
            'tag': result.get('tag'),
            'frequency': result.get('frq'),
            'word_exchanges': result.get('exchange'),
            'audio': result.get('audio')
        }
        
        return detailed_info
    
    def format_translation_output(self, word: str) -> str:
        """格式化输出单词翻译"""
        detailed_info = self.get_detailed_translations(word)
        if not detailed_info:
            return f"未找到单词: {word}"
        
        output = []
        output.append(f"单词: {detailed_info['word']}")
        
        if detailed_info['phonetic']:
            output.append(f"音标: {detailed_info['phonetic']}")
        
        # 词性分布
        if detailed_info['pos_distribution']:
            pos_str = "，".join([f"{pos}({percent}%)" for pos, percent in detailed_info['pos_distribution'].items()])
            output.append(f"词性分布: {pos_str}")
        
        # 英文释义
        if detailed_info['definitions']:
            output.append("\n英文释义:")
            for i, definition in enumerate(detailed_info['definitions'][:5], 1):  # 限制前5个
                output.append(f"  {i}. {definition}")
        
        # 中文翻译
        if detailed_info['translations']:
            output.append("\n中文翻译:")
            for i, translation in enumerate(detailed_info['translations'], 1):
                # 按词性分割显示
                if '/' in translation and any(pos in translation for pos in ['n.', 'v.', 'adj.', 'adv.']):
                    parts = translation.split('。')[0]  # 取第一部分
                    output.append(f"  {i}. {parts}")
                else:
                    output.append(f"  {i}. {translation}")
        
        # 其他信息
        extra_info = []
        if detailed_info['collins_star']:
            extra_info.append(f"柯林斯{detailed_info['collins_star']}星")
        if detailed_info['is_oxford_core']:
            extra_info.append("牛津核心词汇")
        if detailed_info['frequency']:
            extra_info.append(f"频率等级: {detailed_info['frequency']}")
        
        if extra_info:
            output.append(f"\n其他信息: {', '.join(extra_info)}")
        
        return "\n".join(output)
    
    def search_similar_words(self, pattern: str, limit: int = 10) -> List[str]:
        """搜索相似的单词"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT word FROM stardict WHERE word LIKE ? LIMIT ?",
            (f"{pattern}%", limit)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def get_word_family(self, word: str) -> Dict:
        """获取单词的变形形式"""
        result = self.lookup_word(word)
        if not result or not result.get('exchange'):
            return {}
        
        exchanges = result['exchange']
        word_family = {'base': word}
        
        # 解析exchange字段，通常包含: p:过去式, d:过去分词, i:现在分词, 3:第三人称单数, r:比较级, t:最高级, s:复数, 0:词根, 1:变换形式
        if exchanges:
            exchange_map = {
                'p': '过去式',
                'd': '过去分词', 
                'i': '现在分词',
                '3': '第三人称单数',
                'r': '比较级',
                't': '最高级',
                's': '复数形式',
                '0': '词根',
                '1': '变换形式'
            }
            
            parts = exchanges.split('/')
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    if key in exchange_map:
                        word_family[exchange_map[key]] = value
        
        return word_family

def interactive_query(dictionary: StarDictSQLite):
    """交互式查询模式"""
    print("\n" + "="*60)
    print("交互式查询模式 (输入命令: 'quit'退出, 'help'显示帮助)")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n请输入英文单词或命令: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() in ['help', '?']:
                print("\n可用命令:")
                print("  'quit' - 退出程序")
                print("  'help' - 显示此帮助")
                print("  'word' - 查询单词")
                print("  'similar:word' - 搜索相似单词，如 'similar:run'")
                print("  'family:word' - 显示单词变形，如 'family:run'")
                continue
            elif user_input.startswith('similar:'):
                word = user_input[8:].strip()
                similar_words = dictionary.search_similar_words(word, 8)
                if similar_words:
                    print(f"与 '{word}' 相似的单词: {', '.join(similar_words)}")
                else:
                    print(f"未找到与 '{word}' 相似的单词")
                continue
            elif user_input.startswith('family:'):
                word = user_input[7:].strip()
                word_family = dictionary.get_word_family(word)
                if word_family:
                    print(f"'{word}' 的变形形式:")
                    for form, value in word_family.items():
                        if form != 'base':
                            print(f"  {form}: {value}")
                else:
                    print(f"未找到 '{word}' 的变形信息")
                continue
            elif not user_input:
                continue
            
            # 普通单词查询
            output = dictionary.format_translation_output(user_input)
            print(f"\n{output}")
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"查询时出错: {e}")

def main():
    # 替换为你的数据库文件路径
    db_path = r"C:\MY_SPACE\Sources\tools\screenshot_translator\dict_rsrc\ecdict-sqlite-28\stardict.db"  # 修改为实际路径
    
    try:
        # 创建词典实例
        dictionary = StarDictSQLite(db_path)
        
        # 测试几个单词
        test_words = ['hello', 'run', 'python', 'beautiful', 'artificial']
        
        print("快速测试:")
        print("-" * 40)
        for word in test_words:
            print(f"\n{dictionary.format_translation_output(word)}")
            print("-" * 40)
        
        # 进入交互式查询
        interactive_query(dictionary)
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()