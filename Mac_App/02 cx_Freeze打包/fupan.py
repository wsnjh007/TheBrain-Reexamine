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
v0.14: 恢复逻辑为使用modificationDateTime进行查询，同时恢复排除sourceType = 3的ID（为LinkID）
v0.15: 添加功能，只为自定义的typeId（即指定的类型）执行特定功能
v0.15: 引入缓存机制、减少API请求次数、提高排序效率、提升递归调用效率等，用以提供代码效率和稳定性
v0.16: 将fupan.py和anki.py中所有需要配置的参数统一归类
"""
import warnings
warnings.filterwarnings("ignore", message=".*LibreSSL.*")

import requests
from config import api_key, brain_id, review_id, allowed_type_ids, excluded_mod_types, base_url
from datetime import datetime, timedelta, timezone
import pytz
from functools import lru_cache
from pathlib import Path
import os

# 获取用户的主目录路径
user_home = os.path.expanduser("~")  # 使用 expanduser 来确保获取正确的用户主目录

# 确保路径处理正确，即使路径中含有空格
app_data_dir = os.path.abspath(os.path.join(user_home, "Documents", "TbReview"))  # 指定应用程序的文件夹

# 如果文件夹不存在，创建文件夹
if not os.path.exists(app_data_dir):
    os.makedirs(app_data_dir)

# 将 review_time.txt 文件保存到该文件夹中
review_time_path = os.path.join(app_data_dir, 'review_time.txt')

# 配置部分
# api_key：TheBrain的API密钥
# brain_id：TheBrain的Brain ID
# review_id：要添加的父节点ID，即「回顾」节点
# base_url：TheBrain API的基本URL

# 自定义允许的typeIds，请替换为实际的typeId「洞见卡片」和「原则卡片」
# allowed_type_ids：类型为「洞见卡片」和「原则卡片」ID

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
    401: "改变连线粗细",
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
# excluded_mod_types：需要去除的thought更新类型，如：102'已删除'、301'忘记'

# 设置API访问的headers，包括认证信息和模拟浏览器的缓存控制
headers = {
    'Authorization': f'Bearer {api_key}',  # 认证信息 Your_api_key替换成自己的
    'Cache-Control': 'no-cache, no-store, must-revalidate',  # 指示不使用缓存
    'Pragma': 'no-cache',  # 同样指示不使用缓存
    'Expires': '0',  # 设置内容过期时间为0
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',  # 模拟浏览器的用户代理
    'Accept': 'application/json',  # 接受的内容类型
    'Accept-Language': 'en-US,en;q=0.5',  # 接受的语言
    'Connection': 'keep-alive'  # 保持连接
}

def get_current_utc_time():
    """获取当前UTC时间"""
    return datetime.now(timezone.utc)

def get_utc_time(dt):
    """将本地时间转换为UTC时间"""
    local_tz = pytz.timezone('Asia/Shanghai')  # 替换为你的本地时区
    local_dt = local_tz.localize(dt, is_dst=None)
    return local_dt.astimezone(pytz.utc)

def get_latest_modification_datetime(brain_id, review_id):
    """
    使用新的API查询方式获取指定思维节点的最新modificationDateTime。
    参数:
    brain_id: 脑图ID
    review_id: 思维节点ID
    """
    url = f'{base_url}/thoughts/{brain_id}/{review_id}/modifications?maxLogs=1&includeRelatedLogs=true'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        modifications = response.json()
        if modifications:
            modification_datetime = modifications[0].get('modificationDateTime')
            if modification_datetime:
                print(f'「上次回顾时间」：{modification_datetime}', flush=True)
                return modification_datetime + 'Z'  # 添加 'Z' 表示 UTC 时间
        return None
    except requests.RequestException as e:
        print(f'请求错误：{e}', flush=True)
        return None

def get_modifications(brain_id, start_time, end_time):
    """使用新的API查询方式获取指定时间段内的所有修改日志"""
    url = f'{base_url}/brains/{brain_id}/modifications?maxLogs=100&startTime={start_time}&endTime={end_time}'
    print(f'GET请求URL: {url}', flush=True)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f'响应内容: {response.json()}\n', flush=True)
        return response.json()
    except requests.HTTPError as e:
        print(f'HTTP错误：{e}', flush=True)
        if response.status_code == 401:
            print("401错误：认证失败，请检查API密钥。", flush=True)
        elif response.status_code == 403:
            print("403错误：可能是权限问题，请检查API密钥和权限。", flush=True)
        elif response.status_code == 404:
            print(f"404错误：资源未找到，URL可能错误或资源不存在。请求的URL: {url}", flush=True)
        return None
    except requests.RequestException as e:
        print(f'请求错误：{e}', flush=True)
        return None

@lru_cache(maxsize=None)
def get_thought_name(brain_id, thought_id):
    """获取指定思维节点的名称，仅当节点的typeId在允许的列表中时"""
    url = f'{base_url}/thoughts/{brain_id}/{thought_id}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if str(data.get('typeId')) in allowed_type_ids:
            return data.get('name', '未知名称')
    return None  # 如果不在允许的列表中，不返回名称

def add_parent(brain_id, child_id, review_id, modification_time, thought_name):
    """为指定的子节点添加一个父节点，仅当节点的typeId在允许的列表中时"""
    if thought_name:  # 如果名称存在，表示typeId符合条件
        url = f'{base_url}/links/{brain_id}'
        payload = {
            'thoughtIdA': review_id,
            'thoughtIdB': child_id,
            'relation': 1  # 关系类型：1代表父节点关系
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': '添加父节点失败', 'statusCode': response.status_code}
    else:
        return {'error': '不符合typeId条件，未添加'}

# 获取思维图的Graph数据，并缓存
@lru_cache(maxsize=None)
def get_graph_data(review_id):
    """通过API获取Graph数据，并缓存结果"""
    url = f'{base_url}/thoughts/{brain_id}/{review_id}/graph?includeSiblings=false'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# 主执行逻辑
# 获取最新的修改时间
start_time_str = get_latest_modification_datetime(brain_id, review_id)
if start_time_str:
    # 处理时间字符串，截取微秒部分，去掉纳秒
    if '.' in start_time_str:
        start_time_str = start_time_str[:start_time_str.index('Z')]  # 去掉 'Z'
        if len(start_time_str.split('.')[-1]) > 6:  # 如果小数部分长度大于6（即纳秒级）
            start_time_str = start_time_str[:start_time_str.index('.') + 7]  # 只保留微秒部分
    
    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%f')  # 解析时间
    start_time = start_time.replace(tzinfo=timezone.utc)  # 确保时间是UTC
else:
    # 如果没有修改时间，则设置为当天的 00:00:00 UTC
    start_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

# 增加1秒，以避免重复获取相同的修改日志
start_time += timedelta(seconds=1)

# 获取当前UTC时间
end_time = get_current_utc_time()

# 格式化为字符串
start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# 获取修改日志
modifications = get_modifications(brain_id, start_time_str, end_time_str)

# 如果有修改日志，提取并打印所有的ThoughtID，排除已删除的ID和linkId，并去重
if modifications:
    thought_ids = {}
    for log in modifications:
        # 同时满足 sourceType 不为 3 和 modType 不在 excluded_mod_types 里
        if log['sourceType'] != 3 and log['modType'] not in excluded_mod_types:
            # 在这里添加多个数值，形成“或”的关系，例如803, 804, 805
            if log['modType'] in [801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 900, 901, 902, 903]:
                thought_id = log.get('extraAId')
            else:
                thought_id = log.get('sourceId')

            modification_time = log.get('modificationDateTime', '未知时间')
            thought_ids[thought_id] = (modification_time, log['modType'])

    for thought_id, (modification_time, mod_type) in thought_ids.items():
        thought_name = get_thought_name(brain_id, thought_id)
        # 如果 thought_name 为 None，跳过这个 thought_id
        if thought_name is None:
            continue
        mod_type_desc = mod_type_dict.get(mod_type, "未知操作")
        print(f'添加父节点请求数据: ThoughtID: {thought_id} (名称: {thought_name}) 父节点ID: {review_id} 修改时间: {modification_time} 操作类型: {mod_type_desc}', flush=True)
        result = add_parent(brain_id, thought_id, review_id, modification_time, thought_name)
        if result:
            print(f"成功为 ThoughtID {thought_id} (名称: {thought_name}) 添加父节点 {review_id}\n", flush=True)
        else:
            print(f"为 ThoughtID {thought_id} (名称: {thought_name}) 添加父节点 {review_id} 失败\n", flush=True)
else:
    print("未找到任何修改日志\n", flush=True)

# 获取review_time数据，并写入review_time.txt
review_time = get_current_utc_time()  # 获取当前UTC时间
review_time += timedelta(seconds=1)  # 加1秒
if review_time:
    with open(review_time_path, 'w') as file:
        file.write(str(review_time))  # 写入文件
    print("review_time数据已成功写入review_time.txt\n", flush=True)
else:
    print("未能获取review_time数据\n", flush=True)
