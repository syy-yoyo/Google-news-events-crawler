import os
import json

data_root_path = r'E:\Data\SG_news\raw_data'
article_text_dir = os.path.join(data_root_path, "article_text")

# have articles in common / valid cnt too low should be removed
for file in os.listdir(article_text_dir):
    print(file)
    with open(os.path.join(article_text_dir, file), "r") as f:
        article_text = json.load(f)
    for article_url in article_text:
        if "valid" not in article_text[article_url]:
        # if "valid" not in article_text[article_url] or article_text[article_url]["valid"] == False:
            if "text" not in article_text[article_url]:
                article_text[article_url]["valid"] = False
            else:
                print(article_text[article_url]["text"])
                valid = input("11: good, 22: bad")
                if valid == "11":
                    article_text[article_url]["valid"] = True
                elif valid == "22":
                    article_text[article_url]["valid"] = False
            print("\n**********************************\n")
    with open(os.path.join(article_text_dir, file), "w") as f:
        json.dump(article_text, f)

valid_cnts = {}
for file in os.listdir(article_text_dir):
    valid_cnt = 0
    with open(os.path.join(article_text_dir, file), "r") as f:
        article_text = json.load(f)
    for article_url in article_text:
        if article_text[article_url]["valid"] == True:
            valid_cnt += 1
    print(file, valid_cnt)
    valid_cnts[file] = valid_cnt

print("Invalid events:")
invalid_events = []
dayu_5_cnt, dayu_10_cnt = 0, 0
for fn in valid_cnts:
    if valid_cnts[fn] < 5:
        invalid_events.append(fn.split(".")[0])
    else:
        dayu_5_cnt += 1
        if valid_cnts[fn] >= 10:
            dayu_10_cnt += 1
print(invalid_events)
print("大于5个articles的stories数量:", dayu_5_cnt)
print("大于10个articles的stories数量:", dayu_10_cnt)