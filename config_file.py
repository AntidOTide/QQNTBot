import json

with open("config.json", "r",
          encoding='utf-8') as jsonfile:
    config_data = json.load(jsonfile)
with open(u"command.json", "r", encoding='utf-8') as f:
    command_data = json.load(f)
with open(u"web_collection.json", "r", encoding='utf-8') as sexy_pic:
    web_collection = json.load(sexy_pic)
session_config = {
    'msg': [
        {"role": "system", "content": config_data['chatgpt']['preset']}
    ],
    'send_voice': False,
    'new_bing': False
}


def load_json_from_file(file):
    """
    从已知的文件路径加载一个json文件
    :param file: 需要加载的json文件路径
    :return: 已读的json文件
    """

    with open(file, 'r', encoding='utf-8') as f:
        json_file = json.loads(f.read())
    return json_file
