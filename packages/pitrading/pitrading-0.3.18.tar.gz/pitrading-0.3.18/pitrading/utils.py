#!/usr/bin/python3
import ctypes
import json
import os
import platform
import random
import string
import sys
import threading
import traceback
from datetime import datetime, timedelta

import requests
from pi_utils import Logger
from qcloud_cos import CosConfig, CosS3Client

BOTS = {
    "saaltfiish": "155f3be9-e37c-4b1f-bfed-8b35a3e6540c",
    "pitech": "c1202b85-28e7-4170-be60-e69f02f8cbee"
}

def Ntf_fishball(text, url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1a02ca30-e207-427e-b5e9-08e917f66f8d"):
        data = {
            "msgtype": "text",
            "text": {
                    "content": text,
                }
        }
        res = requests.post(url=url,data=json.dumps(data))
        print("res:",res)
        return res.text

def Ntf_saaltfiish(text = "settle_price ☠", title="", author="", url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=155f3be9-e37c-4b1f-bfed-8b35a3e6540c"):
    try:
        data = {
            "msgtype": "text",
            "text": {
                    "content": str(text),
                }
        }
        threading.Thread( target = lambda : requests.post(url=url,data=json.dumps(data), headers = {'X-wgo-appid': 'gxfstpp'}) ).start()
    except:
        print(traceback.format_exc())

def pi_alert(msg: str, title , author = "HuJiazhen", msgtype = "text"):
    url = "https://openapi.dianyao.ai/msg/@pi_alert?level=notify"
    data = {
            "request": {
                "msgtype": msgtype,
                msgtype: {
                    "content": msg,
                },
                "title": title,
                "from": author,
            }
    }
    threading.Thread( target = lambda : requests.post(url=url,data=json.dumps(data), headers = {'X-wgo-appid': 'gxfstpp'}) ).start()

def get_tencent_client(proxy=False, region='ap-shanghai', sct_id="", sct_key=""):
    secret_id = 'AKIDEF2cEe16B80iDFqoVC8pWzDRF4uzRoOq'
    secret_key = 'lXCL6dx68xkPorfT8YourZ8fAfFZfXMy'
    if sct_id:
        secret_id = sct_id
    if sct_key:
        secret_key = sct_key

    scheme = 'https'

    if not proxy:
        config = CosConfig(Region=region, SecretId=secret_id,
                           SecretKey=secret_key, Scheme=scheme)
    else:
        proxy = {
            'http': "127.0.0.1:7890",
            'https': "127.0.0.1:7890"
        }
        config = CosConfig(Region=region, SecretId=secret_id,
                           SecretKey=secret_key, Proxies=proxy, Scheme=scheme)
    client = CosS3Client(config)
    return client

def postWechat(text = "settle_price ☠", url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c1202b85-28e7-4170-be60-e69f02f8cbee"):
    try:
        data = {
            "msgtype": "text",
            "text": {
                    "content": text,
                }
        }
        threading.Thread( target = lambda : requests.post(url=url,data=json.dumps(data), headers = {'X-wgo-appid': 'gxfstpp'}) ).start()
    except:
        print(traceback.format_exc())

def get_free_space_mb(folder):
    """
    获取磁盘剩余空间
    :param folder: 磁盘路径 例如 D:\\
    :return: 剩余空间 单位 G
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024 // 1024
    else:
        st = os.statvfs(folder)
        print(st)
        return st.f_bavail * st.f_frsize / 1024 // 1024

def post_file(file, bot = "saaltfiish"):
    data = {'file': open(file,'rb')}
    key = BOTS["saaltfiish"]
    if bot in BOTS:
        key = BOTS[bot]
    id_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file'
    wx_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}'
    response = requests.post(url=id_url, files=data)
    json_res = response.json()
    media_id = json_res['media_id']

    data = {
        "msgtype": "file",
        "file": {
            "media_id": media_id
    }}
    result = requests.post(url=wx_url, json=data)
    Logger.info(result)

def random_string(N: int) -> str:
    return ''.join(random.choices(string.printable, k=N))

if __name__ == '__main__':
    sys.exit(0)
