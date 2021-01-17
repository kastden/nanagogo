#!/usr/bin/env python3

from logging import warning

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


class NanagogoUser(object):
    def __init__(self, userid):
        self.userid = userid

    @property
    def info(self):
        path = ("users", self.userid)
        return get(path)

    @property
    def maintalk(self):
        path = ("users", self.userid, "mainTalk")
        return get(path)

    @property
    def grouptalks(self):
        path = ("users", self.userid, "groupTalks")
        return get(path)

    @property
    def ownertalks(self):
        path = ("users", self.userid, "ownerTalks")
        return get(path)
        
    @property
    def following(self):
        path = ("users", self.userid, "followTalks")
        params = {'limit': 500}
        data = get(path, params=params)
        
        if data['nextExisted']:
            warning("nextExisted array not empty in {}".format('/'.join(path)))
        
        following = data['talk']
        
        return following



class NanagogoTalk(object):
    def __init__(self, name):
        self.name = name

    @property
    def info(self):
        path = ("talks", self.name)
        return get(path)

    @property
    def userid(self):
        return self.info['user']['userId']

    def feed(self, count=30, targetid=None, direction="PREV"):
        path = ("talks", self.name, "posts")
        params = {'limit': count,
                  'targetId': targetid,
                  'direction': direction.upper()}

        return get(path, params=params)

    def iterfeed(self, count=200, targetid=None, direction="PREV"):
        direction = direction.upper()
             
        while True:
            # when using next as a parameter to the direction argument
            # the results are off by 10
            # if (direction == "NEXT" and targetid):
            #     targetid = int(targetid) - 10

            feed = self.feed(count=count,
                             targetid=targetid,
                             direction=direction)

            # if direction == "NEXT":
            #     feed = feed[::-1]

            if len(feed) == 0:
                break

            yield feed

            previous_targetid = targetid
            if direction == "NEXT":
                targetid = feed[-1]['post']['postId'] + 1
            else:
                targetid = feed[-1]['post']['postId'] - 1

            if targetid <= 0:
                break
            elif ((direction == "NEXT") and
                     (previous_targetid == targetid - 10)):
                break


if __name__ == "__main__":
    from pprint import pprint

    nt = NanagogoTalk('okada-nana')
    nu = NanagogoUser(nt.userid)
    
    for i in nu.following:
        print(i)
    # for feed in nt.iterfeed(count=300, targetid=1000, direction="next"):
    #     for post in feed:
    #         pprint(post['post']['postId'])
    #     print()
