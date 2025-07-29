<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-flomic

_✨ 多功能的 jmcomic 使用插件 ✨_

</div>

---

## 📖 介绍

### 基本功能

1. 通过本子号获取简介并下载。
2. 通过用户下载的本子生成XP记录。
3. SUPERUSER可设置违禁标签与使用次数限制。

### 存储机制

1. 对本子下载产生的中间文件进行及时清除以节省资源。
2. 设置数据库以记录查询过的本子信息，设置下载缓存以防止大量的重复下载（采用FIFO），节省资源和时间。

### 下载保护

1. 限制下载队列长度。
2. 设置用户每日使用上限，查询和下载均计入次数。
3. 设置标签与本子id黑名单检查。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-flomic

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-flomic

</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-flomic

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-flomic

</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-flomic

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_flomic"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|       配置项       |  类型   | 必填 | 默认值 |       说明       |
|:---------------:|:-----:|:--:|:---:|:--------------:|
|   jm_username   |  str  | 否  |  无  |    JM登录用户名     |
|   jm_password   |  str  | 否  |  无  |     JM登录密码     |
| threading_image |  int  | 否  | 20  |    同时请求的图片数    |
| threading_photo |  int  | 否  | 15  |    同时请求的章节数    |
| pdf_cache_size  | float | 否  |  1  | PDF文件的缓存大小（GB） |
| pic_cache_size  | float | 否  | 0.5 | 本子首图的缓存大小（GB）  |

## 🎉 使用

### 指令表

（以下指令均需要前缀）

|              指令              |    权限     | 需要@ | 范围 |                      说明                       |
|:----------------------------:|:---------:|:---:|:--:|:---------------------------------------------:|
|       jm.d \<id> \[-f]       |    所有     |  否  | 所有 |       下载本子号为id的本子，SUPERUSER可使用-f参数绕过黑名单       |
|       jm.q \<id> \[-i]       |    所有     |  否  | 所有 |         查询本子号为id的本子，默认附带首图，可使用-i参数取消          |
|          jm.r \[-q]          |    管理员    |  否  | 所有 |           随机生成可用的本子号，使用-q选项可以直接查询。            |
|   jm.xp \[-u QQ号] \[-l 长度]   |    所有     |  否  | 所有 | 查询用户xp。使用-u选项指定查询用户，默认查询自身。使用-l选项指定展示长度，默认为5。 |
|          jm.m cache          | SUPERUSER |  否  | 所有 |                  查看当前缓存使用情况。                  |
|           jm.m f_s           | SUPERUSER |  否  | 所有 |              查看今日用户使用次数。（查询和下载）               |
|       jm.m (d/u)_(s/c)       | SUPERUSER |  否  | 所有 |                显示或清空当前下载或上传队列。                |
|           jm.m l_s           | SUPERUSER |  否  | 所有 |                  查看当前用户使用限制，                  |
|     jm.m l_i <QQ号> <次数>      | SUPERUSER |  否  | 所有 |            限制用户每日最多使用cnt次。（查询和下载）             |
|        jm.m l_d <QQ号>        | SUPERUSER |  否  | 所有 |                    取消用户限制。                    |
|           jm.m r_s           | SUPERUSER |  否  | 所有 |               查看当前黑名单。（标签和本子id）               |
| jm.m r_i <tag/album_id> <内容> | SUPERUSER |  否  | 所有 |     加入黑名单。若为标签请指定为tag，若为本子号请指定为album_id。      |
| jm.m r_d <tag/album_id> <内容> | SUPERUSER |  否  | 所有 |     删除黑名单。若为标签请指定为tag，若为本子号请指定为album_id。      |

### 效果图

<img src="./resource/commands.png" alt="如果有效果图的话">
<img src="./resource/intro.png" alt="如果有效果图的话">

### 其他

1. 如果显示“发送失败了”，可能是消息被和谐了（多半是因为图片），试着从私聊获取再转发到群聊。
2. 强制要求下载前必须查询。
3. 版本号：0.1.7
