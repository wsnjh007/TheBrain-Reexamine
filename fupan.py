#!/usr/bin/env python3
"""
版本更新日志:
v0.01: 初始版本，包含基础的API请求和处理逻辑。
v0.02: 添加了通过startTime和endTime进行查询的功能，确保查询的内容为两次复盘之间修改的。
v0.03: 修复了时区问题，确保查询时间为UTC时间。
v0.04: 美化输出结果，并添加修改时间信息。
v0.05: 查询需要添加父节点的ThoughtID的名称信息，并在恰当的地方进行输出。
v0.06: 修改逻辑为使用syncUpdateDateTime进行查询，并输出详细信息。
v0.07: 如果初始运行时没有log.txt文档，则默认startTime=当天的00:00:00。
v0.08: 根据'modType'数值的字典，在“添加父节点请求数据”的内容中输出对应的内容。
v0.09: 去除modType为102的ThoughtID，并去重。
v0.10: 去除modType为301的ThoughtID，并处理缺失syncUpdateDateTime的情况。
v0.11: 自定义配置需要去除的modType。
v0.12: 查询「复盘」节点的最新修改（断开连接）时间为startTime，后来在这基础上+1秒，避免断开的节点下次复盘时重新出现。
v0.13: 添加查询「复盘」节点修改记录的自定义查询时间区间。默认为1天，减轻历史日志多了之后的计算压力
"""

import requests
from datetime import datetime, timedelta
import pytz

# 自定义时间区间配置，用于指定查询修改日志的时间跨度。需要在「def get_latest_modification_datetime」模块中设置time_span值
time_config = {
    'day': 1,    # 1天
    'week': 7,   # 1周
    'month': 30, # 1月
    'custom': 14 # 自定义14天
}

# 定义modType的字典，包括各类型操作的描述
mod_type_dict = {
    101: "创建",
    102: "已删除",
    103: "更改名称",
    104: "由粘贴创建",
    105: "由粘贴修改",
    201: "改变颜色",
    202: "更改标签",
    203: "设置类型",
    204: "更改颜色2",
    205: "创建图标",
    206: "已删除的图标",
    207: "更改图标",
    208: "更改了字段实例",
    209: "创建字段实例",
    210: "已删除的字段实例",
    301: "忘记",
    302: "记住",
    303: "更改了思想访问类型",
    304: "改变种类",
    401: "改变连线厚度",
    402: "移动链接",
    403: "改变方向",
    404: "更改了含义",
    405: "关系发生了变化",
    501: "内容已更改",
    502: "更改位置",
    503: "改变位置",
    601: "更改设置",
    602: "重新排序的别针",
    701: "更改了大脑访问条目",
    801: "创建注释",
    802: "删除的注释",
    803: "更改注释",
    804: "删除笔记资产",
    805: "创建笔记资产",
    806: "更改笔记资产",
    807: "删除的Markdown图像",
    808: "创建Markdown图像",
    809: "更改了Markdown图像",
    810: "已删除的动态壁纸图像",
    811: "创建动态壁纸图像",
    812: "更改了动态壁纸图像",
    900: "创建日历事件",
    901: "修改日历事件",
    902: "已删除的日历事件",
    903: "删除的日历事件循环实例",
    1001: "更改字段定义",
    1002: "创建字段定义",
    1003: "删除字段定义"
}

# 自定义需要去除的modType
excluded_mod_types = [102, 301]

# 定义API的基本URL
base_url = 'https://api.bra.in'

# 设置API访问的headers，包括认证信息和模拟浏览器的缓存控制
headers = {
    'Authorization': 'Bearer 你的key',  # 认证信息，“你的key”这个字段替换成你的API key
    'Cache-Control': 'no-cache, no-store, must-revalidate',  # 指示不使用缓存
    'Pragma': 'no-cache',  # 同样指示不使用缓存
    'Expires': '0',  # 设置内容过期时间为0
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',  # 模拟浏览器的用户代理
    'Accept': 'application/json',  # 接受的内容类型
    'Accept-Language': 'en-US,en;q=0.5',  # 接受的语言
    'Connection': 'keep-alive'  # 保持连接
}

# 定义相关ID
brain_id = '脑图ID'  # “脑图ID”进行替换，确保这个ID是正确的
new_parent_id = '复盘节点的ID'  # “复盘节点的ID”进行替换，要添加的父节点ID

def get_current_utc_time():
    """获取当前UTC时间"""
    return datetime.utcnow()

def get_utc_time(dt):
    """将本地时间转换为UTC时间"""
    local_tz = pytz.timezone('Asia/Shanghai')  # 替换为你的本地时区
    local_dt = local_tz.localize(dt, is_dst=None)
    return local_dt.astimezone(pytz.utc)

def get_latest_modification_datetime(brain_id, thought_id, time_span='day'):
    """
    获取指定思维节点的最新modificationDateTime，可以自定义查询的时间区间。
    参数:
    brain_id: 脑图ID
    thought_id: 思维节点ID
    time_span: 时间跨度配置，可选'day', 'week', 'month', 'custom'
    """
    end_time = get_current_utc_time()  # 获取当前时间
    start_time = end_time - timedelta(days=time_config[time_span])  # 根据配置计算起始时间

    url = f'{base_url}/brains/{brain_id}/modifications'
    params = {
        'startTime': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'endTime': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'maxLogs': 100
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        modifications = response.json()
        latest_modification_datetime = None
        for log in modifications:
            if log.get('extraAId') == thought_id and log['modType'] == 102:
                modification_datetime = log.get('modificationDateTime', None)
                if modification_datetime:
                    modification_datetime += 'Z'
                    if latest_modification_datetime is None or modification_datetime > latest_modification_datetime:
                        latest_modification_datetime = modification_datetime
        return latest_modification_datetime
    except requests.HTTPError as e:
        print(f'HTTP错误：{e}')
        return None
    except requests.RequestException as e:
        print(f'请求错误：{e}')
        return None

def get_modifications(brain_id, params):
    """获取指定时间段内的所有修改日志"""
    url = f'{base_url}/brains/{brain_id}/modifications'
    print(f'GET请求URL: {url}')
    print(f'startTime: {params["startTime"]}')
    print(f'endTime: {params["endTime"]}')
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        print(f'响应内容: {response.json()}')
        return response.json()
    except requests.HTTPError as e:
        print(f'HTTP错误：{e}')
        if response.status_code == 401:
            print("401错误：认证失败，请检查API密钥。")
        elif response.status_code == 403:
            print("403错误：可能是权限问题，请检查API密钥和权限。")
        elif response.status_code == 404:
            print(f"404错误：资源未找到，URL可能错误或资源不存在。请求的URL: {url}")
        return None
    except requests.RequestException as e:
        print(f'请求错误：{e}')
        return None

def get_thought_name(brain_id, thought_id):
    """获取指定思维节点的名称"""
    url = f'{base_url}/thoughts/{brain_id}/{thought_id}'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('name', '未知名称')
    except requests.HTTPError as e:
        print(f'HTTP错误：{e}')
        return '未知名称'
    except requests.RequestException as e:
        print(f'请求错误：{e}')
        return '未知名称'

def add_parent(brain_id, child_id, parent_id, modification_time, thought_name):
    """为指定的子节点添加一个父节点"""
    url = f'{base_url}/links/{brain_id}'
    payload = {
        'thoughtIdA': parent_id,
        'thoughtIdB': child_id,
        'relation': 1  # 关系类型：1代表父节点关系
    }
    print(f'添加父节点请求数据: ThoughtID: {child_id} (名称: {thought_name}) 父节点ID: {parent_id} 修改时间: {modification_time}')
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print(f'HTTP错误：{e}')
        return None
    except requests.RequestException as e:
        print(f'请求错误：{e}')
        return None

# 主执行逻辑
start_time_str = get_latest_modification_datetime(brain_id, new_parent_id, 'day')  # 默认查询1天内的修改日志
if start_time_str:
    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
else:
    start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

start_time += timedelta(seconds=1)  # 增加1秒
end_time = get_current_utc_time()

params = {
    'startTime': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    'endTime': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    'maxLogs': 100
}

# 获取修改日志
modifications = get_modifications(brain_id, params)

# 如果有修改日志，提取并打印所有的ThoughtID，排除已删除的ID和linkId，并去重
if modifications:
    thought_ids = {}
    for log in modifications:
        if log['modType'] == 803:
            thought_id = log.get('extraAId')
        else:
            thought_id = log.get('sourceId')

        if log['modType'] not in excluded_mod_types:
            modification_time = log.get('syncUpdateDateTime', '未知时间')
            thought_ids[thought_id] = (modification_time, log['modType'])

    for thought_id, (modification_time, mod_type) in thought_ids.items():
        thought_name = get_thought_name(brain_id, thought_id)
        mod_type_desc = mod_type_dict.get(mod_type, "未知操作")
        print(f'添加父节点请求数据: ThoughtID: {thought_id} (名称: {thought_name}) 父节点ID: {new_parent_id} 修改时间: {modification_time} 操作类型: {mod_type_desc}')
        result = add_parent(brain_id, thought_id, new_parent_id, modification_time, thought_name)
        if result:
            print(f"成功为 ThoughtID {thought_id} (名称: {thought_name}) 添加父节点 {new_parent_id}")
        else:
            print(f"为 ThoughtID {thought_id} (名称: {thought_name}) 添加父节点 {new_parent_id} 失败")
else:
    print("未找到任何修改日志")
