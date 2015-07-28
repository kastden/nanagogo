#!/usr/bin/env python3

import json
import re
import time

import requests


class NanagogoException(Exception):
    pass


class NanagogoResponse(dict):

    """The response from the 7gogo private JSON API, returned as a dict.

    The HTTP headers is accessible in :attr:`NanagogoResponse.headers <NanagogoResponse.headers>`
    and the original text response in :attr:`NanagogoResponse.text <NanagogoResponse.text>`.

    :param data: The data from the Nanagogo API, in the form of a dict.
    :param status_code: The HTTP status code in the response, in the form of a integer.
    :param raw_text: The raw text in the HTTP response.
    :param headers: The HTTP headers in the HTTP response.
    :param error_message: (optional) In case of errors, a error message returned from the API.
    """

    def __init__(self, data, status_code, raw_text, headers, error_message=None):
        if not isinstance(data, dict):
            raise TypeError('data needs to be a dictionary. Got: {}'.format(
                type(data)))
        if not isinstance(status_code, int):
            raise TypeError('status_code needs to an integer. Got: {}'.format(
                type(status_code)))
        if error_message and not isinstance(error_message, str):
            raise TypeError('error_message needs to be a string. Got: {}'.format(
                type(error_message)))

        data['status_code'] = status_code
        if status_code != 200 and error_message:
            data['error_message'] = error_message

        super().__init__(data)


class NanagogoRequest(object):
    url_template = 'https://7gogo.jp/api/{}'
    dump_valueerrors = False

    def __init__(self, path, params={}, data=None, wrap_errors=False):
        """Constructs a request and returns a :class:`NanagogoResponse <NanagogoResponse>`
        object when :meth:`NanagogoResponse.get() <NanagogoResponse.get()>` is called.

        :param path: Path for the new :class:`NanagogoRequest` object. Can be either a tuple/list or a string. If `path` is a string and starts with 'http' then the string will be used for the URL instead. If `path` is a `tuple` or `list` then the strings will be joined with '/' as a seperator and appended to the API URL template. If `path` is a string it will be appended to the API URL template as is.
        :param params: (optional) Dictionary of URL parameters to append to the URL.
        :param wrap_errors: (optional) If an invalid resource is requested from the 7gogo API it will respond with a 4xx/5xx status code and a HTML page instead of the usual JSON response. Setting `wrap_error` to True will result in a dictionary looking like {'status_code' : 404} being returned instead. Setting it to False will cause a `requests.exceptions.HTTPError` exception to be raised on errors (default requests behavior). Default: False.
        """
        if isinstance(path, str) and path.startswith('http'):
            self.url = path
        elif isinstance(path, (list, tuple)):
            self.url = self.url_template.format('/'.join(path))
        else:
            self.url = self.url_template.format(path)

        self.params = params
        self.data = data

        self.wrap_errors = wrap_errors

    def get(self, return_raw=False):
        """
        Performs the request against the 7gogo API.

        :param return_raw: (optional) Instead of wrapping the JSON response and returning a :class:`NanagogoResponse <NanagogoResponse>` directory the raw text from the HTTP response will be returned instead. Default: False
        :return: A :class:`NanagogoResponse <NanagogoResponse>` dictionary.
        :rtype: nanagogo.NanagogoResponse
        """

        r = requests.get(self.url, params=self.params, data=self.data)

        if not self.wrap_errors:
            r.raise_for_status()
        else:
            if 400 <= r.status_code < 600:
                data = {}
                error_message = self._get_error_message_from_html(r.text)
                return NanagogoResponse(data,
                                        r.status_code,
                                        r.text,
                                        r.headers,
                                        error_message=error_message)

        if return_raw:
            return r.text

        try:
            data = json.loads(r.text)
        except ValueError as e:
            # TODO: Dump the text response from the API to
            # /tmp/nanagogo-exception_{timestamp}.txt
            if self.dump_valueerrors:
                pass
            raise NanagogoException(
                'Invalid JSON from the 7gogo JSON API even though we got HTTP status code {}'.format(
                    r.status_code))

        return NanagogoResponse(data, r.status_code, r.text, r.headers)

    def _get_error_message_from_html(self, html):
        match = re.compile(r'<p class="errorMessage">([^<]+)</p>')
        error = match.search(html)
        if error:
            error_message = error.group(1)
        else:
            error_message = "N/A"

        return error_message

    def _log_json_exception(self, e, r):
        pass


def request(path, params, wrap_errors=True):
    req = NanagogoRequest(path,
                          params=params,
                          wrap_errors=wrap_errors)

    response = req.get()

    return response

def _get_user_info(talkid):
    path = ('talk', 'info')
    params = {'talkIds': talkid}
    response = request(path, params)
    return response


def batch_user_lookup(*args, delay=0.6, parallel=5, cache=True):
    """Looks up information about users via the 'talk/info' endpoint, up to five users at a time.

    :param user_ids: The users to look up the information for, either as arguments, list or a tuple.
    :param delay: (optional) ---. Default: 0.6 seconds between each request.
    :param parallel: (optional) How many users to look up the information for at the same time. Default: 5 at a time

    :return: A dictionary with two lists. The users list contains user information received from the API, the failed list contains the talkId's of the users the API weren't able to return any information on.
    """

    if parallel > 5:
        parallel = 5

    users_to_lookup = []
    single_user_lookups = []
    users = {'users': [], 'failed': []}

    for arg in args:
        if isinstance(arg, (list, tuple)):
            for u in arg:
                users_to_lookup += (u),
        else:
            users_to_lookup += (arg),

    chunks = [users_to_lookup[i:i + parallel]
              for i in range(0, len(users_to_lookup), parallel)]

    for chunk in chunks:
        talkids = ','.join(chunk)
        response = _get_user_info(talkids)

        if 'talks' in response:
            users['users'] += response['talks']
        else:
            single_user_lookups += chunk

    for talkid in single_user_lookups:
        response = _get_user_info(talkid)

        if 'talks' in response:
            users['users'] += response['talks']
        else:
            users['failed'] += talkid,

    return users


class NanagogoUser(object):
    _info = {}

    def __init__(self, talkid, lookup_info_on_init=False, _info=None):
        """
        :param id: The user's 7gogo talkId. **The talkId is case sensitive.**
        :param lookup_info_on_init: (optional) Fetch the information for the user on initialization of the class.
        :param _info: (optional) A dict containing the information about the user. The intended usage is when this class is initialized when you already have up to date user info (i.e. when doing batch lookups).
        """

        self.talkid = talkid

        if lookup_info_on_init:
            self.info
        elif _info:
            # A simple check to see if this is a user info dict or not
            if 'talkId' not in _info:
                raise ValueError
            self._info = _info

    @property
    def info(self):
        """ Return user information from the 7gogo API.

        This is a cached property, call :meth:`NanagogoUser.flush() <NanagogoUser.flush()>` to clear it."""

        if not self._info:
            response = _get_user_info(self.talkid)

            # TODO: Better error handling if invalid/wrong result from the API
            info = response['talks'][0]
            self._info = info

        return self._info

    def feed(self, postid=None, limit=100, posts_only=True):
        if not postid:
            postid = self.info['lastPostId']

        path = ('talk', 'post', 'list')
        params = {'direction': 'PREV',
                  'limit': limit,
                  'postId': postid,
                  'talkId': self.talkid}
        response = request(path, params)

        if posts_only:
            return response['posts']
        else:
            return response

    def iterfeed(self, postid=None, limit=100):
        while True:
            data = self.feed(postid=postid, limit=limit)

            if len(data) == 0:
                break

            for post in data:
                yield post

            postid = int(data[-1]['postId']) - 1
            if postid <= 0:
                break

    def flush(self):
        """ Wipes the :attr:`NanagogoUser.info <NanagogoUser.info>` dictionary containing the user information returned from the 7gogo API. The next time :attr:`NanagogoUser.info <NanagogoUser.info>` is accessed it will fetch up to date data from the API.
        """
        self._info = {}


if __name__ == "__main__":
    u = batch_user_lookup(['MqsG1FLTi-_9GtN76wEuUm==', 'Kx09K9lOsMF9GtN76wEuUm==', '768QPJZLbu9GtN76wEuUm=='])
    print(u)

    # nu = NanagogoUser('5768qpjzlbu9GtN76wEuUm==')
    # print(nu.info)

    # for p in nu.iterfeed():
    #     print(p)
    # ngg = Nanagogo()
    # ngg._get_user_info('5768QPJZLbu9GtN76wEuUm==')
