# Copyright 2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

"""Git plug-in module for portage.
Performs a git pull on repositories
"""


from portage.sync.config_checks import CheckSyncConfig


module_spec = {
	'name': 'git',
	'description': __doc__,
	'provides':{
		'git-module': {
			'name': "git",
			'class': "GitSync",
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
					'required-keys': ['options', 'settings', 'logger', 'repo',
						'xterm_titles', 'spawn_kwargs'],
				},
			},
			'validate_config': CheckSyncConfig,
		}
	}
}
