#-*- coding: utf-8 -*-
""" Youtube track source module """

import os
from apiclient.discovery import build  # pylint:disable=import-error
# TODO: Catch and handle this accordingly
#from apiclient.errors import HttpError  # pylint:disable=import-error
from oauth2client.client import GoogleCredentials
from voiceplay.utils.score import VideoScoreCalculator

from .basesource import TrackSource

class YoutubeSource(TrackSource):
    """
    Youtube track source (used as last resort)
    """
    __baseurl__ = 'https://youtu.be/'
    __priority__ = 40

    @classmethod
    def youtube(cls):
        """
        Prepare YouTube API object
        """
        credentials = GoogleCredentials.from_stream(os.path.expanduser('~/.config/voiceplay/credentials.json'))
        return build('youtube', 'v3', credentials=credentials)

    @classmethod
    def process_list(cls, vlist, limit=24):
        """
        Process youtube video list
        """
        youtube = cls.youtube()
        def run_chunk(videos, vids):
            """
            internal method that processes portion of returned results
            """
            part = 'snippet, contentDetails, status, statistics'
            video_response = youtube.videos().list(id=videos, part=part).execute()
            for item in video_response.get('items', []):
                if item['kind'] == 'youtube#video':
                    vids[item['id']] = item
            return vids
        vids = {}
        videos = vlist.split(',')
        for idx in range(len(videos) // limit + 1):
            vids = run_chunk(','.join(videos[idx * limit: idx * limit + limit]), vids)
        return vids

    @classmethod
    def search(cls, query, max_results=25):
        """
        Run youtube search
        """
        youtube = cls.youtube()
        search_response = youtube.search().list(q=query,
                                                part="id,snippet",
                                                maxResults=max_results).execute()
        search_videos = []

        # Merge video ids
        for search_result in search_response.get("items", []):
            vid = search_result.get('id',{}).get('videoId', '')
            # skip playlists
            if not vid:
                continue
            search_videos.append(vid)
        video_ids = ",".join(search_videos)

        vsc = VideoScoreCalculator()
        vids = cls.process_list(video_ids)

        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                vname = search_result["snippet"]["title"]
                vid = search_result["id"]["videoId"]
                snippet = search_result['snippet']
                snippet['metadata'] = vids.get(vid, {})
                score = vsc.calculate([vname, vid, snippet], query)
                videos.append([vname, vid, score])
        # sort by highest score and remove score itself
        result = [[vname, vid] for vname, vid, _ in sorted(videos, key=lambda item: item[2], reverse=True)]
        return result
