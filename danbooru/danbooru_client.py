#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright 2009 Luca Beltrame <einar@heavensinferno.net>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License, under 
#   version 2 of the License, or (at your option) any later version.
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

"""Danbooru Client is a program to access Danbooru based websites. Danbooru is a
Ruby on Rails-powered image board. The Danbooru software offers a POST and a
REST API to programmatically access the board images, and this program is a KDE
implementation of said API coupled with a graphical user interface."""

import sys

from PyKDE4.kdecore import KAboutData, ki18n, KCmdLineArgs
from PyKDE4.kdeui import KApplication

import mainwindow

def main():

    app_name="danbooru_client"
    catalog = "danbooru_client"
    program_name = ki18n("Danbooru Client")
    version = "0.4"
    description = ki18n("A client for Danbooru sites.")
    license = KAboutData.License_GPL
    copyright = ki18n("(C) 2009 Luca Beltrame")
    text = ki18n("Danbooru Client is a program to access Danbooru image boards.")
    home_page = "http://www.dennogumi.org"
    bug_email = "einar@heavensinferno.net"

    about_data = KAboutData(app_name, catalog, program_name, version, description,
                        license, copyright, text, home_page, bug_email)

    about_data.setProgramIconName("internet-web-browser")

    KCmdLineArgs.init(sys.argv, about_data)
    app = KApplication()
    mw = mainwindow.MainWindow()
    mw.show()
    app.exec_()

if __name__ == '__main__':
    main()
