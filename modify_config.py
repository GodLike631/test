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

lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# ⏰ 【每月 1 号自动大洗牌与控制开关自动生成逻辑 - 4位纯数字版】
# ====================================================================
today = datetime.datetime.now()
current_month = str(today.month) 
is_reset_day = (today.day == 1)

saved_month = ""
saved_code = ""

# 1. 尝试读取现有的开关状态
if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            saved_code = content

# 🎯 判定：如果是 1 号，且跨月了，全自动生成 4 位纯数字新密锁
if is_reset_day and saved_month != current_month:
    current_token = ''.join(random.choices(string.digits, k=4))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【進入新月份】已全自动抽签生成本月 4 位數字新密锁: {current_token}")

elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全阀】今日 1 号已运行过，保持本月暗号: {current_token}")

else:
    # 平时如果空了或格式不对，初始化为 4 位纯数字
    if not saved_code or len(saved_code) != 4 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.digits, k=4))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月數字密锁: {current_token}")

# 🎯 核心優化：直链 URL 永远固定！粉丝一劳永逸不用换链接！
output_filename = "老杨TV全量版.json"
output_path = f"datas/{output_filename}"
print(f"🎯 最终结算 -> 目标输出固定直链：{output_filename}")

# 清理历史可能残余的带动态后缀的旧文件，归于纯净
old_files_to_clean = glob.glob('datas/老杨TV全量版*.json')
for old_f in old_files_to_clean:
    if os.path.basename(old_f) != output_filename:
        try: os.remove(old_f)
        except: pass

for garbage in glob.glob('datas/config_*.json'):
    try: os.remove(garbage)
    except: pass


# ====================================================================
# 🧠 【核心逻辑：正统 JSON 对象读取与合并逻辑】
# ====================================================================
def load_json_safe(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
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
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"

# 精准插入“乡村电视”到直播数组
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
# 🚀 数组大合并：海豚 ➡️ 老张 ➡️ cnb 基座
# ====================================================================
cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

json_cnb["sites"] = haitun_sites + lz_nsfw_list + cnb_sites
json_cnb["lives"] = haitun_lives + cnb_lives

# 转换为文本后进行基础清洗与特调
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

# ====================================================================
# 🛡️ 硬核升华：解析/网络棧優化與「點播+直播」雙重數字密碼鎖實裝
# ====================================================================
try:
    final_obj = json.loads(final_json_text)
    
    # 1. 注入 DoH 加密 DNS（防運營商污染與劫持） 
    final_obj["doh"] = [
        {
            "name": "阿里 DNS",
            "url": "https://dns.alidns.com/dns-query",
            "ips": ["223.5.5.5", "223.6.6.6"]
        },
        {
            "name": "騰訊 DNS",
            "url": "https://doh.pub/dns-query",
            "ips": ["119.29.29.29"]
        }
    ]
    
    # 2. 升級 parses：在最前端強行注入「超級並行解析專線」，大幅提升加載秒播率 
    parallel_parse = {
        "name": "🚀 老楊專屬 • 聚合秒播專線",
        "type": 4,
        "url": "Parallel"
    }
    final_obj["parses"] = [parallel_parse] + final_obj.get("parses", [])
    
    # 3. 實裝【點播站點密碼鎖】：遍歷所有點播站點，為敏感/特殊源加鎖 [cite: 492, 493, 509]
    for site in final_obj.get("sites", []):
        site_name = site.get("name", "")
        # 匹配成人站點、磁力站點或特定的盤搜站點進行點播鎖定
        if "🔞" in site_name or "磁力" in site_name or "搜索" in site_name or "4K" in site_name:
            site["pass"] = current_token  # 注入4位純數字密碼 [cite: 511, 543]
            clean_sname = site_name.split("｜")[0].replace("🦋", "").strip()
            site["name"] = f"🦋 {clean_sname} ｜🔑本月暗號鎖"

    # 4. 實裝【直播分組密碼鎖】：遍歷所有直播源，為成人源或全量源加鎖 [cite: 584, 586, 617]
    for live in final_obj.get("lives", []):
        live_name = live.get("name", "")
        if "🔞" in live_name or "各大源合集" in live_name or "午夜剧场" in live_name:
            live["pass"] = current_token  # 直播源上鎖 [cite: 620, 622]
            clean_lname = live_name.split("｜")[0].strip()
            live["name"] = f"{clean_lname} ｜🔑群內獲取解鎖暗號"

    # 5. 生成精美的動態開機公告與聲明，直接展示密碼
    thanks_warning = "👑 特别致谢与版权声明\n本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\n🐋 感谢鱼佬的付出\n源码基础与发布主页: fish2018/webhtv\nTelegram 官方群组: 👉 https://t.me/webhtv\n 感谢佬的付出\n核心仓库主页: FGBLH/GHK\nTelegram 官方群组: 👉 https://t.me/hshsjk9"
    welcome_notice = f"👑 歡迎使用【老楊TV粉絲專屬縫合專線】！🚨 核心安全提示：本月核心點播站點與直播分組的解鎖密碼為：【{current_token}】（每月1號全自動洗牌）。輸入一次即可完美記錄，無需重輸！如果斷流請及時回 Telegram 頻道（@huliys9）或微信群獲取最新動態！"

    final_obj["notice"] = welcome_notice
    final_obj["warningText"] = thanks_warning
    
    # 調整頂層欄位順序
    ordered_obj = {}
    if "notice" in final_obj: ordered_obj["notice"] = final_obj.pop("notice")
    if "warningText" in final_obj: ordered_obj["warningText"] = final_obj.pop("warningText")
    ordered_obj.update(final_obj)
    
    # 🦋 保持其餘未加鎖站點的蝴蝶美化邏輯
    for site in ordered_obj.get("sites", []):
        if "name" in site and "🔑" not in site["name"]:
            name_val = site["name"]
            for char in ['丨', '┃', ' ']:
                name_val = name_val.strip(char)
            name_val = re.sub(r'\s+', ' ', name_val)
            if not name_val.startswith("🦋"):
                site["name"] = f"🦋 {name_val}"

    # 🌟 寫出最終固定的完美全量版配置
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 全量加密版更新成功！配置已安全落盤至: {output_path}")

except Exception as e:
    print(f"❌ 严重错误：最后的本地渲染失败，原因: {e}")

# 双重保险
if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
