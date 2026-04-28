import os

class MediaDownloader:

    def __init__(self, media_agent):
        self.media_agent = media_agent

    def download_all(self, scenes):

        video_paths = []

        for i, scene in enumerate(scenes):

            keyword = scene.split(" ")[0]

            path = self.media_agent.select_media(keyword, i)

            if path and os.path.exists(path):
                video_paths.append(path)

        return video_paths