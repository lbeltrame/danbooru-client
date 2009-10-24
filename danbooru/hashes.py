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

from hashlib import sha1

"""This module contains the strings needed to salt the passwords for Danboorun
access. Use the generate_hash function to create an appropriate hash."""

#TODO:Move to configuration?

_MAPPING = {"http://konachan.net":"So-I-Heard-You-Like-Mupkids-?--your-password--",
 "http://konachan.com":"So-I-Heard-You-Like-Mupkids-?--your-password--",
 "http://moe.imouto.org":"choujin-steiner--your-password--"}

def generate_hash(url, password):

    """Generates a hash basing on the Danbooru URL supplied. If there is no
    match in the mapping, returns None, otherwise it returns the SHA1
    hexadecimal hash of the salted password."""

    if url not in _MAPPING:
        return
    
    salt = _MAPPING[url]
    salt.replace("your-password",password)
    sha1_hash = sha1(salt)

    return sha1_hash.hexdigest()


