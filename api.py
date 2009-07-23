#!/usr/bin/env python

import json

from PyKDE4.kdecore import KUrl, KTemporaryFile
from PyKDE4.kio import KIO

"Module that provides a wrapper for Danbooru API calls."

class Danbooru(object):

    POST_URL = "post.json"
    TAG_URL = ""

    def __init__(self, api_url):
        
        if not api_url.endswith("/"):
            api_url = api_url + "/"

        self.url = api_url

    def get_post_list(self, limit=5, tags=None):
        
        limit_parameter = "limit=%d" % limit
        request_url = KUrl(''.join((self.url, self.POST_URL, "?".
                                    limit_parameter)))
        data = None
        
        tempfile = KTemporaryFile()
        
        if tempfile.open():
            flags = KIO.JobFlags(KIO.Overwrite | KIO.HideProgressInfo)
            job = KIO.file_copy(KUrl(self.api_url),
                                KUrl(tempfile.fileName()), -1, flags)
            #job.ui().setWindow(self)
            if KIO.NetAccess.synchronousRun(job, self):
                dest_url = job.destUrl()
                api_response = open(dest_url.path())
                data = json.load(api_response)
                
                api_response.close()
                KIO.NetAccess.removeTempFile(tempfile)
        
        return data
    
    def get_thumbnail_urls(json_data):

        urls = list()
        for item in json_data:
            preview_url = item["preview_url"]
            urls.append(preview_url)

        return urls

    def get_picture_url(json_data):
        pass


