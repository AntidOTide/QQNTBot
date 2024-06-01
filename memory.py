import os
import time

from config_file import load_json_from_file, config_data
import json
from bot_function import get_bj_time


def load_memory_private_config(uid) -> dict:
    if not os.path.exists(f"../resource/memory/private/{uid}"):
        os.makedirs(f"../resource/memory/private/{uid}")
        with open(f"../resource/memory/private/{uid}/{uid}.json", "w", encoding='utf-8') as f:
            default_data = {
                "memory": [
                    {
                        "role": "system",
                        "content": config_data["chatgpt"]["preset"]
                    },
                    {
                        "role": "system",
                        "content": "current time is:" + get_bj_time()
                    }
                ]
            }
            f.write(json.dumps(default_data, ensure_ascii=False, indent=4))
            f.close()
    else:
        memory = load_json_from_file(f"../resource/memory/private/{uid}/{uid}.json")
        return memory


def write_memory_private_config(uid: str, data: dict):
    # memory = load_json_from_file(f"memory/private/{uid}/{uid}.json")
    # memory["memory"].append(data)
    with open(f"../resource/memory/private/{uid}/{uid}.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))
        f.close()


def load_memory_group_config(gid) -> list:
    if not os.path.exists(f"../resource/memory/group/{gid}"):
        os.makedirs(f"../resource/memory/group/{gid}")
        with open(f"../resource/memory/group/{gid}/{gid}_config.json", "w", encoding='utf-8') as f:
            default_data = {
                "config": [
                    {
                        "role": "system",
                        "content": config_data["chatgpt"]["preset"]
                    },
                    {
                        "role": "system",
                        "content": "Current time now is:" + get_bj_time()
                    },
                    {
                        "role": "system",
                        "content": "以下是之前的对话记录，你在回答问题时需要参照以下的事实进行回答\n"
                    }
                ]
            }
            f.write(json.dumps(default_data, ensure_ascii=False, indent=4))
            f.close()
        with open(f"../resource/memory/group/{gid}/{gid}.json", "w", encoding='utf-8') as f:
            data = {"memory": []}
            f.write(json.dumps(data, ensure_ascii=False, indent=4))
            f.close()
        group_config = load_json_from_file(f"../resource/memory/group/{gid}/{gid}_config.json")
        group_memory = load_json_from_file(f"../resource/memory/group/{gid}/{gid}.json")

        return [group_config, group_memory]
    else:
        group_config = load_json_from_file(f"../resource/memory/group/{gid}/{gid}_config.json")
        group_memory = load_json_from_file(f"../resource/memory/group/{gid}/{gid}.json")
        summary = "以下是聊天室里的之前的对话记录，这里是一个聊天室，信息的输入格式是[名字]:[内容]，你在回答问题时需要参照以下的事实进行回答"
        memory_len = len(group_memory["memory"])
        if memory_len < 30:
            for i in group_memory["memory"]:
                summary += f"{i['role']}:{i['content']}\n"
        else:
            memory_list = group_memory["memory"][-30:]
            for i in memory_list:
                summary += f"{i['role']}:{i['content']}\n"
        group_config["config"][2]["content"] = summary
        print(group_config)
        print(summary)
        return [group_config, group_memory]


def write_memory_group_config(gid, uid: str, data: dict):
    with open(f"../resource/memory/group/{gid}/{gid}_config.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))
        f.close()


def write_memory_group(gid, uid: str, data: dict):
    with open(f"../resource/memory/group/{gid}/{gid}.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))
        f.close()
# data = {
#     "role": "user",
#     "message": "114514",
#     "time": "114514"
# }
# write_memory_private_config("1158519478", data)
# with open(u"memory/private/1158519478/1.json","w") as f:
#     data ={
#         "11":"11"
#     }
#     f.write(json.dumps(data))
# load_memory_group_config(225649416)
