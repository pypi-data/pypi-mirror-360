import sqlite3
import requests
import pandas as pd
import os
import json
import traceback


# c1d3a814-1a02-4bbd-b5c2-f756fef92cb8: b层机器人消息群-非聊天 的 pythonspark
# 013547da-3d78-4a7f-b4a7-e668b192c293: b层机器人消息群-非聊天 的 数仓B层服务端部署通知

# 发送消息到企业微信机器人
# vx_key: string类型，自己的企业微信机器人的key
# s:string类型，要发送的消息
def send_vx(vx_key, s, i=0):
    vx_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + vx_key
    headers = {"Content-Type": "text/plain"}
    data = {
        "msgtype": "text",
        "text": {
            "content": s,
        }
    }
    if i > 3:
        raise Exception(str(traceback.format_exc()))
    try:
        requests.post(url=vx_url, headers=headers, json=data, timeout=30)
    except:
        i = i + 1
        send_vx(vx_key, str(traceback.format_exc()), i)


# 发送文件到企业微信机器人
# vx_key: string类型，自己的企业微信机器人的key
# file_path: string类型，文件地址
def post_file(vx_key, file_path):
    id_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=' + vx_key + '&type=file'
    wx_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + vx_key
    data = {'file': open(file_path, 'rb')}
    response = requests.post(url=id_url, files=data)
    json_res = response.json()
    media_id = json_res['media_id']
    data = {"msgtype": "file",
            "file": {"media_id": media_id}
            }
    try:
        requests.post(url=wx_url, json=data)
    except:
        send_vx(send_vx, str(traceback.format_exc()))


# data: dataframe|string|dict|list|tuple|array
# file_name: 带后缀的完整文件名
# file_type: 文件类型，包括csv、excel、txt、json、sql
def file_to_vx(vx_key, data, file_name):
    file_type = file_name.split('.')[-1]
    if file_type == "xls" or file_type == "xlsx":
        file_type = "excel"
    current_dir = os.getcwd()
    temp_dir = os.path.join(os.getcwd(), "tmp")
    if os.path.exists(temp_dir):
        pass
    else:
        os.makedirs(temp_dir)
    file_path = current_dir + "/" + file_name
    try:
        if isinstance(data, pd.DataFrame) and file_type != "txt":
            if file_type == "db3":
                conn = sqlite3.connect(file_path)
                data.to_sql('base_table', conn, if_exists='replace', index=False)
                post_file(vx_key, file_path)
            else:
                code_str = "data.to_" + file_type + "(file_path,index=False)"
                eval(code_str)
                post_file(vx_key, file_path)
            os.system('rm ' + file_path + '')
        else:
            if isinstance(data, dict):
                data_str = json.dumps(data, ensure_ascii=False)
            elif isinstance(data, list):
                data_str = ""
                for i in data:
                    if isinstance(i, dict):
                        data_str = data_str + json.dumps(i, ensure_ascii=False) + "\n"
                    else:
                        data_str = data_str + str(i) + "\n"
            else:
                data_str = str(data)
            print(data_str[:100])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data_str)
            post_file(vx_key, file_path)
    except:
        send_vx(vx_key, str(traceback.format_exc()))
    os.system('rm -r' + temp_dir + '')
