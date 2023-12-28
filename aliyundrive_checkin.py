import random
import time
import requests
from notify import send_message_pushplus
from utils import get_env

# refresh_token = ""

refresh_token = get_env("refresh_token")


def get_access_token(token) -> dict:
    """
    通过refresh_token获取accessToken和相关信息
    """
    url = 'https://auth.alipan.com/v2/account/token'
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': token
    }
    resp = requests.post(url, json=payload).json()

    if 'code' in resp:
        msg = {
            "status": False,
            "message": resp['message'],
        }
    else:
        msg = {
            "status": True,
            "name": resp['nick_name'] if resp['nick_name'] else resp['user_name'],
            "access_token": resp['access_token'],
            "refresh_token": resp['refresh_token'],
        }
    return msg


def check_in(access_token: str) -> dict:
    """
    签到
    """
    url = 'https://member.alipan.com/v1/activity/sign_in_list'
    payload = {'isReward': False}
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'_rx-s': 'mobile'}
    resp = requests.post(url, json=payload, params=params, headers=headers).json()

    if 'success' not in resp:
        msg = {
            "status": False,
            "message": resp['message'],
        }
    else:
        sign_in_count = resp['result']['signInCount']
        msg = {
            "status": True,
            "success ": resp['success'],
            "signin_count": sign_in_count,
        }
    return msg


def get_reward_and_task(access_token: str) -> dict:
    """
    获取奖励信息和今日任务
    """
    url = 'https://member.alipan.com/v2/activity/sign_in_list'
    headers = {'Authorization': f'Bearer {access_token}'}
    payload = {}
    params = {'_rx-s': 'mobile'}
    resp = requests.post(url, json=payload, params=params, headers=headers).json()

    if 'result' not in resp:
        return {
            "status": False,
            "message": resp['message'],
        }

    success = resp['success']
    sign_in_infos = resp['result']['signInInfos']

    day = resp['result']['signInCount']
    rewards = filter(lambda info: int(info.get('day', 0)) == day, sign_in_infos)

    award_notice = ''
    task_notice = ''

    for reward in next(rewards)['rewards']:
        name = reward['name']
        remind = reward['remind']
        types = reward['type']

        # 签到奖励
        if types == "dailySignIn":
            award_notice = name
            reward_status = reward['status']
            if reward_status == 'finished':
                b = receive_reward(access_token, day)
                award_notice += '【领取成功】' if b else '【领取失败】'
            elif reward_status == 'verification':
                award_notice += '【已领取】'
            else:
                award_notice += '【领取失败】'
        # 每日任务
        if types == "dailyTask":
            task_notice = f'{remind}（{name}）'
    return {
        "status": success,
        "message": resp['message'],
        "award_notice": award_notice,
        "task_notice": task_notice
    }


def receive_reward(access_token: str, day: int) -> bool:
    """
    领取奖励
    :param access_token: token
    :param day: 领取第几天的奖励
    :return: 是否领取成功
    """
    url = 'https://member.alipan.com/v1/activity/sign_in_reward'
    payload = {'signInDay': day}
    headers = {'Authorization': f'Bearer {access_token}'}
    resp = requests.post(url, json=payload, headers=headers).json()
    return resp['success']


def main():
    time.sleep(random.randint(3, 5))
    print(" 阿里云盘任务 ".center(30, "#"))
    res = get_access_token(refresh_token)
    title = '阿里云盘签到'
    content = ''
    print(" 开始签到 ".center(30, "#"))
    if res['status']:
        access_token = res['access_token']
        check_in_json = check_in(access_token)
        if check_in_json["status"]:
            print("签到成功")
            title += '成功'
            reward_and_task_info_json = get_reward_and_task(access_token)
            if reward_and_task_info_json["status"]:
                print("获取奖励信息和任务信息成功")
                result = (f"今日奖励：{reward_and_task_info_json['award_notice']}\n"
                          f"用户：{res['name']}\n"
                          f"连续签到天数：{check_in_json['signin_count']}\n"
                          f"今日任务：{reward_and_task_info_json['task_notice']}")
                print(result)
                content += result
            else:
                print("获取奖励信息和任务信息失败")
                title += '成功'
                content += f"获取奖励信息和任务信息失败【{res['reward_and_task_info_json']}】"
        else:
            print("签到失败")
            title += '失败'
            content += res['message']
    else:
        title += '失败【获取token失败】'
        content += res['message']
        print(f"签到失败：{res['message']}")
    print(" 签到完成 ".center(30, "#"))
    send_message_pushplus(title, content, "txt")
    print(" 结束阿里云盘任务 ".center(30, "#"))
    print("\n")


if __name__ == '__main__':
    main()
