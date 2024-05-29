import re
import requests

# res = requests.post('http://localhost:3000/send_private_msg', json={
#     'user_id': 1158519478,
#     'message': [{
#         'type': 'text',
#         'data': {
#             'text': 'Hello, World!'
#         }
#     }]
# })
# res = requests.post('http://localhost:3000/set_group_card', json={
#     'group_id': 225649416,
#     'user_id': 1158519478,
#     'card': "114514"
# })
# print(res.json())
# str1 = """哦吼[CQ:image,file=71c1a013e1de6af70641949b5bb8205e.image,\
# url=https://c2cpicdw.qpic.cn/offpic_new/1158519478//1158519478-705127058-71C1A013E1DE6AF70641949B5BB8205E/0?term=(amp);is_origin=1]"""
# print(str1.strip("[ ]"))
# if "[CQ:image" in str1:
#     print(True)
# if "[CQ:image" in str1:
#     print(True)
# else:
#     print(False)
# a = str1.split("[CQ:image")
# print(a)
# if str1.split("[CQ:image"):
#     print(True)
# else:
#     print(False)
#
# pattern = r'url=([^ ]+)'
# # 使用正则表达式查找匹配的字符串
# match = re.search(pattern, str1.strip())
# st = match.group(1).split(']')
# print(st[0])
# import requests
#
# url = "https://cn2us02.opapi.win/api/v1/openapi/search/serper/v1"
#
# payload = {
#     'q': '芝士雪豹',
#     'cache': '3',
#     'gl': 'us',
#     'hl': 'en',
#     'page': '1',
#     'num=': '10'
# }
# headers = {
#     'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
#     'Authorization': 'sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
# }
#
# response = requests.request("POST", url, headers=headers, data=payload)
#
# print(response.text)
import requests
import json


def load_json_from_file(file):
    """
    从已知的文件路径加载一个json文件
    :param file: 需要加载的json文件路径
    :return: 已读的json文件
    """

    with open(file, 'r', encoding='utf-8') as f:
        json_file = json.loads(f.read())
    return json_file


text = ""
for i in load_json_from_file(u"amswer.json")["organic"]:
    text += (str(i['position'])+". "+i["snippet"]+"\n")

print(text)

url = "https://cn2us02.opapi.win/v1/chat/completions"

payload = json.dumps({
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "请为我总结以下的几段文字，告诉我芝士雪豹是什么，包括时间地点人物"
        },
        {
            "role": "user",
            "content": text
        }
    ]
})
headers = {
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Content-Type': 'application/json',
    'Authorization': 'sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'

}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
