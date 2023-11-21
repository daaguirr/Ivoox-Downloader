import argparse
import os

import bs4
import requests
import re


def new_bs(url: str):
    return bs4.BeautifulSoup(requests.get(url).content, "html5lib")


def get_urls_page(soup: bs4.BeautifulSoup) -> list[str]:
    rect = soup.find_all("p", "title-wrapper text-ellipsis-multiple")
    return [r.find('a').get('href') for r in rect]


def has_next(soup: bs4.BeautifulSoup) -> str | None:
    new_url = None
    pagination = soup.find("ul", "pagination")
    if not pagination:
        return new_url
    pages = pagination.find_all("li")
    next_page = pages[-1]
    if next_page.get("class") is None or "disabled" not in next_page.get("class"):
        new_url = next_page.find('a').get('href')
    return new_url


def get_urls(root_url: str) -> list[str]:
    next_page = root_url
    ans = []
    while next_page is not None:
        soup = new_bs(next_page)
        ans += get_urls_page(soup)
        next_page = has_next(soup)
    return ans


def get_download_url(url: str):
    scripts = new_bs(url).find_all('script')

    bingo = re.compile(r".downloadlink'\)")

    def search():
        for script in scripts:
            if len(script.contents) > 0:
                for r in script.contents[0].split('\n'):
                    if bingo.search(r):
                        return "https://www.ivoox.com/" + r.strip(' ')[25:-3]

    return new_bs(search()).find('a').get('href')


def get_download_urls(root):
    pages = get_urls(root)
    return [get_download_url(x) for x in pages]


def format_n(n):
    return ("000" + str(n))[-3:]


def download_link(_url: str, target_path: str):
    print(_url)
    req = requests.get(_url, stream=True, headers={'Referer': 'https://www.ivoox.com/'})
    with open(target_path, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def main():
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
        local_filename = os.path.join(download_path, f"{name}_{format_n(i + 1)}.mp3")
        download_link(_url, local_filename)
        print(f"Download : {100 * (i + 1) / len(links):.2f}%")


if __name__ == '__main__':
    main()
