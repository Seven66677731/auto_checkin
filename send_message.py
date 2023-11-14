import json

import requests

from utils import get_env


def send_message_pushplus(title, content, template='json'):
    url = "http://www.pushplus.plus/send"
    global pushplus_token
    if pushplus_token == "":
        pushplus_token = get_env('pushplus_token')
        if pushplus_token is None:
            print('未配置推送加token，请检查配置')
        return
    data = {
        "token": pushplus_token,
        "title": title,
        "content": content,
        "template": template
    }
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, data=body, headers=headers)
    resp_json = resp.json()
    if resp_json["code"] == 200:
        print("[Pushplus]发送通知成功")
    if resp_json["code"] != 200:
        print(f"[Pushplus]发送通知失败{resp.text}")


if __name__ == '__main__':
    send_message_pushplus('title', 'content')
