from datetime import datetime, timezone, timedelta
from config_file import web_collection, config_data
import requests
import os
import re
from loguru import logger
import traceback
from copy import deepcopy
import tiktoken
import re
import random
from answer_online import search_serper_online, summary_answer
from credit_summary import get_credit_summary
import json

summary = get_credit_summary()
model_str = summary[3]
model_list = summary[4]
logger.info("已获取到模型列表")
logger.info(model_str)
sessions = {}
session_config = {
    'msg': [
        {"role": "system", "content": config_data['chatgpt']['preset']}
    ],
    'send_voice': False,
    'model': 'gpt-4o',
    "api_key": "sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462"
}


def get_sexy_pic(message: str):
    try:
        path = os.path.abspath(os.getcwd())
        parent_dir = os.path.dirname(path)
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
        files = os.listdir(f"{parent_dir}\\resource/sexy_img/{key_word}")  # 读入文件夹
        num_png = len(files)
        img_path = ""
        if url[-3:] == "png":
            img_path = f"{parent_dir}\\resource\sexy_img\\{key_word}\\{key_word}_{num_png + 1}.png"
            with open(img_path, "wb") as f:
                f.write(content)
                f.close()
        elif url[-3:] == "jpg":
            img_path = f"{parent_dir}\\resource\sexy_img\\{key_word}\\{key_word}_{num_png + 1}.jpg"
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


def chat(msg, session, memory, chat_type: str):
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
            if type == "private":
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
                return [message, memory]
            else:
                message = chat_with_gpt(memory["config"])
                return [message, memory]
        else:
            if chat_type == "private":
                # 设置本次对话内容
                memory["memory"].append({"role": "user", "content": msg, "time": time_cache})
                # 设置时间
                memory["memory"][1] = {"role": "system", "content": "Current time now is:" + time_cache}
                # # 检查是否超过tokens限制
                # while num_tokens_from_messages(session['msg']) > config_data['chatgpt']['max_tokens']:
                #     # 当超过记忆保存最大量时，清理一条
                #     del session['msg'][2:3]
                # 与ChatGPT交互获得对话内容
                message = chat_with_gpt(memory["memory"])
                # 记录上下文
                memory["memory"].append({"role": "assistant", "content": message, "time": time_cache})
            else:
                message = chat_with_gpt(memory["config"])
                return [message, memory]
            logger.info("大模型返回内容")
            logger.info(message)
            return [message, memory]
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
    path = os.path.abspath(os.getcwd())
    parent_dir = os.path.dirname(path)
    file_url = f"{parent_dir}\\resource\\pic\\{date}.jpg"
    with open(file_url, 'wb+') as file_obj:
        file_obj.write(response.content)
    return file_url


def send_img_to_gpt(messages):
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
    return resp
