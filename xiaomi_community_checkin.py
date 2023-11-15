import base64
import binascii
import datetime
import hashlib
import json
import random
import requests
import time
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad

from notify import send_message_pushplus
from utils import get_env

account = get_env('xiaomi_uid')
password = get_env('xiaomi_password')
user_agent = get_env('user_agent')

content = {}


# 随机字符
def random_str(length):
    s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-=_+~`{}[]|:<>?/.'
    return ''.join(random.choice(s) for _ in range(length))


# AES加密
def aes_encrypt(key, data):
    iv = '0102030405060708'.encode('utf-8')
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    padded_data = pad(data.encode('utf-8'), AES.block_size, style='pkcs7')
    ciphertext = cipher.encrypt(padded_data)
    return base64.b64encode(ciphertext).decode('utf-8')


# RSA加密
def rsa_encrypt(key, data):
    public_key = RSA.import_key(key)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(base64.b64encode(data.encode('utf-8')))
    return base64.b64encode(ciphertext).decode('utf-8')


# 获取Token
def get_token():
    key = random_str(16)
    public_key = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArxfNLkuAQ/BYHzkzVwtu
    g+0abmYRBVCEScSzGxJIOsfxVzcuqaKO87H2o2wBcacD3bRHhMjTkhSEqxPjQ/FE
    XuJ1cdbmr3+b3EQR6wf/cYcMx2468/QyVoQ7BADLSPecQhtgGOllkC+cLYN6Md34
    Uii6U+VJf0p0q/saxUTZvhR2ka9fqJ4+6C6cOghIecjMYQNHIaNW+eSKunfFsXVU
    +QfMD0q2EM9wo20aLnos24yDzRjh9HJc6xfr37jRlv1/boG/EABMG9FnTm35xWrV
    R0nw3cpYF7GZg13QicS/ZwEsSd4HyboAruMxJBPvK3Jdr4ZS23bpN0cavWOJsBqZ
    VwIDAQAB
    -----END PUBLIC KEY-----"""
    data = '{"type":0,"startTs":' + str(round(time.time() * 1000)) + ',"endTs":' + str(round(
        time.time() * 1000)) + (',"env":{"p1":"","p2":"","p3":"","p4":"","p5":"","p6":"","p7":"","p8":"","p9":"",'
                                '"p10":"","p11":"","p12":"","p13":"","p14":"","p15":"","p16":"","p17":"","p18":"",'
                                '"p19":5,"p20":"","p21":"","p22":5,"p23":"","p24":"","p25":"","p26":"","p28":"",'
                                '"p29":"","p30":"","p31":"","p32":"","p33":"","p34":""},"action":{"a1":[],"a2":[],'
                                '"a3":[],"a4":[],"a5":[],"a6":[],"a7":[],"a8":[],"a9":[],"a10":[],"a11":[],"a12":[],'
                                '"a13":[],"a14":[]},"force":false,"talkBack":false,"uid":"') + random_str(
        27) + '","nonce":{"t":' + str(round(time.time())) + ',"r":' + str(
        round(time.time())) + '},"version":"2.0","scene":"GROW_UP_CHECKIN"}'
    s = rsa_encrypt(public_key, key)
    d = aes_encrypt(key, data)
    url = 'https://verify.sec.xiaomi.com/captcha/v2/data?k=3dc42a135a8d45118034d1ab68213073&locale=zh_CN'
    data = {'s': s, 'd': d, 'a': 'GROW_UP_CHECKIN'}
    result = requests.post(url=url, data=data).json()
    if result['msg'] != '参数错误':
        return result['data']['token']


# 用户信息
def info(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/homepage/mineInfo'
    result = requests.get(url=url, cookies=cookie).json()
    info = (f'昵称：{result["entity"]["userInfo"]["userName"]}'
            f'等级：{result["entity"]["userInfo"]["userGrowLevelInfo"]["showLevel"]}'
            f'积分：{result["entity"]["userInfo"]["userGrowLevelInfo"]["point"]}')
    print(info)
    content.update({"info": info})


# 签到
def check_in(cookie):
    url = f'https://api.vip.miui.com/mtop/planet/vip/user/getUserCheckinInfo?miui_vip_ph={cookie["miui_vip_ph"]}'
    result = requests.get(url=url, cookies=cookie).json()
    if result['entity']['checkin7DaysDetail'][datetime.date.today().weekday()] == 0:
        url = f'https://api.vip.miui.com/mtop/planet/vip/user/checkinV2'
        data = {'miui_vip_ph': cookie['miui_vip_ph'], 'token': get_token()}
        result = requests.post(url=url, cookies=cookie, data=data).json()
        if 'success' not in result['message']:
            content.update({"签到": f"每日签到失败【{result['message']}】"})
            print(f'签到失败: {result["message"]}')


# 点赞
def like(cookie):
    url = 'https://api.vip.miui.com/mtop/planet/vip/content/announceThumbUp'
    data = {'postId': '36625780', 'sign': '36625780', 'timestamp': int(round(time.time() * 1000))}
    requests.get(url=url, cookies=cookie, data=data)


# 浏览帖子
def browse(cookie):
    url = (f'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByActionV2?'
           f'miui_vip_ph={cookie["miui_vip_ph"]}')
    for action in ['BROWSE_POST_10S', 'BROWSE_SPECIAL_PAGES_SPECIAL_PAGE', 'BROWSE_SPECIAL_PAGES_USER_HOME']:
        data = {'action': action, 'miui_vip_ph': cookie['miui_vip_ph']}
        requests.post(url, cookies=cookie, data=data)


# 拔萝卜
def carrot(cookie):
    url = 'https://api.vip.miui.com/api/carrot/pull'
    requests.post(url=url, cookies=cookie, params={'miui_vip_ph': cookie['miui_vip_ph']})


# 获取cookie


def md5_crypto(password: str) -> str:
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result.upper()


def login(uid, password, user_agent):
    password = md5_crypto(password)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'https://account.xiaomi.com/fe/service/login/password?sid=miui_vip&qs=%253Fcallback%253Dhttp'
                   '%25253A%25252F%25252Fapi.vip.miui.com%25252Fsts%25253Fsign%25253D4II4ABwZkiJzkd2YSkyEZukI4Ak'
                   '%2525253D%252526followup%25253Dhttps%2525253A%2525252F%2525252Fapi.vip.miui.com%2525252Fpage'
                   '%2525252Flogin%2525253FdestUrl%2525253Dhttps%252525253A%252525252F%252525252Fweb.vip.miui.com'
                   '%252525252Fpage%252525252Finfo%252525252Fmio%252525252Fmio%252525252FinternalTest%252525253Fref'
                   '%252525253Dhomepage%2526sid%253Dmiui_vip&callback=http%3A%2F%2Fapi.vip.miui.com%2Fsts%3Fsign'
                   '%3D4II4ABwZkiJzkd2YSkyEZukI4Ak%253D%26followup%3Dhttps%253A%252F%252Fapi.vip.miui.com%252Fpage'
                   '%252Flogin%253FdestUrl%253Dhttps%25253A%25252F%25252Fweb.vip.miui.com%25252Fpage%25252Finfo'
                   '%25252Fmio%25252Fmio%25252FinternalTest%25253Fref%25253Dhomepage&_sign=L%2BdSQY6sjSQ%2FCRjJs4p'
                   '%2BU1vNYLY%3D&serviceParam=%7B%22checkSafePhone%22%3Afalse%2C%22checkSafeAddress%22%3Afalse%2C'
                   '%22lsrp_score%22%3A0.0%7D&showActiveX=false&theme=&needTheme=false&bizDeviceType=',
        'User-Agent': user_agent,
        'Origin': 'https://account.xiaomi.com',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': 'deviceId=; pass_ua=web; uLocale=zh_CN'
    }

    data = {'callback': 'https://api.vip.miui.com/sts', '_json': 'true', 'user': str(uid), 'hash': str(password),
            'sid': 'miui_vip', '_sign': 'ZJxpm3Q5cu0qDOMkKdWYRPeCwps=', '_locale': 'zh_CN'}

    url = 'https://account.xiaomi.com/pass/serviceLoginAuth2'
    sha1 = hashlib.sha1()
    login_json = json.loads(requests.post(url=url, headers=headers, data=data).text.replace('&&&START&&&', ''))
    if login_json['description'] == '登录验证失败':
        return 'Error'
    sha1.update(('nonce=' + str(login_json['nonce']) + '&' + login_json['ssecurity']).encode('utf-8'))
    client_sign = base64.encodebytes(binascii.a2b_hex(sha1.hexdigest().encode('utf-8'))).decode(
        encoding='utf-8').strip()
    location_url = login_json['location'] + '&_userIdNeedEncrypt=true&clientSign=' + client_sign
    cookie = dict(requests.get(url=location_url).cookies)
    return cookie


# 签到情况
def check_status(cookie):
    url = f'https://api.vip.miui.com/mtop/planet/vip/member/getCheckinPageCakeList?miui_vip_ph={cookie["miui_vip_ph"]}'
    result = requests.get(url=url, cookies=cookie).json()
    for i in result['entity'][2]['data']:
        if i['jumpText'] == '已完成':
            content.update({i['title']: '√'})
            print(i['title'], '√')
        elif i['jumpText'] == '':
            content.update({i['title']: '×'})
            print(i['title'], '×')


# 主程序
def main():
    time.sleep(random.randint(3, 5))
    print(" 小米社区任务开始 ".center(30, "#"))
    cookie = {}
    for i in range(5):
        cookie = login(account, password, user_agent)
        if len(cookie) != 0:
            break
        else:
            time.sleep(i)
    if len(cookie) == 0 or cookie == 'Error':
        print(f'{account}：登录失败')
    else:
        for action in ['info', 'check_in', 'like', 'browse', 'carrot', 'check_status']:
            eval(f'{action}(cookie)')
    title = "小米社区"
    send_message_pushplus(title, content, "json")
    print(" 小米社区任务结束 ".center(30, "#"))


if __name__ == '__main__':
    main()
