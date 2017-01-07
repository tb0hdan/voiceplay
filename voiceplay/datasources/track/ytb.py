#-*- coding: utf-8 -*-
""" Youtube track source module """

from apiclient.discovery import build  # pylint:disable=import-error
from apiclient.errors import HttpError  # pylint:disable=import-error

from .basesource import TrackSource

class YoutubeSource(TrackSource):
    __baseurl__ = 'https://youtu.be/'
    __priority__ = 40

    @classmethod
    def search(cls, query, max_results=25):
        """
        Run youtube search
        """
        youtube = build('youtube', 'v3', developerKey=cls.cfg_data()['google']['key'])
        search_response = youtube.search().list(q=query,
                                                part="id,snippet",
                                                maxResults=max_results).execute()
        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append([search_result["snippet"]["title"], search_result["id"]["videoId"]])
        return videos
