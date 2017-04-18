#-*- coding: utf-8 -*-
""" VoicePlay plugin loader module """

import inspect
import os
import sys
from copy import copy
from voiceplay.utils.helpers import debug_traceback

class PluginLoader(object):
    """
    Recursive plugin loader
    """
    @staticmethod
    def tryimport(package):
        """
        Try to import module, on success return module,
        on error return None and log exception.
        """
        try:
            module = __import__(package, fromlist=['dummy'])
        except Exception as _:
            debug_traceback(sys.exc_info(), __file__, message='Import of %r failed (see message below)' % package)
            module = None
        return module

    @staticmethod
    def file_to_package(fname, base_path, base_package):
        """
        Convert path to package suitable for import
        """
        result = fname.replace(os.path.join(base_path, ''),
                               '').replace('.py', '').replace(os.path.sep, '.')
        result = base_package + '.' + result
        return result

    def package_to_path(self, package):
        """
        Convert package to path (absolute)
        """
        path = None
        module = self.tryimport(package)
        if module:
            fname = module.__file__
            path = os.path.dirname(os.path.abspath(fname))
        return path

    @staticmethod
    def find_files(start_dir):
        """
        Iterate over directory recursively and return *.py files as a list
        (omit package init)
        """
        fnames = []
        for root, _, files in os.walk(start_dir, topdown=False):
            for name in files:
                fname = os.path.join(root, name)
                if not fname.endswith('.py') or name == '__init__.py':
                    continue
                fnames.append(fname)
        return fnames

    def find_packages(self, base_package):
        """
        Return list of packages within base package
        """
        packages = []
        path = self.package_to_path(base_package)
        for fname in self.find_files(path):
            packages.append(self.file_to_package(fname, path, base_package))
        return packages

    def find_classes(self, base_package, base_class, try_sys=True):
        """
        Return list of classes within base package that are descendants of base_class
        """
        cls_list = []
        packages = self.find_packages(base_package)
        for package in packages:
            module = self.tryimport(package)
            if not module:
                continue
            classes = inspect.getmembers(module, inspect.isclass)
            for _, cls in classes:
                if issubclass(cls, base_class) and cls != base_class:
                    cls_list.append(cls)
        if try_sys:
            sys_modules = copy(sys.modules)
            for module_name in sys_modules:
                if module_name.startswith(base_package):
                    module = sys.modules.get(module_name)
                    classes = inspect.getmembers(module, inspect.isclass)
                    for _, cls in classes:
                        if issubclass(cls, base_class) and cls != base_class and not cls in cls_list:
                            cls_list.append(cls)
        return cls_list
