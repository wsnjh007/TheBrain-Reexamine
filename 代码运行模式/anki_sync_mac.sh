#!/bin/bash

# 检查 Anki 是否正在运行
if pgrep -x "anki" > /dev/null
then
    echo "Anki已经运行，正在后台同步Anki卡片..."
else
    echo "启动Anki..."
    osascript -e 'tell application "Anki" to launch'
    # 使用 AppleScript 启动 Anki 并确保窗口隐藏
    sleep 2  # 等待2秒，确保 Anki 启动完成
    echo "正在后台同步Anki卡片..."
fi

# 隐藏Anki窗口后进行同步
osascript -e 'tell application "System Events" to set visible of process "Anki" to false'
echo ""
curl http://localhost:8765 -X POST -d "{\"action\": \"sync\", \"version\": 6}" > /dev/null
# 同步完成后再次隐藏Anki窗口
sleep 2
osascript -e 'tell application "System Events" to set visible of process "Anki" to false'
# 再次确认并保持 Anki 窗口处于隐藏状态
osascript <<EOF
    tell application "System Events"
        if exists (process "Anki") then
            set visible of process "Anki" to false
        end if
    end tell
EOF
echo "同步完成！"
echo ""