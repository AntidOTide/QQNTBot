from memory import write_memory_private_config, write_memory_group_config
import bot_function
from loguru import logger
import requests
from config_file import config_data
from send_message import send_private_message_image


def get_private_message(uid: str, message: str, private_memory: dict) -> str | list:
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
        return "人格已重置"
    elif message.strip().startswith('设置人格'):
        # 清空对话并设置人设
        private_memory["memory"][0]["content"] = message.strip().replace('设置人格', '')
        write_memory_private_config(uid=uid, data=private_memory)
        return "设置人格成功"
    elif "来点涩图" == message.strip():
        return ("有以下类别\n1.[碧蓝航线]\n2.[碧蓝档案]\n3.[原神]\n4.[方舟]\n5.[崩坏三]\n6.[命运]\n7.[少前]\n8.[公主连结]\n9.[偶像大师]\n10.["
                "皮套人]\n11.[东方]\n")
    elif "来点涩图" in message:
        img_path = bot_function.get_sexy_pic(message)
        return ["生成成功", img_path]
    # if message.strip().startswith('生成图像'):
    #     message = str(message).replace('生成图像', '')
    #     session = get_chat_session('P' + str(uid))
    #     msg_text = chat(message, session)  # 将消息转发给ChatGPT处理
    #     # 将ChatGPT的描述转换为图画
    #     print('开始生成图像')
    #     pic_path = get_openai_image(msg_text)
    #     file_path = 'file:///' + download_img(pic_path)
    #     send_private_message_image(uid, file_path, msg_text)
    elif message.strip().startswith('直接生成图像'):
        message = str(message).replace('直接生成图像', '')
        print('开始直接生成图像')
        pic_path = bot_function.get_openai_image(message)
        file_path = 'file:///' + bot_function.download_img(pic_path)
        send_private_message_image(uid, file_path, '')
        return ["", file_path]
    else:
        # 获得对话session
        session = bot_function.get_chat_session('P' + str(uid))
        msg_list = bot_function.chat(message, session, private_memory,chat_type="private")  # 将消息转发给ChatGPT处理
        if isinstance(msg_list, str):
            # write_memory_private_config(uid=uid, data=msg_list)
            logger.info(msg_list)
            return msg_list
        elif isinstance(msg_list, list):
            write_memory_private_config(uid=uid, data=msg_list[1])
            logger.info(msg_list)
            return msg_list[0]


def get_group_message(uid: str, gid: str, message: str, group_memory: dict):
    logger.info("收到群聊消息：")
    logger.info(message)
    if "来点涩图" == message.strip():
        return ("有以下类别\n1.[碧蓝航线]\n2.[碧蓝档案]\n3.[原神]\n4.[方舟]\n5.[崩坏三]\n6.[命运]\n7.[少前]\n8.[公主连结]\n9.[偶像大师]\n10.["
                "皮套人]\n11.[东方]\n")
    if "来点涩图" in message:
        img_path = bot_function.get_sexy_pic(message)
        return ["生成成功", img_path]
    # if message.strip().startswith('生成图像'):
    #     message = str(message).replace('生成图像', '')
    #     session = bot_function.get_chat_session('G' + str(gid))
    #     msg_text = bot_function.chat(message, session)  # 将消息转发给ChatGPT处理
    #     # 将ChatGPT的描述转换为图画
    #     logger.info('开始生成图像')
    #     pic_path = bot_function.get_openai_image(msg_text)
    #     file_path = 'file:///' + bot_function.download_img(pic_path)
    #     send_group_message_image(gid, file_path, uid, msg_text)
    elif message.strip().startswith('直接生成图像'):
        message = str(message).replace('直接生成图像', '')
        logger.info('开始直接生成图像')
        pic_path = bot_function.get_openai_image(message)
        file_path = 'file:///' + bot_function.download_img(pic_path)
        return ["", pic_path]
    # elif message.strip().startswith('/sd'):
    #     logger.info("开始stable-diffusion生成")
    #     pic_url = ""
    #     try:
    #         pic_url = sd_img(message.replace("/sd", "").strip())
    #     except Exception as e:
    #         logger.error("stable-diffusion 接口报错: " + str(e))
    #         send_group_message(gid, "Stable Diffusion 接口报错: " + str(e), uid)
    #     logger.info("stable-diffusion 生成图像: " + pic_url)
    #     send_group_message_image(gid, pic_url, uid, '')
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
            session = bot_function.get_chat_session('G' + str(gid))
            return msg_text
        else:
            return "更改名字失败,请重试"
    else:
        # 下面你可以执行更多逻辑，这里只演示与ChatGPT对话
        # 获得对话session
        session = bot_function.get_chat_session('G' + str(gid))
        msg_list = bot_function.chat(message, session, group_memory, chat_type="group")  # 将消息转发给ChatGPT处理
        if isinstance(msg_list, str):
            # write_memory_private_config(uid=uid, data=msg_list)
            logger.info(msg_list)
            return msg_list
        elif isinstance(msg_list, list):
            write_memory_group_config(gid=gid, uid=uid, data=msg_list[1])
            logger.info(msg_list)
            return msg_list[0]
