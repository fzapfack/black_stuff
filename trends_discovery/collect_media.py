import json
from datetime import datetime, timedelta

from utils.youtube_client import YoutubeClient

query = 'entretien cheveux naturels'

def search_youtube_video(q, save=True):
    youtube = YoutubeClient()
    publishedAfter = datetime.now()-timedelta(365*4)
    items = youtube.search(
        q=q,
        order='relevance', #viewCount
        publishedAfter=publishedAfter
    )

    if save:
        filename = 'data/youtube/extract_{}.json'.\
            format(publishedAfter.strftime('%Y%m%d'))
        with open(filename, 'w') as f:
            json.dump(items, f)

if __name__ == '__main__':
    search_youtube_video(query)