#!/usr/bin/env python3
"""
版本更新日志:
v0.01: 初始版本，包含基础的API请求和处理逻辑。
v0.02: 目前只支持本地通过AnkiConnect插件进行卡片创建
v0.03: 添加[To TheBrain]的本地路径连接，但是碰到编码问题，还在解决，已反馈官方
v0.04: 支持「洞见卡片」卡片下面还有「洞见卡片」
v0.05: 优化TB中.1、.1.1、.1.2之类在anki中的排序问题，并优化anki有序列表和无须列表显示效果
V0.06: 启用重复检测功能，检查卡片是否已存在，如果已存在则完全删除后重新建卡，保证卡片的内容最新
V0.07: 引入缓存机制、减少API请求次数、提高排序效率、提升递归调用效率等，用以提供代码效率和稳定性
V0.08: 将fupan.py和anki.py中所有需要配置的参数统一归类
"""

import requests
from config import api_key, brain_id, review_id, question_id, up_id, solutions_id, base_url
import re
from bs4 import BeautifulSoup
from functools import lru_cache  # 引入LRU缓存机制
import os
from datetime import datetime, timezone
from pathlib import Path
import base64
import uuid

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
# base_url：TheBrain API的基本URL
anki_connect_url = "http://localhost:8765"  # 替换为您的AnkiConnect API地址

# 其他节点配置
# review_id：要添加的父节点ID，即「回顾」节点
# question_id：「问题卡片」类型ID
# up_id：「精进域」类型ID
# solutions_id：即洞见类型卡片ID，例如「洞见卡片」、「原则卡片」

def get_start_time_from_file():
    """从review_time.txt文件中读取start_time数据"""
    try:
        with open(review_time_path, 'r') as file:
            start_time = file.read().strip()  # 只去掉换行符和前后空白字符
            if start_time:
                return start_time  # 直接返回字符串内容
            else:
                print("review_time.txt文件为空\n", flush=True)
                return None
    except FileNotFoundError:
        print("未找到review_time.txt文件\n", flush=True)
        return None
    except SyntaxError:
        print("文件内容格式有误\n", flush=True)
        return None

def clear_review_graph():
    """清空review_time.txt文件的内容"""
    with open(review_time_path, 'w') as file:
        file.truncate(0)  # 确保文件被清空
    print("\n成功清空review_time.txt文件", flush=True)

# 对API请求的结果进行缓存，减少重复请求
@lru_cache(maxsize=None)
def get_graph_data(review_id):
    url = f'https://api.bra.in/thoughts/{brain_id}/{review_id}/graph?includeSiblings=false'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def custom_sort_key(x):
    """自定义排序规则，确保根据特定数字序列优先排序，其他按字典序排序"""
    # 提取数字序列，例如从“.1.1.2”得到元组(1, 1, 2)
    digits = re.findall(r'\.(\d+)', x['name'])
    if digits:
        # 如果存在数字序列，将其转换为整数元组，并确保较短的序列在前
        return (0,) + tuple(int(num) for num in digits) + (float('inf'),) * (3 - len(digits))
    # 对于不包含数字序列的名称，按照字典序排在所有数字序列之后
    return (1, x['name'])

def get_modifications(brain_id, start_time_str):
    """使用新的API查询方式获取指定时间段内的所有修改日志"""
    
    url = f'{base_url}/brains/{brain_id}/modifications?maxLogs=100&startTime={start_time_str}'
    print(f'GET请求URL: {url}', flush=True)

    # 定义 headers，包含 API 密钥
    headers = {'Authorization': f'Bearer {api_key}'}
    
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

def get_insights_ids(brain_id, start_time_str):
    """获取修改后的「洞见卡片」和「原则卡片」的ID，并打印节点详细信息"""
    insights_data = get_modifications(brain_id, start_time_str)
    
    if insights_data:
        matching_extra_b_ids = []
        # 遍历获取的数据，筛选出符合条件的记录
        for record in insights_data:
            if (record.get('sourceType') == 3 and
                record.get('extraAId') == "8591cfa3-3ef7-40a1-9d57-f5001a0a06aa" and
                record.get('extraAType') == 2 and
                record.get('extraBType') == 2 and
                record.get('modType') == 102):
                
                extra_b_id = record.get('extraBId')
                if extra_b_id:
                    matching_extra_b_ids.append(extra_b_id)

        # 获取 activeThought 的 ID 列表
        active_thought_ids = []
        print("已回顾的「洞见卡片」和「原则卡片」详情:", flush=True)
        for extra_b_id in matching_extra_b_ids:
            thought_data = get_graph_data(extra_b_id)
            if thought_data:
                active_thought = thought_data.get('activeThought', {})
                if active_thought:
                    print(f"ID: {active_thought['id']}, Name: {active_thought['name']}, CleanedUpName: {active_thought['cleanedUpName']}", flush=True)
                    active_thought_ids.append(active_thought['id'])  # 提取 activeThought ID
                else:
                    print(f"未找到ID为 {extra_b_id} 的 activeThought 数据", flush=True)
            else:
                print(f"未找到ID为 {extra_b_id} 的节点数据", flush=True)
        print("", flush=True)  # 输出空行
        return active_thought_ids  # 返回 activeThought 的 ID 列表
    else:
        print(f"请求失败或数据为空", flush=True)
        print("", flush=True)  # 输出空行
        return []

def get_parents_by_type(brain_id, child_ids):
    """递归查找父节点，直到找到符合typeId的父节点，并去重"""
    parents_info = {}
    def recursive_search_parent(child_id):
        """递归查找符合typeId的父节点"""
        data = get_graph_data(child_id)
        if data:
            parents = data.get('parents', [])
            for parent in parents:
                # 查找类型为「问题卡片」的父节点
                if parent.get('typeId') == question_id:
                    if parent['id'] not in parents_info:
                        parents_info[parent['id']] = parent['cleanedUpName']
                        print(f"ID: {parent['id']}, CleanedUpName: {parent['cleanedUpName']}", flush=True)
                else:
                    # 递归查找上级节点
                    recursive_search_parent(parent['id'])

    # 对所有子节点进行递归父节点查找
    for child_id in child_ids:
        recursive_search_parent(child_id)

    return list(parents_info.keys()), list(parents_info.values())

def get_recursive_parents(brain_id, initial_parent_ids, type_id=up_id):
    """递归查询特定typeId（即类型为「精进域」）的父节点，并聚合每个起始父节点的cleanedUpName"""
    all_parents = {}
    for parent_id in initial_parent_ids:
        all_parents[parent_id] = []
        recursive_parents_search(brain_id, [parent_id], type_id, all_parents[parent_id])
    return all_parents

def recursive_parents_search(brain_id, current_parents, type_id, parent_names):
    """实际执行递归查询的函数，聚合cleanedUpName"""
    new_parents = []
    for parent_id in current_parents:
        data = get_graph_data(parent_id)
        if data:
            parents = data.get('parents', [])
            for parent in parents:
                if parent.get('typeId') == type_id:
                    parent_names.append(parent['cleanedUpName'])
                    new_parents.append(parent['id'])

    if new_parents:
        recursive_parents_search(brain_id, new_parents, type_id, parent_names)

def to_short_guid(guid_str):
    """
    将标准的 GUID 转换为缩短的 Base64 GUID
    """
    guid = uuid.UUID(guid_str)  # 将 GUID 字符串转换为 UUID 对象
    guid_bytes = guid.bytes_le  # 获取字节数组，按小端序排列（模拟 C# 的 ToByteArray() 方法）
    
    short_guid = base64.urlsafe_b64encode(guid_bytes).decode('utf-8').rstrip('=')  # 将字节数组转换为 Base64 字符串，并移除填充字符
    return short_guid  # 返回缩短后的 GUID 字符串

def generate_brain_local_path(brain_id, parent_id, cleaned_name):
    """生成 TheBrain 本地路径"""
    brain_id_short = to_short_guid(brain_id)  # 将 brain_id 转换为缩短后的 GUID
    parent_id_short = to_short_guid(parent_id)  # 将 parent_id 转换为缩短后的 GUID
    base_url = f"brain://api.thebrain.com/{brain_id_short}/{parent_id_short}"
    cleaned_name_encoded = requests.utils.quote(cleaned_name)
    return f"{base_url}/{cleaned_name_encoded}"

def check_and_create_deck(deck_name):
    """检查并创建指定的牌组"""
    data = {
        "action": "deckNames",
        "version": 6
    }
    response = requests.post(anki_connect_url, json=data)
    if response.status_code == 200:
        decks = response.json().get("result", [])
        if deck_name not in decks:
            create_deck_data = {
                "action": "createDeck",
                "version": 6,
                "params": {
                    "deck": deck_name
                }
            }
            create_response = requests.post(anki_connect_url, json=create_deck_data)
            if create_response.status_code == 200 and create_response.json().get("error") is None:
                print(f"牌组 '{deck_name}' 已成功创建", flush=True)
            else:
                print(f"创建牌组失败：{create_response.json().get('error')}", flush=True)
        else:
            print(f"牌组 '{deck_name}' 已存在", flush=True)
    else:
        print(f"获取牌组列表失败，状态码：{response.status_code}", flush=True)

def get_model_name():
    """获取Anki模型名称，默认返回第一个模型或'Basic'"""
    data = {
        "action": "modelNames",
        "version": 6
    }
    response = requests.post(anki_connect_url, json=data)
    if response.status_code == 200:
        models = response.json().get("result", [])
        if models:
            return models[0]  # 使用第一个模型
        else:
            print("未找到任何模型", flush=True)
            return "Basic"  # 如果没有模型，返回默认值
    else:
        print(f"获取模型名称失败，状态码：{response.status_code}", flush=True)
        return "Basic"

def format_and_send_to_anki(all_parents, cleaned_up_names, brain_id, parent_ids):
    """格式化并发送至Anki，同时获取和排序子节点"""
    def recursive_get_children(parent_id, level=0):
        """递归查找子节点，并按层级格式化添加到列表，使用HTML列表标签"""
        if level == 0:
            content_list = [f"<ol class='level-{level}'>"]
        else:
            content_list = [f"<ul class='level-{level}'>"]

        data = get_graph_data(parent_id)
        if data:
            children = data.get('children', [])
            sorted_children = sorted(children, key=custom_sort_key)

            for i, child in enumerate(sorted_children):
                # 检查 typeId 是否存在，然后查找类型为「洞见卡片」或「原则」卡片的子节点
                if 'typeId' in child and child['typeId'] in solutions_id:
                    child_entry = f"<li>{child['cleanedUpName']}</li>"
                    content_list.append(child_entry)
                    # 递归获取子节点内容，增加级别
                    subchildren_content = recursive_get_children(child['id'], level + 1)
                    if subchildren_content:
                        content_list.append(subchildren_content)

        if level == 0:
            content_list.append("</ol>")  # 结束有序列表
        else:
            content_list.append("</ul>")  # 结束无序列表

        return "".join(content_list)  # 返回HTML格式的字符串

    for parent_id in parent_ids:
        if cleaned_up_names:
            parent_cleaned_name = cleaned_up_names.pop(0)
            brain_local_path = generate_brain_local_path(brain_id, parent_id, parent_cleaned_name)
            front_side = f"<strong>{parent_cleaned_name}</strong> <a href='{brain_local_path}' style='font-weight:bold'>[To TheBrain]</a>"
            back_side = recursive_get_children(parent_id)  # 获取并格式化子节点内容为卡片背面
            
            sorted_names = sorted(all_parents[parent_id], reverse=True)
            deck_name = "::".join(sorted_names)  # 使用 '::' 连接成Anki牌组名
            
            # 打印即将发送的信息
            print(f"Deck Name: {deck_name}", flush=True)
            print(f"Front Side: {front_side}", flush=True)
            print(f"Back Side: {back_side}", flush=True)

            # 检查并创建牌组
            check_and_create_deck(deck_name)
            
            # 获取模型名称并发送到Anki
            model_name = get_model_name()
            send_to_anki(deck_name, front_side, back_side, model_name)
        else:
            print("Error: No more parent names available to process.", flush=True)

def clean_front_content(front):
    """去除HTML标签并删除' [To TheBrain]'文本"""
    soup = BeautifulSoup(front, 'html.parser')
    front_text = soup.get_text().strip()
    # 删除' [To TheBrain]'文本
    front_text = re.sub(r'\s*\[To TheBrain\]', '', front_text)
    return front_text

def send_to_anki(deck_name, front, back, model_name):
    """通过AnkiConnect将卡片发送至Anki"""
    
    # 提取并清理Front内容
    clean_front_text = clean_front_content(front)
    
    # 查找相同的卡片并删除
    find_and_delete_notes(deck_name, clean_front_text)
    
    # 添加新的卡片
    add_note_to_anki(deck_name, front, back, model_name)

def find_and_delete_notes(deck_name, front_text):
    """查找并删除相同的Anki卡片"""
    check_note_data = {
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": f'deck:"{deck_name}"'
        }
    }
    response = requests.post(anki_connect_url, json=check_note_data)
    if response.status_code == 200:
        notes = response.json().get("result", [])
        if notes:
            for note_id in notes:
                delete_note_if_duplicate(note_id, front_text)

def delete_note_if_duplicate(note_id, front_text):
    """如果卡片内容相同，删除卡片"""
    get_note_data = {
        "action": "notesInfo",
        "version": 6,
        "params": {
            "notes": [note_id]
        }
    }
    note_response = requests.post(anki_connect_url, json=get_note_data)
    if note_response.status_code == 200:
        note_info = note_response.json().get("result", [])[0]
        anki_front = clean_front_content(note_info['fields']['Front']['value'])
        if anki_front == front_text:
            delete_note_data = {
                "action": "deleteNotes",
                "version": 6,
                "params": {
                    "notes": [note_id]
                }
            }
            delete_response = requests.post(anki_connect_url, json=delete_note_data)
            if delete_response.status_code == 200:
                print(f"旧卡片已删除: {anki_front}", flush=True)

def add_note_to_anki(deck_name, front, back, model_name):
    """添加新的Anki卡片"""
    data = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": {
                    "Front": front,
                    "Back": back
                },
                "options": {
                    "allowDuplicate": False
                },
                "tags": []
            }
        }
    }
    response = requests.post(anki_connect_url, json=data)
    if response.status_code == 200:
        print(f"成功发送至Anki: {deck_name}\n", flush=True)
    else:
        print(f"发送至Anki失败，状态码：{response.status_code}\n", flush=True)

# 主函数调用
def main():
    # 获取「回顾」节点的修改时间为start_time时间
    start_time_str = get_start_time_from_file()  # 获取字符串形式的 start_time

    # 打印读取的时间字符串，排查问题
    print(f"本次「回顾」开始时间: {start_time_str}", flush=True)
    
    # 检查 start_time_str 是否有效，并解析为 datetime 对象
    if start_time_str:
        try:
            # 将字符串解析为 datetime 对象，匹配 "2024-09-06 07:43:27.736259+00:00" 格式
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f%z')
        except ValueError as e:
            print(f"时间字符串格式无效，无法解析: {e}", flush=True)
            return
    else:
        # 如果没有修改时间，则设置为当天的 00:00:00 UTC
        start_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # 格式化为字符串
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    # 获取子节点信息
    insights_ids = get_insights_ids(brain_id, start_time_str)
    
    print(f"对应的「问题卡片」详情：", flush=True)
    # 获取父节点信息及其cleanedUpName
    parent_ids, cleaned_up_names = get_parents_by_type(brain_id, insights_ids)
    
    # 递归获取父节点详情
    advanced_parents = get_recursive_parents(brain_id, parent_ids)
    
    print(f"\n创建并发送卡片至Anki：", flush=True)
    # 格式化并发送最终结果至Flomo，包括获取子节点详情
    format_and_send_to_anki(advanced_parents, cleaned_up_names, brain_id, parent_ids)

    # 在所有卡片处理完成后，清空 review_time.txt。后来决定不清空，防止一次没复盘完毕，时间被误删了
    # clear_review_graph()

if __name__ == '__main__':
    main()
