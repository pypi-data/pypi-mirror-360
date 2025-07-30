"""
并查集（Union-Find）是一种用于管理元素分组的数据结构，主要用于解决动态连通性问题。它支持以下两种核心操作：

查找（Find）：确定某个元素属于哪个集合。

合并（Union）：将两个集合合并为一个集合。

并查集广泛应用于图论、网络连接、社交网络分析、图像处理等领域。
"""


class UnionFind:
    def __init__(self):
        """
        初始化并查集。
        使用字典动态存储 parent 和 rank。
        """
        self.parent = {}  # 存储每个元素的父节点，用于表示集合的树结构
        self.rank = {}  # 存储每个集合的秩（树的高度），用于优化合并操作

    def find(self, x):
        """
        查找元素 x 的根节点（路径压缩优化）。
        如果元素不存在，则动态添加。
        """
        if x not in self.parent:  # 如果元素 x 不在 parent 字典中
            self.parent[x] = x  # 将 x 的父节点设置为自己（初始化）
            self.rank[x] = 1  # 将 x 的秩初始化为 1
        if self.parent[x] != x:  # 如果 x 不是根节点（路径压缩优化）
            self.parent[x] = self.find(self.parent[x])  # 递归查找根节点，并更新 x 的父节点
        return self.parent[x]  # 返回 x 的根节点

    def union(self, x, y):
        """
        合并元素 x 和 y 所在的集合（按秩合并优化）。
        如果元素不存在，则动态添加。
        """
        root_x = self.find(x)  # 找到 x 的根节点
        root_y = self.find(y)  # 找到 y 的根节点
        if root_x != root_y:  # 如果 x 和 y 不在同一个集合中
            # 按秩合并
            if self.rank[root_x] > self.rank[root_y]:  # 如果 x 所在集合的秩更大
                self.parent[root_y] = root_x  # 将 y 的根节点指向 x 的根节点
            elif self.rank[root_x] < self.rank[root_y]:  # 如果 y 所在集合的秩更大
                self.parent[root_x] = root_y  # 将 x 的根节点指向 y 的根节点
            else:  # 如果两个集合的秩相等
                self.parent[root_y] = root_x  # 将 y 的根节点指向 x 的根节点
                self.rank[root_x] += 1  # 增加 x 所在集合的秩

    def get_groups(self):
        """
        获取所有分组，返回一个字典，键为根节点，值为该组的所有元素。
        """
        groups = {}  # 初始化一个空字典，用于存储分组
        for x in self.parent:  # 遍历所有元素
            root = self.find(x)  # 找到当前元素的根节点
            if root not in groups:  # 如果根节点不在 groups 字典中
                groups[root] = []  # 初始化一个空列表
            groups[root].append(x)  # 将当前元素添加到对应根节点的列表中
        return groups  # 返回分组结果
