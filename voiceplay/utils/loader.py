import inspect
import os
import re
from voiceplay.logger import logger

class PluginLoader(object):
    '''
    Recursive plugin loaded
    '''
    @staticmethod
    def tryimport(package):
        try:
            module = __import__(package, fromlist=['dummy'])
        except Exception as exc:
            logger.error(exc)
            module = None
        return module

    @staticmethod
    def file_to_package(fname, base_path, base_package):
        result = fname.replace(os.path.join(base_path, ''), '').replace('.py', '').replace(os.path.sep, '.')
        result = base_package + '.' + result
        return result

    def package_to_path(self, package):
        path = None
        module = self.tryimport(package)
        if module:
            fname = module.__file__
            path = os.path.dirname(os.path.abspath(fname))
        return path

    def find_files(self, start_dir):
        fnames = []
        for root, dirs, files in os.walk(start_dir, topdown=False):
            for name in files:
                fname = os.path.join(root, name)
                if not fname.endswith('.py') or name == '__init__.py':
                    continue
                fnames.append(fname)
        return fnames

    def find_packages(self, base_package):
        '''
        Return list of packages within base package
        '''
        packages = []
        path = self.package_to_path(base_package)
        for fname in self.find_files(path):
            packages.append(self.file_to_package(fname, path, base_package))
        return packages

    def find_classes(self, base_package, base_class):
        '''
        Return list of classes within base package that are descendants of base_class
        '''
        cls_list = []
        packages = self.find_packages(base_package)
        for package in packages:
            module = self.tryimport(package)
            if not module:
                continue
            classes = inspect.getmembers(module, inspect.isclass)
            for name, cls in classes:
                if issubclass(cls, base_class) and cls != base_class:
                    cls_list.append(cls)
        return cls_list
