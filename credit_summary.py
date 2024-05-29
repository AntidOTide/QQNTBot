import requests


def get_credit_summary():
    url = "https://aigptx.top/api/v1/user/admin/get-api-tokens"

    payload = {}
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Authorization': 'sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    json = response.json()
    api_id = json['data'][2]["remark"]
    used_fee = json['data'][2]["used_fee"]
    permissions = json['data'][2]["permissions"]
    max_fee = json['data'][2]["max_fee"]
    # print("API:" + api_id)
    # print("used_fee:" + used_fee)
    model_str = ""
    model_list = []
    for i in permissions:
        model_str += i + "\n"
        model_list.append(i)
    result = [api_id, used_fee, max_fee, model_str, model_list]
    return result
