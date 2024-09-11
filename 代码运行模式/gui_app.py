#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import webbrowser  # 用于打开URL
import re
import certifi
import ssl
import os
# 确保 `requests` 使用正确的 SSL 证书
os.environ['SSL_CERT_FILE'] = certifi.where()

import jaraco.text
import jaraco.context
import jaraco.functools
import more_itertools
from config import card_Nb, thoughts_Nb

# 获取当前脚本的路径
gui_app_path = os.path.dirname(os.path.abspath(__file__))

# 假设 anki.py 和 gui_app.py 在同一目录下
anki_script_path = os.path.join(gui_app_path, 'anki.py')

# 使用 resource_path 获取文件路径
fupan_path = os.path.join(gui_app_path, 'fupan.py')
anki_path = os.path.join(gui_app_path, 'anki.py')
flomo_path = os.path.join(gui_app_path, 'flomo.py')
anki_sync_mac_path = os.path.join(gui_app_path, 'anki_sync_mac.sh')
tb_rul_path = os.path.join(gui_app_path, 'TB_rul.txt')
config_mr_path = os.path.join(gui_app_path, 'config_mr.txt')
config_py_path = os.path.join(gui_app_path, 'config.py')

# 获取「回顾」节点的本地路径
def get_TB_rul():
    try:
        with open(tb_rul_path, 'r') as f:
            content = f.read()
            # 使用正则表达式匹配以 "brain://" 开头的URL
            match = re.search(r'brain://[^\s]+', content)
            if match:
                TB_rul = match.group(0)  # 获取匹配到的URL
            else:
                TB_rul = '没有找到以 brain:// 开头的连接'
    except FileNotFoundError:
        TB_rul = 'TB_rul.txt 文件未找到'
    return TB_rul

def center_window(root, width, height):
    # 获取屏幕宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算居中位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # 设置窗口的尺寸和位置
    root.geometry(f"{width}x{height}+{x}+{y}")

# 更新状态标签和步骤标签的函数
def update_status(step, message):
    step_label.config(text=step, fg="blue")
    status_label.config(text=message, fg="green")
    status_label.update()
    step_label.update()

# 在每个阶段前添加分隔符
def add_separator(output_text, message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    separator = f"\n{'='*15} {timestamp} {message} {'='*15}\n"
    output_text.tag_configure("separator", foreground="blue", justify='center')
    output_text.insert(tk.END, separator, "separator")
    output_text.see(tk.END)
    output_text.update()

# 运行脚本的函数
def run_script(command, output_text, step, message, delay):
    # 更新状态信息并添加分隔符
    update_status(step, message)
    add_separator(output_text, message)

    # 运行脚本并捕获输出
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # 实时显示脚本输出
    for line in iter(process.stdout.readline, ''):
        if line:
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
            output_text.update()

    # 显示错误输出（如果有）
    stderr_output = process.stderr.read()
    if stderr_output:
        output_text.insert(tk.END, stderr_output, "error")
        output_text.see(tk.END)
        output_text.update()

    process.stdout.close()
    process.stderr.close()
    process.wait()

    # 确保脚本运行结束后等待指定时间
    time.sleep(delay)

def start_review():
    # 禁用按钮防止重复点击
    start_button.config(state=tk.DISABLED)
    config_button.config(state=tk.DISABLED)  # 禁用参数设置按钮
    thoughts_combobox.config(state=tk.DISABLED)  # 禁用是思考情况选择框
    mode_combobox.config(state=tk.DISABLED)  # 禁用制卡方式选择框
    progress_bar.start()

    # 在新线程中运行脚本，避免阻塞主线程
    threading.Thread(target=run_scripts_sequence).start()

def check_and_start_anki():
    # 检查 Anki 是否正在运行
    process = subprocess.run("pgrep -x 'anki'", shell=True, stdout=subprocess.PIPE)
    if process.returncode != 0:  # 如果 Anki 没有运行
        update_status("Step 2/3 ", "正在启动 Anki 应用...")
        # 使用 AppleScript 后台启动 Anki
        applescript = """
        tell application "Anki" to launch
        delay 1
        tell application "System Events" to set visible of process "Anki" to false
        """
        subprocess.run(["osascript", "-e", applescript], shell=False)
        time.sleep(2)  # 等待 Anki 启动完成
    else:
        update_status("Step 2/3 ", "Anki 应用已在运行。")
    # 确保窗口隐藏
    applescript_hide = """
    tell application "System Events"
        if exists (process "Anki") then
            set visible of process "Anki" to false
        end if
    end tell
    """
    subprocess.run(["osascript", "-e", applescript_hide], shell=False)

# 弹出窗口函数
def show_popup(title, left_button_text, right_button_text, left_button_command, right_button_command, dismiss_on_left=False):
    popup = tk.Toplevel(root)
    popup.title(title)
    
    label = tk.Label(popup, text="请选择下一步操作:")
    label.pack(pady=10)
    
    button_frame = tk.Frame(popup)
    button_frame.pack(pady=5)
    
    # 左边按钮
    def on_left_click():
        left_button_command()
        if dismiss_on_left:  # 如果左键点击需要关闭窗口
            popup.destroy()

    left_button = tk.Button(button_frame, text=left_button_text, command=on_left_click)
    left_button.pack(side=tk.LEFT, padx=10)
    
    # 右边按钮，如果提供
    if right_button_text and right_button_command:
        def on_right_click():
            popup.destroy()  # 先关闭窗口
            right_button_command()  # 然后继续执行后续操作

        right_button = tk.Button(button_frame, text=right_button_text, command=on_right_click)
        right_button.pack(side=tk.LEFT, padx=10)
    
    popup.geometry("300x100")
    center_window(popup, 300, 100)
    popup.grab_set()  # 禁用其他窗口
    root.wait_window(popup)  # 等待弹出窗口关闭后再继续执行后续代码

def run_scripts_sequence():
    # 获取当前思考情况的选项
    thoughts = thoughts_combobox.get()
    # 获取当前制卡方式的选项
    mode = mode_combobox.get()
    # 获取「回顾」节点的本地路径
    TB_rul = get_TB_rul()

    # 根据选择的思考情况执行不同的流程
    if thoughts == "New Ths":
        # 根据选择的制卡方式执行不同的流程
        if mode == "Anki卡片":
            # 运行 fupan.py
            run_script(f'python3 "{fupan_path}"', output_text, "Step 1/3 ", "正在建立「回顾」节点链接...", 5)

            # 弹出窗口选择
            show_popup(
                "Anki 卡片选项",
                "To TheBrain",
             "创建Anki卡片",
             lambda: webbrowser.open(TB_rul),  # 点击To TheBrain按钮的操作
             lambda: [  # 点击创建Anki卡片按钮的操作
                    # 在运行 anki.py 之前检查 Anki 是否在运行
                    check_and_start_anki(),
                    # 运行 anki.py
                    run_script(f'python3 "{anki_path}"', output_text, "Step 2/3 ", "正在创建Anki卡片...", 5),
                    # 运行 anki_sync_mac.sh
                    run_script(f'sh "{anki_sync_mac_path}"', output_text, "Step 3/3 ", "正在同步Anki卡片...", 0)
                ]
            )

        elif mode == "flomo卡片":
            # 运行 fupan.py
            run_script(f'python3 "{fupan_path}"', output_text, "Step 1/2 ", "正在建立「回顾」节点链接...", 5)

            # 弹出窗口选择
            show_popup(
                "flomo 卡片选项",
                "To TheBrain",
                "创建flomo卡片",
                lambda: webbrowser.open(TB_rul),  # 点击To TheBrain按钮的操作
                lambda: run_script(f'python3 "{flomo_path}"', output_text, "Step 2/2 ", "正在创建flomo卡片...", 0)  # 点击创建flomo卡片的操作
            )

        elif mode == "不制卡":
            # 运行 fupan.py
            run_script(f'python3 "{fupan_path}"', output_text, "Step 1/1 ", "正在建立「回顾」节点链接...", 0)

            # 弹出窗口选择
            show_popup(
                "不制卡选项",
                "To TheBrain",
                None,  # 没有右侧按钮
                lambda: webbrowser.open(TB_rul),  # 点击To TheBrain按钮的操作
                None,
                dismiss_on_left=True  # 点击左侧按钮后关闭窗口
            )

    elif thoughts == "No Ths":
        # 根据选择的制卡方式执行不同的流程
        if mode == "Anki卡片":

            # 在运行 anki.py 之前检查 Anki 是否在运行
            check_and_start_anki()

            # 运行 anki.py
            run_script(f'python3 "{anki_path}"', output_text, "Step 1/2 ", "正在创建Anki卡片...", 5)

            # 运行 anki_sync_mac.sh
            run_script(f'sh "{anki_sync_mac_path}"', output_text, "Step 2/2 ", "正在同步Anki卡片...", 0)

        elif mode == "flomo卡片":

            # 运行 flomo.py
            run_script(f'python3 "{flomo_path}"', output_text, "Step 1/1 ", "正在创建flomo卡片...", 0)

    # 结束操作，启用按钮
    update_status("完成 ", "所有步骤已完成！")
    progress_bar.stop()
    start_button.config(state=tk.NORMAL)  # 启用立即回顾按钮
    config_button.config(state=tk.NORMAL)  # 启用参数设置按钮
    mode_combobox.config(state=tk.NORMAL)  # 启用制卡方式选择框
    thoughts_combobox.config(state=tk.NORMAL)  # 启用是思考情况选择框

# 创建参数设置窗口
def open_config_window():
    config_window = tk.Toplevel(root)
    config_window.title("参数设置")
    
    # 创建标签页控件
    tab_control = ttk.Notebook(config_window)

    # 第一个标签页：config.py 的设置
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text="参数设置")

    # 文本框，用于显示 config.py 文件的内容
    config_text = tk.Text(tab1, wrap=tk.WORD)
    config_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 读取 config.py 文件内容并显示
    try:
        with open(config_py_path, 'r') as f:
            config_content = f.read()
            config_text.insert(tk.END, config_content)
    except FileNotFoundError:
        config_text.insert(tk.END, "找不到 config.py 文件")
    
    # 保存修改后的 config.py 文件
    def save_config():
        new_content = config_text.get("1.0", tk.END)
        try:
            with open(config_py_path, 'w') as f:
                f.write(new_content)
            messagebox.showinfo("成功", "参数已保存")
        except Exception as e:
            messagebox.showerror("错误", f"无法保存参数: {e}")

    # 恢复默认配置
    def restore_default_config():
        answer = messagebox.askquestion("恢复默认", "是否要恢复默认配置？", icon="warning")
        if answer == "yes":
            try:
                with open(config_mr_path, 'r') as f:
                    default_content = f.read()
                with open(config_py_path, 'w') as f:
                    f.write(default_content)
                config_text.delete("1.0", tk.END)
                config_text.insert(tk.END, default_content)
                messagebox.showinfo("成功", "默认配置已恢复")
            except FileNotFoundError:
                messagebox.showerror("错误", "找不到 config_mr.txt 文件")
            except Exception as e:
                messagebox.showerror("错误", f"无法恢复默认配置: {e}")

    # 创建按钮框架，用于水平居中按钮
    button_frame = tk.Frame(tab1)
    button_frame.pack(pady=10)

    # 创建恢复默认按钮
    restore_button = tk.Button(button_frame, text="恢复默认", command=restore_default_config)
    restore_button.pack(side=tk.LEFT, padx=5)

    # 创建保存按钮
    save_button = tk.Button(button_frame, text="保存", command=save_config)
    save_button.pack(side=tk.LEFT, padx=5)

    # 第二个标签页：TB_rul.txt 的设置
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text="TB_rul 设置")

    # 文本框，用于显示 TB_rul.txt 文件的内容
    tb_rul_text = tk.Text(tab2, wrap=tk.WORD)
    tb_rul_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 读取 TB_rul.txt 文件内容并显示
    try:
        with open(tb_rul_path, 'r') as f:
            tb_rul_content = f.read()
            tb_rul_text.insert(tk.END, tb_rul_content)
    except FileNotFoundError:
        tb_rul_text.insert(tk.END, "找不到 TB_rul.txt 文件")

    # 保存修改后的 TB_rul.txt 文件
    def save_tb_rul():
        new_tb_rul_content = tb_rul_text.get("1.0", tk.END)
        try:
            with open(tb_rul_path, 'w') as f:
                f.write(new_tb_rul_content)
            messagebox.showinfo("成功", "TB_rul.txt 参数已保存")
        except Exception as e:
            messagebox.showerror("错误", f"无法保存TB_rul.txt 参数: {e}")

    # 创建保存按钮框架，用于水平居中
    button_frame2 = tk.Frame(tab2)
    button_frame2.pack(pady=10)

    # 创建保存按钮
    save_tb_rul_button = tk.Button(button_frame2, text="保存", command=save_tb_rul)
    save_tb_rul_button.pack(side=tk.LEFT, padx=5)

    tab_control.pack(expand=1, fill="both")

# 创建主窗口
root = tk.Tk()
root.title("TheBrain 回顾工具")

# 窗口大小
window_width = 600
window_height = 500

# 居中显示窗口
center_window(root, window_width, window_height)

# 设置窗口为弹出在最上层
root.attributes('-topmost', True)

# 创建“立即回顾”按钮
start_button = tk.Button(root, text="立即回顾", command=start_review)
start_button.pack(pady=10)

# 创建框架，用于在同一行放置步骤标签和状态标签
status_frame = tk.Frame(root)
status_frame.pack(pady=5)

# 创建步骤标签和状态标签，并将它们放在同一行
step_label = tk.Label(status_frame, text="", font=("Arial", 12), anchor="w")
step_label.pack(side=tk.LEFT)

status_label = tk.Label(status_frame, text="", font=("Arial", 12), anchor="w")
status_label.pack(side=tk.LEFT)

# 创建进度条，放置在状态标签和步骤标签的下方
progress_bar = ttk.Progressbar(root, mode="determinate", maximum=100)
progress_bar.pack(fill=tk.X, pady=10)

# 创建滚动文本框显示输出
output_text_frame = tk.Frame(root)
output_text_frame.pack(fill=tk.BOTH, expand=True, pady=2)  # 调整位置和大小

output_text = tk.Text(output_text_frame, wrap=tk.WORD)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 创建滚动条并与文本框关联
scrollbar = tk.Scrollbar(output_text_frame, command=output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text.config(yscrollcommand=scrollbar.set)

# 创建“参数”按钮，并放置在Text小部件下方左侧，使用 Unicode 齿轮符号
config_button = tk.Button(root, text="⚙︎", command=open_config_window)
config_button.pack(side=tk.LEFT, anchor="sw", padx=5, pady=8)

# 创建一个框架来包含“思考情况”下拉菜单
thoughts_frame = tk.Frame(root)
thoughts_frame.pack(side=tk.LEFT, anchor="sw", padx=5, pady=8)

# 创建“思考情况”下拉菜单，调整下拉框的宽度
thoughts_combobox = ttk.Combobox(thoughts_frame, values=["New Ths", "No Ths"], state="readonly", width=6)
thoughts_combobox.current(thoughts_Nb)  # 设置默认值为"New Thoughts"
thoughts_combobox.pack(side=tk.LEFT, anchor="center", padx=2)

# 创建一个框架来包含“制卡方式”标签和下拉菜单
mode_frame = tk.Frame(root)
mode_frame.pack(side=tk.LEFT, anchor="sw", padx=5, pady=8)

# 创建“制卡方式”下拉菜单，调整下拉框的宽度
mode_combobox = ttk.Combobox(mode_frame, values=["Anki卡片", "flomo卡片", "不制卡"], state="readonly", width=7)
mode_combobox.current(card_Nb)  # 设置默认值为"Anki卡片"
mode_combobox.pack(side=tk.LEFT, anchor="center", padx=2)

# 恢复窗口层级
root.after(2000, lambda: root.attributes('-topmost', False))

# 运行主循环
root.mainloop()
