import os
import re
import random
import string
import glob
import datetime
import json

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
lz_path = 'datas/lz.json'

# 控制开关和追踪器文件路径
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
    print(f"🔒 【安全阀拦截】今日 1 号已在早晨完成大洗牌，晚上保持原暗号不再重复抽签: {current_token}")
else:
    if is_reset_day or not current_token:
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(current_token)
        print(f"⏰ 【密锁强制纠偏/新月抽签】已生成全量版严格 3 位新密锁: {current_token}")

# 🎯 严格保真：输出为 老杨TV + 随机密锁
output_filename = f"老杨TV{current_token}.json"
output_path = f"datas/{output_filename}"

# ====================================================================
# 🛡️ 【黑科技：全量版过期旧线一键调包为纯文字滚动大轰炸】
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
                    },
                    {
                        "key": "老杨纯文字提示2",
                        "name": "🚨 不要看这里了 ➡️ 链接已断 ｜ 加QQ群“532637640”获取",
                        "type": 3,
                        "api": "csp_JuDou",
                        "searchable": 0,
                        "quickSearch": 0,
                        "filterable": 0
                    }
                ],
                "lives": [
                    {
                        "group": "🚨 接口过期断流 ｜ 加QQ群“532637640”获取最新密码",
                        "channels": [
                            {
                                "name": "👉 当前线路已过期 ➡️ 加QQ群“532637640”获取最新密码",
                                "urls": [
                                    "http://127.0.0.1"
                                ]
                            }
                        ]
                    }
                ]
            }
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
            print(f"📡 【金蝉脱壳】已成功将过期旧线调包为纯文字大轰炸: {old_file}")
        except Exception as e:
            pass

for garbage in glob.glob('datas/config_*.json'):
    try: os.remove(garbage)
    except: pass


def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)
text_lz = read_file_text(lz_path)

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

# 1. 物理提取海豚源的全部内容
haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

# 2. 物理提取老张源里的 sites，并用高级逻辑过滤
lz_sites_text = get_array_inner_text(text_lz, "sites")
lz_nsfw_list = []

if lz_sites_text:
    try:
        wrapped_lz_json = json.loads(f"[{lz_sites_text}]")
        for item in wrapped_lz_json:
            if "🔞" in item.get("name", ""):
                raw_name = item["name"].replace("🔞", "").strip()
                item["name"] = f"{raw_name}｜🔞"
                if "api" in item and isinstance(item["api"], str):
                    if item["api"].startswith("./py/"):
                        item["api"] = item["api"].replace("./py/", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/py/")
                    elif item["api"].startswith("./js/"):
                        item["api"] = item["api"].replace("./js/", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/js/")
                    elif item["api"].startswith("./"):
                        item["api"] = item["api"].replace("./", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/")
                lz_nsfw_list.append(json.dumps(item, ensure_ascii=False, indent=4))
    except Exception as e:
        pass

# 把过滤且完美绝对化之后的老张 🔞 片段组装起来
lz_nsfw_final_text = ",\n    ".join(lz_nsfw_list)

# 3. 给海豚自带的站点和直播打上原始标签
name_regex = r'"name"\s*:\s*"([^"]+)"'
if haitun_sites_text:
    haitun_sites_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_sites_text)
if haitun_lives_text:
    haitun_lives_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_lives_text)

# 🚀 4. 【乡村电视及直播源全量去重机制】
# 构建乡村电视大组明文
country_live_dict = {
    "name": "乡村电视 ｜Tg：@huliys9",
    "type": 0,
    "playerType": 2,
    "ua": "okhttp",
    "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
}
country_live_text = json.dumps(country_live_dict, ensure_ascii=False, indent=4)

# 🔬 【CNB直播源对比海豚去重保留机制】
cnb_lives_text = get_array_inner_text(text_cnb, "lives")
cnb_unique_lives_list = []

if cnb_lives_text and haitun_lives_text:
    try:
        # 获取海豚现有的所有直播大组名称集合，作为去重雷达
        haitun_lives_json = json.loads(f"[{haitun_lives_text}]")
        haitun_groups = {item.get("name", "").replace("｜Tg：@huliys9", "").strip() for item in haitun_lives_json}
        
        # 解析CNB的直播大组，对比去重
        cnb_lives_json = json.loads(f"[{cnb_lives_text}]")
        for item in cnb_lives_json:
            cnb_group_name = item.get("name", "").strip()
            # 如果海豚直播里没有这个大组，则判定为CNB独家好源，予以全量保留
            if cnb_group_name and cnb_group_name not in haitun_groups:
                cnb_unique_lives_list.append(json.dumps(item, ensure_ascii=False, indent=4))
    except:
        pass
cnb_unique_lives_final_text = ",\n    ".join(cnb_unique_lives_list)

final_json_text = text_cnb

# ====================================================================
# 🚀 逆向注入：海豚站点大军开路，后面死死粘着老张的 🔞 突击队
# ====================================================================
if '"sites": [' in final_json_text:
    combined_sites = ""
    if haitun_sites_text:
        combined_sites += haitun_sites_text.rstrip(',') + ',\n    '
    if lz_nsfw_final_text:
        combined_sites += lz_nsfw_final_text.rstrip(',') + ',\n    '
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {combined_sites}', 1)

# ====================================================================
# 🚀 直播源核心组装：海豚全量保留 + 乡村电视精准插队 + CNB独家去重源兜底
# ====================================================================
if '"lives": [' in final_json_text:
    # 🌟 A. 实现乡村电视精准插队到“海燕直播”的前面
    if haitun_lives_text and '"name": "海燕' in haitun_lives_text:
        # 精准定位海燕大字典的起始左大括号
        haitun_lives_text = haitun_lives_text.replace(
            '{\n        "name": "海燕', 
            f'{country_live_text},\n    {{\n        "name": "海燕'
        )
        haitun_lives_text = haitun_lives_text.replace(
            '{\n    "name": "海燕', 
            f'{country_live_text},\n    {{\n    "name": "海燕'
        )
    else:
        # 如果没抓到海燕，作为降级安全防线，直接加在海豚的最前头
        if haitun_lives_text:
            haitun_lives_text = f"{country_live_text},\n    {haitun_lives_text}"

    # 🌟 B. 拼装大合集：海豚全量(含插队的乡村电视) + CNB独家去重保留源
    combined_lives = ""
    if haitun_lives_text:
        combined_lives += haitun_lives_text.rstrip(',') + ',\n    '
    if cnb_unique_lives_final_text:
        combined_lives += cnb_unique_lives_final_text.rstrip(',') + ',\n    '
        
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {combined_lives}', 1)

# ====================================================================
# 路径固定清洗与核心拦截
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

# ====================================================================
# 🎯 强力拦截注入开机大公告栏提示
# ====================================================================
if '"warningText":' not in final_json_text:
    thanks_warning = (
        '👑 特别致谢与版权声明\\n'
        '本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\\n'
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
        '本接口由老杨TV结合海豚佬&老张特调&鱼佬的优质核心资源缝合而成，纯净无广告！'
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
    
    # 提取并纯净化已有的尾部标识
    if "｜Tg：@huliys9" in name_val:
        name_val = name_val.replace("｜Tg：@huliys9", "")
        tg_suffix = "｜Tg：@huliys9"
    elif "｜🔞" in name_val:
        name_val = name_val.replace("｜🔞", "")
        tg_suffix = "｜🔞"
        
    for char in ['丨', '┃', ' ']:
        name_val = name_val.strip(char)
        
    name_val = re.sub(r'\s+', ' ', name_val)
    
    # 🎯 规范化大组改名：蝴蝶 + 空格 + 纯正名称 + 专属尾缀
    return f'"name": "🦋 {name_val}{tg_suffix}"'

# 🚀 【核心性能调优：直播间安全隔离壁垒】
# 只对前半段包含 sites（影视点播大组）的区域加蝴蝶。后半段 lives 里不论是插队的乡村电视、海豚还是CNB独家去重源，
# 其内部上千个具体的电视节目单 100% 保持纯净明文状态，绝不塞任何蝴蝶符号，彻底消灭线路加载死卡
if '"sites": [' in final_json_text and '"lives": [' in final_json_text:
    parts = final_json_text.split('"lives": [', 1)
    parts[0] = re.sub(r'"name"\s*:\s*"([^"]+)"', clean_and_add_butterfly, parts[0])
    final_json_text = '"lives": ['.join(parts)
else:
    final_json_text = re.sub(r'"name"\s*:\s*"([^"]+)"', clean_and_add_butterfly, final_json_text)

final_json_text = final_json_text.replace(
    '"name": "🦋 爱奇艺｜Tg：@huliys9"',
    '"name": "🦋 爱奇艺｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"'
)

final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

with open(tracker_path, 'w', encoding='utf-8') as f:
    f.write(output_filename)

print(f"🎉 【完美插队与全量去重集成版】部署成功！配置名: {output_path}")
