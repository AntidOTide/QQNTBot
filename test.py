# # #
# # # import requests
# # #
# # # url = "https://aigptx.top/api/v1/user/admin/get-api-tokens"
# # #
# # # payload = {}
# # # headers = {
# # #     'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
# # #     'Authorization': 'sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
# # # }
# # #
# # # response = requests.request("POST", url, headers=headers, data=payload)
# # # json = response.json()
# # # api_id = json['data'][2]["remark"]
# # # used_fee = json['data'][2]["used_fee"]
# # # permissions = json['data'][2]["permissions"]
# # # max_fee =json['data'][2]["max_fee"]
# # # # print("API:" + api_id)
# # # # print("used_fee:" + used_fee)
# # # a = ""
# # # for i in permissions:
# # #     a += i + "\n"
# # #
# # # result = [api_id, used_fee, max_fee, a]
# # #
# # #
# # # # print("该API编号:"+result[0]+"\n该API已使用代币数量:"+result[1]+"\n该API最大额度:" +result[2] +"\n该API可用的语言模型:"+result[4])
# # # print("sa"+result[0])
# #
# #
# # import requests
# # import json
# #
# # url = "https://cn2us02.opapi.win/v1/chat/completions"
# #
# # payload = json.dumps({
# #    "model": "gpt-3.5-turbo",
# #    "messages": [
# #       {
# #          "role": "system",
# #          "content": 'AI'
# #       },
# #       {
# #          "role": "user",
# #          "content": 'SAY TEST'
# #       }
# #    ]
# # })
# # headers = {
# #    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
# #    'Content-Type': 'application/json',
# #    'Authorization': 'Bearer sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
# # }
# # response = requests.request("POST", url, headers=headers, data=payload)
# #
# # # print(session_config['model'])
# # resp_json = response.json()
# # resp = resp_json['choices'][0]['message']['content']
# # print(resp_json)
#
# # import time
# # import datetime
# # from datetime import timezone, timedelta,datetime
# #
# #
# # def get_bj_time():
# #     utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
# #     SHA_TZ = timezone(
# #         timedelta(hours=8),
# #         name='Asia/Shanghai',
# #     )
# #     # 北京时间
# #     beijing_now = utc_now.astimezone(SHA_TZ)
# #     fmt = '%Y-%m-%d-%H-%M-%S'
# #     now_fmt = beijing_now.strftime(fmt)
# #     return now_fmt
# #
# #
# # print(get_bj_time())
# import json
#
# li = [
#     "指令说明",
#     "语音开启",
#     "语音关闭",
#     "重置会话",
#     "重置人格",
#     "群指令类型",
#     "逻辑端指令类型",
#     "聊天指令类型",
# ]
#
# des = [ "指令如下(群内需@机器人)：请选择需要的指令类型\n1.[群指令类型]\n2.[逻辑端指令类型]\n3.[聊天指令类型]", "语音回复已开启", "语音回复已关闭", "会话已重置", "人格已重置",
# "指令如下(群内需@机器人)：\n1.[换个头像] 请发送 换个头像 \n2.[换个名字] 请发送 换个名字 \n", "指令如下(群内需@机器人)：1.[切换模型] 请发送 切换模型 \n2.[查询当前模型] 请发送
# 查询当前模型\n3.[直接生成图像] 请发送 直接生成图像 + 图像的描述\n例如：直接生成图像 一只猫\n4.[查询余额] 请发送 查询余额\n5.[指令说明] 请发送 指令说明", "指令如下(群内需@机器人)：\n1.[
# 重置会话] 请发送 重置会话\n2.[设置人格] 请发送 设置人格+人格描述\n3.[重置人格] 请发送 重置人格\n4.[指令说明] 请发送 " \ "指令说明\n5.[识图]
# 首先发送文字描述，再文字描述后面加上图片（推荐电脑端，手机端目前无法发送）]\n6.[谷歌查询] 请发送 谷歌查询 需要查询的问题\n 例如：\n 谷歌查询 芝士雪豹\n" \ "注意：\n重置会话不会清空人格,
# 重置人格会重置会话!\n设置人格后人格将一直存在，除非重置人格或重启逻辑端!",
#
#
# ]
# #    "余额查询（特殊性API）",    "切换模型（特殊性API）",查询当前模型，谷歌查询，换个头像
# with open(u'command.json', 'r', encoding="UTF-8") as f:
#     json_file = json.loads(f.read())
#     print(type(json))
#     for i in range(len(li)):
#         json_file["command"].append({
#             "id": i,
#             "name": li[i],
#             "des": des[i]
#         })
#     with open(u'command.json', 'w', encoding='utf-8') as w:
#         w.write(json.dumps(json_file, ensure_ascii=False, indent=4, sort_keys=True))
#         w.close()
#     print(json)
# def summ(a, b):
#     return a, b
# import os
# path = os.path.abspath(os.getcwd())
# parent_dir = os.path.dirname(path)
# print(parent_dir)
# from config_file import load_json_from_file
#
# dict1 = load_json_from_file(u"memory/group/225649416/225649416.json")
# dict2 = load_json_from_file(u"memory/group/225649416/225649416_config.json")
# print(dict1 | dict2)
li = []
for i in range(1, 32):
    li.append(i)

print(li)
print(li[-30:])
