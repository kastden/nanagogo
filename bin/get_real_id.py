#!/usr/bin/env python3

import re
import yaml
import sys

import requests

''' Get a 755 user's real talkId. 

As an example, the ID for Furuhata Nao's page is 
Xe8jJ0D40_aWkVIvojdMdG== (http://7gogo.jp/lp/Xe8jJ0D40_aWkVIvojdMdG==),
but her real talkId (for use with the API) is MqsG1FLTi-_9GtN76wEuUm==.'''

def get_real_id(url):
    r = requests.get(url)
    r.raise_for_status()

    match = re.compile('setting = ({.*?});', re.DOTALL)
    setting = match.search(r.text).group(1)
    data = yaml.load(setting)

    return data['talkId']


if __name__ == "__main__":
    args = sys.argv[1:]
    for id in args:
        if id.startswith('http'):
            url = id
        else:
            url = 'http://7gogo.jp/lp/{}'.format(id)

        real_id = get_real_id(url)
        print('{} : {}'.format(url, real_id))
