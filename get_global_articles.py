import requests
import re
import random
import json
from urllib.parse import quote
from lxml import etree
import os

# 切换成全部代理的轮询！
use_proxies = True
proxy_port = 17890
max_articles_per_story = 20
skip_until = ""

data_root_path = r'E:\Data\Google_Global_news\raw_data'
articles_urls_fp = os.path.join(data_root_path, "article_urls.json")
story_urls_fp = os.path.join(data_root_path, "story_urls.json")
duplicate_story_urls_fp = os.path.join(data_root_path, "duplicate_story_urls.json")

def get_google_params(url):
    """
    从给定的Google新闻链接中获取所需的参数: source、sign 和 ts
    """
    proxies = {
        'http': f'http://localhost:{proxy_port}',
        'https': f'http://localhost:{proxy_port}'
    }
    # 发送GET请求，获取HTML内容
    if use_proxies:
        response = requests.get(url, proxies=proxies)
    else:
        response = requests.get(url)
    # 使用lxml解析HTML
    tree = etree.HTML(response.text)
    # 使用XPath提取参数
    sign = tree.xpath('//c-wiz/div/@data-n-a-sg')[0]
    ts = tree.xpath('//c-wiz/div/@data-n-a-ts')[0]
    source = tree.xpath('//c-wiz/div/@data-n-a-id')[0]
    return source, sign, ts

def get_origin_url(source, sign, ts):
    """
    根据提取的参数构造请求并获取重定向的原始新闻链接
    """
    url = f"https://news.google.com/_/DotsSplashUi/data/batchexecute"
    req_data = [[[  
        "Fbv4je",  # 请求类型
        f"[\"garturlreq\",[[\"zh-HK\",\"HK\",[\"FINANCE_TOP_INDICES\",\"WEB_TEST_1_0_0\"],null,null,1,1,\"HK:zh-Hant\",null,480,null,null,null,null,null,0,5],\"zh-HK\",\"HK\",1,[2,4,8],1,1,null,0,0,null,0],\"{source}\",{ts},\"{sign}\"]",
        None,
        "generic"
    ]]]
    payload = f"f.req={quote(json.dumps(req_data))}"
    headers = {
      'Host': 'news.google.com',
      'X-Same-Domain': '1',
      'Accept-Language': 'zh-CN',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      'Accept': '*/*',
      'Origin': 'https://news.google.com',
      'Referer': 'https://news.google.com/',
      'Accept-Encoding': 'gzip, deflate, br',
    }
    proxies = {
        'http': f'http://localhost:{proxy_port}',
        'https': f'http://localhost:{proxy_port}'
    }
    # 发送POST请求，获取响应
    response = requests.post(url, headers=headers, data=payload, proxies=proxies)
    # 使用正则表达式匹配重定向URL
    match = re.search(r'https?://[^\s",\\]+', response.text)
    if match:
        redirect_url = match.group()
    return redirect_url

def visit_google_news_story(story_url):
    proxies = {
        'http': f'http://localhost:{proxy_port}',
        'https': f'http://localhost:{proxy_port}'
    }
    print("    Searching url:",story_url)

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
    ]

    User_Agent = random.choice(user_agents)
    headers={
        'User-Agent':User_Agent,
    }

    while 1:
        try:
            if use_proxies:
                response=requests.get(url=story_url,headers=headers,proxies=proxies)
            else:
                response=requests.get(url=story_url,headers=headers)
            break
        except:
            continue

    page_text=response.text
    # 使用正则表达式匹配所有url
    article_ids = re.findall('track:click,vis" tabindex="-1" href="./(read/.*?)"', page_text)
    article_urls = ['https://news.google.com/'+article_id for article_id in article_ids]
    return article_urls


if __name__ == '__main__':
    story_urls = json.load(open(story_urls_fp, "r"))

    if os.path.exists(articles_urls_fp):
        all_article_urls = json.load(open(articles_urls_fp, "r"))
    else:
        all_article_urls = {}
    print("Already had articles num:", len(all_article_urls))

    if os.path.exists(duplicate_story_urls_fp):
        duplicate_story_urls = json.load(open(duplicate_story_urls_fp, "r"))
    else:
        duplicate_story_urls = []
    if len(duplicate_story_urls) > 30:
        duplicate_story_urls = duplicate_story_urls[-30:]

    if skip_until == "":
        if len(all_article_urls) > 10:
            skip_until = list(sorted(all_article_urls.keys(), key=lambda x:int(all_article_urls[x]["event_id"])))[-10]
            print("Skip until:", skip_until, all_article_urls[skip_until]["event_id"])
        else:
            skip_until = list(story_urls.keys())[0]

    article_to_story_url = {}
    continue_to_skip_flag = True
    for story_url in story_urls:
        if story_url == skip_until:
            continue_to_skip_flag = False
        if continue_to_skip_flag:
            # record the event id for each article
            for article_url in all_article_urls[story_url]["articles_urls"]:
                origin_url = all_article_urls[story_url]["articles_urls"][article_url]
                article_to_story_url[origin_url] = story_url
            continue
        if story_url in duplicate_story_urls:
            continue

        # get articles urls for this story
        event_id = story_urls[story_url]
        print("Processing story:", story_url, event_id)
        
        article_urls = visit_google_news_story(story_url)
        if story_url in all_article_urls:
            print("    Already had articles for this story")
            # examine if all article urls are already in the dict
            for article_url in article_urls:
                if len(all_article_urls[story_url]["articles_urls"]) >= max_articles_per_story:
                    break
                if article_url not in all_article_urls[story_url]["articles_urls"]:
                    all_article_urls[story_url]["articles_urls"][article_url] = ""
        else:
            all_article_urls[story_url] = {"event_id":event_id, "articles_urls":{}}
            for article_url in article_urls:
                if len(all_article_urls[story_url]["articles_urls"]) >= max_articles_per_story:
                    break
                all_article_urls[story_url]["articles_urls"][article_url] = ""
        
        # get originial urls for each article url, and detect duplicated stories
        for article_url in all_article_urls[story_url]["articles_urls"]:
            if all_article_urls[story_url]["articles_urls"][article_url] != "":
                continue
            # get originial urls for each article url
            print("        article_url:", article_url)
            try:    # get originial urls successfully
                source, sign, ts = get_google_params(article_url)
                origin_url = get_origin_url(source, sign, ts)
                all_article_urls[story_url]["articles_urls"][article_url] = origin_url
                print("        origin_url:", origin_url)
                print("************")
                # detect duplicated stories
                if origin_url in article_to_story_url:
                    print("*******************************************************")
                    print("Duplicated article found: ", event_id, article_to_story_url[origin_url])
                    print("*******************************************************")
                    duplicate_story_urls.append(story_url)
                    print("To delete story url: ", story_url)
                    all_article_urls.pop(story_url)
                    break
            except Exception as e:  # failed to get originial urls
                print("Error:", e)
                for story_url in duplicate_story_urls:
                    if story_url in story_urls:
                        story_urls.pop(story_url)
                    json.dump(story_urls, open(story_urls_fp, "w"), indent=4)
                json.dump(duplicate_story_urls, open(duplicate_story_urls_fp, "w"), indent=4)
                json.dump(all_article_urls, open(articles_urls_fp, "w"), indent=4)
                exit(0)

        
        # record the event id for each article
        if story_url not in duplicate_story_urls:
            for article_url in all_article_urls[story_url]["articles_urls"]:
                origin_url = all_article_urls[story_url]["articles_urls"][article_url]
                article_to_story_url[origin_url] = story_url

        json.dump(all_article_urls, open(articles_urls_fp, "w"), indent=4)
        print("To delete story urls: ", duplicate_story_urls)
        # print(article_to_story_url)
        
    for story_url in duplicate_story_urls:
        if story_url in story_urls:
            story_urls.pop(story_url)
    json.dump(story_urls, open(story_urls_fp, "w"), indent=4)
    json.dump(duplicate_story_urls, open(duplicate_story_urls_fp, "w"), indent=4)