#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$

"""'The emaint program module provides checks and maintenancefor:
  Scanning, checking and fixing problems in the vardb keys.
"""


module_spec = {
    'name': "vdbkey",
    'description': "Provides functions to scan, check and " + \
        'fix: Installed package data ["HOMEPAGE", "SRC_URI", "KEYWORDS", "DESCRIPTION"]',
    'provides':{
        'module1': {
            'name': "vdbkeys",
            'class': "VdbKeyHandler",
            'description':  "Perform checks and fixes problems with an " + \
                "installed package's data",
            'options': ['check', 'fix']
            }
        }
    }
