#!/usr/bin/env python3

import json

from api import NanagogoAPI

ngg = NanagogoAPI()


class Nanagogo(object):
    users = {}

    def flush(self):
        self.info = {}

    def info(self, *args):
        users = {}

        # The API info endpoint will return max five users at a time.
        # Trying to request more than that will return in a HTTP 400 error.
        chunks = [args[i:i + 5] for i in range(0, len(args), 5)]

        for chunk in chunks:
            talkids = ','.join(chunk)
            response = ngg.talk.info(talkIds=talkids)
            data = response['talks']
            for user in data:
                talkid = user['talkId']
                users[talkid] = user

        self.users.update(users)
        return users

    def user(self, id):
        kwargs = {}
        if id in self.users:
            kwargs['_info'] = self.users[id]
        return NanagogoUser(id, **kwargs)


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

            if not info['talkId'] == self.id:
                raise

            self._info = info

        return self._info

    def flush(self):
        self._info = {}

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
    n = Nanagogo()
