#!/bin/bash

# 检查 Anki 是否正在运行
if pgrep -x "anki" > /dev/null
then
    echo "Anki已经运行，正在后台同步Anki卡片..."
else
    echo "启动Anki..."
    
    # 使用 AppleScript 后台启动 Anki 并将窗口设置为不可见
    osascript -e 'tell application "Anki" to launch' \
              -e 'delay 1' \
              -e 'tell application "System Events" to set visible of process "Anki" to false'
    
    sleep 2  # 等待2秒，确保 Anki 启动完成
    echo "正在后台同步Anki卡片..."
fi

# 隐藏Anki窗口后进行同步
osascript -e 'tell application "System Events" to set visible of process "Anki" to false'
curl http://localhost:8765 -X POST -d "{\"action\": \"sync\", \"version\": 6}"

# 同步完成后再次隐藏Anki窗口
osascript -e 'tell application "System Events" to set visible of process "Anki" to false'
