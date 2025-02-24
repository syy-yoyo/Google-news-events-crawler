import time
import os
import json
import trafilatura
from urllib.parse import urlparse
import threading
from trafilatura.downloads import fetch_url

data_root_path = r'E:\Data\SG_news\raw_data'
story_urls_fp = os.path.join(data_root_path, "story_urls.json")
article_urls_fp = os.path.join(data_root_path, "article_urls.json")
output_text_dir = os.path.join(data_root_path, "article_text")
if not os.path.exists(output_text_dir):
    os.makedirs(output_text_dir)

crawled_text = {}
for file in os.listdir(output_text_dir):
    with open(os.path.join(output_text_dir, file), "r") as f:
        crawled_text[file.split(".")[0]] = json.load(f)

def save_to_file(result):
    if result["event_id"] not in crawled_text:
        crawled_text[result["event_id"]] = {}
    crawled_text[result["event_id"]][result["google_read_url"]] = result
    output_text_fp = os.path.join(output_text_dir, result["event_id"] + ".json")

    with open(output_text_fp, "w") as f:
        json.dump(crawled_text[result["event_id"]], f)

def check_if_news_crawled(event_id, article_url):
    if event_id in crawled_text and article_url in crawled_text[event_id]:
        return True
    else:
        return False


def url_handler_selector(to_crawl_item, bad_domains):
    news_results, successful_flag = news_url_handler(to_crawl_item["origin_url"], bad_domains)

    # merge the results dicts
    results = to_crawl_item
    results.update(news_results)
    # print(results)
    # exit(0)
    return results, successful_flag

def is_bad_media(url, bad_domains):
    excluded = False
    for media_host in bad_domains:
        if "." not in media_host:
            continue
        if media_host in url:
            excluded = True
    return excluded

def news_url_handler(url, bad_domains):
    successful_flag = 0
    crawled = {"status": "failed"}
    crawled["domain"] = urlparse(url).netloc
    if is_bad_media(url, bad_domains):
        pass    # failed
    else:
        down = fetch_url(url)
        if down is None:
            pass    # failed
        try:
            result = trafilatura.extract(down, with_metadata=True, output_format="json")
            if result is not None:
                crawled["title"] = json.loads(result)['title']
                crawled["date"] = json.loads(result)['date']
                crawled["text"] = json.loads(result)['text']
                crawled["domain"] = urlparse(url).netloc
                crawled["status"] = "successful"
                successful_flag += 1
        except BaseException as err:
            print(err)
    return crawled, successful_flag

def thread_crawler(to_crawl_items, x):
    global total_cnt, successful_cnt, crawled_domains, lock

    while True:
        if to_crawl_items == []:
            break
        
        it_to_crawl_items = iter(to_crawl_items)
        to_crawl_item = next(it_to_crawl_items)
        to_crawl_url = to_crawl_item["origin_url"]
        cnt = 0
        while True:
            domain= urlparse(to_crawl_url).netloc
            if domain not in crawled_domains:
                print(to_crawl_url)
                crawled_domains[domain] = [time.time(), 0]
                break
            elif time.time() - crawled_domains[domain][0] < 5:
                try:
                    to_crawl_item = next(it_to_crawl_items)
                    to_crawl_url = to_crawl_item["origin_url"]
                    cnt += 1
                    time.sleep(0.5)
                except StopIteration:
                    break
            else:
                print(to_crawl_url)
                crawled_domains[domain][0] = time.time()
                break
            
        crawled, successful_flag = url_handler_selector(to_crawl_item, bad_domains)
        
        lock.acquire()
        total_cnt += 1
        successful_cnt += successful_flag
        if successful_flag:
            crawled_domains[domain][1] += 1
        else:
            crawled_domains[domain][1] -= 1
            if crawled_domains[domain][1] == -3:
                bad_domains.append(domain)
                print("Domain added to bad_domains after 3 fails: ", domain)
        print("From thread:", threading.current_thread().name, "Crawled:", total_cnt, "succeeded:", successful_cnt)
        lock.release()

        save_to_file(crawled)
        to_crawl_items.pop(cnt)


total_cnt = 0
successful_cnt = 0
crawled_domains = {}
bad_domains = []
lock = threading.Lock()

if __name__ == "__main__":
    with open(story_urls_fp, 'r') as f:
        story_urls_list = json.load(f)
    with open(article_urls_fp, 'r') as f:
        article_urls_list = json.load(f)
    
    to_crawl_items = []
    for story_url in article_urls_list:
        event_id = article_urls_list[story_url]["event_id"]
        for article_url in article_urls_list[story_url]["articles_urls"]:
            item_is_crawled = check_if_news_crawled(event_id, article_url)
            if item_is_crawled == False:
                to_crawl_items.append({"event_id": event_id, "google_read_url": article_url, "origin_url": article_urls_list[story_url]["articles_urls"][article_url]})

    thread_num = 10
    threads_list = []
    for i in range(thread_num):
        start = i * int(len(to_crawl_items)/thread_num)
        end = (i+1) * int(len(to_crawl_items)/thread_num)
        if i == thread_num-1:
            end = len(to_crawl_items)

        print(start,end)
        t = threading.Thread(target=thread_crawler, name=f"Thread-{i}", args=(to_crawl_items[start:end], 1))
        t.start()
        time.sleep(1)
        threads_list.append(t)

    print("All threads started !!!")
    for t in threads_list:
        t.join()

    sorted_keys = sorted(crawled_domains, key=lambda k: crawled_domains[k][1], reverse=True)[:10]
    for key in sorted_keys:
        print("successful cnt: ", crawled_domains[key][1], key)