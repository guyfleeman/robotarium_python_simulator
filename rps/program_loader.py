from rps.program import DrivenRobotariumProgram

import inspect

from importlib.util import spec_from_file_location
from importlib.util import module_from_spec


import os
from os.path import abspath
from os.path import dirname
from os.path import isabs
from os.path import join
from os.path import split

import sys
from sys import argv

class ProgramLoader:
	def __init__(self, module_file, start=None):
		# if a start location is not given, start from the director
		# containing the file with the program entry point
		if start is None:
			start = argv[0]

		# make sure we get the absolute path of the root
		root_loc = abspath(dirname(start))

		# if an an absolute path for the file to loaded was given, use it
		# otherwise concat with the starting location to generate an abs path
		if not isabs(module_file):
			full_path = abspath(join(root_loc, module_file))
		else:
			full_path = abspath(module_file)

		# various names for the module as requires by loader functions
		module_path = dirname(full_path)
		module_path_name = str(full_path)
		_, module_name = split(full_path)
		module_name = module_name.replace('.py', '')
		self._program_module = module_name

		# add the path containing the module to ensure it can be found and loaded
		sys.path.append(module_path)

		# generate a ModuleSpec from the path, and then load the module using the spec
		spec = spec_from_file_location(module_name, module_path_name)
		module = module_from_spec(spec)
		spec.loader.exec_module(module)

		# add the module to system module for later import
		sys.modules[module_name] = module

		# store classes defined by this module in a list
		# (imported modules are also returned by inspection, so we need to discard them)
		self._classes_defined_by_module = []
		classes_in_module = inspect.getmembers(sys.modules[module_name], inspect.isclass)
		for clazz in classes_in_module:
			if clazz[1].__module__ == module_name:
				self._classes_defined_by_module.append(clazz)


	def load(self, required_ancestor=None):
		# no ancestry filter, return everything
		if not required_ancestor:
			return self._classes_defined_by_module

		# search for classes
		matching_children = []
		for clazz in self._classes_defined_by_module:
			class_ancestry = inspect.getmro(clazz[1])
			if required_ancestor in class_ancestry:
				matching_children.append(clazz)
		
		return matching_children	


	def get_program_module(self):
		return self._program_module

