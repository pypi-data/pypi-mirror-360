import datetime
import gzip
import io
import time

import joblib
from hdfs import InsecureClient

from re_common.v2.baselibrary.helpers.search_packge.fit_text_match import FitTextMatcher

if __name__ == '__main__':
    matcher = FitTextMatcher(
        algorithm='auto',  # 对于小数据集，暴力搜索足够快 brute
        n_jobs=2  # 使用所有CPU核心

    )

    client = InsecureClient("http://VIP-DC-MASTER-2:9870", user="xujiang")

    lists = []
    for i in ["vectorizer", "nn_model", "corpus", "idx"]:
        fit_file_path = f"/b_task_data/class_smi/fit_file/t_23600_{i}.joblib.gz"
        with client.read(fit_file_path) as reader:
            tp = io.BytesIO(reader.read())
            tp.seek(0)
            lists.append(tp)

    with gzip.GzipFile(fileobj=lists[2], mode='rb') as gz:
        matcher.corpus = joblib.load(gz)

    with gzip.GzipFile(fileobj=lists[3], mode='rb') as gz:
        matcher.idx = joblib.load(gz)
    matcher.corpus_size = max(len(matcher.corpus), len(matcher.idx))
    print(f"加载bytes完成，共 {matcher.corpus_size} 篇文献")

    matcher.fit(matcher.corpus)

    print(matcher.nn._fit_method)

    print("fit 训练完成")

    count = 0
    bacth_list = []
    n = min(100, matcher.corpus_size)
    for i in matcher.corpus:
        count = count + 1
        bacth_list.append(i)
        if count % 10000 == 0:
            t1 = time.time()
            index, similarities = matcher.batch_search(bacth_list, n=n)
            for rank, (idxs, sims) in enumerate(zip(index, similarities)):
                print({"keyid": matcher.idx[rank],
                       "search_list": [(matcher.idx[idx], sim) for idx, sim in zip(idxs, sims)]})

            t2 = time.time()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            print(now, count, t2 - t1)
            bacth_list.clear()







    # with open("t_8220_corpus.joblib","rb") as f:
    #     buf = io.BytesIO(f.read())
    #     buf.seek(0)
    #     corpus = buf
    #
    # matcher.corpus = joblib.load(corpus)
    # print(len(matcher.corpus))

    # matcher.load_bytes(vec, nn, corpus)

    # with open(r"C:\Users\Administrator\Desktop\update\part-02440\part-02440_1", "r", encoding="utf-8") as f:
    #     lists = [line.strip() for line in f if line]
    #
    # matcher.fit(lists)

    # matcher.load("./","test")

    # query = r"herbdrug interaction in the protective effect of alpinia officinarum against gastric injury induced by indomethacin based on pharmacokinetic tissue distribution and excretion studies in rats"
    # result = matcher.search(query, n=100)
    # print("query", query)
    # for rank, (idx, sim) in enumerate(result):
    #     print(f"\nTop {rank + 1} [相似度: {sim:.4f}]:")
    #     print(f"文献 #{idx}: {lists[idx]}")
    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    # time.sleep(100)

    # for query in lists[:1000]:
    #     indices, similarities = matcher.search(query, n=100)
    #     print("query", query)
    #     for rank, (idx, sim) in enumerate(zip(indices, similarities)):
    #         print(f"\nTop {rank + 1} [相似度: {sim:.4f}]:")
    #         print(f"文献 #{idx}: {lists[idx]}")
    #     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    #     time.sleep(100)
    #
    # idx,sim = matcher.batch_search(lists[:1000], n=100)
    # for rank, (idxs, sims) in enumerate(zip(idx,sim)):
    #     tp = (lists[rank],[(lists[idx], sim) for idx,sim in zip(idxs,sims)])
    #     print(tp)
    # time.sleep(100)
