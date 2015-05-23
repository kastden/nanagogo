#!/usr/bin/env python3


import json

import requests


class NGGResponse(dict):
    pass


class NGGClassCall(object):
    url_template = 'https://7gogo.jp/api/{}'

    def __init__(self, callable_cls, uriparts=None):
        self.callable_cls = callable_cls
        if not uriparts:
            self.uriparts = ()
        else:
            self.uriparts = uriparts

    def __getattr__(self, k):
        # Return a initialized instance of the callable_class, with the
        # appended uripart, k
        return self.callable_cls(callable_cls=self.callable_cls,
                                 uriparts=self.uriparts + (k,))

    def append(self, uripart):
        """ Some of the API URLs on 7gogo might include the talkId or a numeric ID.
        Since it's not possible to do NGGClassCall.talk.post.detail.talkId==.600
        this method is included so you instead can write
        NGGClassCall.talk.post.detail.append(talkId==).append(600).

        See also NanagogoAPI.path"""
        uripart = str(uripart)
        return self.__getattr__(uripart)

    def __call__(self, **params):
        for param in params:
            params[param] = str(params[param])

        url = self.url_template.format('/'.join(self.uriparts))

        req = requests.get(url, params=params)
        req.raise_for_status()

        data = json.loads(req.text)

        resp = NGGResponse(data)
        resp.headers = req.headers

        return resp


class NanagogoAPI(NGGClassCall):

    def __init__(self):
        uriparts = ()
        NGGClassCall.__init__(self, callable_cls=NGGClassCall)

    def path(self, path):
        uriparts = tuple(path.split('/'))
        return NGGClassCall(callable_cls=NGGClassCall,
                            uriparts=uriparts)


if __name__ == "__main__":
    NGG = NanagogoAPI()
