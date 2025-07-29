import jmcomic

from nonebot.log import logger


class Downloader:
    def __init__(self, config_str: str):
        self.option = jmcomic.create_option_by_str(config_str)

    def download(self, album_id: str) -> None:
        try:
            self.option.download_album(album_id)
        except jmcomic.RequestRetryAllFailException:
            pass
        except jmcomic.PartialDownloadFailedException:
            pass
        except jmcomic.JmcomicException as error:
            raise error
        else:
            pass
