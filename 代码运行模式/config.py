# config.py

# API配置
# TheBrain的API密钥
api_key = 'your_api_key_here'
# 定义API的基本URL
base_url = 'https://api.bra.in'
# TheBrain的Brain ID
brain_id = 'your_brain_id_here'
# 「回顾」thought ID
review_id = 'your_review_id_here'

# fupan.py特定配置
# 类型为「洞见卡片」和「原则卡片」ID
allowed_type_ids = ['type_id_1', 'type_id_2']
# 需要去除的thought更新类型，如：102'已删除'、301'忘记'，详见《操作类型字典.md》，注意直接填写数字，不需要''
excluded_mod_types = ['mod_type_1', 'mod_type_2']

# anki.py & flomo.py 共用配置
# 「问题卡片」类型ID
question_id = 'your_question_id_here'
# 「精进域」类型ID
up_id = 'your_up_id_here'
# 即洞见类型卡片ID，例如「洞见卡片」、「原则卡片」
solutions_id = ['solution_id_1', 'solution_id_2']

# flomo.py特定配置
# flomoAPI链接
flomo_api_url = "https://flomoapp.com/api_key/"

# 默认思考情况和制卡方式配置
# 思考情况有["New Ths", "No Ths"]，对应的数字为0 1 
thoughts_Nb = 0
# 制卡方式有["Anki卡片", "flomo卡片", "不制卡"]，对应的数字为0 1 2
card_Nb = 0