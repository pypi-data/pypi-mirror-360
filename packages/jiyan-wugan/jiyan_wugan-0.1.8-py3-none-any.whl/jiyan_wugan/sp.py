import subprocess
import sys
import os
import subprocess
from functools import partial

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# from utils.proxy_utils import ProxyManager
from app.utils.proxy import get_quality_proxy
from js.util import get_lib, get_abo, process_and_build_dict, get_sign, get_pos

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8", errors="ignore")

import json
import re
import time
import requests

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"}


det = None


def func_time_logger(func):
    def wrapper(*args, **kwargs):
        # start_time = time.perf_counter()
        # print(f"Function {func.__name__} started at {start_time}")
        result = func(*args, **kwargs)
        # end_time = time.perf_counter()
        # print(f"Function {func.__name__} end at {end_time}")
        # execution_time = (end_time - start_time) * 1000
        # print(f"函数 {func.__name__} 执行时间为: {execution_time} 毫秒")
        return result

    return wrapper


def get_uuid():
    import uuid
    # 生成随机 UUID（基于随机数）
    random_uuid = uuid.uuid4()
    return random_uuid


@func_time_logger
def load(captchaId, proxy, lot_number=None):
    callback = 'geetest_{}'.format(int(time.time() * 1000))
    data = {
        "captcha_id": captchaId,
        "challenge": get_uuid(),
        'lot_number': lot_number,
        # 'client_type': 'slide',
        'risk_type': 'slide',
        'client_type': 'h5',
        # 'pt': 0,
        'callback': callback,
        'lang': 'zh-cn'
    }
    url = 'https://gcaptcha4.geetest.com/load'
    max_retries = 3
    retries = 0
    while retries < max_retries:

        try:
            x = requests.get(url=url, params=data, headers=header, proxies=proxy).text
            break
        except requests.exceptions.ConnectionError as e:
            print(f"连接错误: {e}，尝试第 {retries + 1} 次重试...")
            # ProxyManager().mark_proxy_failed(proxy)
            # proxy = ProxyManager().get_proxy()
            from app.utils.proxy import get_quality_proxy
            proxy = get_quality_proxy()
            retries += 1
    else:
        print("达到最大重试次数，请求失败。")
        return None, callback
    b = re.findall(r'geetest_[0-9]*\((.*)\)', x)
    json_obj = json.loads(b[0])
    return json_obj, callback


@func_time_logger
def v(callback, captcha_id, lot_number, payload, process_token, w, proxy):
    cookies = {
        'captcha_v4_user': '6a7e29c4644a4e798f33a68025527491',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.okx.com/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'script',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }
    params = {
        'callback': callback,
        'captcha_id': captcha_id,
        'client_type': 'h5',
        'lot_number': lot_number,
        'payload': payload,
        'risk_type': 'slide',
        'process_token': process_token,
        'payload_protocol': '1',
        'pt': '1',
        'w': w
    }
    response = requests.get('https://gcaptcha4.geetest.com/verify', params=params, cookies=cookies, headers=headers,
                            proxies=proxy)
    return response.text


@func_time_logger
def get_w(target, lot_number, captchaId, data):
    t = lot_number
    n = captchaId
    i = data['data']['pow_detail']['hashfunc']
    r = data['data']['pt']
    _ = data['data']['pow_detail']['bits']
    a = data['data']['pow_detail']['datetime']
    s = ""
    pos = get_pos(t, n, i, r, _, a, s)
    if target is not None:
        setLeft = int((target[0] + target[2]) / 2) - 40
        userresponse = setLeft / 1.0059466666666665 + 2
        e = {"setLeft": setLeft, "passtime": 2385, "userresponse": userresponse, "device_id": "",
             "lot_number": lot_number,
             "pow_msg": pos['pow_msg'],
             "pow_sign": pos['pow_sign'], "geetest": "captcha", "lang": "zho", "ep": "123",
             "biht": data['data']['pow_detail']['bits'],
             "gee_guard": {
                 "roe": {"aup": "3", "sep": "3", "egp": "3", "auh": "3", "rew": "3", "snh": "3", "res": "3",
                         "cdc": "3"}},
             "em": {"ph": 0, "cp": 0, "ek": "11", "wd": 1, "nt": 0, "si": 0, "sc": 0}}
    else:
        e = {"device_id": "",
             "lot_number": lot_number,
             "pow_msg": pos['pow_msg'],
             "pow_sign": pos['pow_sign'], "geetest": "captcha", "lang": "zh", "ep": "123",
             # 'Wfvi':"Uk4W",
             "biht": "1426265548", "gee_guard": {
                "roe": {"aup": "3", "sep": "3", "egp": "3", "auh": "3", "rew": "3", "snh": "3", "res": "3",
                        "cdc": "3"}},
             "tXc3": {"AF8a": "GgVKDy", "51tJ": "SK5G4r"}, "lBg3": {"lASq": "vWFb9W", "VRmi": "pYBzFP",
                                                                    "Czwn": {"ivJK": "tJ6zo7",
                                                                             "HvGu": {"4CRA": "z0cW6I",
                                                                                      "Jwyq": "fw4Hy0",
                                                                                      "1HYb": "mZipOo",
                                                                                      "eJOE": "mqMllv"},
                                                                             "lMDs": "sgq35f"}},
             "em": {"ph": 0, "cp": 0, "ek": "11", "wd": 1, "nt": 0, "si": 0, "sc": 0}}
    abo = get_abo()
    veriy = process_and_build_dict(abo, lot_number)
    e = {**e, **veriy, **get_lib()}
    e = json.dumps(e)
    t = {'options': {
        "captchaId": captchaId,
        "pt": "1",
    }}
    xs = get_sign(e, t)
    return xs


# @func_time_logger
def jy_main(captchaId, proxy=None, lot_number=None):
    # proxy = ProxyManager().get_proxy()
    if proxy is None:
        proxy = get_quality_proxy()
    load_res, callback = load(captchaId, proxy = proxy, lot_number=lot_number)
    lot_number = load_res['data']['lot_number']
    captcha_type = load_res['data']['captcha_type']
    payload = load_res['data']['payload']
    process_token = load_res['data']['process_token']
    static_path = load_res['data']['static_path']
    # print("aaaa",load_res)
    # 检查并写入 static_path
    static_path_file = os.path.join(os.path.dirname(__file__), 'static_path.txt')
    print(f"[调试] static_path_file 绝对路径: {os.path.abspath(static_path_file)}")
    current_static_path = None

    try:
        with open(static_path_file, 'r') as f:
            current_static_path = f.read().strip()
    except FileNotFoundError:
        pass

    js_dir = os.path.dirname(os.path.abspath(__file__))
    source_js_path = os.path.join(js_dir, 'source.js')
    if current_static_path != static_path or not os.path.exists(source_js_path):
        # 检查source.js是否存在，不存在也满足条件
        if not os.path.exists(source_js_path):
            print(f"[提示] {source_js_path} 不存在，将创建新文件。")
        with open(static_path_file, 'w') as f:
            f.write(static_path)
        print(f"[自动更新] 已写入static_path到: {os.path.abspath(static_path_file)}")
        url = 'https://static.geetest.com/{}/js/gcaptcha4.js'.format(static_path)
        js_text = requests.get(url=url, proxies=proxy).text
        p = js_text[0:5]
        js_text = js_text + " \n window.u = {}".format(p)
        with open(source_js_path, 'w', encoding='utf-8') as f:
            f.write(js_text)
    if captcha_type != 'ai':
        bg = load_res['data']['bg']
        slice = load_res['data']['slice']
        url = 'https://static.geetest.com/{}'.format(bg)
        bg_content = requests.get(url=url, proxies=proxy).content
        url = 'https://static.geetest.com/{}'.format(slice)
        slice_content = requests.get(url=url, proxies=proxy).content
        res = det.slide_match(slice_content, bg_content, simple_target=True)
        target = res['target']
    else:
        target = None
    w = get_w(target=target, captchaId=captchaId, lot_number=lot_number,
              data=load_res)
    x = v(callback, captchaId, lot_number, payload, process_token, w, proxy)
    b = re.findall(r'geetest_[0-9]*\((.*)\)', x)
    # print(b)
    json_obj = json.loads(b[0])
    if json_obj['data']['result'] == 'continue':
        json_obj = jy_main(captchaId=captchaId, lot_number=lot_number)
    return json_obj


if __name__ == '__main__':
    start = time.time()
    jy_main('1461c6af6d31942bae54833e928fb5db')
    end = time.time()
    print(end - start)
