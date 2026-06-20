import os
import re
import random
import string
import glob
import datetime
import json

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'

# 控制开关和追踪器的文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# ⏰ 【安全阀门升级：全量版方案 A 】
# ====================================================================
today = datetime.datetime.now()
is_reset_day = (today.day == 1)

current_token = ""

if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        current_token = f.read().strip()

if len(current_token) != 3:
    current_token = ""

if is_reset_day and len(current_token) == 3:
    print(f"🔒 【安全阀拦截】今日 1 号保持原暗号不再重复抽签: {current_token}")
else:
    if is_reset_day or not current_token:
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(current_token)
        print(f"⏰ 【密锁自动生成】严格 3 位新密锁: {current_token}")

output_filename = f"老杨TV{current_token}.json"
output_path = f"datas/{output_filename}"

# ====================================================================
# 🛡️ 【黑科技：全量版过期旧线一键调包】
# ====================================================================
old_configs = glob.glob('datas/老杨TV*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            trap_json = {
                "spider": "", 
                "notice": "⚠️ 警告：当前“老杨TV”专线密码已过期断流！老链接已彻底作废！\n\n最新密码加QQ群“532637640”获取",
                "warningText": "👑 特别提示：加QQ群“532637640”获取",
                "sites": [
                    {
                        "key": "老杨纯文字提示",
                        "name": "🚨 加QQ群“532637640”获取最新密码",
                        "type": 3,
                        "api": "csp_JuDou",
                        "searchable": 0,
                        "quickSearch": 0,
                        "filterable": 0
                    }
                ],
                "lives": [
                    {
                        "group": "🚨 接口过期断流 ｜ 进群拿新密码",
                        "channels": [
                            {
                                "name": "👉 当前线路已过期 ➡️ 加QQ群“532637640”获取最新密码",
                                "urls": ["http://127.0.0.1"]
                            }
                        ]
                    }
                ]
            }
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass

for garbage in glob.glob('datas/config_*.json'):
    try: os.remove(garbage)
    except: pass


# ====================================================================
# 🚀 核心：【标准内存对象深度解析缝合】直接秒杀一切格式与卡顿问题
# ====================================================================
try:
    with open(cnb_path, 'r', encoding='utf-8') as f:
        cnb_obj = json.load(f)
except Exception as e:
    print(f"❌ 读取 cnb.json 失败，请检查文件格式: {e}")
    cnb_obj = {}

try:
    with open(haitun_path, 'r', encoding='utf-8') as f:
        haitun_obj = json.load(f)
except Exception as e:
    print(f"❌ 读取 haitun.json 失败，请检查文件格式: {e}")
    haitun_obj = {}

# 1. 提取并安全处理海豚佬的 sites
haitun_sites = haitun_obj.get("sites", [])
for site in haitun_sites:
    if "name" in site:
        site["name"] = f"{site['name']}｜Tg：@huliys9"

# 2. 提取并安全处理海豚佬的 lives
haitun_lives = haitun_obj.get("lives", [])
for live in haitun_lives:
    if "group" in live:
        live["group"] = f"{live['group']}｜Tg：@huliys9"
    if "channels" in live:
        for channel in live["channels"]:
            if "name" in channel:
                channel["name"] = f"{channel['name']}｜Tg：@huliys9"

# 3. 缝合到 cnb 的基础框架上
# 影视站：海豚在前，鱼佬在后
cnb_obj["sites"] = haitun_sites + cnb_obj.get("sites", [])
# 直播源：彻底抛弃鱼佬直播，100% 只保留海豚佬直播
cnb_obj["lives"] = haitun_lives

# 4. 把对象重新转换为标准高容错文本，让后续的正则和 replace 继续安全工作
final_json_text = json.dumps(cnb_obj, ensure_ascii=False, indent=4)


# ====================================================================
# 路径补全与 Jar 包强力拦截
# ====================================================================
final_json_text = final_json_text.replace(
    '"key": "hajim-腾讯备"', 
    '"spider": "./tvbox.jar",\n           "key": "hajim-腾讯备"'
)
final_json_text = final_json_text.replace(
    '"key": "茫茫"', 
    '"spider": "./tvbox.jar",\n        "key": "茫茫"'
)

final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

final_json_text = final_json_text.replace(
    '"logo": "http://127.0.0.1:9978/file/TVBox/logo.png"', 
    '"logo": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"'
)

# 开机公告注入
if '"warningText":' not in final_json_text:
    thanks_warning = (
        '👑 特别致谢与版权声明\\n'
        '本接口合并自海豚佬 and 鱼佬接口，感谢两位大佬的无私付出！\\n'
        '🐋 鱼佬主页: fish2018/webhtv\\n'
        '🐬 海豚佬主页: FGBLH/GHK'
    )
    
    welcome_notice = (
        '👑 欢迎使用【老杨TV专属缝合专线】！\\n\\n'
        '本线由老杨结合鱼佬与HT大佬的优质资源缝合而成，纯净无广告！\\n'
        '🚨 特别声明：此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9\\n\\n'
        '📢 提示：接口密码不定期更换！失效请及时回频道或微信群获取今日最新密码续杯！'
    )
    
    final_json_text = final_json_text.replace(
        '{\n    "spider":',
        f'{{\n    "notice": "{welcome_notice}",\n    "warningText": "{thanks_warning}",\n    "spider":'
    )

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
    '"name": "🦋爱奇艺｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"',
    '"name": "🦋老杨自用专线 ｜ 安全纯净版"'
)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

with open(tracker_path, 'w', encoding='utf-8') as f:
    f.write(output_filename)

print(f"🎉 【对象级高容错缝合 · 纯海豚直播终极版】更新成功！配置名: {output_path}")
