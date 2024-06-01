import requests
import json


def search_serper_online(question, api_key):
    url = "https://cn2us02.opapi.win/api/v1/openapi/search/serper/v1"
    payload = {
        'q': question,
        'cache': '3',
        'gl': 'us',
        'hl': 'en',
        'page': '1',
        'num=': '10'
    }
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Authorization': api_key
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


def summary_answer(search_json):
    text = ""
    print("找到以下信息")
    for i in search_json["organic"]:
        try:
            text += (str(i['position']) + ". " + i["snippet"] + "\n")

        except Exception:
            continue
    print(text)
    question = search_json["searchParameters"]["q"]
    url = "https://cn2us02.opapi.win/v1/chat/completions"

    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": f"请为我总结以下的几段文字，告诉我{question}是什么，尽可能的详细，包括时间地点人物"
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
    print(response.json()['choices'][0]['message']['content'])
    return response.json()['choices'][0]['message']['content']
