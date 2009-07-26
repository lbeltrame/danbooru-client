#!/usr/bin/env python

import json
import urllib

from PyKDE4.kdecore import KUrl

"Module that provides a wrapper for Danbooru API calls."

class Danbooru(object):

    "Class to provide a Python wrapper to the Danbooru API."

    POST_URL = "post/index.json"
    TAG_URL = "tag/index.json"

    def __init__(self, api_url, parent=None):
        
        if not api_url.endswith("/"):
            api_url = api_url + "/"

        self.url = api_url
        self.parent = parent

    def get_post_list(self, limit=5, tags=None):
        
        limit_parameter = "limit=%d" % limit
        request_url = ''.join((self.url, self.POST_URL, "?",
                                    limit_parameter))
        data = None
        print request_url
        api_response = urllib.urlopen(request_url)
        data = json.load(api_response)
                
        return data
    
    def get_thumbnail_urls(self, json_data):

        urls = list()
        for item in json_data:
            preview_url = KUrl(item["preview_url"])
            urls.append(preview_url)

        return urls

    def get_picture_url(self, picture_index, json_data):
        
        picture_data = json_data[picture_index]
        picture_url = KUrl(picture_data["file_url"])

        return picture_url
        


