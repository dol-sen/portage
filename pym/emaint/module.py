#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$


from __future__ import print_function

from portage import os
from portage.exception import PortageException


class InvalidModuleName(PortageException):
	"""An invalid or unknown module name."""


class Module(object):
	"""Class to define and hold our plug-in modules

	@type name: string
	@param name: the module name
	@type path: the path to the new module
	"""

	def __init__(self, name, path):
		"""Some variables initialization"""
		self.name = name
		self.path = path
		self.kids_names = []
		self.initialized = self._initialize()

	def _initialize(self):
		"""Initialize the plug-in module

		@rtype: boolean
		"""
		try:
			os.chdir(self.path)
			mod_name = ".".join(["emaint", "modules", self.name])
			self._module = __import__(mod_name, [],[], ["not empty"])
			self.valid = True
		except ImportError, e:
			self.valid = False
			return False
		self.module_spec = self._module.module_spec
		#self._module.get_class = self.get_class
		self.kids = {}
		for submodule in self.module_spec['provides']:
			kid = self.module_spec['provides'][submodule]
			kidname = kid['name']
			kid['module_name'] = '.'.join([mod_name, self.name])
			#kid['parent'] = self._module
			kid['is_imported'] = False
			self.kids[kidname] = kid
			self.kids_names.append(kidname)
		return True

	def get_class(self, name):
		if not name or name not in self.kids_names:
			raise InvalidModuleName("Module name '%s' was invalid or not"
				%modname + "part of the module '%s'" %self.name)
		kid = self.kids[name]
		if kid['is_imported']:
			module = kid['instance']
		else:
			try:
				module = __import__(kid['module_name'], [],[], ["not empty"])
				kid['instance'] = module
				kid['is_imported'] = True
			except ImportError, e:
				raise
			mod_class = getattr(module, kid['class'])
		return mod_class


class Modules(object):
	"""Dynamic modules system for loading and retrieving any of the
	installed emaint modules and/or provided class's

	@param path: Optional path to the "modules" directory or
			defaults to the directory of this file + '/modules'
	"""

	def __init__(self, path=None):
		if path:
			self.module_path = path
		else:
			self.module_path = os.path.join((
				os.path.dirname(os.path.realpath(__file__))), "modules")
		self.modules = self._get_all_modules()
		self.module_names = list(self.modules)
		self.module_names.sort()

	def _get_all_modules(self):
		"""scans the emaint modules dir for loadable modules

		@rtype: dictionary of module_plugins
		"""
		module_dir =  self.module_path
		importables = []
		names = os.listdir(module_dir)
		for entry in names:
			if os.path.isdir(os.path.join(module_dir, entry)):
				try:
					statinfo = os.stat(os.path.join(module_dir, entry, '__init__.py'))
					if statinfo.st_nlink == 1:
						importables.append(entry)
				except EnvironmentError, er:
					pass
		os.chdir(module_dir)
		kids = {}
		for entry in importables:
			new = Module(entry, module_dir) #, self)
			for module_name in new.kids:
				kid = new.kids[module_name]
				kid['parent'] = new
				kids[kid['name']] = kid
		return kids

	def get_module_names(self):
		"""Convienence function to return the list of installed modules
		available

		@rtype: list
		@return: the installed module names available
		"""
		return self.module_names

	def get_class(self, modname):
		"""Retrieves a module class desired

		@type modname: string
		@param modname: the module class name
		"""
		if modname and modname in self.module_names:
			mod = self.modules[modname]['parent'].get_class(modname)
		else:
			raise InvalidModuleName("Module name '%s' was invalid or not"
				%modname + "found")
		return mod

	def get_description(self, modname):
		"""Retrieves the module class decription

		@type modname: string
		@param modname: the module class name
		@type string
		@return: the modules class decription
		"""
		if modname and modname in self.module_names:
			mod = self.modules[modname]['description']
		else:
			raise InvalidModuleName("Module name '%s' was invalid or not"
				%modname + "found")
		return mod

	def get_functions(self, modname):
		"""Retrieves the module class  exported functions

		@type modname: string
		@param modname: the module class name
		@type list
		@return: the modules class exported functions
		"""
		if modname and modname in self.module_names:
			mod = self.modules[modname]['functions']
		else:
			raise InvalidModuleName("Module name '%s' was invalid or not"
				%modname + "found")
		return mod

	def get_func_descriptions(self, modname):
		"""Retrieves the module class  exported functions descriptions

		@type modname: string
		@param modname: the module class name
		@type list
		@return: the modules class exported functions descriptions
		"""
		if modname and modname in self.module_names:
			desc = self.modules[modname]['func_desc']
		else:
			raise InvalidModuleName("Module name '%s' was invalid or not"
				%modname + "found")
		return desc
