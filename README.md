# Nanagogo

##### A python library for the [7gogo.jp](http://7gogo.jp/) private API

## Get a user's talkId
7gogo has two kind of IDs for users, a shareUrl ID that is used for accessing a user's page, and a talkId that is used when accessing something with the API.
So in the case of Nao, her shareUrl ID is [Xe8jJ0D40_aWkVIvojdMdG==](http://7gogo.jp/lp/Xe8jJ0D40_aWkVIvojdMdG==) but her talkId is `MqsG1FLTi-_9GtN76wEuUm==`.

There's a script included that gets a user's talkId by parsing the HTML/JSON from 7gogo.

    nanagogo.git/bin$ ./get_real_id.py http://7gogo.jp/lp/Xe8jJ0D40_aWkVIvojdMdG== mj0SMU4NQJhWkVIvojdMdG==
    http://7gogo.jp/lp/Xe8jJ0D40_aWkVIvojdMdG== : MqsG1FLTi-_9GtN76wEuUm==
    http://7gogo.jp/lp/mj0SMU4NQJhWkVIvojdMdG== : ZfBGUyrVNdV9GtN76wEuUm==


## Example usage
    >>> from nanagogo import Nanagogo
    >>> n = Nanagogo()

    # Lookup the info for one or multiple users
    # This will also create NanagogoUser objects for the user, that will be returned if
    # n.user(some_talkId) is called later. This is done so we can cache the info, since 
    # the latest postId is needed when using NanagogoUser.feed() 
    >>> n.info('ZfBGUyrVNdV9GtN76wEuUm==', 'l3A8zzksqtb9GtN76wEuUm==', 'c_hnwvneyJV9GtN76wEuUm==')
    

## Example usage, user objects:

    # Create a user object:
    >>> u = n.user('c_hnwvneyJV9GtN76wEuUm==')

    # Get the user's info
    >>> u.info

    # Get the user's most recent statuses:
    >>> feed = u.feed()

    # Get a status
    >>> status = u.status(20)

    # Iterate over a user's timeline
    >>> for post in u.iterfeed:
    >>>     print(post)