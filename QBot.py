import json
import traceback
from copy import deepcopy
from flask import request, Flask
import openai
import requests
import tiktoken
from stable_diffusion import get_stable_diffusion_img
from config_file import config_data
from img2prompt import img_to_prompt
import re
import random
from credit_summary import get_credit_summary
from loguru import logger
from answer_online import search_serper_online, summary_answer
from send_message import (send_private_message, send_private_message_image,
                          send_group_message, send_group_message_image,
                          set_friend_add_request, set_group_invite_request)
from bot_function import get_sexy_pic, get_bj_time, change_avatar
from memory import load_memory_private_config, write_memory_private_config

logger.add("logs/runtime_{time}.log", format="[{time}] [{level}] {message}", rotation="500 KB")
qq_no = config_data['qq_bot']['qq_no']
session_config = {
    'msg': [
        {"role": "system", "content": config_data['chatgpt']['preset']}
    ],
    'send_voice': False,
    'model': 'gpt-4o',
    "api_key": "sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462"
}

sessions = {}
current_key_index = 0
summary = get_credit_summary()
model_str = summary[3]
model_list = summary[4]
logger.info("已获取到模型列表")
logger.info(model_str)
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
        sender = request.get_json().get('sender')  # 消息发送者的资料
        private_memory = load_memory_private_config(uid=uid)
        logger.info("收到私聊消息：")
        logger.info(message)
        if '重置会话' == message.strip():
            # 清除对话内容但保留人设
            del private_memory['memory'][2:len(private_memory['memory'])]
            write_memory_private_config(uid=uid, data=private_memory)
            return "会话已重置"
        elif '重置人格' == message.strip():
            # 清空对话内容并恢复预设人设
            private_memory["memory"][0]["content"] = config_data['chatgpt']['preset']
            write_memory_private_config(uid=uid, data=private_memory)
            send_private_message(uid=uid, message='人格已重置')
        elif message.strip().startswith('设置人格'):
            # 清空对话并设置人设
            private_memory["memory"][0]["content"] = message.strip().replace('设置人格', '')
            write_memory_private_config(uid=uid, data=private_memory)
            send_private_message(uid=uid, message='人格设置成功')
        elif "来点涩图" == message.strip():
            send_private_message(
                ("有以下类别\n1.[碧蓝航线]\n2.[碧蓝档案]\n3.[原神]\n4.[方舟]\n5.[崩坏三]\n6.[命运]\n7.[少前]\n8.[公主连结]\n9.[偶像大师]\n10.["
                 "皮套人]\n11.[东方]\n"))
        elif "来点涩图" in message:
            img_path = get_sexy_pic(message)
            send_private_message_image(uid, img_path, "")
            return "生成成功"
        # if message.strip().startswith('生成图像'):
        #     message = str(message).replace('生成图像', '')
        #     session = get_chat_session('P' + str(uid))
        #     msg_text = chat(message, session)  # 将消息转发给ChatGPT处理
        #     # 将ChatGPT的描述转换为图画
        #     print('开始生成图像')
        #     pic_path = get_openai_image(msg_text)
        #     file_path = 'file:///' + download_img(pic_path)
        #     send_private_message_image(uid, file_path, msg_text)
        # elif message.strip().startswith('直接生成图像'):
        #     message = str(message).replace('直接生成图像', '')
        #     print('开始直接生成图像')
        #     pic_path = get_openai_image(message)
        #     file_path = 'file:///' + download_img(pic_path)
        #     send_private_message_image(uid, file_path, '')
        # elif message.strip().startswith('/sd'):
        #     print("开始stable-diffusion生成")
        #     pic_url = ""
        #     try:
        #         pic_url = sd_img(message.replace("/sd", "").strip())
        #     except Exception as e:
        #         print("stable-diffusion 接口报错: " + str(e))
        #         send_private_message(uid, "Stable Diffusion 接口报错: " + str(e))
        #     print("stable-diffusion 生成图像: " + pic_url)
        #     send_private_message_image(uid, pic_url, '')
        elif message.strip().startswith('[CQ:image'):
            print("开始分析图像")
            # 定义正则表达式
            pattern = r'url=([^ ]+)'
            # 使用正则表达式查找匹配的字符串
            match = re.search(pattern, message.strip())
            prompt = img_to_prompt(match.group(1))
            send_private_message(uid, prompt)  # 将消息返回的内容发送给用户
        else:
            # 获得对话session
            session = get_chat_session('P' + str(uid))
            msg_tuple = chat(message, session, private_memory)  # 将消息转发给ChatGPT处理
            if len(msg_tuple) == 2:
                write_memory_private_config(uid=uid, data=msg_tuple[1])
                logger.info(send_private_message(uid, msg_tuple[0]))  # 将消息返回的内容发送给用户
            logger.info(send_private_message(uid, msg_tuple))  # 将消息返回的内容发送给用户
    if request.get_json().get('message_type') == 'group':  # 如果是群消息
        gid = request.get_json().get('group_id')  # 群号
        uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
        message = request.get_json().get('raw_message')  # 获取原始信息
        # 判断当被@时才回答
        if str("[CQ:at,qq=%s]" % qq_no) in message:
            sender = request.get_json().get('sender')  # 消息发送者的资料
            logger.info("收到群聊消息：")
            logger.info(message)
            message = str(message).replace(str("[CQ:at,qq=%s]" % qq_no), '')
            if "来点涩图" == message.strip():
                return ("有以下类别\n1.[碧蓝航线]\n2.[碧蓝档案]\n3.[原神]\n4.[方舟]\n5.[崩坏三]\n6.[命运]\n7.[少前]\n8.[公主连结]\n9.[偶像大师]\n10.["
                        "皮套人]\n11.[东方]\n")
            if "来点涩图" in message:
                img_path = get_sexy_pic(message)
                send_group_message_image(uid, img_path, uid, "")
                return "生成成功"
            if message.strip().startswith('生成图像'):
                message = str(message).replace('生成图像', '')
                session = get_chat_session('G' + str(gid))
                msg_text = chat(message, session)  # 将消息转发给ChatGPT处理
                # 将ChatGPT的描述转换为图画
                logger.info('开始生成图像')
                pic_path = get_openai_image(msg_text)
                file_path = 'file:///' + download_img(pic_path)
                send_group_message_image(gid, file_path, uid, msg_text)
            elif message.strip().startswith('直接生成图像'):
                message = str(message).replace('直接生成图像', '')
                logger.info('开始直接生成图像')
                pic_path = get_openai_image(message)
                file_path = 'file:///' + download_img(pic_path)
                send_group_message_image(gid, file_path, uid, message)
            elif message.strip().startswith('/sd'):
                logger.info("开始stable-diffusion生成")
                pic_url = ""
                try:
                    pic_url = sd_img(message.replace("/sd", "").strip())
                except Exception as e:
                    logger.error("stable-diffusion 接口报错: " + str(e))
                    send_group_message(gid, "Stable Diffusion 接口报错: " + str(e), uid)
                logger.info("stable-diffusion 生成图像: " + pic_url)
                send_group_message_image(gid, pic_url, uid, '')
            elif "换个名字" in message:
                command, name = message.split()
                res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/set_group_card", json={
                    'group_id': gid,
                    'user_id': qq_no,
                    'card': name
                }).json()
                if res['status'] == 'ok':
                    msg_text = f"更改群号[{gid}]的qq名字为 [ {name} ] "
                    logger.info(msg_text)
                    session = get_chat_session('G' + str(gid))
                    send_group_message(gid, msg_text, uid)  # 将消息转发到群里
                else:
                    return "更改名字失败,请重试"
            else:
                # 下面你可以执行更多逻辑，这里只演示与ChatGPT对话
                # 获得对话session
                session = get_chat_session('G' + str(gid))
                msg_text = chat(message, session,session['msg'])  # 将消息转发给ChatGPT处理
                send_group_message(gid, msg_text, uid)  # 将消息转发到群里

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
@server.route('/chat', methods=['post'])
def chatapi():
    requestJson = request.get_data()
    if requestJson is None or requestJson == "" or requestJson == {}:
        resu = {'code': 1, 'msg': '请求内容不能为空'}
        return json.dumps(resu, ensure_ascii=False)
    data = json.loads(requestJson)
    if data.get('id') is None or data['id'] == "":
        resu = {'code': 1, 'msg': '会话id不能为空'}
        return json.dumps(resu, ensure_ascii=False)
    print(data)
    try:
        s = get_chat_session(data['id'])
        msg = chat(data['msg'], s)
        if '查询余额' == data['msg'].strip():
            msg = msg.replace('\n', '<br/>')
        resu = {'code': 0, 'data': msg, 'id': data['id']}
        return json.dumps(resu, ensure_ascii=False)
    except Exception as error:
        print("接口报错")
        resu = {'code': 1, 'msg': '请求异常: ' + str(error)}
        return json.dumps(resu, ensure_ascii=False)


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
def chat(msg, session, memory):
    print(f"memory是{memory}")
    time_cache = get_bj_time()
    try:
        if '语音开启' == msg.strip():
            session['send_voice'] = True
            return '语音回复已开启'
        if '语音关闭' == msg.strip():
            session['send_voice'] = False
            return '语音回复已关闭'
        if '查询余额' == msg.strip():
            result = get_credit_summary()
            return "该API编号:" + result[0] + "\n该API已使用代币数量:" + result[1] + "\n该API最大额度:" + result[
                2] + "\n该API可用的语言模型:" + result[3]
        if '指令说明' == msg.strip():
            return "指令如下(群内需@机器人)：请选择需要的指令类型\n1.[群指令类型]\n2.[逻辑端指令类型]\n3.[聊天指令类型]"
        if "群指令类型" == msg.strip():
            return "指令如下(群内需@机器人)：\n1.[换个头像] 请发送 换个头像 \n2.[换个名字] 请发送 换个名字 \n"
        if "逻辑端指令类型" == msg.strip():
            return "指令如下(群内需@机器人)：1.[切换模型] 请发送 切换模型 \n2.[查询当前模型] 请发送 查询当前模型\n" \
                   "3.[直接生成图像] 请发送 直接生成图像 + 图像的描述\n例如：直接生成图像 一只猫\n4.[查询余额] 请发送 查询余额\n5.[指令说明] 请发送 指令说明"
        if "聊天指令类型" == msg.strip():
            return "指令如下(群内需@机器人)：\n1.[重置会话] 请发送 重置会话\n2.[设置人格] 请发送 设置人格+人格描述\n3.[重置人格] 请发送 重置人格\n4.[指令说明] 请发送 " \
                   "指令说明\n5.[识图] 首先发送文字描述，再文字描述后面加上图片（推荐电脑端，手机端目前无法发送）]\n6.[谷歌查询] 请发送 谷歌查询 需要查询的问题\n 例如：\n 谷歌查询 " \
                   "芝士雪豹\n 注意：\n重置会话不会清空人格,重置人格会重置会话!\n设置人格后人格将一直存在，除非重置人格或重启逻辑端!"
        if '切换模型' == msg.strip():
            return f"有以下模型可选择：\n {model_str}\n 请输入 / + [模型名字]\n 例如:\n[gpt-4o] 请复制以下发送\n/gpt-4o"
        if "查询当前模型" == msg.strip():
            return "当前模型为" + session_config['model']
        if "谷歌查询" in msg:
            command, question = msg.split()
            answer = summary_answer(search_json=search_serper_online(question, session_config["api_key"]))
            return answer
        # 更换头像
        if "换个头像" in msg:
            return change_avatar(msg)
        # 更换模型
        for i in model_list:
            if '/' + i == msg:
                session_config['model'] = i
                return f'已切换至{i}'
        if msg.strip().startswith('/img'):
            msg = str(msg).replace('/img', '')
            logger.info("直接开始生成图像")
            pic_path = get_openai_image(msg)
            return "![](" + pic_path + ")"
        if "[CQ:image" in msg:
            msg, url = msg.split("[CQ:image")
            pattern = r'url=([^ ]+)'
            # 使用正则表达式查找匹配的字符串
            match = re.search(pattern, url)
            url = match.group(1).split(']')[0]
            logger.info("获取的url地址为" + url)
            # 设置本次对话内容
            memory["memory"].append(
                {"role": "user", "content":
                    [
                        {
                            'type': "text",
                            "text": msg
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url
                            }
                        }
                    ]
                 }
            )
            # 设置时间
            memory["memory"][1] = {"role": "system", "content": "current time is:" + get_bj_time()}
            # # 检查是否超过tokens限制
            # while num_tokens_from_messages(session['msg']) > config_data['chatgpt']['max_tokens']:
            #     # 当超过记忆保存最大量时，清理一条
            #     del session['msg'][2:3]
            # 与ChatGPT交互获得对话内容
            message = chat_with_gpt(memory["memory"])
        else:

            # 设置本次对话内容
            memory["memory"].append({"role": "user", "content": msg, "time": time_cache})
            # 设置时间
            memory["memory"][1] = {"role": "system", "content": "Last conversation's time is:" + time_cache}
            # # 检查是否超过tokens限制
            # while num_tokens_from_messages(session['msg']) > config_data['chatgpt']['max_tokens']:
            #     # 当超过记忆保存最大量时，清理一条
            #     del session['msg'][2:3]
            # 与ChatGPT交互获得对话内容
            message = chat_with_gpt(memory["memory"])
        # 记录上下文
        memory["memory"].append({"role": "assistant", "content": message, "time": time_cache})
        logger.info("大模型返回内容")
        logger.info(message)
        return message, memory
    except Exception as error:
        traceback.print_exc()
        logger.error("出现异常！")
        return str('异常: ' + str(error))


# 获取对话session
def get_chat_session(sessionid):
    if sessionid not in sessions:
        config = deepcopy(session_config)
        config['id'] = sessionid
        config['msg'].append({"role": "system", "content": "current time is:" + get_bj_time()})
        sessions[sessionid] = config
    return sessions[sessionid]


def chat_with_gpt(messages):
    global current_key_index
    max_length = len(config_data['openai']['api_key']) - 1
    try:
        if not config_data['openai']['api_key']:
            return "请设置Api Key"
        else:
            if current_key_index > max_length:
                current_key_index = 0
                return "全部Key均已达到速率限制,请等待一分钟后再尝试"
            openai.api_key = config_data['openai']['api_key'][current_key_index]

        url = "https://cn2us02.opapi.win/v1/chat/completions"

        payload = json.dumps({
            "model": session_config['model'],
            "messages": messages
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        resp_json = response.json()
        resp = resp_json['choices'][0]['message']['content']
    except openai.OpenAIError as e:
        if str(e).__contains__("Rate limit reached for default-gpt-3.5-turbo") and current_key_index <= max_length:
            # 切换key
            current_key_index = current_key_index + 1
            logger.warning("速率限制，尝试切换key")
            return chat_with_gpt(messages)
        elif str(e).__contains__(
                "Your access was terminated due to violation of our policies") and current_key_index <= max_length:
            logger.warning("请及时确认该Key: " + str(openai.api_key) + " 是否正常，若异常，请移除")
            if current_key_index + 1 > max_length:
                return str(e)
            else:
                logger.warning("访问被阻止，尝试切换Key")
                # 切换key
                current_key_index = current_key_index + 1
                return chat_with_gpt(messages)
        else:
            logger.warning("接口报错")
            resp = str(e)
    return resp


# 生成图片


# openai生成图片
def get_openai_image(des):
    openai.api_key = config_data['openai']['api_key'][current_key_index]
    response = openai.Image.create(
        prompt=des,
        n=1,
        size=config_data['openai']['img_size']
    )
    image_url = response['data'][0]['url']
    print('图像已生成')
    print(image_url)
    return image_url


# 计算消息使用的tokens数量
def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        num_tokens = 0
        for message in messages:
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # 如果name字段存在，role字段会被忽略
                    num_tokens += -1  # role字段是必填项，并且占用1token
        num_tokens += 2
        return num_tokens
    else:
        raise NotImplementedError(f"""当前模型不支持tokens计算: {model}.""")


# sd生成图片,这里只做了正向提示词，其他参数自己加
def sd_img(msg):
    res = get_stable_diffusion_img({
        "prompt": msg,
        "width": 768,
        "height": 512,
        "num_inference_steps": 20,
        "guidance_scale": 7.5,
        "negative_prompt": "",
        "scheduler": "K_EULER_ANCESTRAL",
        "seed": random.randint(1, 9999999),
    }, config_data['replicate']['api_token'])
    return res[0]


def image(uid, pic_path, msg):
    try:
        message = "[CQ:image,file=" + pic_path + "]"
        if msg != "":
            message = msg + '\n' + message
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_private_msg",
                            params={'user_id': int(uid), 'message': [
                                {
                                    'type': 'text',
                                    'data': message
                                }
                            ]}).json()
        if res["status"] == "ok":
            print("私聊消息发送成功")
        else:
            print(res)
            print("私聊消息发送失败，错误信息：" + str(res['wording']))

    except Exception as error:
        print("私聊消息发送失败")
        print(error)


def download_img(url):
    img_src = url
    response = requests.get(img_src)
    date = get_bj_time()
    print(date)
    file_url = "D:\\Programming\\BOT\\QBot2号\\py\\fonts\\pic\\" + date + ".jpg"
    with open(file_url, 'wb+') as file_obj:
        file_obj.write(response.content)
    return file_url


def send_img_to_gpt(messages):
    global current_key_index
    max_length = len(config_data['openai']['api_key']) - 1
    try:
        if not config_data['openai']['api_key']:
            return "请设置Api Key"
        else:
            if current_key_index > max_length:
                current_key_index = 0
                return "全部Key均已达到速率限制,请等待一分钟后再尝试"
            openai.api_key = config_data['openai']['api_key'][current_key_index]

        url = "https://cn2us02.opapi.win/v1/chat/completions"
        payload = json.dumps({
            "model": session_config['model'],
            "messages": messages
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        print(session_config['model'])
        resp_json = response.json()
        resp = resp_json['choices'][0]['message']['content']
        print(resp_json)
    except openai.OpenAIError as e:
        if str(e).__contains__("Rate limit reached for default-gpt-3.5-turbo") and current_key_index <= max_length:
            # 切换key
            current_key_index = current_key_index + 1
            print("速率限制，尝试切换key")
            return chat_with_gpt(messages)
        elif str(e).__contains__(
                "Your access was terminated due to violation of our policies") and current_key_index <= max_length:
            print("请及时确认该Key: " + str(openai.api_key) + " 是否正常，若异常，请移除")
            if current_key_index + 1 > max_length:
                return str(e)
            else:
                print("访问被阻止，尝试切换Key")
                # 切换key
                current_key_index = current_key_index + 1
                return chat_with_gpt(messages)
        else:
            print('openai 接口报错: ' + str(e))
            resp = str(e)
    return resp


if __name__ == '__main__':
    server.run(port=5555, host='0.0.0.0', use_reloader=False)
