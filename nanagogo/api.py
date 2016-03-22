#!/usr/bin/env python3

import json

import requests


s = requests.Session()


class NanagogoError(Exception):
    def __init__(self, status_code, http_status_code, error_message):
        self.status_code = status_code
        self.http_status_code = http_status_code
        self.error_message = error_message


class NanagogoResponse(object):
    """The response from the 7gogo private JSON API, returned as
    either a dict or a list."""
    pass


class NanagogoResponseDict(dict, NanagogoResponse):
    pass


class NanagogoResponseList(list, NanagogoResponse):
    pass


class NanagogoRequest(object):
    url_template = 'https://api.7gogo.jp/web/v2/{}'

    response = None

    error_translations = {'リンクに問題があるか、ページが削除された可能性があります。': 'Not found'}

    def __init__(self, path, method="GET", params={}, data=None):
        if isinstance(path, str) and path.startswith('https'):
            self.url = path
        elif isinstance(path, (list, tuple)):
            self.url = self.url_template.format('/'.join(path))
        else:
            self.url = self.url_template.format(path)

        self.method = method.lower()

        self.params = params
        self.data = data

        self.start()

    def start(self):
        try:
            requests_method = getattr(s, self.method)
        except AttributeError:
            raise

        self.response = requests_method(self.url,
                                        params=self.params,
                                        data=self.data)

        try:
            self.response.raise_for_status()
        except requests.exceptions.HTTPError:
            error = self._get_error(self.response)
            raise NanagogoError(*error)

    def _get_error(self, response):
        http_status_code = response.status_code
        try:
            data = json.loads(response.text)

            if isinstance(data['error'], dict):
                status = data['error']['code']
                error_message = data['error']['message']
                if error_message in self.error_translations:
                    error_eng = self.error_translations[error_message]
                    error_message = '{} ({})'.format(error_eng,
                                                     error_message)
            else:
                status = data['status']
                error_message = data['error']

            return (status, http_status_code, error_message)

        except ValueError:
            raise

    def wrap(self):
        data = json.loads(self.response.text)['data']

        if isinstance(data, list):
            res = NanagogoResponseList(data)
        elif isinstance(data, dict):
            res = NanagogoResponseDict(data)

        res.response = self.response
        res.headers = res.response.headers

        return res

if __name__ == "__main__":
    pass
