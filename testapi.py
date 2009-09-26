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

import unittest

from PyQt4.QtCore import QString
from PyQt4.QtGui import QImage
from PyKDE4.kdecore import KUrl, KTemporaryFile
from PyKDE4.kio import KIO

import api

"Module that provides unit tests for the Danbooru API"

class testAPI(unittest.TestCase):

    URL = "http://www.konachan.com"

    def setUp(self):
        self.api = api.Danbooru("http://www.konachan.net")

    def testData(self):
        pass

    def testGetPostList(self):
        pass

    def testGetThumbnailUrls(self):
        pass

    def testGetPicture(self):
        pass

