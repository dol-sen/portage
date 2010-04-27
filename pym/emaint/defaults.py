#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$

# parser option data
CHECK = {"short": "-c", "long": "--check",
	"help": "Check for problems",
	'status': "Checking %s for problems",
	'func': 'check'
	}

FIX = {"short": "-f", "long": "--fix",
	"help": "Attempt to fix problems",
	'status': "Attempting to fix %s",
	'func': 'fix'
	}

# parser options
DEFAULT_OPTIONS = [CHECK, FIX]
