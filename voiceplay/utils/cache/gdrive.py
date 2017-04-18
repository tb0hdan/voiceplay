#-*- coding: utf-8 -*-
""" Google Drive module """

import argparse

import logging
import os

import httplib2
import requests

from apiclient import discovery
from apiclient.http import MediaFileUpload  # pylint:disable=import-error
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from voiceplay import __title__
from voiceplay.config import Config
from voiceplay.logger import logger

# https://developers.google.com/drive/v3/web/quickstart/python#step_1_turn_on_the_api_name


class GDrive(object):
    """
    GDrive access
    """
    SCOPES = 'https://www.googleapis.com/auth/drive.appfolder https://www.googleapis.com/auth/drive.metadata.readonly'

    def __init__(self):
        self._credentials = None
        self._service = None
        self.CLIENT_SECRET_FILE = os.path.join(Config().cfg_data().get('persistent_dir'),
                                               'client_secret.json')
        self.STORED_CREDENTIALS = os.path.join(Config().cfg_data().get('persistent_dir'),
                                               'stored_credentials.json')
        self.healthy = True


    @property
    def credentials(self):
        """
        Google API credentials object
        """
        if not self._credentials:
            self._credentials = self.get_credentials()
        return self._credentials

    @property
    def service(self):
        """
        Google API service object
        """
        if not self._service:
            self._service = self.get_service()
        return self._service

    def get_credentials(self):
        """Gets valid user credentials from storage.
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        Returns:
            Credentials, the obtained credential.
        """
        credential_path = self.STORED_CREDENTIALS
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = __title__
            args = ['--logging_level', 'DEBUG'] if logger.level == logging.DEBUG else []
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args(args)
            credentials = tools.run_flow(flow, store, flags)
            logger.debug('Storing credentials to %r', credential_path)
        return credentials

    def get_service(self):
        """
        Return Google Drive API service using Google API
        """
        service = None
        if self.credentials:
            http = self.credentials.authorize(httplib2.Http())
            service = discovery.build('drive', 'v3', http=http)
        return service

    def search(self, query="mimeType='audio/mpeg'"):
        """
        Search for files using their MIME types
        """
        files = []
        page_token = None
        while True:
            response = self.service.files().list(q=query,
                                                 fields='nextPageToken, files(id, name)',
                                                 spaces='appDataFolder',
                                                 pageToken=page_token).execute()
            for remote_file in response.get('files', []):
                file_id = remote_file.get('id')
                file_name = remote_file.get('name')
                files.append([file_name, file_id])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        logger.debug('GDrive: found %s files', len(files))
        return files

    def download(self, file_id, file_name):
        """
        Download file from Google Drive
        """
        request = self.service.files().get_media(fileId=file_id)
        r = requests.get(request.uri, headers={'Authorization': 'Bearer {0!s}'.format(self.credentials.access_token)},
                         stream=True)
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=8196):
                fd.write(chunk)

    def upload(self, fname):
        """
        Upload file to Google Drive
        """
        if not self.health_check():
            return
        file_metadata = {
            'name': os.path.basename(fname),
            'parents': ['appDataFolder']
        }
        media = MediaFileUpload(fname,
                                mimetype='audio/mpeg',
                                resumable=True)
        file_obj = self.service.files().create(body=file_metadata,
                                               media_body=media,
                                               fields='id').execute()
        logger.debug('File ID: %s', file_obj.get('id'))

    def get_available_space(self):
        """
        Return available space (bytes)
        """
        # https://developers.google.com/drive/v3/reference/about/get
        # https://developers.google.com/drive/v3/web/query-parameters
        response = self.service.about().get(fields='storageQuota').execute().get('storageQuota')
        return int(response.get('limit')) - int(response.get('usage'))

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
            logger.error('GDrive: No free space available!')
            status = False
        return status
