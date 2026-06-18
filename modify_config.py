import os
import re
import random
import string
import glob
import datetime

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'

# 控制开关和追踪器的文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# 🚨 【老杨专属：全自动地毯式大扫除补丁】
# 专门对付手机端无法手动删除文件的 Bug， Actions 一跑，历史垃圾全部灰飞烟灭！
# ====================================================================
garbage_files = [
    'datas/local_config.json',
    *glob.glob('datas/config_*.json')  # 揪出所有 config_ 开头的历史死线
]
for garbage in garbage_files:
    if os.path.exists(garbage):
        try:
            os.remove(garbage)
            print(f"🧹 【大扫除成功】已自动强擦历史残留文件: {garbage}")
        except:
            pass

# ====================================================================
# ⏰ 【方案 A 定时自动脱壳机制：老杨TV + 3位随机字符定制版】
# ====================================================================
today = datetime.datetime.now()
is_reset_day = (today.day == 1)

current_token = ""

if not is_reset_day and os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        current_token = f.read().strip()

if not current_token:
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(current_token)
    print(f"⏰ 【触发金蝉脱壳】已全自动更换 3 位新密锁: {current_token}")

output_filename = f"老杨TV{current_token}.json"
output_path = f"datas/{output_filename}"

# 物理擦除不合规的过期老线
old_configs = glob.glob('datas/老杨TV*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            os.remove(old_file)
            print(f"🗑️ 【断流成功】已物理抹除历史过期老线: {old_file}")
        except Exception as e:
            pass

def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 1. 物理提取海豚源里的 sites 和 lives 内部的纯文本
# ====================================================================
def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    after_key = content.split(split_key, 1)[1]
    if '],' in after_key:
        inner_text = after_key.split('],', 1)[0]
    else:
        inner_text = after_key.split(']', 1)[0]
    return inner_text.strip()

haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

# 【海豚专属尾缀手术】
name_regex = r'"name"\s*:\s*"([^"]+)"'
if haitun_sites_text:
    haitun_sites_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_sites_text)
if haitun_lives_text:
    haitun_lives_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_lives_text)

# ====================================================================
# 2. 逆向注入：把海豚的内容，无缝贴进 CNB 对应的数组最前面
# ====================================================================
final_json_text = text_cnb

if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 3. 靶向拦截手术：揪出这两个瘫痪的 4K 线路
# ====================================================================
final_json_text = final_json_text.replace(
    '"key": "hajim-腾讯备"', 
    '"spider": "./tvbox.jar",\n           "key": "hajim-腾讯备"'
)
final_json_text = final_json_text.replace(
    '"key": "茫茫"', 
    '"spider": "./tvbox.jar",\n        "key": "茫茫"'
)

# ====================================================================
# 【全方位无死角路径清洗】：让 CNB 的其余线路走官方绝对 network 链接
# ====================================================================
final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 4. 定制老杨自用全量缝合专线 brand 头部
# ====================================================================
final_json_text = final_json_text.replace(
    '"logo": "http://127.0.0.1:9978/file/TVBox/logo.png"', 
    '"logo": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"'
)

if '"warningText":' not in final_json_text:
    thanks_warning = (
        '👑 特别致谢与版权声明\\n'
        '本接口的诞生离不开大后方两位业内顶流技术大佬的无私奉献，特此致谢：\\n'
        '🐋 感谢鱼佬的付出\\n'
        '源码基础与发布主页: fish2018/webhtv\\n'
        '版本发布绝对地址: fish2018/webhtv/releases\\n'
        'Telegram 官方群组: 👉 https://t.me/webhtv\\n'
        '🐬 感谢海豚佬的付出\\n'
        '核心仓库主页: FGBLH/GHK\\n'
        '数据源直链地址: FGBLH/GHK/海豚.json\\n'
        'Telegram 官方群组: 👉 https://t.me/hshsjk9'
    )
    final_json_text = final_json_text.replace(
        '{\n    "spider":',
        f'{{\n    "warningText": "{thanks_warning}",\n    "spider":'
    )

# ====================================================================
# 5. 全方位名称大清洗与品牌脱敏手术
# ====================================================================
final_json_text = final_json_text.replace('🐬', '')
final_json_text = final_json_text.replace('海豚影视', '')
final_json_text = final_json_text.replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '')
final_json_text = final_json_text.replace('交流群 TG：@hshsjk9', '')

def clean_and_add_butterfly(match):
    name_val = match.group(1)
    tg_suffix = ""
    if "｜Tg：@huliys9" in name_val:
        name_val = name_val.replace("｜Tg：@huliys9", "")
        tg_suffix = "｜Tg：@huliys9"
        
    for char in ['丨', '┃', ' ']:
        name_val = name_val.strip(char)
        
    name_val = re.sub(r'\s+', ' ', name_val)
    return f'"name": "🦋{name_val}{tg_suffix}"'

final_json_text = re.sub(r'"name"\s*:\s*"([^"]+)"', clean_and_add_butterfly, final_json_text)

final_json_text = final_json_text.replace(
    '"name": "🦋爱奇艺｜Tg：@huliys9"',
    '"name": "🦋爱奇艺｜此接口非原创，合并自海豚佬和鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"'
)

# ====================================================================
# 6. 消除尾部逗号瑕疵
# ====================================================================
final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

with open(tracker_path, 'w', encoding='utf-8') as f:
    f.write(output_filename)

print(f"🎉 【大扫除版同步成功】当前最新出库配置名: {output_path}")
