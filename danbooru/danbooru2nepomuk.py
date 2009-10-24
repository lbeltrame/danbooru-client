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

from PyQt4.QtCore import *
from PyKDE4.kdecore import *
from PyKDE4.nepomuk import *
from PyKDE4.kdeui import *

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
                tag(filename.absoluteFilePath())
    else:
        contents = QDir(path)
        contents.setFilter(QDir.Files)
        files = contents.entryInfoList()

        for filename in files:
            tag(filename.absoluteFilePath())

def tag(filename):

    "Convenience function that wraps extract_tags and tag_file."

    tags = extract_tags(filename)
    tag_file(filename, tags=tags)

def all_tags():

    """Function to query Nepomuk for available tags. Returns a list of all
   available tags."""

    tags = Nepomuk.Tag.allTags()
    named_tags = list()

    for tag in tags:
        tagname = unicode(tag.label())
        named_tags.append(tagname)

    return named_tags

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
        print "Skipping file %s" % filename
        return

    data = data.split()
    data = [item for item in data if item not in blacklist]

    return data

def tag_file(filename, tags=None):

    """Tags a file in Nepomuk using the provided tag list. If tags are not
    present in Nepomuk, they are added automatically. "tags" must be a Python
    list of strings, one item for each tag."""

    NEPOMUK_TAGS = all_tags()
    if tags is None:
        return

    absolute_path = QFileInfo(filename).filePath()
    # To work, this needs QUrl
    resource = Nepomuk.Resource(QUrl(absolute_path))

    taglist = list()

    for tag in tags:

        if tag not in NEPOMUK_TAGS:
            newtag = Nepomuk.Tag(tag)
            newtag.setLabel(tag)
            newtag.addIdentifier(tag)
        else:
            newtag = Nepomuk.Tag(tag)

        taglist.append(newtag)
    resource.addTag(newtag)
    resource.setTags(taglist)

def setup_kapplication():

    "Function to set up KAboutData."

    app_name="danbooru2nepomuk"
    catalog = ""
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

    if not nepomuk_running():
        print "Nepomuk service not running. Please check your installation."
        sys.exit(-1)

    if args.count() == 0:
        KCmdLineArgs.enable_i18n()
        KCmdLineArgs.usageError(i18n("Not enough arguments."))

    target = args.arg(0)

    info = QFileInfo(args.arg(0))

    if info.isDir():
        tag_directory(target, recursive=args.isSet("recursive"))
    elif info.isFile():
        tag(info.filePath())
    else:
        print "You need to specify either a file or a valid path."
        sys.exit(-1)

if __name__ == '__main__':
    main()
