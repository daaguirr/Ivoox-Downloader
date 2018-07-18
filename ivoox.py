import argparse
import os

import bs4
import requests


def new_bs(url):
    return bs4.BeautifulSoup(requests.get(url).content, "html5lib")


def get_urls_page(soup: bs4.BeautifulSoup):
    ans = []
    rect = soup.find_all("p", "title-wrapper text-ellipsis-multiple")
    for r in rect:
        ans += [r.find('a').get('href')]
    return ans


def hasnext(soup: bs4.BeautifulSoup):
    new_url = None
    pag = soup.find("ul", "pagination")
    if not pag:
        return new_url
    pags = pag.find_all("li")
    sig = pags[-1]
    if sig.get("class") is None or "disabled" not in sig.get("class"):
        new_url = sig.find('a').get('href')
    return new_url


def get_urls(root_url: str):
    soup = new_bs(root_url)
    ans = []
    while 1:
        ans += get_urls_page(soup)
        next_page = hasnext(soup)
        if not next_page:
            break
        soup = new_bs(next_page)
    return ans


def get_download_url(url: str):
    link = new_bs(url).find_all('script')

    import re

    bingo = re.compile(".downloadlink'\)")

    def search():
        for l in link:
            if len(l.contents) > 0:
                for r in l.contents[0].split('\n'):
                    if bingo.search(r):
                        return "https://www.ivoox.com/" + r.strip(' ')[25:-3]

    return new_bs(search()).find('a').get('href')


def get_download_urls(root):
    pages = get_urls(root)
    return list(map(lambda x: get_download_url(x), pages))


def format_n(n):
    return ("000" + str(n))[-3:]


if __name__ == '__main__':
    # Lectura
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="url of audio")
    parser.add_argument("name", type=str, help="name of audio")
    parser.add_argument("path", type=str, help="path to save")
    parser.add_argument("-r", "--reversed",
                        action="store_true", dest="rev", default=False,
                        help="reversed order")

    args = parser.parse_args()

    url_r = args.url
    name = args.name
    download_path = os.path.join(args.path, name)
    rev = args.rev

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    print("Getting urls")
    links = get_download_urls(url_r)

    if not rev:
        links = links[::-1]

    print("Start Download")
    for i, _url in enumerate(links):
        local_filename = os.path.join(download_path, f"{name}_{format_n(i+1)}.mp3")
        print(_url)
        req = requests.get(_url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Download : {100*(i+1) / len(links):.2f}%")
