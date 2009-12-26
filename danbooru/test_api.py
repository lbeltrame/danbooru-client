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
import copy
import time

from PyQt4.QtCore import *
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *

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

    URL = "http://moe.imouto.org"

    def setUp(self):

        self.api = api.Danbooru(self.URL)
        self.old = None
        self.api.dataReady.connect(self._dataTest)

    def _dataTest(self):
        self.assertEqual(len(self.api.data), 15)
        self.api.dataReady.disconnect(self._dataTest)

    def testData(self):

        "Post list retrieval"


        self.api.dataReady.connect(self._dataTest)
        self.api.get_post_list(limit=1)

    def _updateTest(self):

        self.assertEqual(1, False)

        if not self.old:
            print "Here"
            self.old = copy.deepcopy(self.api)
            self.api.update(page=2)
        else:
            current_data = self.api.data
            if self.old:
                print "here"
                self.assertNotEqual(self.current_data, self.old.data)

    def testUpdate(self):

        "Checking update() method"

        self.api.dataReady.connect(self._updateTest)
        self.api.get_post_list(limit=5)

    def testGetThumbnailUrls(self):

        "Thumbnail list retrieval"

        ok = self.api.get_post_list(limit=1)
        data = self.api.data[0]
        self.assertTrue(data)
        url = data.thumbnail_url
        check = self.api.validate_url(url)
        self.assertTrue(check)

    def testGetPicture(self):

        "Image URL and image retrieval"

        self.api.get_post_list(limit=1)
        data = self.api.data[0]
        self.assertTrue(data)
        url = data.full_url
        check = self.api.validate_url(url)
        self.assertTrue(check)
        self.api.get_image(url, verbose=True)
        self.api.dataDownloaded.connect(self.checkImage)

    def checkImage(self, name, pixmap):
        self.assertFalse(pixmap.isNull())
        self.assertFalse(name.isEmpty())

def main():

    print "Testing currently disabled."

    # suite = unittest.TestLoader().loadTestsFromTestCase(TestDanbooruAPI)
    # unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
