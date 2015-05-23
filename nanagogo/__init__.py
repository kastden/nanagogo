#!/usr/bin/env python3

import json

from nanagogo.api import NanagogoAPI

ngg = NanagogoAPI()


class Nanagogo(object):
    users = {}

    def flush(self):
        for user in self.users:
            self.users[user].flush()

    def info(self, *args):
        users = {}

        # The API info endpoint will return info about maximum five users at a time.
        # Trying to request any more than that will result in a HTTP 400 error.
        chunks = [args[i:i + 5] for i in range(0, len(args), 5)]

        for chunk in chunks:
            talkids = ','.join(chunk)
            response = ngg.talk.info(talkIds=talkids)
            data = response['talks']
            for userinfo in data:
                talkid = userinfo['talkId']
                users[talkid] = userinfo

                if talkid in self.users:
                    self.users[talkid]._info = userinfo
                else:
                    self.users[talkid] = NanagogoUser(talkid, _info=userinfo)

        return users

    def user(self, id):
        kwargs = {}
        if not id in self.users:
            self.users[id] = NanagogoUser(id)

        return self.users[id]


class NanagogoUser(object):
    _info = {}

    def __init__(self, id, _info=None):
        self.id = id
        if _info:
            self._info = _info

    @property
    def info(self):
        if not self._info:
            response = ngg.talk.info(talkIds=self.id)
            info = response['talks'][0]

            self._info = info

        return self._info

    def flush(self):
        self._info = {}

    def status(self, status_id):
        path = 'talk/post/detail/{}/{}'.format(self.id, status_id)
        e = ngg.path(path)
        status = e()
        return status

    def feed(self, postid=None, limit=100, posts_only=True):
        if not postid:
            postid = self.info['lastPostId']

        params = {'direction': 'PREV',
                  'limit': limit,
                  'postId': postid,
                  'talkId': self.id}
        data = ngg.talk.post.list(**params)

        if posts_only:
            return data['posts']
        else:
            return data

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


if __name__ == "__main__":
    from pprint import pprint
    n = Nanagogo()
