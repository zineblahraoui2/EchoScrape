import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

start = time()

urls = []
with open("links.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        urls.append(row["links"])

contents = []


def fetch_post(url):
    domain = urlparse(url).netloc
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    post = {"url": url}

    if domain == "www.instagram.com":
        meta = soup.find(property="og:description")
        content = meta["content"]
        post["content"] = content[content.find('"') + 1 : content.rfind('"')]
    elif domain == "www.linkedin.com":
        meta = soup.find(property="og:description")
        post["content"] = meta["content"]

    return post


processes = []

with ThreadPoolExecutor(max_workers=10) as executer:
    for url in urls:
        processes.append(executer.submit(fetch_post, url))

for task in as_completed(processes):
    post = task.result()
    if post is None:
        print(f"Skipping {post['url']}")
    else:
        contents.append(task.result())

with open("contents.json", "w") as f:
    json.dump(contents, f, ensure_ascii=False, indent=2)

end = time()

print(end - start)
