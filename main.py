import re
import argparse
import time
import json
import requests
import pymongo

def get_qinghua_by_page(page_no):
    offset = page_no * 10
    url = "https://www.zhihu.com/api/v4/topics/20225177/feeds/essence?include=data%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Darticle%29%5D.target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Dpeople%29%5D.target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Darticle%29%5D.target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dquestion%29%5D.target.annotation_detail%2Ccomment_count%3B&limit=10&offset={}".format(offset)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    }
    r = requests.get(url, verify=False, headers=headers)
    content = r.content.decode("utf-8")
    data = json.loads(content)
    is_end = data["paging"]["is_end"]
    items = data["data"]
    client = pymongo.MongoClient()
    db = client["qinghua"]
    if len(items) > 0:
        db.answers.insert_many(items)
    return is_end

def get_qinghua():
    page_no = 0
    client = pymongo.MongoClient()
    db = client["qinghua"]
    while True:
        print(page_no)
        is_end = get_qinghua_by_page(page_no)
        page_no += 1
        if is_end:
            break

def split_content(content):
    content = re.sub(r'</p><p>', r'\n', content)
    content = re.sub(r'<br>', r'\n', content)
    content = re.sub(r'<[^>]*>', r'', content)
    items = content.split("\n")
    return items

def query():
    client = pymongo.MongoClient()
    db = client["qinghua"]
    items = db.answers.find({"target.voteup_count": {"$gte": 100}})
    for item in items:
        item_type = item["target"]["type"]
        if item_type != "answer":
            continue
        question = item["target"]["question"]["title"]
        answer = item["target"]["content"]
        vote_num = item["target"]["voteup_count"]
        url = item["target"]["url"]
        print("=" * 50)
        result = split_content(answer)
        for line in result:
            print(line)
        print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", help="save data", action="store_true", dest="save")
    parser.add_argument("--query", help="query data", action="store_true", dest="query")
    args = parser.parse_args()

    if args.save:
        get_qinghua()
    elif args.query:
        query()
