import requests


# 注意；basic_json是一个字典，存储一些平台基本信息，样例如下：
# {"user_name":"fuyu",     # 用户名
#  "token":"cce8747e20881dfasdf66b0511cdc9fb2", # 个人令牌
#  "project_name":"project_name",  # 项目名称
#  "task_name":"project_name" # 任务名称
#}

# 用于获取项目代码和任务代码
def get_dolphin_scheduler_code(basic_json):
    # 设置请求头，包含认证token
    headers = {
        "token": basic_json['token']
    }

    # 发送GET请求，获取项目列表
    response = requests.get(url='http://192.168.98.21:12345/cqvip/projects/list',
                            headers=headers)

    # 解析响应中的JSON数据，获取项目列表
    project_list = response.json()['data']

    # 遍历项目列表，查找与指定项目名称匹配的项目
    projectCode=-1
    for i in project_list:
        if i['name'] == basic_json['project_name']:
            projectCode = i['code']  # 获取匹配项目的代码
            break

    # 检查是否找到了匹配的项目代码
    if projectCode!=-1:
        # 发送GET请求，获取指定项目下的任务定义列表
        response = requests.get(
            url='http://192.168.98.21:12345/cqvip/projects/' + str(projectCode) + '/process-definition/list',
            headers=headers)

        # 解析响应中的JSON数据，获取任务定义列表
        task_list = response.json()['data']

        # 遍历任务定义列表，查找与指定任务名称匹配的任务
        task_code=-1
        for task in task_list:
            if task['processDefinition']['name'] == basic_json['task_name']:
                task_code = task['processDefinition']['code']  # 获取匹配任务的代码
                break
        if task_code==-1:
            raise Exception('未找到', basic_json['task_name'], '任务')
    else:
        raise Exception('未找到',basic_json['project_name'],'项目')
    return (str(projectCode),str(task_code))

# 定义一个函数dolphinscheduler_run，用于在DolphinScheduler中运行指定的任务
def dolphinscheduler_run(basic_json):
    # 设置请求头，包含认证token
    headers = {
        "token": basic_json['token']
    }
    code=get_dolphin_scheduler_code(basic_json)
    # 准备请求数据，用于启动任务实例
    data = {
        "projectCode": code[0],  # 项目代码
        "processDefinitionCode": code[1],  # 任务定义代码
        "tenantCode": basic_json['user_name'],  # 用户名称
        "scheduleTime": "",  # 调度时间（留空表示立即执行）
        "failureStrategy": "END",  # 失败策略（END表示失败后结束）
        "warningType": "NONE",  # 警告类型（NONE表示不发送警告）
        "processInstancePriority": "MEDIUM",  # 任务实例优先级（MEDIUM表示中等）
    }
    # 发送POST请求，启动任务实例
    r = requests.post(url='http://192.168.98.21:12345/cqvip/projects/' + str(
        code[0]) + '/executors/start-process-instance',
                      headers=headers, params=data)

    # 打印响应内容，通常包含任务启动的结果信息
    print(r.text)

## 修改 DolphinScheduler 平台上任务的上下线状态
def alter_dolphinscheduler_state(basic_json, releaseState):
    """
    参数:
    - basic_json (dict): 包含用户认证信息的字典，必须包含 'token'、'user_name'，'project_name'和'spark_test' 字段。
    - releaseState (str): 任务的目标状态，'ONLINE' 表示上线，'OFFLINE' 表示下线。
    """

    # 设置请求头，包含认证 token
    headers = {
        "token": basic_json['token']
    }

    # 获取任务代码，假设 get_dolphin_scheduler_code 是一个函数，返回项目代码和任务代码
    code = get_dolphin_scheduler_code(basic_json)  # code[0] 是项目代码，code[1] 是任务代码

    # 构建 API URL，用于修改任务的上下线状态
    API_URL = "http://192.168.98.21:12345/cqvip/projects/" + code[0] + "/process-definition/" + code[1] + "/release"

    # 准备请求数据，包含任务的目标状态
    data = {
        "releaseState": releaseState  # 'OFFLINE' 表示下线状态，'ONLINE' 表示上线状态
    }

    # 发送 POST 请求，修改任务的上下线状态
    # - url: API 地址
    # - headers: 请求头，包含认证信息
    # - params: 请求参数，包含任务的目标状态
    r = requests.post(url=API_URL, headers=headers, params=data)

    # 打印 API 响应内容，通常包含修改状态的结果信息
    print(r.text)


# 修改 DolphinScheduler 平台上的文件内容
def alter_dolphinscheduler_file(basic_json, local_file_path, dolphin_scheduler_file_path):
    """
    参数:
    - basic_json (dict): 包含用户认证信息的字典，必须包含 'token' 和 'user_name' 字段。
    - local_file_path (str): 本地文件的路径，用于读取更新后的内容。
    - dolphin_scheduler_file_path (str): 需要修改的文件在 DolphinScheduler 中的路径（相对路径）。
    """

    # DolphinScheduler 的 API 地址，用于更新文件内容
    URL = "http://192.168.98.21:12345/cqvip/resources/update-content"

    # 打开本地文件，读取文件内容
    with open(local_file_path, 'r', encoding='utf-8') as f:
        content_text = f.read()  # 读取文件的全部内容

    # 设置请求头，包含认证 token
    headers = {
        "token": basic_json['token']
    }

    # 准备请求数据，包含文件内容、用户信息和文件路径
    data = {
        "content": content_text,  # 更新后的文件内容
        "tenantCode": basic_json['user_name'],  # 用户名称
        "fullName": "dolphinscheduler/" + basic_json['user_name'] + "/resources" + dolphin_scheduler_file_path
        # 文件在 DolphinScheduler 中的完整路径
    }

    # 发送 PUT 请求，更新 DolphinScheduler 中的文件内容
    # - url: API 地址
    # - headers: 请求头，包含认证信息
    # - data: 请求数据，包含文件内容和路径信息
    r = requests.put(url=URL, headers=headers, data=data)

    # 打印 API 响应内容，通常包含更新结果信息
    print(r.text)


# 将本地文件上传到 DolphinScheduler 的资源目录中
def upload_dolphinscheduler_file(basic_json, local_file_path, file_name, dolphin_scheduler_file_path):
    """
    参数:
    - basic_json (dict): 包含用户认证信息的字典，必须包含 'token' 和 'user_name' 字段。
    - local_file_path (str): 本地文件的路径。
    - file_name (str): 上传到 DolphinScheduler 后的文件名。
    - dolphin_scheduler_file_path (str): 文件在 DolphinScheduler 中的目标路径（相对路径）。
    """

    # DolphinScheduler 的 API 地址
    API_URL = "http://192.168.98.21:12345/cqvip/resources"

    # 设置请求头，包含认证 token
    headers = {
        "token": basic_json['token'],
    }

    # 准备请求数据，包含文件类型、文件名、描述和目标路径
    data = {
        "type": "FILE",  # 文件类型
        "name": file_name,  # 上传后的文件名
        "description": "undefined",  # 文件描述（此处为默认值）
        "currentDir": "dolphinscheduler/" + basic_json['user_name'] + "/resources" + dolphin_scheduler_file_path  # 目标路径
    }

    # 发送 POST 请求，上传文件
    # - url: API 地址
    # - headers: 请求头，包含认证信息
    # - files: 上传的文件内容，以二进制形式读取本地文件
    # - params: 其他请求参数，包含文件信息和目标路径
    r = requests.post(url=API_URL, headers=headers, files={'file': open(local_file_path, 'rb')}, params=data)

    # 打印 API 响应内容，通常包含上传结果信息
    print(r.text)

