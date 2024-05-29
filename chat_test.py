import requests
import json


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
