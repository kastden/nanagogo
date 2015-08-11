#!/usr/bin/env python3

"""Get a 755 user's real talkId from their public ID on the website.

As an example, the ID for Furuhata Nao's page is
Xe8jJ0D40_aWkVIvojdMdG== (http://7gogo.jp/lp/Xe8jJ0D40_aWkVIvojdMdG==), but her
real talkId (for use with the API) is MqsG1FLTi-_9GtN76wEuUm==.

Example usage and output:
$ python3 get_real_id.py http://7gogo.jp/lp/Xe8jJ0D40_aWkVIvojdMdG== 9YFoGjThCxeWkVIvojdMdG==
http://7gogo.jp/lp/Xe8jJ0D40_aWkVIvojdMdG== : MqsG1FLTi-_9GtN76wEuUm==
http://7gogo.jp/lp/9YFoGjThCxeWkVIvojdMdG== : Kx09K9lOsMF9GtN76wEuUm==
"""

import re
import yaml
import sys

import requests


def get_real_id(url):

    """ Get a user's talkId from their nanangogo page.

    This function requests the HTML page on the given URL, extracts the
    the settings dictionary from the embedded javascript, parses it as YAML
    and returns their talkId.
    """
    r = requests.get(url)
    r.raise_for_status()

    pattern = re.compile('setting = ({.*?});', re.DOTALL)

    try:
        setting = pattern.search(r.text).group(1)
    except AttributeError:
        raise ValueError("Couldn't find settings dictionary in page")

    data = yaml.load(setting)
    return data['talkId']


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        sys.exit(__doc__)

    for id in args:
        if id.startswith('http'):
            url = id
        else:
            url = 'http://7gogo.jp/lp/{}'.format(id)

        real_id = get_real_id(url)
        print('{} : {}'.format(url, real_id))
