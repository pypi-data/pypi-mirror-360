import jmcomic
from nonebot.log import logger

from .utils import *


class Client:
    def __init__(self):
        self.client = jmcomic.JmOption.default().new_jm_client()

    def isValidAlbumId(self, album_id: str) -> bool:
        try:
            self.client.get_album_detail(album_id)
        except jmcomic.JmcomicException:
            return False
        else:
            return True

    def getAlbumInfo(self, album_id: str) -> dict:
        try:
            album_detail = self.client.get_album_detail(album_id)
        except jmcomic.JmcomicException as error:
            raise error
        else:
            tags = ""
            for tag in album_detail.tags:
                tag = tag.strip()
                if tag != "":
                    tags += f"#{tag} "
            return getDict((album_id, album_detail.title, album_detail.author,
                            tags, album_detail.page_count, 0.0))
