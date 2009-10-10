#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2009 Luca Beltrame <einar@heavensinferno.net>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License, version 2.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import unittest

from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
from PyKDE4.kio import KIO

import api

"Module that provides unit tests for the Danbooru API"

app_name="DanbooruRetrieve"
catalog = ""
program_name = ki18n("Danbooru Client")
version = "1.0"
description = ki18n("A client for Danbooru sites.")
license = KAboutData.License_GPL
copyright = ki18n("(C) 2009 Luca Beltrame")
text = ki18n("Test")
home_page = "http://www.dennogumi.org"
bug_email = "einar@heavensinferno.net"

about_data = KAboutData(app_name, catalog, program_name, version, description,
                license, copyright, text, home_page, bug_email)
KCmdLineArgs.init(sys.argv, about_data)
app = KApplication()

class TestDanbooruAPI(unittest.TestCase):

    URL = "http://konachan.com"

    def setUp(self):

        self.api = api.Danbooru(self.URL)

    def testData(self):

        "Post list retrieval"

        data = self.api.get_post_list(limit=1)
        self.assertTrue(data)

    def testGetThumbnailUrls(self):

        "Thumbnail list retrieval"

        self.api.get_post_list(limit=1)
        urls = self.api.get_thumbnail_urls()
        self.assertEqual(len(urls), 1)
        check = KIO.NetAccess.exists(urls[0], KIO.NetAccess.SourceSide, None)
        self.assertTrue(check)

    def testGetPicture(self):

        "Image URL and image retrieval"

        self.api.get_post_list(limit=1)
        url = self.api.get_picture_url(0)
        check = KIO.NetAccess.exists(url, KIO.NetAccess.SourceSide, None)
        self.assertTrue(check)
        picture, name = self.api.get_image(url, verbose=True)
        self.assertFalse(picture.isNull())

def main():

    suite = unittest.TestLoader().loadTestsFromTestCase(TestDanbooruAPI)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
