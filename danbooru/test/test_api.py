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
import SimpleHTTPServer
import SocketServer
import threading
import unittest

from PyQt4.QtCore import QTimer, QByteArray
from PyKDE4.kdeui import KApplication
from PyKDE4.kdecore import KAboutData, KCmdLineArgs, ki18n

sys.path.insert(0, "../../")

from danbooru import api

"Module that provides unit tests for the Danbooru API"

app_name = "test_danbooru_client"
program_name = ki18n("Danbooru Client")

about_data = KAboutData(QByteArray(app_name), "", program_name,
                        QByteArray("version"))
KCmdLineArgs.init(sys.argv, about_data)
app = KApplication()

class ApiTest(unittest.TestCase):

    def setUp(self):

        self.api = api.Danbooru("http://localhost:8080")

    def testConnection(self):

        self.api.dataReady.connect(self.length_test)
        self.api.get_post_list(limit=5)

    def length_test(self):

        try:
            print "Testing connection and length...",
            self.assertEqual(len(self.api.data), 5)
        except AssertionError as error:
            print "ERROR: %s" % error
        else:
            print "OK"

    def testRating(self):

        self.api.dataReady.connect(self.rating_test)
        self.api.selected_ratings = "Safe"
        self.api.get_post_list(limit=5)

    def rating_test(self):

        try:
            print "Testing rating...",
            self.assertEqual(len(self.api.data), 4)
        except AssertionError as error:
            print "ERROR: %s" % error
        else:
            print "OK"

    def testBlacklist(self):

        blacklist = ["vocaloid", "tagme"]
        self.api.blacklist = blacklist
        self.api.dataReady.connect(self.blacklist_test)
        self.api.get_post_list(limit=5)

    def blacklist_test(self):

        try:
            print "Testing blacklist...",
            self.assertEqual(len(self.api.data), 1)
        except AssertionError as error:
            print "ERROR: %s" % error
        else:
            print "OK"

    def testThumbnailRetrieval(self):

        self.api.dataReady.connect(self.thumbnail_test_first)
        self.api.get_post_list(limit=5)

    def thumbnail_test_first(self):

        url = self.api.data[0].thumbnail_url
        self.api.dataDownloaded.connect(self.thumbnail_test_second)
        self.api.get_image(url)

    def thumbnail_test_second(self, name, pixmap):

        try:
            print "Testing thumbnail/image retrieval...",
            self.assertFalse(pixmap.isNull())
        except AssertionError as error:
            print "ERROR: %d" % error
        else:
            print "OK"

class TestServer(SocketServer.TCPServer):
    allow_reuse_address = True

def main():

    PORT = 8080

    handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    httpd = TestServer(("", PORT), handler)

    httpd_thread = threading.Thread(target=httpd.serve_forever)
    httpd_thread.daemon = True
    httpd_thread.start()

    suite = unittest.TestLoader().loadTestsFromTestCase(ApiTest)
    unittest.TextTestRunner(verbosity=0).run(suite)

    # So we can end the testing once it's done
    QTimer.singleShot(5000, app.quit)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
