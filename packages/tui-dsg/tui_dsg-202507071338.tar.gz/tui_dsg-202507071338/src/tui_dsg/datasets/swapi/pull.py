import json
from pathlib import Path
from time import sleep

import requests

BASE_URL = 'https://swapi.dev/api/'
BASE_PATH = Path('./data/')

BASE_PATH.mkdir(exist_ok=True)


def extract_page(base: Path, p: str) -> tuple[str, int, Path]:
    if len(p) >= 8 and p[-7:-1] == '?page=':
        page = int(p[-1:])
        p = p[:-8]
    elif len(p) >= 9 and p[-8:-2] == '?page=':
        page = int(p[-2:])
        p = p[:-9]
    else:
        page = 1

    file = base / Path(f'{p}_page{page}.json')

    return p, page, file


def handle(data: any, already_pulled: set[str]):
    if isinstance(data, str):
        if data.startswith(BASE_URL):
            new_url = data[len(BASE_URL):]
            if new_url.endswith('/'):
                new_url = new_url[:-1]

            pull(new_url, already_pulled)

    elif isinstance(data, dict):
        for k, v in data.items():
            handle(v, already_pulled)

    elif isinstance(data, list):
        for v in data:
            handle(v, already_pulled)


def pull(p: str, already_pulled: set[str]):
    # get target url and file
    url = f'{BASE_URL}{p}'
    _, _, file = extract_page(BASE_PATH, p)

    # only pull if not already pulled
    if url not in already_pulled:
        # request
        response = requests.get(url, verify=False)
        data = response.json()

        # store in pulled set
        already_pulled.add(url)
        sleep(0.5)

        # create parent folder and store to file
        file.parent.mkdir(exist_ok=True)
        with open(file, 'w', encoding='utf-8') as f:
            # json.dump(data, f, indent=4)
            json.dump(data, f)

        # handle data to find all other urls recursively
        handle(data, already_pulled)


def main():
    already_pulled = set()
    pull('', already_pulled)


if __name__ == '__main__':
    main()
