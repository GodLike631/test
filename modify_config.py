import os
import re
import random
import string
import glob
import datetime
import json
import urllib.request

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
lz_path = 'datas/lz.json'

lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# ⏰ 【4位纯数字动态密码锁自适应洗牌逻辑】
# ====================================================================
today = datetime.datetime.now()
current_month = str(today.month) 
is_reset_day = (today.day == 1)

saved_month = ""
saved_code = ""

if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            saved_code = content

if is_reset_day and saved_month != current_month:
    current_token = ''.join(random.choices(string.digits, k=4))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【進入新月份】已全自动抽签生成本月 4 位純數字新密锁: {current_token}")
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全阀】今日 1 号已运行过，保持本月暗号: {current_token}")
else:
    if not saved_code or len(saved_code) != 4 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.digits, k=4))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月數字密锁: {current_token}")

output_filename = "老杨TV全量版.json"
output_path = f"datas/{output_filename}"

# ====================================================================
# 🧠 【正统 JSON 对象读取与纯净清洗】
# ====================================================================
def load_json_safe(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except: return {}

# 網絡TXT遠端流解析為內嵌 JSON Channel 的核心工具
def parse_txt_to_channels(url_or_path):
    channels = []
    try:
        if url_or_path.startswith("http"):
            req = urllib.request.Request(url_or_path, headers={'User-Agent': 'okhttp'})
            content = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        else:
            if not os.path.exists(url_or_path): return []
            content = open(url_or_path, 'r', encoding='utf-8', errors='ignore').read()
            
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or "#genre#" in line or "," not in line: continue
            name, urls_str = line.split(",", 1)
            urls = urls_str.split("#")
            channels.append({"name": name.strip(), "urls": [u.strip() for u in urls if u.strip()]})
    except Exception as e:
        print(f"⚠️ 解析外部直播流失敗: {url_or_path}, 原因: {e}")
    return channels

json_cnb = load_json_safe(cnb_path)
json_haitun = load_json_safe(haitun_path)
json_lz = load_json_safe(lz_path)

haitun_sites = json_haitun.get("sites", [])
haitun_lives = json_haitun.get("lives", [])
lz_sites = json_lz.get("sites", [])

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

for item in haitun_sites:
    if "name" in item: item["name"] = f"{item['name']}｜Tg：@huliys9"

# 大合併基座
json_cnb["sites"] = haitun_sites + lz_nsfw_list + json_cnb.get("sites", [])

# ====================================================================
# 📺 【直播源降維打擊：外部 URL 直鏈全自動轉內嵌分組（100% 彈密碼鎖）】
# ====================================================================
embedded_groups = []

# 1. 抓取並無感嵌入「鄉村電視」（免密碼常規分組）
country_channels = parse_txt_to_channels("https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt")
if country_channels:
    embedded_groups.append({
        "name": "鄉村電視 ｜ 免密全開放頻道",
        "channel": country_channels
    })

# 2. 遍歷抓取海豚等外部直播源，並進行動態加密轉化
for live in haitun_lives:
    live_name = live.get("name", "")
    live_url = live.get("url", "")
    if not live_url: continue
    
    # 清洗名稱標籤
    clean_gname = live_name.replace("｜Tg：@huliys9", "").strip()
    
    # 核心判定：哪些分組需要被強制灌入 4 位隨機密碼鎖
    if "🔞" in live_name or "各大源合集" in live_name or "午夜剧场" in live_name:
        channels_data = parse_txt_to_channels(live_url)
        if channels_data:
            embedded_groups.append({
                "name": f"{clean_gname} ｜🔑本月暗號[{current_token}]解鎖",
                "pass": current_token,  # 注入內嵌分組強制密碼鎖！100%攔截彈窗！
                "channel": channels_data
            })
    else:
        # 普通公開分組（港台、綜合等）免密碼內嵌放行
        channels_data = parse_txt_to_channels(live_url)
        if channels_data:
            embedded_groups.append({
                "name": f"{clean_gname} ｜ 免密頻道",
                "channel": channels_data
            })

# 3. 疊加基座 cnb 自帶的 Lives
embedded_groups = embedded_groups + json_cnb.get("lives", [])
json_cnb["lives"] = [{"name": "老楊TV 縫合旗艦專線", "boot": True, "groups": embedded_groups}]

# 轉換文本進行基礎清洗
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
# 🛡️ 【網路棧優化與點播站點高階安全策略】
# ====================================================================
try:
    final_obj = json.loads(final_json_text)
    
    # 注入 DoH 加密 DNS 防污染 [cite: 497, 498]
    final_obj["doh"] = [
        {"name": "阿里 DNS", "url": "https://dns.alidns.com/dns-query", "ips": ["223.5.5.5", "223.6.6.6"]}, [cite: 498, 671, 672]
        {"name": "騰訊 DNS", "url": "https://doh.pub/dns-query", "ips": ["119.29.29.29"]} [cite: 498, 671, 672]
    ]
    
    # 注入超級並行解析 [cite: 494]
    parallel_parse = {"name": "🚀 老楊專屬 • 聚合秒播專線", "type": 4, "url": "Parallel"} [cite: 557, 560, 561, 572]
    final_obj["parses"] = [parallel_parse] + final_obj.get("parses", []) [cite: 494]
    
    # 實裝點播站點分類限制策略 [cite: 492]
    for site in final_obj.get("sites", []): [cite: 492]
        site_name = site.get("name", "") [cite: 514]
        if "🔞" in site_name or "磁力" in site_name or "搜索" in site_name or "4K" in site_name: [cite: 514]
            # 對於 type: 3 的點播，將 pass 與分類重命名相結合，高亮警示
            site["pass"] = current_token [cite: 543]
            clean_sname = site_name.split("｜")[0].replace("🦋", "").strip() [cite: 514]
            site["name"] = f"🦋 {clean_sname} ｜🔑本月數字暗號鎖" [cite: 514]

    thanks_warning = "👑 特别致谢与版权声明\n本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\n🐋 感谢鱼佬的付出\n源码基础与发布主页: fish2018/webhtv\nTelegram 官方群组: 👉 https://t.me/webhtv\n 感谢佬的付出\n核心仓库主页: FGBLH/GHK\nTelegram 官方群组: 👉 https://t.me/hshsjk9"
    welcome_notice = f"👑 歡迎使用【老楊TV粉絲專屬縫合專線】！🚨 核心安全提示：本月核心點播站點與直播分組的解鎖密碼為：【{current_token}】（每月1號全自動洗牌）。輸入一次即可完美記錄，無需重輸！如果斷流請及時回 Telegram 頻道（@huliys9）或微信群獲取最新動態！" [cite: 490]

    final_obj["notice"] = welcome_notice [cite: 490]
    final_obj["warningText"] = thanks_warning
    
    ordered_obj = {}
    if "notice" in final_obj: ordered_obj["notice"] = final_obj.pop("notice") [cite: 490]
    if "warningText" in final_obj: ordered_obj["warningText"] = final_obj.pop("warningText")
    ordered_obj.update(final_obj)
    
    for site in ordered_obj.get("sites", []): [cite: 492]
        if "name" in site and "🔑" not in site["name"]: [cite: 514]
            name_val = site["name"] [cite: 514]
            for char in ['丨', '┃', ' ']: name_val = name_val.strip(char)
            name_val = re.sub(r'\s+', ' ', name_val)
            if not name_val.startswith("🦋"): site["name"] = f"🦋 {name_val}" [cite: 514]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 全量加密版更新成功！配置已寫出至: {output_path}")

except Exception as e:
    print(f"❌ 严重错误：最后的本地渲染失败，原因: {e}")

if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
