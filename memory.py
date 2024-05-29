import os
from config_file import load_json_from_file, config_data
import json
from bot_function import get_bj_time


def load_memory_private_config(uid) -> dict:
    if not os.path.exists(f"memory/private/{uid}"):
        os.makedirs(f"memory/private/{uid}")
        with open(f"memory/private/{uid}/{uid}.json", "w", encoding='utf-8') as f:
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
        memory = load_json_from_file(f"memory/private/{uid}/{uid}.json")
        return memory


def write_memory_private_config(uid: str, data: dict):
    # memory = load_json_from_file(f"memory/private/{uid}/{uid}.json")
    # memory["memory"].append(data)
    with open(f"memory/private/{uid}/{uid}.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))
        f.close()


def load_memory_group_config(gid) -> dict:
    if not os.path.exists(f"memory/private/{gid}"):
        os.makedirs(f"memory/private/{gid}")
        with open(f"memory/private/{gid}/{gid}.json", "w", encoding='utf-8') as f:
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
        memory = load_json_from_file(f"memory/private/{gid}/{gid}.json")
        return memory


def write_memory_group_config(uid: str, data: dict):
    with open(f"memory/private/{uid}/{uid}.json", "w", encoding='utf-8') as f:
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
