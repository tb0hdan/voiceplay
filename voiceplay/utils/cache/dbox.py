#-*- coding: utf-8 -*-
""" DropBox module """

import os

import dropbox

from voiceplay.config import Config
from voiceplay.logger import logger

# https://www.dropbox.com/developers/apps
# Status - Development
# Development users - Only you
# Permission type - App folder
# Generated access token

class DBox(object):
    """
    Dropbox cache backend
    """
    def __init__(self):
        self._dbx = None
        self.ACCESS_TOKEN = Config().cfg_data().get('dropbox', {}).get('access_token')

    @property
    def dbx(self):
        """
        Instantiate Dropbox class and return object
        """
        if not self._dbx:
            self._dbx = dropbox.Dropbox(self.ACCESS_TOKEN)
        return self._dbx

    def search(self, query=''):
        """
        Search Dropbox application folder
        """
        files = []
        for entry in self.dbx.files_list_folder(query).entries:
            files.append([entry.name, entry.id])
        logger.debug('DBox: found %s files', len(files))
        return files

    def download(self, file_id, file_name):
        """
        Download file from Dropbox
        """
        fpath = os.path.join(os.path.sep, os.path.basename(file_name))
        self.dbx.files_download_to_file(file_name, fpath)

    def upload(self, file_name):
        """
        Upload file to Dropbox
        """
        if not self.health_check():
            return
        fpath = os.path.join(os.path.sep, os.path.basename(file_name))
        self.dbx.files_upload(open(file_name, 'r').read(), fpath)
        logger.debug('DBox File path: %s', fpath)

    def get_available_space(self):
        """
        Return available space (bytes)
        """
        usage = self.dbx.users_get_space_usage()
        return usage.allocation.get_individual().allocated - usage.used

    def get_safe_available_space(self):
        """
        TODO: Make this configurable, 1G for the time being should be ok
        """
        return self.get_available_space() - 1 * 1024 * 1024 * 1024

    def health_check(self):
        """
        Cache backend health check
        """
        status = True
        if self.get_safe_available_space() <= 0:
            logger.error('DBox: No free space available!')
            status = False
        return status
