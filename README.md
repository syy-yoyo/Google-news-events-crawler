# Google-news-events-crawler
Want to aggregate news articles by events? My repository provides a full pipeline for:
1. Automatically **get news events about a topic** in Google news (actually, only **recent** news events).
2. Get the original urls of the articles in the news events.
3. Get the text content of the news reports, and conveniently check the crawled contents by hand.


Some explanations:

Some topic urls can be:

  Top stories: https://news.google.com/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRFZxYUdjU0JXVnVMVWRDR2dKVFJ5Z0FQAQ?hl=en-SG&gl=SG&ceid=SG%3Aen
  
  Singapore stories: https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRFowTW5RU0JXVnVMVWRDS0FBUAE?hl=en-SG&gl=SG&ceid=SG%3Aen
  
  Entertainment stories: https://news.google.com/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNREpxYW5RU0JXVnVMVWRDR2dKVFJ5Z0FQAQ?hl=en-SG&gl=SG&ceid=SG%3Aen
  
The **news events** refer to the "full coverage" web pages, like: https://news.google.com/stories/CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lSdzcyaERSSDZ6eklqTnRDVXFDZ0FQAQ?hl=en-SG&gl=SG&ceid=SG%3Aen


Should be run at least every day to get track of new events, since google news' topic web pages will delete old articles and events, and update new articles and events, and keep the total number in a stable range. (Show limited content, and update from time to time)



**Recommend to set rules for utilizing your proxy pool**, because using a proxy to send too many requests to a website in a short period of time can easily get you blocked. You can refer to https://jiasupanda.com/clash-load-balance for details. Following is my setting, to use only some specified proxies instead of all of my proxies, to form the proxy pool.
![image](https://github.com/user-attachments/assets/ccfe0f1b-7040-43b0-bff4-12664c1e8ebb)


**References:**

How to get origin article urls: https://blog.csdn.net/weixin_42567622/article/details/142925447
