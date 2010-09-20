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

"""Program to tag Danbooru files using Nepomuk. It takes the tags embedded into
the file name and converts them into Nepomuk tags. Its typical invocation is:

danbooru2nepomuk [-r] <file or directory>

The program automatically determines if you're supplying a directory or a file.
In the former case, the directory is scanned for image files which are
subsequently tagged. To recurse through subdirectories, use the -r option."""

import sys
import re

from PyQt4.QtCore import QDirIterator, QDir, QFileInfo, QUrl
from PyKDE4.kdecore import (KAboutData, KCmdLineArgs, KCmdLineOptions, i18n,
                            ki18n)
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.kdeui import KApplication
from PyKDE4.kdecore import KUrl


# Regexp to filter out the board name and post ID from the filename
BOARD_REGEX = re.compile("(.*[0-9]+)\s(.*)(.jpe?g|.gif|.png|.tif)")
# Tags we don't want in, because they're uninformative
TAGS_BLACKLIST = ["hentai","sample_resized", "tagme", "duplicate",
                  "jpeg_artifacts", "ass", "breasts", "pantsu", "loli",
                 "erect_nipples"]

def tag_directory(path,recursive=False):

    """Scans a directory (recursively, optionally) and tags the files found
   there. Only image files are taken into account."""

    if recursive:
        basedir = QDirIterator(path)

        while basedir.hasNext():
            directory = basedir.next()
            contents = QDir(directory)
            contents.setFilter(QDir.Files)
            files = contents.entryInfoList()

            for filename in files:
                tag(filename)
    else:
        contents = QDir(path)
        contents.setFilter(QDir.Files)
        files = contents.entryInfoList()

        for filename in files:
            tag(filename)

def tag(filename):

    "Convenience function that wraps extract_tags and tag_file."

    tags = extract_tags(filename)
    tag_file(filename, tags=tags)

def extract_tags(filename, blacklist=TAGS_BLACKLIST):

    """Function to extract tags from a Danbooru file name. Returns a list of tags
    found."""

    # filename = filename.fileName() # strip the path

    filename = unicode(filename)
    match = BOARD_REGEX.match(filename)
    if match:
        # Get only the tag part
        data = match.groups()[1]
    else:
        # Skip non-matching files
         return

    data = data.split()
    # Remove empty tags
    data = [item for item in data if item and item not in blacklist]

    return data

def tag_file(filename, tags=None):

    """Tags a file in Nepomuk using the provided tag list. If tags are not
    present in Nepomuk, they are added automatically. "tags" must be a Python
    list of strings, one item for each tag."""

    absolute_path = QFileInfo(filename).absoluteFilePath()
    resource = Nepomuk.Resource(KUrl(absolute_path))

    for tag in tags:

        newtag = Nepomuk.Tag(tag)
        newtag.setLabel(tag)
        resource.addTag(newtag)

def setup_kapplication():

    "Function to set up KAboutData."

    app_name="danbooru2nepomuk"
    catalog = "danbooru_client"
    program_name = ki18n("danbooru2nepomuk")
    version = "0.1"
    description = ki18n("A tagger for files downloaded from Danbooru.")
    license = KAboutData.License_GPL
    copyright = ki18n("(C) 2009 Luca Beltrame")
    text = ki18n("An automatic Nepomuk tagger for Danbooru-downloaded images.")
    home_page = "http://www.dennogumi.org"
    bug_email = "einar@heavensinferno.net"

    about_data = KAboutData(app_name, catalog, program_name, version,
                            description, license, copyright, text, home_page,
                            bug_email)

    return about_data

def nepomuk_running():

    """Function to check whether Nepomuk is running or. Returns False
    if Nepomuk is not running, and True otherwise."""

    result = Nepomuk.ResourceManager.instance().init()

    if result == 0:
        return True
    else:
        return False

def main():

    about_data = setup_kapplication()

    KCmdLineArgs.init(sys.argv, about_data)

    options = KCmdLineOptions()
    options.add("+target", ki18n("File or directory to tag"))
    options.add("r").add("recursive", ki18n("Scan a directory recursively"))

    # We're a command line program! No use for KDE or Qt options.

    KCmdLineArgs.addStdCmdLineOptions(KCmdLineArgs.StdCmdLineArgs(
        KCmdLineArgs.CmdLineArgNone)
    )

    KCmdLineArgs.addCmdLineOptions(options)

    setup_kapplication()
    app = KApplication()

    args = KCmdLineArgs.parsedArgs()
    KCmdLineArgs.enable_i18n()

    if not nepomuk_running():
        KCmdLineArgs.usageError(
            i18n("Nepomuk service not running. Please check your installation.")
        )

    if args.count() == 0:
        KCmdLineArgs.usageError(i18n("Not enough arguments."))

    target = args.arg(0)

    info = QFileInfo(args.arg(0))

    if info.isDir():
        tag_directory(target, recursive=args.isSet("recursive"))
    elif info.isFile():
        tag(info.filePath())
    else:
        KCmdLineArgs.usageError(i18n(
            "You need to specify either a file or a valid path."))

if __name__ == '__main__':
    main()
