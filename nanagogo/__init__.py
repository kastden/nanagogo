#!/usr/bin/env python3

import json
from pprint import pprint

from .api import NanagogoAPI

ngg = NanagogoAPI()


class NanagogoUser(object):

    def __init__(self, id):
        self.id = id

    @property
    def info(self):
        result = ngg.talk.info(talkIds=self.id)
        info = result['talks'][0]

        if not info['talkId'] == self.id:
            raise

        return info

    def feed(self, postid=None, limit=100, data_only=True):
        if not postid:
            postid = self.info['lastPostId']

        params = {'direction': 'PREV',
                  'limit': limit,
                  'postId': postid,
                  'talkId': self.id}
        data = ngg.talk.post.list(**params)

        if data_only:
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
    u = NanagogoUser('AGsfxp1A1kO9GtN76wEuUm==')

    for m in u.iterfeed(postid=10):
        body = m['body']
        for node in body:
            if node.get('image', None) and node['bodyType'] == 3:
                pprint(node['image'])
