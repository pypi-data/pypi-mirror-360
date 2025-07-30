import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class TextMatcher:
    """
    高性能文本匹配器
    基于 TF-IDF + 最近邻搜索实现相似文献查找
    """
    
    def __init__(self, algorithm='brute', metric='cosine', n_jobs=-1):
        """
        初始化文本匹配器
        
        参数:
        algorithm: 搜索算法 ('brute', 'kd_tree', 'ball_tree', 'lshf')
        metric: 距离度量 ('cosine', 'euclidean', 'manhattan')
        n_jobs: 并行作业数 (-1 表示使用所有CPU核心)
        """
        self.vectorizer = TfidfVectorizer(
            max_features=10000,  # 限制特征数量以提高性能
            stop_words='english',  # 移除英文停用词
            ngram_range=(1, 2)  # 使用单字和双字组合
        )
        
        self.nn = NearestNeighbors(
            algorithm=algorithm,
            metric=metric,
            n_jobs=n_jobs  # 并行处理加速搜索
        )
        
        self.corpus = None
        self.corpus_size = 0
    
    def fit(self, corpus):
        """
        训练匹配器
        """
        self.corpus = corpus
        self.corpus_size = len(corpus)
        print(f"处理 {self.corpus_size} 篇文献...")
        
        # 向量化文本
        start_time = time.time()
        X = self.vectorizer.fit_transform(corpus)
        vectorization_time = time.time() - start_time
        print(f"TF-IDF 向量化完成, 耗时: {vectorization_time:.4f}秒")
        print(f"特征维度: {X.shape[1]}")
        
        # 训练最近邻模型
        start_time = time.time()
        self.nn.fit(X)
        training_time = time.time() - start_time
        print(f"最近邻模型训练完成, 耗时: {training_time:.4f}秒")
        
        return self
    
    def search(self, query, n=5, return_scores=True):
        """
        查找相似文献
        
        参数:
        query: 查询文本
        n: 返回最相似文献的数量
        return_scores: 是否返回相似度分数
        
        返回:
        匹配的文献索引和相似度分数
        """
        if self.corpus is None:
            raise ValueError("请先使用 fit() 方法训练模型")
        
        # 向量化查询文本
        query_vec = self.vectorizer.transform([query])
        
        # 查找最近邻
        start_time = time.time()
        distances, indices = self.nn.kneighbors(query_vec, n_neighbors=n)
        search_time = time.time() - start_time
        
        print(f"搜索完成, 耗时: {search_time:.6f}秒")
        
        # 将距离转换为相似度 (余弦距离 = 1 - 余弦相似度)
        similarities = 1 - distances
        
        # 返回结果
        if return_scores:
            return indices[0], similarities[0]
        return indices[0]
    
    def explain_match(self, query, index):
        """
        解释匹配结果 - 显示查询和匹配文献的关键词
        """
        # 获取TF-IDF特征名
        feature_names = self.vectorizer.get_feature_names_out()
        
        # 向量化查询和匹配文献
        query_vec = self.vectorizer.transform([query])
        doc_vec = self.vectorizer.transform([self.corpus[index]])
        
        # 获取重要特征
        query_data = zip(feature_names, query_vec.toarray()[0])
        doc_data = zip(feature_names, doc_vec.toarray()[0])
        
        # 筛选非零特征
        query_keywords = [(word, score) for word, score in query_data if score > 0]
        doc_keywords = [(word, score) for word, score in doc_data if score > 0]
        
        # 按重要性排序
        query_keywords.sort(key=lambda x: x[1], reverse=True)
        doc_keywords.sort(key=lambda x: x[1], reverse=True)
        
        # 打印结果
        print(f"\n匹配文献 #{index} 解释:")
        print(f"查询关键词: {[word for word, _ in query_keywords[:10]]}")
        print(f"文献关键词: {[word for word, _ in doc_keywords[:10]]}")
        
        # 计算共同关键词
        common_keywords = set([word for word, _ in query_keywords[:20]]) & set([word for word, _ in doc_keywords[:20]])
        print(f"共同关键词: {list(common_keywords)}")
        
        return common_keywords

# ======================
# 演示使用
# ======================

if __name__ == "__main__":
    # 1. 准备文献库 (实际应用中可从文件/数据库加载)
    corpus = [
        "机器学习是人工智能的一个分支，专注于开发算法让计算机从数据中学习",
        "深度学习是机器学习的一个子领域，使用多层神经网络处理复杂模式",
        "自然语言处理(NLP)使计算机能够理解、解释和生成人类语言",
        "计算机视觉关注如何让计算机从图像和视频中获得高层次的理解",
        "强化学习是一种机器学习方法，智能体通过与环境互动学习最优行为策略",
        "监督学习使用标记数据训练模型，无监督学习则处理未标记数据",
        "神经网络是受人脑启发的计算模型，由相互连接的节点层组成",
        "卷积神经网络(CNN)特别适合处理图像识别任务",
        "循环神经网络(RNN)设计用于处理序列数据，如文本和时间序列",
        "Transformer模型通过自注意力机制处理序列数据，成为NLP的主流架构",
        "生成对抗网络(GAN)由生成器和判别器组成，用于生成新数据样本",
        "迁移学习允许将在一个任务上学到的知识应用到另一个相关任务",
        "数据挖掘是从大型数据集中发现模式、关联和异常的过程",
        "特征工程是创建更好的输入特征以提高模型性能的过程",
        "过拟合发生在模型过于复杂，过度记忆训练数据而泛化能力差",
        "正则化技术如L1/L2正则化用于防止过拟合",
        "梯度下降是优化神经网络权重的主要算法",
        "反向传播是训练神经网络的关键算法，用于计算梯度",
        "激活函数如ReLU引入非线性，使神经网络能够学习复杂模式",
        "批量归一化通过标准化层输入加速训练并提高稳定性"
    ]
    
    # 2. 创建文本匹配器
    print("="*50)
    print("创建文本匹配器")
    print("="*50)
    matcher = TextMatcher(
        algorithm='brute',  # 对于小数据集，暴力搜索足够快
        n_jobs=-1           # 使用所有CPU核心
    )
    
    # 3. 训练模型
    matcher.fit(corpus)
    
    # 4. 执行查询
    print("\n" + "="*50)
    print("执行查询: '神经网络在人工智能中的应用'")
    print("="*50)
    query = "神经网络在人工智能中的应用"
    indices, similarities = matcher.search(query, n=3)
    
    # 5. 显示结果
    print("\n最相似的文献:")
    for rank, (idx, sim) in enumerate(zip(indices, similarities)):
        print(f"\nTop {rank+1} [相似度: {sim:.4f}]:")
        print(f"文献 #{idx}: {corpus[idx]}")
        
        # 解释匹配
        matcher.explain_match(query, idx)
    
    # 6. 性能测试 (可选)
    print("\n" + "="*50)
    print("性能测试")
    print("="*50)
    
    # 测试不同文献库大小的性能
    corpus_sizes = [100, 500, 1000, 5000]
    times = []
    
    for size in corpus_sizes:
        # 创建更大的文献库
        large_corpus = corpus * (size // len(corpus) + 1)
        large_corpus = large_corpus[:size]
        
        # 创建新的匹配器
        test_matcher = TextMatcher(algorithm='brute', n_jobs=-1)
        
        # 测量训练时间
        start_time = time.time()
        test_matcher.fit(large_corpus)
        train_time = time.time() - start_time
        
        # 测量查询时间
        start_time = time.time()
        test_matcher.search(query, n=5)
        search_time = time.time() - start_time
        
        times.append((size, train_time, search_time))
        print(f"文献库大小: {size} | 训练时间: {train_time:.4f}s | 查询时间: {search_time:.6f}s")
    
    # 可视化性能结果
    sizes, train_times, search_times = zip(*times)
    
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(sizes, train_times, 'o-')
    plt.title('训练时间 vs 文献库大小')
    plt.xlabel('文献数量')
    plt.ylabel('时间 (秒)')
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(sizes, search_times, 'o-')
    plt.title('查询时间 vs 文献库大小')
    plt.xlabel('文献数量')
    plt.ylabel('时间 (秒)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('performance.png')
    print("\n性能图表已保存为 'performance.png'")
    
    # 7. 相似度矩阵可视化 (可选)
    print("\n" + "="*50)
    print("文献相似度矩阵")
    print("="*50)
    
    # 计算所有文献的TF-IDF向量
    vectors = matcher.vectorizer.transform(corpus)
    
    # 计算余弦相似度矩阵
    sim_matrix = cosine_similarity(vectors)
    
    # 创建DataFrame用于可视化
    df = pd.DataFrame(sim_matrix, 
                     columns=[f"Doc{i}" for i in range(len(corpus))],
                     index=[f"Doc{i}" for i in range(len(corpus))])
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(df, cmap="YlGnBu", annot=False)
    plt.title("文献相似度矩阵")
    plt.tight_layout()
    plt.savefig('similarity_matrix.png')
    print("相似度矩阵已保存为 'similarity_matrix.png'")