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
# ⏰ 【安全阀门升级：全量版方案 A 确保 1 号早晚双跑只洗一次牌】
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
        print(f"⏰ 【密锁强制纠偏】已生成全量版严格 3 位新密锁: {current_token}")

output_filename = f"老杨TV{current_token}.json"
output_path = f"datas/{output_filename}"

# ====================================================================
# 🛡️ 【黑科技：过期旧线一键调包为纯文字滚动大轰炸】
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
# 🚀 【大核心】安全读取并采用标准字典对象深度重组缝合，消除不规范硬伤
# ====================================================================
try:
    with open(cnb_path, 'r', encoding='utf-8') as f:
        cnb_obj = json.load(f)
except Exception as e:
    print(f"❌ 读取 cnb.json 失败: {e}")
    cnb_obj = {"sites": [], "lives": []}

try:
    with open(haitun_path, 'r', encoding='utf-8') as f:
        haitun_obj = json.load(f)
except Exception as e:
    print(f"❌ 读取 haitun.json 失败: {e}")
    haitun_obj = {"sites": [], "lives": []}

# 1. 提取并规范化处理海豚佬的 sites
haitun_sites = haitun_obj.get("sites", [])
for site in haitun_sites:
    if isinstance(site, dict) and "name" in site:
        site["name"] = f"{site['name']}｜Tg：@huliys9"

# 2. 🎯 直播源重组洗牌：完全按照鱼佬（CNB）的标准格式，将海豚佬的直播源解构重写
raw_haitun_lives = haitun_obj.get("lives", [])
standard_haitun_lives = []

for group in raw_haitun_lives:
    if not isinstance(group, dict):
        continue
    
    # 初始化符合 CNB 规范的标准大组字典
    new_group = {
        "group": f"{group.get('group', '未命名分类')}｜Tg：@huliys9",
        "channels": []
    }
    
    # 严格按照规矩提取内部频道
    for channel in group.get("channels", []):
        if not isinstance(channel, dict):
            continue
        
        # 强制过滤掉那些不包含有效播放地址的空项目或坏探针，防止电视卡死
        urls = [u for u in channel.get("urls", []) if u and str(u).startswith(('http', 'rtmp', 'p2p', 'mitv'))]
        if not urls:
            continue
            
        # 组装百分之百符合标准语法规范的标准频道字典
        new_channel = {
            "name": channel.get("name", "未命名频道"),
            "urls": urls
        }
        new_group["channels"].append(new_channel)
        
    if new_group["channels"]:
        standard_haitun_lives.append(new_group)

# 3. 内存多轨缝合
# 影视站：海豚在前，鱼佬在后
cnb_obj["sites"] = haitun_sites + cnb_obj.get("sites", [])
# 直播源：保留两家直播！海豚的规范直播在前，鱼佬的在后
cnb_obj["lives"] = standard_haitun_lives + cnb_obj.get("lives", [])

# 4. 把经过标准格式化洗礼的数据转化为干净利落的文本，交给后续逻辑
final_json_text = json.dumps(cnb_obj, ensure_ascii=False, indent=4)


# ====================================================================
# 【相对路径补全与 Jar 包拦截核心功能】（丝毫不动）
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

# 开机提示语公告注入（丝毫不动）
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
    
    welcome_notice = (
        '👑 欢迎使用【老杨TV粉丝专属缝合专线】！'
        '本接口由老杨TV结合海 豚佬&鱼佬的优质资源缝合而成，纯净无广告！'
        '🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！'
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

# 加蝴蝶逻辑，只对 sites 部分做手术，确保不污染直播源具体的上千个频道名字
if '"sites": [' in final_json_text and '"lives": [' in final_json_text:
    parts = final_json_text.split('"lives": [', 1)
    parts[0] = re.sub(r'"name"\s*:\s*"([^"]+)"', clean_and_add_butterfly, parts[0])
    final_json_text = '"lives": ['.join(parts)
else:
    final_json_text = re.sub(r'"name"\s*:\s*"([^"]+)"', clean_and_add_butterfly, final_json_text)

final_json_text = final_json_text.replace(
    '"name": "🦋爱奇艺｜Tg：@huliys9"',
    '"name": "🦋爱奇艺｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"'
)

final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

with open(tracker_path, 'w', encoding='utf-8') as f:
    f.write(output_filename)

print(f"🎉 【海豚直播重新打乱按标准规范重组版】更新成功！配置名: {output_path}")
