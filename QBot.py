import json

import openai
from flask import request, Flask
from loguru import logger

from bot_function import get_chat_session
# from stable_diffusion import get_stable_diffusion_img
from config_file import config_data
from credit_summary import get_credit_summary
from get_message import get_private_message, get_group_message
from memory import load_memory_private_config, load_memory_group_config, \
    write_memory_group_config, write_memory_group
from send_message import (send_private_message, send_private_message_image,
                          send_group_message, send_group_message_image,
                          set_friend_add_request, set_group_invite_request)

logger.add("logs/runtime_{time}.log", format="[{time}] [{level}] {message}", rotation="500 KB")
qq_no = config_data['qq_bot']['qq_no']

openai.api_base = "https://cn2us02.opapi.win/v1/"
current_key_index = 0

# 创建一个服务，把当前这个python文件当做一个服务
server = Flask(__name__)


# 测试接口，可以测试本代码是否正常启动
@server.route('/', methods=["GET"])
def index():
    return f"你好，世界!<br/>"


# 获取账号余额接口
@server.route('/credit_summary', methods=["GET"])
def credit_summary():
    return get_credit_summary()


# qq消息上报接口，qq机器人监听到的消息内容将被上报到这里
@server.route('/', methods=["POST"])
def get_message():
    if request.get_json().get('message_type') == 'private':  # 如果是私聊信息
        uid = request.get_json().get('sender').get('user_id')  # 获取信息发送者的 QQ号码
        message = request.get_json().get('raw_message')  # 获取原始信息
        # sender = request.get_json().get('sender')  # 消息发送者的资料
        private_memory = load_memory_private_config(uid=uid)
        res = get_private_message(uid=uid, message=message, private_memory=private_memory)
        if isinstance(res, str):
            send_private_message(uid=uid, message=res)
        elif isinstance(res, list):
            send_private_message_image(uid=uid, pic_path=res[1], msg=res[0])
    if request.get_json().get('message_type') == 'group':  # 如果是群消息
        gid = request.get_json().get('group_id')  # 群号
        uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
        message = request.get_json().get('raw_message')  # 获取原始信息
        sender = request.get_json().get('sender')  # 消息发送者的资料
        print(sender)
        group_memory = load_memory_group_config(gid=gid)[1]
        # 判断当被@时才回答
        if str("[CQ:at,qq=%s]" % qq_no) in message:
            message = str(message).replace(str("[CQ:at,qq=%s]" % qq_no), '')
            group_config = load_memory_group_config(gid=gid)[0]
            group_config["config"][2]["content"] += f"{sender['nickname']}:{message}"
            res = get_group_message(uid=uid, gid=gid, message=message, group_memory=group_config)
            if isinstance(res, str):
                send_group_message(gid=gid, uid=uid, message=res)
            elif isinstance(res, list):
                send_group_message_image(gid=gid, uid=uid, pic_path=res[1], msg=res[0])
        else:
            group_memory["memory"].append(
                {
                    "role": sender["nickname"],
                    "uid": uid,
                    "content": message
                }
            )
            group_config = load_memory_group_config(gid=gid)[0]
            print(group_config)
            group_config["config"][2]["content"] += f"{sender['nickname']}:{message}"
            print(group_config)
            write_memory_group(gid=gid, uid=uid, data=group_memory)
            write_memory_group_config(gid=gid, uid=uid, data=group_config)
    if request.get_json().get('post_type') == 'request':  # 收到请求消息
        print("收到请求消息")
        request_type = request.get_json().get('request_type')  # group
        uid = request.get_json().get('user_id')
        flag = request.get_json().get('flag')
        comment = request.get_json().get('comment')
        print("配置文件 auto_confirm:" + str(config_data['qq_bot']['auto_confirm']) + " admin_qq: " + str(
            config_data['qq_bot']['admin_qq']))
        if request_type == "friend":
            print("收到加好友申请")
            print("QQ：", uid)
            print("验证信息", comment)
            # 如果配置文件里auto_confirm为 TRUE，则自动通过
            if config_data['qq_bot']['auto_confirm']:
                set_friend_add_request(flag, "true")
            else:
                if str(uid) == config_data['qq_bot']['admin_qq']:  # 否则只有管理员的好友请求会通过
                    print("管理员加好友请求，通过")
                    set_friend_add_request(flag, "true")
        if request_type == "group":
            print("收到群请求")
            sub_type = request.get_json().get('sub_type')  # 两种，一种的加群(当机器人为管理员的情况下)，一种是邀请入群
            gid = request.get_json().get('group_id')
            if sub_type == "add":
                # 如果机器人是管理员，会收到这种请求，请自行处理
                print("收到加群申请，不进行处理")
            elif sub_type == "invite":
                print("收到邀请入群申请")
                print("群号：", gid)
                # 如果配置文件里auto_confirm为 TRUE，则自动通过
                if config_data['qq_bot']['auto_confirm']:
                    set_group_invite_request(flag, "true")
                else:
                    if str(uid) == config_data['qq_bot']['admin_qq']:  # 否则只有管理员的拉群请求会通过
                        set_group_invite_request(flag, "true")
    return "ok"


# 测试接口，可以用来测试与ChatGPT的交互是否正常，用来排查问题
# @server.route('/chat', methods=['post'])
# def chatapi():
#     requestJson = request.get_data()
#     if requestJson is None or requestJson == "" or requestJson == {}:
#         resu = {'code': 1, 'msg': '请求内容不能为空'}
#         return json.dumps(resu, ensure_ascii=False)
#     data = json.loads(requestJson)
#     if data.get('id') is None or data['id'] == "":
#         resu = {'code': 1, 'msg': '会话id不能为空'}
#         return json.dumps(resu, ensure_ascii=False)
#     print(data)
#     try:
#         s = get_chat_session(data['id'])
#         msg = chat(data['msg'], s)
#         if '查询余额' == data['msg'].strip():
#             msg = msg.replace('\n', '<br/>')
#         resu = {'code': 0, 'data': msg, 'id': data['id']}
#         return json.dumps(resu, ensure_ascii=False)
#     except Exception as error:
#         print("接口报错")
#         resu = {'code': 1, 'msg': '请求异常: ' + str(error)}
#         return json.dumps(resu, ensure_ascii=False)


# 重置会话接口
@server.route('/reset_chat', methods=['post'])
def reset_chat():
    requestJson = request.get_data()
    if requestJson is None or requestJson == "" or requestJson == {}:
        resu = {'code': 1, 'msg': '请求内容不能为空'}
        return json.dumps(resu, ensure_ascii=False)
    data = json.loads(requestJson)
    if data['id'] is None or data['id'] == "":
        resu = {'code': 1, 'msg': '会话id不能为空'}
        return json.dumps(resu, ensure_ascii=False)
    # 获得对话session
    session = get_chat_session(data['id'])
    # 清除对话内容但保留人设
    del session['msg'][1:len(session['msg'])]
    resu = {'code': 0, 'msg': '重置成功'}
    return json.dumps(resu, ensure_ascii=False)


# 与ChatGPT交互的方法


if __name__ == '__main__':
    server.run(port=5555, host='0.0.0.0', use_reloader=False)
