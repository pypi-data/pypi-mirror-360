import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import re


def download(url: str, save_dir: str, file_name: str):
    response = requests.get(url)
    os.makedirs(f'{save_dir}', exist_ok=True)
    if response.status_code == 200:
        with open(os.path.join(f'{save_dir}', f"{file_name}"), 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download image for {file_name}. Status code: {response.status_code}")


def to_webp(name: str) -> str:
    return f'{name}.webp'


def get_filename(name: str, extension: str) -> str:
    return f'{name}.{extension}'


def download_all(url: list, save_dir: str, file_name: list, extension: str = None, timeit: bool = False) -> None:
    if timeit:
        from performer_helper import TimeIt
        with TimeIt():
            download_all(url=url, save_dir=save_dir, file_name=file_name, extension=extension, timeit=False)
    else:
        os.makedirs(f'{save_dir}', exist_ok=True)
        if len(url) != len(file_name):
            print(f"The length of url and file_name should be the same.")
        for url, name in tqdm(zip(url, file_name), total=min(len(url), len(file_name))):
            response = requests.get(url)
            if response.status_code == 200:
                if extension is not None:
                    file_name = get_filename(name, extension)
                if os.path.isfile(os.path.join(f'{save_dir}', f"{file_name}")):
                    print(f"{file_name} already exists. Skipping...")
                    continue
                with open(os.path.join(f'{save_dir}', f"{file_name}"), 'wb') as f:
                    f.write(response.content)
            else:
                print(f"Failed to download image for {file_name}. Status code: {response.status_code}")
        print(f"All images have been downloaded to {save_dir}")


def fetch_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    print(f"Request URL: {response.url}")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    # response.encoding = 'utf-8'

    return response.text


def kuaishou_download(url: str, save_dir: str, file_name: str):
    html_content = fetch_html(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    if html_content.strip() == "":
        print("Fetched HTML content is empty.")
    video_element = soup.find_all('script')
    element = str(video_element[1])
    print(type(element), element)
    mp4_urls = re.findall(r'https:\\/\\/[^"]+\.mp4', element)

    # 处理反斜杠
    # mp4_urls = [url.replace('\\/', '/') for url in mp4_urls]

    for url in mp4_urls:
        print(url)


