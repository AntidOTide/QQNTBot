import asyncio
from config_file import config_data
from loguru import logger
import requests
from text_to_speech import gen_speech


# def genImg(message):
#     img = text_to_image(message)
#     filename = str(uuid.uuid1()) + ".png"
#     filepath = config_data['qq_bot']['image_path'] + str(os.path.sep) + filename
#     img.save(filepath)
#     print("图片生成完毕: " + filepath)
#     return filename


# 发送私聊消息方法 uid为qq号，message为消息内容
def send_private_message_voice(uid, message, send_voice):
    try:
        if send_voice:  # 如果开启了语音发送
            voice_path = asyncio.run(
                gen_speech(message, config_data['qq_bot']['voice'], config_data['qq_bot']['voice_path']))
            message = "[CQ:record,file=file://" + voice_path + "]"
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_private_msg",
                            params={'user_id': int(uid), 'message': message}).json()
        if res["status"] == "ok":
            logger.info("私聊消息发送成功")
        else:
            logger.info(res)
            logger.info("私聊消息发送失败，错误信息：" + str(res['wording']))

    except Exception as error:
        logger.error("私聊消息发送失败")
        logger.error(error)


# 发送私聊消息方法 uid为qq号，pic_path为图片地址
def send_private_message_image(uid, pic_path, msg):
    try:
        message = "[CQ:image,file=" + pic_path + "]"
        if msg != "":
            message = msg + '\n' + message
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_private_msg",
                            params={'user_id': int(uid), 'message': message}).json()
        if res["status"] == "ok":
            logger.info("私聊消息发送成功")
        else:
            logger.info(res)
            logger.info("私聊消息发送失败，错误信息：" + str(res['wording']))

    except Exception as error:
        logger.error("私聊消息发送失败")
        logger.error(error)


def send_private_message(uid, message):
    try:
        print(message)
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_private_msg",
                            params={'user_id': int(uid), 'message': message}).json()
        if res["status"] == "ok":
            logger.info("私聊消息发送成功")
            return "私聊消息发送成功"
        else:
            logger.info(res)
            logger.info("私聊消息发送失败，错误信息：" + str(res['wording']))
            return "私聊消息发送失败，错误信息：" + str(res['wording'])
    except Exception as error:
        logger.error("私聊消息发送失败")
        logger.error(error)
        return "私聊消息发送失败"


# 发送群消息方法
def send_group_message(gid, message, uid):
    try:
        message = str('[CQ:at,qq=%s]\n' % uid) + message  # @发言人
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()
        if res["status"] == "ok":
            logger.info("群聊消息发送成功")
        else:
            logger.info(res)
            logger.info("群聊消息发送失败，错误信息：" + str(res['wording']))

    except Exception as error:
        logger.error("群聊消息发送失败")
        logger.error(error)


# 发送群消息方法
def send_group_message_voice(gid, message, uid, send_voice):
    try:
        if send_voice:  # 如果开启了语音发送
            voice_path = asyncio.run(
                gen_speech(message, config_data['qq_bot']['voice'], config_data['qq_bot']['voice_path']))
            message = "[CQ:record,file=file://" + voice_path + "]"
        if not send_voice:
            message = str('[CQ:at,qq=%s]\n' % uid) + message  # @发言人
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()
        if res["status"] == "ok":
            logger.info("群聊消息发送成功")
        else:
            logger.info(res)
            logger.info("群聊消息发送失败，错误信息：" + str(res['wording']))

    except Exception as error:
        logger.error("群聊消息发送失败")
        logger.error(error)


# 发送群消息图片方法
def send_group_message_image(gid, pic_path, uid, msg):
    try:
        message = "[CQ:image,file=" + pic_path + "]"
        if msg != "":
            message = msg + '\n' + message
        message = str('[CQ:at,qq=%s]\n' % uid) + message  # @发言人
        res = requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/send_group_msg",
                            params={'group_id': int(gid), 'message': message}).json()
        if res["status"] == "ok":
            logger.info("群聊消息发送成功")
        else:
            logger.info(res)
            logger.info("群聊消息发送失败，错误信息：" + str(res['wording']))

    except Exception as error:
        logger.error("群聊消息发送失败")
        logger.error(error)


# 处理好友请求
def set_friend_add_request(flag, approve):
    try:
        requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/set_friend_add_request",
                      params={'flag': flag, 'approve': approve})
        logger.info("处理好友申请成功")
    except Exception as e:
        logger.info(e)
        logger.info("处理好友申请失败")


# 处理邀请加群请求
def set_group_invite_request(flag, approve):
    try:
        requests.post(url=config_data['qq_bot']['cqhttp_url'] + "/set_group_add_request",
                      params={'flag': flag, 'sub_type': 'invite', 'approve': approve})
        logger.info("处理群申请成功")
    except Exception as e:
        logger.info(e)
        logger.info("处理群申请失败")
