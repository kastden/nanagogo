# Nanagogo

##### A python library for the [7gogo.jp](http://7gogo.jp/) v2 private API


## Example usage

    In [1]: from nanagogo import NanagogoTalk, NanagogoUser

To create a NanagogoUser object you need their userId.
You can get this by creating a NanagogoTalk object first.

    In [4]: nt = NanagogoTalk("taniguchi-megu")
    In [5]: nu = NanagogoUser(nt.userid)

Display a user's information 

    In [6]: nu.info
    Out[6]:
    {'accountStatus': 0,
     'coverImageThumbnailUrl': 'https://stat.7gogo.jp/appimg_images/20160303/23/45/5j/j/t02200220p.jpg',
     'coverImageUrl': 'https://stat.7gogo.jp/appimg_images/20160303/23/45/5j/j/o04980498p.jpg',
     'description': None,
     'followed': False,
     'following': False,
     'isParticipating': False,
     'name': '谷口めぐ',
     'registerType': 1,
     'sex': None,
     'thumbnailUrl': 'https://stat.7gogo.jp/appimg_images/20160522/00/61/Wo/j/t02400240p.jpg',
     'userId': '47HUmweGhjNt',
     'userType': 1,
     'visible': True}

Get posts

    In [7]: for node in nt.feed(count=5):
        print(node['post']['postId'])
        ....:
    6522
    6521
    6520
    6519
    6518

Get an user's entire timeline:

    In [8]: for page in nt.iterfeed():
        for node in page:
            pass # do something
