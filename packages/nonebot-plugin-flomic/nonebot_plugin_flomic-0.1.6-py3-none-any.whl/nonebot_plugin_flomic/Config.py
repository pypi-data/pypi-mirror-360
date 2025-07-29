import os

from pathlib import Path
from pydantic import BaseModel
from nonebot import get_plugin_config, require

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as localstore

data_dir: Path = localstore.get_plugin_data_dir()
database_file: Path = localstore.get_plugin_data_file("jmcomic.db")
cache_dir: Path = localstore.get_plugin_cache_dir()
album_cache_dir: Path = cache_dir.joinpath("album_cache")
save_cache_dir: Path = cache_dir.joinpath("save_cache")
pdf_dir: Path = save_cache_dir.joinpath("pdf")
pics_dir: Path = save_cache_dir.joinpath("pics")

config_dir_list = [album_cache_dir, save_cache_dir, pdf_dir, pics_dir]

for config_dir in config_dir_list:
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)

class Config(BaseModel):
    jm_username: str = ""
    jm_password: str = ""
    threading_image: int = 20
    threading_photo: int = 15
    pdf_cache_size: float = 1.0
    pic_cache_size: float = 0.5


jm_config = get_plugin_config(Config)

default_options_str = f"""
client:
  impl: api
  retry_times: 10
dir_rule:
  base_dir: {album_cache_dir}
  rule: Bd_Aid_Pindex
download:
  threading:
    image: {jm_config.threading_image}
    photo: {jm_config.threading_photo}
log: true
plugins:
  after_init:
  - plugin: log_topic_filter
    kwargs:
      whitelist:
      - album.before
      - photo.before
  - plugin: login
    kwargs:
      username: {jm_config.jm_username}
      password: {jm_config.jm_password}
  after_photo:
  - plugin: img2pdf
    kwargs:
      filename_rule: Aid
      pdf_dir: {pdf_dir}
"""

firstImage_options_str = f"""
client:
  impl: api
  retry_times: 5
dir_rule:
  base_dir: {album_cache_dir}
  rule: Bd_Pid
download:
  image:
    suffix: .jpg
  threading:
    image: {jm_config.threading_image}
    photo: {jm_config.threading_photo}
log: true
plugins:
  after_init:
  - plugin: log_topic_filter
    kwargs:
      whitelist:
      - album.before
      - photo.before
  - plugin: login
    kwargs:
      username: {jm_config.jm_username}
      password: {jm_config.jm_password}
"""
