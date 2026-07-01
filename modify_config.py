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

# 控制開關和追蹤器檔案路徑
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

# 1. 嘗試讀取現有的開關狀態 (格式為 \"月份-3位密碼\"，例如 \"7-k9x\")
if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            # 如果裡面是老腳本留下的純文本或舊密碼
            saved_code = content

# 🎯 判定：如果是 1 號，且記錄的月份不是當前月份（說明是當月第一次跑，跨月了）
if is_reset_day and saved_month != current_month:
    # 隨機生成 3 位新隨機後綴
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    # 寫入當前月份和新密碼，例如 \"7-k9x\"
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【每月1號全新硬核洗牌】檢測到進入新月份 {current_month} 月！已全自動抽籤生成本月新後綴: {current_token}")

# 🎯 判定：如果是 1 號的第二次及後續運行
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全閥攔截】今日 1 號已經是當月第二次運行，保持原暗號: {current_token}")

# 🎯 平常日子
else:
    # 如果平時發現開關空了，或者裡面還是舊的不帶月份的密碼，立刻初始化
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月密鎖後綴: {current_token}")

# 3. 🎯 嚴格判定最終輸出之檔名
if current_token in ["全量版", "纯净版"]:
    output_filename = "老杨TV全量版.json"
else:
    output_filename = f"老杨TV全量版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 最終結算 -> 目標輸出檔名：{output_filename}")


# ====================================================================
# 🛡️ 【金蝉脱壳：全量版过期旧线自动全文字大轰炸 - 沿用原脚本提示】
# ====================================================================
old_configs = glob.glob('datas/老杨TV全量版*.json') + glob.glob('datas/老杨TV*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            trap_json = {
                "spider": "", 
                "notice": f"⚠️ 警告：當前專線已過期斷流！老連結已徹底作廢！\n\n最新全量版連結或當前密碼請加QQ群“532637640”獲取",
                "warningText": "👑 特別提示：加QQ群“532637640”獲取最新接口",
                "sites": [
                    {"key": "老杨纯文字提示", "name": "🚨 請前往QQ群“532637640”獲取最新密碼🚨 當前專線密碼已過期斷流！", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                    {"key": "老杨纯文字提示2", "name": "🚨 請前往QQ群“532637640”獲取最新全量版連結", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                ],
                "lives": [
                    {"group": "🚨 接口過期斷流 ｜ 提示", "channels": [{"name": "👉 線路已過期 ➡️ 加QQ群“532637640”獲取最新全量版密碼", "urls": ["http://127.0.0.1"]}]}
                ]
            }
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
            print(f"📡 【金蟬脫殼】已成功將過期舊線調包為純文字大轟炸: {old_file}")
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
            print(f"❌ 錯誤：{path} JSON 格式不正確！無法解析。")
            return {}

json_cnb = load_json_safe(cnb_path)
json_haitun = load_json_safe(haitun_path)
json_lz = load_json_safe(lz_path)

haitun_sites = json_haitun.get("sites", [])
haitun_lives = json_haitun.get("lives", [])
lz_sites = json_lz.get("sites", [])

# 過濾老張源裡的 🔞 站點並轉換為絕對路徑
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

# 給海豚源打上後綴標籤
for item in haitun_sites:
    if "name" in item: item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item: item["name"] = f"{item['name']}｜Tg：@huliys9"

# 精準插入“鄉村電視”到直播陣列索引 5（第 6 位）
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
# 🚀 数组大合并：海豚排上面 ➡️ 中间接老张 ➡️ 最后接 cnb
# ====================================================================
cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

json_cnb["sites"] = haitun_sites + lz_nsfw_list + cnb_sites
json_cnb["lives"] = haitun_lives + cnb_lives

# 轉換為文本後進行清洗與特調
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

# 開機公告注入 (原汁原味保留老楊TV公告)
thanks_warning = "👑 特别致谢与版权声明\n本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\n🐋 感谢鱼佬的付出\n源码基础与发布主页: fish2018/webhtv\n版本发布绝对地址: fish2018/webhtv/releases\nTelegram 官方群组: 👉 https://t.me/webhtv\n 感谢佬的付出\n核心仓库主页: FGBLH/GHK\n数据源直链地址: FGBLH/GHK/.json\nTelegram 官方群组: 👉 https://t.me/hshsjk9"
welcome_notice = "👑 欢迎使用【老杨TV粉丝专属缝合专线】！本接口由老杨TV结合佬&鱼佬的优质核心资源缝合而成，纯净无广告！🚨 核心秒播優化版已啟用：網絡棧已實裝 DoH 加密防污染與超級並行解析，遇到線路卡頓請及時回 Telegram 頻道（@huliys9）或微信群獲取當前最新動態！"

try:
    final_obj = json.loads(final_json_text)
    
    # ====================================================================
    # ⚡ 【硬核特調注入：實裝高階秒播骨架與規範優化】
    # ====================================================================
    
    # 1. 升級 DoH 加密 DNS 網絡棧（精準注入 Bootstrap IPs，阻斷查詢污染死循環）
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
    
    # 2. 升級 parses：強行在解析規則最前端注入「超級並行秒播專線」（type: 4）
    parallel_parse = {
        "name": "🚀 老楊專屬 • 聚合秒播專線 (超級並行)",
        "type": 4,
        "url": "Parallel"
    }
    final_obj["parses"] = [parallel_parse] + final_obj.get("parses", [])
    
    # 3. 修正 sites 內的語法欄位（修正 彈幕 spider 欄位、清理 type=1 的過濾多餘屬性）
    for site in final_obj.get("sites", []):
        if site.get("key") == "leo_danmaku":
            site["indexs"] = 1 # 修正鍵名規範
            if "index" in site: site.pop("index")
        if site.get("type") == 1 and "filterable" in site:
            site.pop("filterable") # 依官方高階架構精簡非原生屬性

    # 4. 擴充 lives 高階屬性：動態精準為主要直播頻道群注入動態 EPG 節目單與時區表
    for live in final_obj.get("lives", []):
        lname = live.get("name", "")
        if "綜合直播" in lname or "地方直播" in lname or "各大源合集" in lname:
            live["epg"] = "https://epg.112114.xyz/?ch={name},https://epg.pw/xmltv/assets/china.xml.gz"
            live["timeZone"] = "Asia/Shanghai"
        elif "台灣台" in lname or "港台" in lname:
            live["epg"] = "https://epg.pw/xmltv/assets/taiwan.xml.gz"
            live["timeZone"] = "Asia/Taipei"

    # 5. 修正 IJK 播放器內核參數：將緩存過長導致黑屏斷流的過期快取縮短為健康的 60 秒
    for player in final_obj.get("ijk", []):
        for option in player.get("options", []):
            if option.get("name") == "dns_cache_timeout":
                option["value"] = "60000000" # 由 6億 修正為 6千萬（60秒）

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
        print(f"⚠️ 提示：美化蝴蝶圖案時跳過，原因: {inner_e}")

    # 🌟【前置寫入】強制安全落盤
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 全量版秒播優化配置更新成功！檔案已寫出至: {output_path}")

except Exception as e:
    print(f"❌ 嚴重錯誤：最後的本地渲染失敗，原因: {e}")

# 🌟 雙重保險
if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
