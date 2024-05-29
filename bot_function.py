from datetime import datetime, timezone, timedelta
from config_file import web_collection, config_data
import requests
import os
import re
from loguru import logger


def get_sexy_pic(message: str):
    try:
        path = os.path.abspath(os.curdir)
        command, data = message.split()
        key_word = web_collection["sexy_pic"][f"{data}"]
        res = requests.get(
            url=f"https://image.anosu.top/pixiv/direct?r18=1&keyword={key_word}",
            allow_redirects=False
        )
        url = res.headers.get('Location')
        req = requests.get(
            url=url
        )
        content = req.content
        files = os.listdir(f"resource/sexy_img/{key_word}")  # 读入文件夹
        num_png = len(files)
        img_path = ""
        if url[-3:] == "png":
            img_path = f"{path}\\resource\sexy_img\\{key_word}\\{key_word}_{num_png + 1}.png"
            with open(img_path, "wb") as f:
                f.write(content)
                f.close()
        elif url[-3:] == "jpg":
            img_path = f"{path}\\resource\sexy_img\\{key_word}\\{key_word}_{num_png + 1}.jpg"
            with open(img_path, "wb") as f:
                f.write(content)
                f.close()
        return img_path
    except Exception as e:
        print(e)
        return "fail"


# 获取北京时间
def get_bj_time():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    # 北京时间
    beijing_now = utc_now.astimezone(SHA_TZ)
    fmt = '%Y-%m-%d-%H-%M-%S'
    now_fmt = beijing_now.strftime(fmt)
    return now_fmt


def change_avatar(msg):
    msg, url = msg.split("[CQ:image")
    pattern = r'url=([^ ]+)'
    # 使用正则表达式查找匹配的字符串
    match = re.search(pattern, url)
    url = match.group(1).split(']')[0]
    logger.info("获取的url地址为" + url)
    res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/set_qq_avatar",
                        params={
                            "file": url
                        }
                        ).json()
    if res["status"] == "ok":
        return "头像更改成功"


