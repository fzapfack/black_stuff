import json
import logging
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(level=logging.INFO)

with open('secrets.json', 'r') as f:
    conf = json.load(f)
DEVELOPER_KEY = conf['GOOGLE']['API_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

REGIONCODE = 'FR'
MAX_RESULTS = 100


class YoutubeClient:
    def __init__(self):
        self.youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=DEVELOPER_KEY)

    def paginate(self, ressource, request, max_results=None):
        items = []
        max_results = max_results or MAX_RESULTS
        while request is not None and len(items) < max_results:
            logging.info('Retrieving items. {} out of {} extracted so far'.format(len(items), max_results))
            res = request.execute()
            items.extend(res['items'])
            request = ressource.list_next(request, res)
        return items

    
    # Pagination not working with order 
    def search(self, q, part='id,snippet', maxResults=30, order='relevance',
               publishedAfter=datetime(2017,1,1), search_type='video',
               videoCaption='closedCaption'):
        logging.info('Youtube searching content matching: %s', q)
        ressource = self.youtube.search()
        request = ressource.list(
            q=q, part=part, maxResults=maxResults, order=order,
            publishedAfter='1970-01-01T00:00:00Z', type=search_type,
            videoCaption=videoCaption
        )
        items = self.paginate(ressource, request)
        logging.info('{} items extracted'.format(len(items)))

        videos = []
        channels = []
        playlists = []

        for search_result in items:
            if search_result['id']['kind'] == 'youtube#video':
                videos.append({
                    "id":search_result['id']['videoId'],
                    "title":search_result['snippet']['title'],
                    "publishedAt":search_result['snippet']['publishedAt'],
                    "channelId":search_result['snippet']['channelId'],
                    "description":search_result['snippet']['description'],
                    "channelTitle":search_result['snippet']['channelTitle']
                })
            elif search_result['id']['kind'] == 'youtube#channel':
                channels.append({
                    "id":search_result['id']['channelId'],
                    "title":search_result['snippet']['title'],
                    "publishedAt":search_result['snippet']['publishedAt'],
                    "description":search_result['snippet']['description'],
                    "channelTitle":search_result['snippet']['channelTitle'],
                })
            elif search_result['id']['kind'] == 'youtube#playlist':
                playlists.append({
                    "id":search_result['id']['playlistId'],
                    "title":search_result['snippet']['title'],
                    "publishedAt":search_result['snippet']['publishedAt'],
                    "channelId":search_result['snippet']['channelId'],
                    "description":search_result['snippet']['description'],
                    "channelTitle":search_result['snippet']['channelTitle'],
                })
        return {'videos': videos, 'channels': channels, 'playlists': playlists}
