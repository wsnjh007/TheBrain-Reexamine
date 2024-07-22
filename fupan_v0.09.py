#!/usr/bin/env python3
"""
版本更新日志:
v0.01: 初始版本，包含基础的API请求和处理逻辑。
v0.02: 添加了通过startTime和endTime进行查询的功能，确保查询的内容为两次复盘之间修改的。
v0.03: 修复了时区问题，确保查询时间为UTC时间。
v0.04: 美化输出结果，并添加修改时间信息。
v0.05: 查询需要添加父节点的ThoughtID的名称信息，并在恰当的地方进行输出。
v0.06: 修改逻辑为使用syncUpdateDateTime进行查询，并输出详细信息。
v0.07: 查询后，响应内容中'modType': 803的ThoughtID选择extraAId，否则ThoughtID选择sourceId。
v0.08: 新增功能，增加'modType'字典的内容输出，并处理log.txt不存在的情况。
v0.09: 删除'modType'为102的ThoughtID，并去重处理重复的ThoughtID。
"""

import requests
from datetime import datetime
import pytz
import os

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
brain_id = '脑图ID'  # 确保这个ID是正确的
new_parent_id = '复盘节点的ID'  # 要添加的父节点ID

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
    401: "厚度改变",
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
    804: "已删除的票据资产",
    805: "创建票据资产",
    806: "更改票据资产",
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

def get_current_utc_time():
    """获取当前UTC时间"""
    return datetime.utcnow()

def get_utc_time(dt):
    """将本地时间转换为UTC时间"""
    local_tz = pytz.timezone('Asia/Shanghai')  # 替换为你的本地时区
    local_dt = local_tz.localize(dt, is_dst=None)
    return local_dt.astimezone(pytz.utc)

def read_last_run_time(log_file='log.txt'):
    """读取上次运行的时间"""
    if not os.path.exists(log_file):
        return None
    with open(log_file, 'r') as f:
        last_run_time_str = f.readline().strip().replace('运行时间：', '')
        last_run_time = datetime.strptime(last_run_time_str, '%Y-%m-%d %H:%M:%S')
        return get_utc_time(last_run_time)

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

def add_parent(brain_id, child_id, parent_id, modification_time, thought_name, mod_type):
    """为指定的子节点添加一个父节点"""
    url = f'{base_url}/links/{brain_id}'
    payload = {
        'thoughtIdA': parent_id,
        'thoughtIdB': child_id,
        'relation': 1  # 关系类型：1代表父节点关系
    }
    mod_type_str = mod_type_dict.get(mod_type, "未知操作")
    print(f'添加父节点请求数据: ThoughtID: {child_id} (名称: {thought_name}) 父节点ID: {parent_id} 修改时间: {modification_time} 操作类型: {mod_type_str}')
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

def write_log():
    """写入日志文件"""
    log_file = 'log.txt'
    with open(log_file, 'w') as f:
        f.write(f'运行时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    print(f'日志已写入：{log_file}')

# 主执行逻辑
last_run_time = read_last_run_time()
if not last_run_time:
    # 如果没有上次运行时间，默认从当天零点开始
    start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
else:
    start_time = last_run_time
end_time = get_current_utc_time()

params = {
    'startTime': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    'endTime': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
    'maxLogs': 100
}

# 获取修改日志
modifications = get_modifications(brain_id, params)

# 如果有修改日志，提取并打印所有的ThoughtID，排除已删除的ID和linkId
if modifications:
    thought_ids = set()
    for log in modifications:
        if log['modType'] == 102:  # 跳过已删除的ThoughtID
            continue
        sync_update_time = log.get('syncUpdateDateTime', '未知时间')
        thought_id = log['extraAId'] if log['modType'] == 803 else log['sourceId']
        thought_ids.add((thought_id, sync_update_time, log['modType']))
    
    for thought_id, modification_time, mod_type in thought_ids:
        thought_name = get_thought_name(brain_id, thought_id)
        print(f'添加父节点请求数据: ThoughtID: {thought_id} (名称: {thought_name}) 父节点ID: {new_parent_id} 修改时间: {modification_time} 操作类型: {mod_type_dict.get(mod_type, "未知操作")}')
        result = add_parent(brain_id, thought_id, new_parent_id, modification_time, thought_name, mod_type)
        if result:
            print(f"成功为 ThoughtID {thought_id} (名称: {thought_name}) 添加父节点 {new_parent_id}")
        else:
            print(f"为 ThoughtID {thought_id} (名称: {thought_name}) 添加父节点 {new_parent_id} 失败")
else:
    print("未找到任何修改日志")

# 写入日志文件
write_log()
