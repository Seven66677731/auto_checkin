import requests as req
import re
import time
import random

from send_message import send_message_pushplus
from utils import get_env

# weibo_gsid = ""
# weibo_from = "",
# weibo_s = "",
# weibo_uid = ""

weibo_gsid = get_env("weibo_gsid")
weibo_from = get_env("weibo_from")
weibo_s = get_env("weibo_s")
weibo_uid = get_env("weibo_uid")

SUPERTOPIC_URL = "https://api.weibo.cn/2/cardlist"
CHECKIN_URL = "https://api.weibo.cn/2/page/button"
TASK_URL = "https://m.weibo.cn/c/checkin/ug/v2/signin/signin"
INFO = "https://api.weibo.cn/2/profile"

data = {
    "gsid": weibo_gsid,  # 身份验证
    "c": "android",  # 客户端校验
    "from": weibo_from,  # 客户端校验
    "s": weibo_s,  # 校验参数
    "lang": "zh_CN",
    "networktype": "wifi",
    "uid": weibo_uid,  # 用于获取用户信息
}

headers = {
    "Host": "api.weibo.cn",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip",
    "content-type": "application/json;charset=utf-8",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)",
}


# 获取用户信息
def get_user_name() -> str:
    resp = req.get(INFO, params=data, headers=headers).json()
    if "errno" in resp:
        print(f"获取用户名时出错, 原因: {resp['errmsg']}")
        return "获取取用户名失败"
    else:
        return resp["userInfo"]["name"]


# 获取超话列表
def get_supertopic_list() -> list:
    print(" 开始获取超话列表 ".center(30, "#"))
    since_id = ""
    super_list = []

    while True:
        params = {
            "containerid": "100803_-_followsuper",
            "fid": "100803_-_followsuper",
            "since_id": since_id,
            "cout": 20,
        }

        params.update(data)
        resp = req.get(SUPERTOPIC_URL, headers=headers, params=params).json()

        if "errno" not in resp:
            # 获得超话列表
            for card in resp["cards"]:
                # 解析 card_group  去掉不必要的内容
                list_ = parse_supertopic_item(card["card_group"])
                super_list.extend(list_)

            # 获取下一页 id
            since_id = resp["cardlistInfo"]["since_id"]

            # 获取到空就是爬取完了
            if since_id == "":
                print(f" 超话列表获取完毕({len(super_list)}) ".center(30, "#"))
                break
        else:
            print(f"获取超话列表时出错, 原因:  {resp['errmsg']}")
            break
    return super_list


# 解析超话列表
def parse_supertopic_item(card_group: list) -> list:
    super_list = []

    for card in card_group:
        if card["card_type"] == "8":
            # 获得超话链接
            scheme = card["scheme"]
            # 获得超话的 containerid
            cid = re.findall(
                "(?<=containerid=).*?(?=&)|(?<=containerid=).*",
                scheme,
            )

            super_item = {
                "title": card["title_sub"],
                "level": card["desc1"],
                "id": cid[0],
                "status": card["buttons"][0]["name"],
            }
            if len(cid) > 0:
                super_list.append(super_item)
                print(f"{super_item['title']}")
    return super_list


# 超话签到
def supertopic_checkin(item: dict):
    try:
        if item["status"] != "签到":
            msg = {
                "status": True,
                "title": item["title"],
                "msg": "已签到",
                "exp": "",  # 经验
                "score": "",  # 积分
                "continue": "",
                "rank": "",  # 连续签到
            }
            print(f"[已签到_跳过] {item['title']}")
        else:
            params = {
                "request_url": f"http://i.huati.weibo.com/mobile/super/active_checkin?pageid={item['id']}&in_page=1"
            }

            params.update(data)
            resp = req.get(CHECKIN_URL, headers=headers, params=params).json()

            if "errno" in resp:
                raise Exception(resp["errmsg"])
            else:
                msg = {
                    "status": True,
                    "title": item["title"],
                    "msg": "签到成功",
                    "rank": resp["fun_data"]["check_count"],  # 第几个签到
                    "score": resp["fun_data"]["score"],
                    "exp": resp["fun_data"]["int_ins"],
                    "continue": resp["fun_data"]["check_int"],
                }
                print(f"[签到成功] {item['title']}")
    except Exception as e:
        msg = {
            "status": False,
            "msg": f"签到失败：{e}"
        }
    return msg


if __name__ == '__main__':
    supertopic_list = get_supertopic_list()
    msg_list = []
    success_count = 0
    total_count = len(supertopic_list)
    if total_count > 0:
        print(" 开始签到 ".center(30, "#"))
        for supertopic in supertopic_list:
            msg = supertopic_checkin(supertopic)
            if msg["status"]:
                success_count += 1
            msg_list.append(msg)
            # 添加随机等待值
            time.sleep(random.randint(5, 10))
        print(" 签到完成 ".center(30, "#"))

        title = f"微博超话：共{total_count}个,成功签到{success_count}个"
        content = ""
        for msg in msg_list:
            content += msg["title"] + ":" + ("签到成功" if msg["status"] else "签到失败")
            content += "  "
        # 发送通知
        send_message_pushplus(title, content, "txt")
