from setuptools import setup

APP = ['gui_app.py']
DATA_FILES = ['config.py', 'config_mr.txt', 'TB_rul.txt', 'anki_sync_mac.sh', 'review_time.txt', 'fupan.py', 'anki.py', 'flomo.py']
OPTIONS = {
    'includes': [
        'requests', 'lxml', 'pytz', 'bs4', 'certifi',
        'jaraco', 'jaraco.text', 'jaraco.context', 'jaraco.functools', 'more_itertools'
    ],
    'packages': [
        'certifi', 'jaraco.text', 'jaraco.context', 'jaraco.functools', 'more_itertools'
    ],
    'verbose': True,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    zip_safe=False,
)

