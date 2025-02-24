import json
import os

data_root_path = r'E:\Data\SG_news\raw_data'
articles_urls_fp = os.path.join(data_root_path, "article_urls.json")

with open(articles_urls_fp, 'r') as f:
    articles_urls = json.load(f)

num_articles = []
for event in articles_urls:
    if len(articles_urls[event]) < 100:
        num_articles.append(len(articles_urls[event]))

# draw the histogram
import matplotlib.pyplot as plt
import numpy as np
# 绘制分布直方图
plt.hist(num_articles, bins=20, edgecolor='black')
plt.title('Num of articles Distribution')
plt.xlabel('Num of articles')
plt.ylabel('Frequency')

# 在每个条形顶部显示单词数
bin_edges = plt.hist(num_articles, bins=20, edgecolor='black')[1]
bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
for count, x in zip(np.histogram(num_articles, bins=20)[0], bin_centers):
    plt.text(x, count, str(count), ha='center', va='bottom')

plt.show()

