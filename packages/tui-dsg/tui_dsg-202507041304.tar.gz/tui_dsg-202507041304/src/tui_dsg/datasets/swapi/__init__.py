import os
from pathlib import Path

import requests
from requests import adapters

from .pull import extract_page

__location__ = Path(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))) / 'data'


class __LocalFileAdapter(adapters.HTTPAdapter):
    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        response = requests.Response()
        response.url = request.url

        # extract file
        file = Path(request.url[7:])
        response.status_code, response.reason = self._check_path(file)

        # read file
        if response.status_code == 200:
            try:
                response.raw = open(file, 'rb')
            except (OSError, IOError) as e:
                response.status_code = 500
                response.reason = str(e)

        # return response
        return response

    @staticmethod
    def _check_path(file: Path) -> tuple[int, str]:
        # thanks @ https://stackoverflow.com/a/27786580
        if os.path.isdir(file):
            return 400, 'Path Not A File'
        elif not os.path.isfile(file):
            return 404, 'File Not Found'
        elif not os.access(file, os.R_OK):
            return 403, 'Access Denied'
        else:
            return 200, 'OK'


def __new_get(*args, **kwargs):
    # extract url from parameters
    if len(args) > 0:
        url = args[0]
    elif 'url' in kwargs:
        url = kwargs['url']
    else:
        raise AssertionError

    # handle urls not related to api
    if url.startswith('https://swapi.dev/api/'):
        path = url[len('https://swapi.dev/api/'):]
    elif url.startswith('http://swapi.dev/api/'):
        path = url[len('http://swapi.dev/api/'):]
    else:
        return __old_get(*args, **kwargs)

    if path.endswith('/'):
        path = path[:-1]

    # serve urls from local files
    _, _, file = extract_page(__location__, path)

    with requests.session() as session:
        session.mount('file://', __LocalFileAdapter())

        response = session.get(f'file://{file}')
        response.url = url

        return response


__old_get = requests.get
requests.get = __new_get
