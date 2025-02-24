import requests
import re
import random
import json
import os

use_proxies = False

data_root_path = r'E:\Data\SG_news\raw_data'
stories_urls_fp = os.path.join(data_root_path, "story_urls.json")
duplicate_story_urls_fp = os.path.join(data_root_path, "duplicate_story_urls.json")

def visit_google_news_topic(topic_url):
    proxies = {
        'http': 'http://localhost:17890',
        'https': 'http://localhost:17890',
    }
    print("   search url:",topic_url)

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    ]

    User_Agent = random.choice(user_agents)

    print(User_Agent)
    headers={
        'User-Agent':User_Agent,
    }

    while 1:
        try:
            if use_proxies:
                response=requests.get(url=topic_url,headers=headers,proxies=proxies)
            else:
                response=requests.get(url=topic_url,headers=headers)
            break
        except:
            continue
    
    page_text=response.text
    # 使用正则表达式匹配所有url
    stories_ids = re.findall('<a class="jKHa4e" href="./(stories/.*?)"', page_text)
    stories_urls = ['https://news.google.com/'+article_id for article_id in stories_ids] 
    print(stories_urls)
    print("Found stories:", len(stories_urls))
    return stories_urls

if __name__ == '__main__':
    SG_topic_url = "https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRFowTW5RU0JXVnVMVWRDS0FBUAE?hl=en-SG&gl=SG&ceid=SG%3Aen"

    if os.path.exists(duplicate_story_urls_fp):
        duplicate_story_urls = json.load(open(duplicate_story_urls_fp, "r"))
        if len(duplicate_story_urls) > 30:
            duplicate_story_urls = duplicate_story_urls[-30:]
    else:
        duplicate_story_urls = []
        
    if not os.path.exists(stories_urls_fp):
        new_stories_urls = visit_google_news_topic(SG_topic_url)
        stories_urls = {}
        for url in new_stories_urls:
            stories_urls[url] = str(len(stories_urls))
        json.dump(stories_urls, open(stories_urls_fp, "w"))
    else:
        stories_urls = json.load(open(stories_urls_fp, "r"))
        new_stories_urls = visit_google_news_topic(SG_topic_url)
        new_cnt = 0
        for url in new_stories_urls:
            if url not in stories_urls and url not in duplicate_story_urls:
                new_event_id = str(max([int(x) for x in stories_urls.values()]) + 1)
                stories_urls[url] = new_event_id
                new_cnt += 1
        print("New stories found: ", new_cnt)
        json.dump(stories_urls, open(stories_urls_fp, "w", encoding="utf-8"),indent=4)