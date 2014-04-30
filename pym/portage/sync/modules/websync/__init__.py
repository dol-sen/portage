# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

"""WebRSync plug-in module for portage.
Performs a http download of a portage snapshot and verifies and
 unpacks it to the repo location.
"""

import os

DEFAULT_CLASS = "WebRsync"
AVAILABLE_CLASSES = [ "WebRsync",  "PyWebsync"]
options = {"1": "WebRsync", "2": "PyWebsync"}


config_class = DEFAULT_CLASS
try:
	test_param = os.environ["TESTIT"]
	if test_param in options:
		config_class = options[test_param]
except KeyError:
	pass


module_spec = {
	'name': 'webrsync',
	'description': __doc__,
	'provides':{
		'module1': {
			'name': "websync",
			'class': config_class,
			'description': __doc__,
			'functions': ['sync', 'new', 'exists'],
			'func_desc': {
				'sync': 'Performs a git pull on the repository',
				'new': 'Creates the new repository at the specified location',
				'exists': 'Returns a boolean of whether the specified dir ' +
					'exists and is a valid Git repository',
			},
			'func_parameters': {
				'kwargs': {
					'type': dict,
					'description': 'Standard python **kwargs parameter format' +
						'Please refer to the sync modules specs at ' +
						'"https://wiki.gentoo.org:Project:Portage" for details',
				},
			},
		},
	}
}
