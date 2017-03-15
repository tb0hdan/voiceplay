import io
import httplib2
import os

import requests

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

from voiceplay import __title__

# https://developers.google.com/drive/v3/web/quickstart/python#step_1_turn_on_the_api_name

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json

SCOPES = 'https://www.googleapis.com/auth/drive.appfolder'
CLIENT_SECRET_FILE = 'client_secret.json'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_path = './quickstart.json'
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = __title__
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    return service

def search():
    service = get_service()
    page_token = None
    while True:
        response = service.files().list(q="mimeType='audio/mpeg'",
                                        fields='nextPageToken, files(id, name)',
                                        spaces='appDataFolder',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            download(file.get('id'), file.get('name'))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break;


def download(file_id, fname):
    credentials = get_credentials()
    service = get_service()
    request = service.files().get_media(fileId=file_id)
    r = requests.get(request.uri, headers={'Authorization': 'Bearer {0!s}'.format(credentials.access_token)},
                     stream=True)
    with open(fname, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=8196):
            fd.write(chunk)


def upload(fname):
    service = get_service()
    file_metadata = {
        'name' : os.path.basename(fname),
        'parents': [ 'appDataFolder']
    }
    media = MediaFileUpload(fname,
                        mimetype='audio/mpeg',
                        resumable=True)
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    print ('File ID: %s' % file.get('id'))
