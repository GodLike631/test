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
# ⏰ 【每月 1 号自动大洗牌与控制开关自动生成逻辑 - 引入月份判定版】
# ====================================================================
today = datetime.datetime.now()
current_month = str(today.month) 
is_reset_day = (today.day == 1)

saved_month = ""
saved_code = ""

# 1. 尝试读取现有的开关状态 (格式为 "月份-3位密码"，例如 "7-k9x")
if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            saved_code = content

# 🎯 判定：如果是 1 号，且记录的月份不是当前月份（说明是当月第一次跑，跨月了）
if is_reset_day and saved_month != current_month:
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【每月1號全新硬核洗牌】檢測到進入新月份 {current_month} 月！已全自動抽籤生成本月新後綴: {current_token}")

# 🎯 判定：如果是 1 号的第二次及后续运行
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全阀拦截】今日 1 号已经是当月第二次运行，保持原暗号: {current_token}")

# 🎯 平常日子
else:
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月密锁后缀: {current_token}")

# 3. 🎯 严格判定最终输出之文件名
if current_token in ["全量版", "纯净版"]:
    output_filename = "老杨TV全量版.json"
else:
    output_filename = f"老杨TV全量版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 最终结算 -> 目标输出文件名：{output_filename}")


# ====================================================================
# 🛡️ 【金蝉脱壳：全量版过期旧线自动全文字大轰炸 - 沿用原脚本提示】
# ====================================================================
old_configs = glob.glob('datas/老杨TV全量版*.json') + glob.glob('datas/老杨TV*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            trap_json = {
                "spider": "", 
                "notice": f"⚠️ 警告：当前专线已过期断流！老链接已彻底作废！\n\n最新全量版链接请加QQ群“532637640”获取",
                "warningText": "👑 特别提示：加QQ群“532637640”获取最新接口",
                "sites": [
                    {"key": "老杨纯文字提示", "name": "🚨 请前往QQ群“532637640”获取最新链接🚨 当前专线已过期断流！", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                    {"key": "老杨纯文字提示2", "name": "🚨 请前往QQ群“532637640”获取最新全量版链接", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                ],
                "lives": [
                    {"group": "🚨 接口过期断流 ｜ 提示", "channels": [{"name": "👉 线路已过期 ➡️ 加QQ群“532637640”获取最新全量版链接", "urls": ["http://127.0.0.1"]}]}
                ]
            }
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
            print(f"📡 【金蝉脱壳】已成功将过期旧线调包为纯文字大轰炸: {old_file}")
        except:
            pass

for garbage in glob.glob('datas/config_*.json'):
    try: os.remove(garbage)
    except: pass


# ====================================================================
# 🧠 【核心逻辑：正统 JSON 对象读取与合并逻辑】
# ====================================================================
def load_json_safe(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except Exception as e:
            print(f"❌ 错误：{path} JSON 格式不正确！无法解析。")
            return {}

json_cnb = load_json_safe(cnb_path)
json_haitun = load_json_safe(haitun_path)
json_lz = load_json_safe(lz_path)

haitun_sites = json_haitun.get("sites", [])
haitun_lives = json_haitun.get("lives", [])
lz_sites = json_lz.get("sites", [])

# 过滤老张源里的 🔞 站点并转换为绝对路径
lz_nsfw_list = []
for item in lz_sites:
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
        lz_nsfw_list.append(item)

# 给海豚源打上后缀标签
for item in haitun_sites:
    if "name" in item: item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item: item["name"] = f"{item['name']}｜Tg：@huliys9"

# 精准插入“乡村电视”到直播数组索引 5（第 6 位）
country_live_dict = {
    "name": "乡村电视 ｜Tg：@huliys9",
    "type": 0,
    "playerType": 2,
    "ua": "okhttp",
    "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
}
if len(haitun_lives) >= 5:
    haitun_lives.insert(5, country_live_dict)
else:
    haitun_lives.append(country_live_dict)

# ====================================================================
# 🎯 注入你的 JavBus 點播爬蟲線路 (依照官方 type: 3 規範整合)
# ====================================================================
javbus_site_dict = {
    "key": "JavBus_Private",
    "name": "🦋 老楊私房 • JavBus專線",
    "type": 3,
    "api": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/py_JavBus.py",
    "searchable": 1,
    "quickSearch": 1,
    "filterable": 0
}

# 🚀 数组大合并：海豚排上面 ➡️ 插入 JavBus ➡️ 中间接老张 ➡️ 最后接 cnb
cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

json_cnb["sites"] = haitun_sites + [javbus_site_dict] + lz_nsfw_list + cnb_sites
json_cnb["lives"] = haitun_lives + cnb_lives

# 转换为文本后进行清洗与特调
final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)

final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"')
final_json_text = final_json_text.replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"')

final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '')

path_replacements = {
    './spider.jar': 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar',
    './XBPQ/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/',
    './XYQHiker/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/',
    './js/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/',
    './json/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/',
    './py/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/',
    'http://127.0.0.1:9978/file/TVBox/logo.png': 'https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg'
}
for src, dst in path_replacements.items():
    final_json_text = final_json_text.replace(src, dst)

# 开机公告注入 (原汁原味保留老杨TV公告，去除密码提示)
thanks_warning = "👑 特别致谢与版权声明\n本接口的诞生离不开大后方几位业内顶流技术大佬 of 无私奉献，特此致谢：\n🐋 感谢鱼佬的付出\n源码基础与发布主页: fish2018/webhtv\n版本发布绝对地址: fish2018/webhtv/releases\nTelegram 官方群组: 👉 https://t.me/webhtv\n 感谢佬的付出\n核心仓库主页: FGBLH/GHK\n数据源直链地址: FGBLH/GHK/.json\nTelegram 官方群组: 👉 https://t.me/hshsjk9"
welcome_notice = "👑 欢迎使用【老杨TV粉丝专属缝合专线】！🚨 核心秒播優化版已啟用：網絡棧已實裝 DoH 加密防污染與超級並行解析專線，已無縫縫合 JavBus 私房點播站點。遇到線路卡頓請及時回 Telegram 頻道（@huliys9）或微信群獲取當前最新動態！"

try:
    final_obj = json.loads(final_json_text)
    
    # ====================================================================
    # ⚡ 【硬核特调注入：实装高阶秒播骨架与规范优化】
    # ====================================================================
    
    # 1. 升级 DoH 加密 DNS 网络栈（精准注入 Bootstrap IPs，阻断查询污染死循环）
    final_obj["doh"] = [
        {
            "name": "Google-DoH",
            "url": "https://dns.google/dns-query",
            "ips": ["8.8.8.8", "8.8.4.4"]
        },
        {
            "name": "Cloudflare-DoH",
            "url": "https://cloudflare-dns.com/dns-query",
            "ips": ["1.1.1.1", "1.0.0.1"]
        },
        {
            "name": "阿里加密 DNS",
            "url": "https://dns.alidns.com/dns-query",
            "ips": ["223.5.5.5", "223.6.6.6"]
        }
    ]
    
    # 2. 升级 parses：强行在解析规则最前端注入「超级并行秒播专线」（type: 4）
    parallel_parse = {
        "name": "🚀 老楊專屬 • 聚合秒播專線 (超級並行)",
        "type": 4,
        "url": "Parallel"
    }
    final_obj["parses"] = [parallel_parse] + final_obj.get("parses", [])
    
    # 3. 修正 sites 内的语法栏位
    for site in final_obj.get("sites", []):
        if site.get("key") == "leo_danmaku":
            site["indexs"] = 1 
            if "index" in site: site.pop("index")
        if site.get("type") == 1 and "filterable" in site:
            site.pop("filterable") 

    # 4. 扩充 lives 高阶属性：动态精准为主要直播频道群注入动态 EPG 节目单与时区表
    for live in final_obj.get("lives", []):
        lname = live.get("name", "")
        if "綜合直播" in lname or "地方直播" in lname or "各大源合集" in lname:
            live["epg"] = "https://epg.112114.xyz/?ch={name},https://epg.pw/xmltv/assets/china.xml.gz"
            live["timeZone"] = "Asia/Shanghai"
        elif "台灣台" in lname or "港台" in lname:
            live["epg"] = "https://epg.pw/xmltv/assets/taiwan.xml.gz"
            live["timeZone"] = "Asia/Taipei"

    # 5. 修正 IJK 播放器内核参数：将缓存过长导致黑屏断流的过期快取缩短为健康的 60 秒
    for player in final_obj.get("ijk", []):
        for option in player.get("options", []):
            if option.get("name") == "dns_cache_timeout":
                option["value"] = "60000000" 

    # ====================================================================

    final_obj["notice"] = welcome_notice
    final_obj["warningText"] = thanks_warning
    
    ordered_obj = {}
    if "notice" in final_obj: ordered_obj["notice"] = final_obj.pop("notice")
    if "warningText" in final_obj: ordered_obj["warningText"] = final_obj.pop("warningText")
    ordered_obj.update(final_obj)
    
    # 🦋 加 transition 蝴蝶逻辑 (做报错防阻断保护)
    try:
        for site in ordered_obj.get("sites", []):
            if "name" in site:
                name_val = site["name"]
                for char in ['丨', '┃', ' ']:
                    name_val = name_val.strip(char)
                name_val = re.sub(r'\s+', ' ', name_val)
                if not name_val.startswith("🦋"):
                    site["name"] = f"🦋 {name_val}"

        for site in ordered_obj.get("sites", []):
            if "key" in site and site["key"] == "AQY":
                site["name"] = "🦋 爱奇艺｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"
    except Exception as inner_e:
        print(f"⚠️ 提示：美化蝴蝶图标时跳过，原因: {inner_e}")

    # 🌟【前置写入】强制安全落盘
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 全量版秒播优化配置更新成功！档案已写出至: {output_path}")

except Exception as e:
    print(f"❌ 严重错误：最后的本地渲染失败，原因: {e}")

# 🌟 双重保险
if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
