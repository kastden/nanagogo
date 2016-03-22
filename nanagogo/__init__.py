#!/usr/bin/env python3

from nanagogo.api import NanagogoRequest, NanagogoError, s


def get(path, params={}):
    r = NanagogoRequest(path,
                        method="GET",
                        params=params)
    return r.wrap()


def post(path, params={}, data=None):
    r = NanagogoRequest(path,
                        method="POST",
                        params=params,
                        data=data)
    return r.wrap()


class NanagogoTalk(object):
    def __init__(self, name):
        self.name = name

    @property
    def info(self):
        path = ("talks", self.name)
        return get(path)

    def feed(self, count=30, targetid=None, direction="PREV"):
        path = ("talks", self.name, "posts")
        params = {'limit': count,
                  'targetId': targetid,
                  'direction': direction.upper()}
        return get(path, params=params)

    def iterfeed(self, count=200, targetid=None):
        while True:
            feed = self.feed(count=count,
                             targetid=targetid,
                             direction="PREV")

            if len(feed) == 0:
                break

            yield feed

            targetid = feed[-1]['post']['postId'] - 1
            if targetid <= 0:
                break


if __name__ == "__main__":
    tani = NanagogoTalk('tani-marika')
    print(tani.info)
