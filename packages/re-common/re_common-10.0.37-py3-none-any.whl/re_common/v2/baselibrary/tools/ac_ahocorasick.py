import pickle

import ahocorasick


class ACTool(object):

    def __init__(self):
        self.automaton = ahocorasick.Automaton()

    def add_word(self, key, value, overwrite=True) -> bool:
        """
        为 AC 机添加数据,默认情况下 key重复直接覆盖
        :param key: 要添加的关键字
        :param value: 对应的值
        :param overwrite: 是否覆盖已有的 key，默认为 True
        :return: 是否成功添加或覆盖
        """
        if key in self.automaton:  # 检查 key 是否已存在
            if overwrite:  # 如果允许覆盖
                self.automaton.add_word(key, value)
                return True
            else:  # 不允许覆盖，跳过
                return False
        else:  # key 不存在，直接添加
            self.automaton.add_word(key, value)
            return True

    def is_exists_key(self, key) -> bool:
        # 是否存在key
        if self.automaton.exists(key):
            return True
        else:
            return False

    def make_automaton(self):
        """
        添加完词后需要构建
        """
        self.automaton.make_automaton()

    def iter(self, key):
        """
        结果为可迭代对象 可通过list 转换 [(end_index, value)]
        tool.add_word("he", "word1")
        tool.add_word("hello", "word2")

        # 在字符串中查找匹配
        input_string = "hello world"
        matches = list(tool.automaton.iter(input_string))
        print(matches)  # [(1, 'word1'), (4, 'word2')]

        (1, 'word1'):
        end_index = 1: 表示匹配的关键字 "he" 在 input_string = "hello world" 中的结束位置是索引 1（即字符串 "he" 的最后一个字符 'e' 的位置）。
        "hello world" 的索引：h(0)e(1)l(2)l(3)o(4) (5)w(6)o(7)r(8)l(9)d(10)。
        value = 'word1': 表示匹配的关键字 "he" 对应的值是 "word1"。
        (4, 'word2'):
        end_index = 4: 表示匹配的关键字 "hello" 在 input_string = "hello world" 中的结束位置是索引 4（即字符串 "hello" 的最后一个字符 'o' 的位置）。
        value = 'word2': 表示匹配的关键字 "hello" 对应的值是 "word2"。

        注意: 结果只会返回 value 不会返回 key，如果需要key  请将key 组合到结果中
        """

        result_iter = self.automaton.iter(key)  # ahocorasick.AutomatonSearchIter
        return result_iter
    def save(self,local_temp_path):
        """
        将构建好的ac自动机保存到本地
        """
        self.automaton.save(local_temp_path,pickle.dumps)

    def load(self,local_temp_path):
        """
        加载已经构建好的ac自动机
        """
        self.automaton=ahocorasick.load(local_temp_path, pickle.loads)