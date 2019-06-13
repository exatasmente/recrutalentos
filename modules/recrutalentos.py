

class Recrutalentos(object):

    def __init__(
        self,
        t = None,  # label
        c = None,  # controller
        f = None,  # function
        i = None,  # id
        u = None  # url
    ):
        self.label = t or current.response.view_title
        self.controller = c or current.request.controller
        self.function = f or current.request.function
        self.arg = i or (current.request.args[0] if current.request.args else None)
        self.url = u or URL()

        # self.request = current.request
        # self.response = current.response
        # self.auth = current.auth

        key = '{}/{}'.format(self.controller, self.function)
        if self.arg:
            key = '{}/{}'.format(key, self.arg)

        self.key = key

    @classmethod
    def from_dict(cls, bookmark_dict):
        if isinstance(bookmark_dict, str):
            bookmark_dict = eval(bookmark_dict)

        return cls(
            t = bookmark_dict['data']['t'],
            c = bookmark_dict['data']['c'],
            f = bookmark_dict['data']['f'],
            i = bookmark_dict['data']['i'],
            u = bookmark_dict['data']['u'],
        )

    def dict(self):
        return {
            'key': self.key,
            'data': {
                't': self.label,
                'c': self.controller,
                'f': self.function,
                'i': self.arg,
                'u': self.url
            }
        }

    def __repr__(self):
        return repr(self.dict())

    def add(self):
        if not current.auth.user.bookmarks:
            current.auth.user.bookmarks = {}
        elif not isinstance(current.auth.user.bookmarks, dict):
            current.auth.user.bookmarks = eval(current.auth.user.bookmarks)

        if self.key not in Bookmark.list():
            current.auth.user.bookmarks[self.key] = self.dict()['data']
            query = (current.db.auth_user.id == current.auth.user.id)
            current.db(query).update(bookmarks=current.auth.user.bookmarks)

        return

    def delete(self):

        # appadmin and user/profile save bookmarks as str
        if not isinstance(current.auth.user.bookmarks, dict):
            current.auth.user.bookmarks = eval(current.auth.user.bookmarks)

        # update session and db
        try:
            del current.auth.user.bookmarks[self.key]
            query = (current.db.auth_user.id == current.auth.user.id)
            current.db(query).update(bookmarks=current.auth.user.bookmarks)
        except:
            pass

        return

    def is_active(self):
        '''returns 'active' if bookmark in bookmark list'''

        # if current.auth.user and \
        #     current.auth.user.bookmarks and \
        #     current.response.bookmark.dict()['key'] in Bookmark.list():
        #     # current.response.bookmark['key'] in current.auth.user.bookmarks:
        if self.key in Bookmark.list():
            return 'active'
        else:
            return

    @classmethod
    def list(cls):
        '''returns list of bookmarks as k,v pairs'''
        if not current.auth.user or not current.auth.user.bookmarks:
            return {}
        elif isinstance(current.auth.user.bookmarks, dict):
            return current.auth.user.bookmarks
        elif isinstance(current.auth.user.bookmarks, str):
            return eval(current.auth.user.bookmarks)
