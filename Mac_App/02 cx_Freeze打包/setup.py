from cx_Freeze import setup, Executable
import sys
import os
import shutil

# 删除 build 和 dist 目录（防止旧的文件残留）
if os.path.exists('build'):
    shutil.rmtree('build')

if os.path.exists('dist'):
    shutil.rmtree('dist')

# 当前路径
here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="TbReviewTool",
    version="1.0",
    description="A review tool integrated with TheBrain, Anki, and Flomo",
    options={
        "build_exe": {
            "packages": ["requests", "tkinter", "ssl", "certifi", "os", "subprocess", "queue"],
                "include_files": [
                    (os.path.join(here, "fupan.py"), "fupan.py"),
                    (os.path.join(here, "anki.py"), "anki.py"),
                    (os.path.join(here, "flomo.py"), "flomo.py"),
                    (os.path.join(here, "anki_sync_mac.sh"), "anki_sync_mac.sh"),
                    (os.path.join(here, "config.py"), "config.py"),
                    (os.path.join(here, "config_mr.txt"), "config_mr.txt"),
                    (os.path.join(here, "TB_rul.txt"), "TB_rul.txt"),
                    (os.path.join(here, "app.icns"), "app.icns")
                ],
            "build_exe": "build/exe.macosx-14.0-arm64-3.12"
        },
        "bdist_mac": {
            "iconfile": os.path.join(here, "app.icns"),
            "bundle_name": "TbReviewTool"
        }
    },
    executables=[Executable(script="gui_app.py", target_name="TbReviewTool", icon=os.path.join(here, "app.icns"))]
)

