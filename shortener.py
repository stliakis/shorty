import base64
from hashlib import md5

import pymongo

import config


class UrlShortener:
    def __init__(self):
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        mongo_database = mongo_client["shorty"]
        self.urls = mongo_database["urls"]
        self.urls.create_index([("hash", 1)], unique=True)

    def shortcode(self, url):
        """
        Our main shortening function. The rationale here is that
        we are relying on the fact that for similarly sized inputs
        such as URLs the potential for collision in the 32 last bits
        of the MD5 hash is rather unlikely.

        The following things happen, in order:

        * compute the md5 digest of the given source
        * extract the lower 4 bytes
        * base64 encode the result
        * remove trailing padding if it exists

        Of course, should a collision happen, we will evict the previous
        key.

        """
        return base64.b64encode(md5(url.encode('utf-8')).digest()[-8:]).decode("utf-8", "ignore").replace('=',
                                                                                                          '').replace(
            '/', '_')

    def shorten(self, url):
        """
        The shortening workflow is very minimal. We try to
        set the redis key to the url value. We catch any
        exception in the process to properly report failures
        in the client
        """

        code = self.shortcode(url)

        if not self.lookup(code):
            self.urls.insert_one({"hash": code, "url": url})

        return {'success': True,
                'url': url,
                'code': code,
                'shorturl': config.URL_PREFIX + code}

    def lookup(self, code):
        """
        The same strategy is used for the lookup than for the
        shortening. Here a None reply will imply either an
        error or a wrong code.
        """
        entry = self.urls.find_one({"hash": code})
        if entry:
            return entry.get("url")
        return None
