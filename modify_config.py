import os
import re
import random
import string
import glob
import datetime
import json
import urllib.request
import urllib.parse

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
lz_path = 'datas/lz.json'

# 控制开关和追踪器文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# 🎛️ 【上游海豚仓库 - 智能化全自动检索与手动控制中心】
# ====================================================================
# 💡【手动控制权 1】：如果你手动发现了确切的最新完整下载链接，请填在这里（如不为空，则雷打不动优先走它）
# 平时请保持空字符串 ""，脚本即会自动开启硬核 API 实时精准抓取。
HAITUN_MANUAL_URL = ""

# 💡【手动控制权 2】：固定不变或你手动更改的 GitHub Raw 基础下载路径前缀
HAITUN_BASE_DOWNLOAD_URL = "https://raw.githubusercontent.com/FGBLH/HKL/refs/heads/main/"

# 📡 【API 检索路径】：用于拉取根目录文件列表的 GitHub 官方接口
HAITUN_API_URL = "https://api.github.com/repos/FGBLH/HKL/contents/"


def fetch_haitun_filename_via_api():
    """
    通过 GitHub API 实时获取远程仓库文件列表（带 Token 认证与四重条件过滤版）
    """
    try:
        print("📡 正在调用 GitHub API 检索海豚仓库最新文件列表...")
        
        # 从 Actions 环境变量中获取安全令牌（在 workflow yml 中配置传入）
        token = os.environ.get("MY_GITHUB_TOKEN")
        
        req = urllib.request.Request(
            HAITUN_API_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        # 如果存在令牌，则注入认证头，将匿名限制直接飙升到每小时 5000 次，彻底防超限
        if token:
            req.add_header('Authorization', f'token {token}')
            print("🔑 [安全认证] 已成功挂载 GITHUB_TOKEN 凭据，解除 API 频次限制。")
        else:
            print("⚠️ [匿名警告] 未检测到环境变量中的 Token，正以匿名模式请求（易触发额度超限）。")

        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status == 200:
                files_list = json.loads(response.read().decode('utf-8'))
                
                # 🎯 精准多重条件筛选
                for file_info in files_list:
                    file_name = file_info.get("name", "")
                    
                    # 条件 1：必须以 .json 结尾
                    if not file_name.endswith(".json"):
                        continue
                        
                    # 条件 2：名字里必须包含“海豚”
                    if "海豚" not in file_name:
                        continue
                        
                    # 条件 3：【强力拦截】精准排除包含 “py”、“无18”、“鱼壳” 的干扰测试项
                    if "py" in file_name.lower() or "无18" in file_name or "鱼壳" in file_name:
                        print(f"🚫 [已自动跳过干扰项]: {file_name}")
                        continue
                    
                    # 🎯 突破所有防线，剩下的就是最纯正的 OK海豚 变体主线
                    return file_name
    except Exception as e:
        print(f"⚠️ GitHub API 请求失败（可能触发匿名限制或网络波动）: {e}")
    return None


def load_haitun_with_smart_fallback(file_path):
    """
    海豚接口专属加载器：结合手动指定、API精准检索以及本地历史兜底的完美闭环
    """
    remote_data = None
    chosen_url = ""

    # ---- 🛑 第一阶段：尝试获取远程地址 ----
    # 优先检测是否配置了【手动指定URL】
    if HAITUN_MANUAL_URL.strip():
        chosen_url = HAITUAL_URL.strip()
        print(f"👑 [手动控制触发] 优先采用你手动硬编码指定的下载链接: {chosen_url}")
    else:
        # 没有手动指定，启动 API 盲搜索
        real_filename = fetch_haitun_filename_via_api()
        if real_filename:
            print(f"🎯 [精准捕获] 探测到海豚仓库今日实际主线文件名为: 【{real_filename}】")
            encoded_name = urllib.parse.quote(real_filename)
            chosen_url = f"{HAITUN_BASE_DOWNLOAD_URL}{encoded_name}"

    # ---- 📥 第二阶段：发起内容下载 ----
    if chosen_url:
        try:
            print(f"📥 正在从目标地址下载海豚数据: {chosen_url}")
            download_req = urllib.request.Request(
                chosen_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(download_req, timeout=10) as response:
                if response.status == 200:
                    remote_data = json.loads(response.read().decode('utf-8'))
                    
                    # 💡 下载成功：顺手写入本地缓存，留作日后无感兜底
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(remote_data, f, ensure_ascii=False, indent=4)
                    print(f"✅ 远程数据同步成功，已刷新本地缓存: {file_path}")
                    return remote_data
        except Exception as e:
            print(f"⚠️ 虽锁定了下载地址，但尝试读取内容时失败（可能该手动链接已失效或网络超时）: {e}")

    # ---- 🛟 第三阶段：全自动降级兜底 ----
    if os.path.exists(file_path):
        print(f"🛟 [🔥 容错触发] 远程同步无果，成功启用本地历史留存文件进行缝合: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                print(f"❌ 错误：本地缓存文件 {file_path} 损坏。")
                return {}
    else:
        print(f"❌ [严重警告] 既无法连接远程，本地也无历史缓存: {file_path}")
        return {}


# ====================================================================
# ✍️ 【通道一：老杨专属点播手工加线区】
# 提示：想单独加点播爬虫线贴在这里，如果上游有同 key 线路，脚本会自动蒸发上游、以此处为准。
# ====================================================================
MY_CUSTOM_SITES = [
    {
        "key": "山楂影视",
        "name": "山楂影视.py", 
        "type": 3,
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E5%B1%B1%E6%A5%82%E5%BD%B1%E8%A7%86.py",
        "searchable": 1,
        "quickSearch": 1
    },
    {
        "key": "红果短剧",
        "name": "红果短剧.py", 
        "type": 3,
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E7%BA%A2%E6%9E%9C%E7%9F%AD%E5%89%A7.py",
        "searchable": 1,
        "quickSearch": 1
    }
]

# ====================================================================
# 📺 【通道二：老杨专属直播手工加线区（从第 6 位开始正向依序后排）】
# 提示：乡村电视已完美收录！第一个手工源(乡村电视)占第 6 位，第二个(最新电影)自动顺延排第 7 位！
# 如果手工加的直播线路名字与上游重复，脚本会自动触发“特权锁”全自动蒸发上游同名源！
# 🌟 特别规则：若线路名称中含有 🔞，则放弃前排特权，自动融入大池子并追加到末尾进行沉底。
# ====================================================================
MY_CUSTOM_LIVES = [
    {
        "name": "乡村电视 ｜Tg：@huliys9",
        "type": 0,
        "playerType": 2,
        "ua": "okhttp/5.3.2",
        "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
    },
    {
        "name": "最新电影｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/Ly_18/refs/heads/main/datas/%E6%9C%80%E6%96%B0%E7%94%B5%E5%BD%B1.m3u"
    },
    {
        "name": "Kimentanm",
        "type": 0,
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
        "playerType": 2
    },
    {
      "name": "综合直播",
      "type": 0,
      "playerType": 2,
      "url": "https://ghfast.top/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt",
      "ua": "bingcha/1.1 (mianfeifenxiang) "
    },
    {
        "name": "央卫TV｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "http://47.120.41.246:8025/vip/jar/zb.php"
    },
    {
        "name": "超稳定流畅｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E8%B6%85%E7%A8%B3%E5%AE%9A%E6%B5%81%E7%95%85.txt"
    },
    {
        "name": "国产直播🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%9B%B4%E6%92%AD_20260417_024507.m3u"
    },
    {
        "name": "国产精品🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%B2%BE%E5%93%81_20260417_024507.m3u"
    },
    {
        "name": "4K福利🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/4k%E7%A6%8F%E5%88%A9.m3u"
    },
    {
        "name": "探花🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E6%8E%A2%E8%8A%B1%E7%BA%A6%E7%82%AE_20260417_024507.m3u"
    },
    {
        "name": "欧美🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/%E6%AC%A7%E7%BE%8E%E9%A2%91%E9%81%93.m3u"
    },
    {
        "name": "咪咕｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://develop202.github.io/migu_video/interface.txt"
    }
]

# ====================================================================
# ⏰ 【每月 1 号自动大洗牌与控制开关自动生成逻辑】 (原汁原味保留)
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
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【每月1号全新硬核洗牌】检测到进入新月份 {current_month} 月！已全自动抽签生成本月新密锁: {current_token}")
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全阀拦截】今日 1号已经是当月第二次运行，保持原暗号: {current_token}")
else:
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月密锁: {current_token}")

if current_token in ["全量版", "纯净版"]:
    output_filename = "老杨TV全量版.json"
else:
    output_filename = f"老杨TV全量版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 最终结算 -> 目标输出：{output_filename}")

# ====================================================================
# 🛡️ 【金蝉脱壳：全量版过期旧线自动全文字大轰炸】 (原汁原味保留)
# ====================================================================
old_configs = glob.glob('datas/老杨TV全量版*.json') + glob.glob('datas/老杨TV*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            trap_json = {
                "spider": "", 
                "notice": f"⚠️ 警告：当前专线已过期断流！老链接已彻底作废！\n\n最新全量版链接或当前密码请加QQ群“532637640”获取",
                "sites": [
                    {"key": "老杨纯文字提示", "name": "🚨 请前往QQ群“532637640”获取最新密码🚨 当前专线密码已过期断流！", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                    {"key": "老杨纯文字提示2", "name": "🚨 请前往QQ群“532637640”获取最新全量版链接", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                ],
                "lives": [
                    {"group": "🚨 接口过期断流 ｜ 提示", "channels": [{"name": "👉 线路已过期 ➡️ 加QQ群“532637640”获取最新全量版密码", "urls": ["http://127.0.0.1"]}]}
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
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"❌ 错误：{path} JSON 格式不正确！无法解析。")
            return {}

# 常规且路径固定的上游加载
json_cnb = load_json_safe(cnb_path)
json_lz = load_json_safe(lz_path)

# 🚀 海豚接口：直接调用全新升级的智能化 API 检索与历史兜底加载器
json_haitun = load_haitun_with_smart_fallback(haitun_path)

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
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"

cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

# 🎯 直接安全地收集上游所有原本的解析器（parses）
combined_parses = json_haitun.get("parses", []) + json_lz.get("parses", []) + json_cnb.get("parses", [])

# ➕ 【手工特权点播去重锁】智能检测上游，若有冲突，物理蒸发上游重名 key 线路
custom_keys = {site.get("key") for site in MY_CUSTOM_SITES if site.get("key")}
upstream_sites = haitun_sites + lz_nsfw_list + cnb_sites
clean_upstream_sites = [site for site in upstream_sites if site.get("key") not in custom_keys]
json_cnb["sites"] = clean_upstream_sites + MY_CUSTOM_SITES

# ➕ 【手工特权直播去重锁 & 从第6位正向依序后排核心算法】
custom_live_names = {live.get("name") for live in MY_CUSTOM_LIVES if live.get("name")}
base_lives = haitun_lives + cnb_lives

# 🛠️ 核心修改：同时清洗并剔除名称中带有“日本女优”或“日本女友”的上游直播线路
clean_base_lives = [
    live for live in base_lives 
    if live.get("name") not in custom_live_names 
    and "日本女优" not in live.get("name", "") 
    and "日本女友" not in live.get("name", "")
]

# 🛠️ 核心修改：使用正向切片递增算法。如果手工直播源带 🔞 则不占前排，直接归入大池子末尾。
inserted_count = 0  # 追踪真正插入前排的手工源数量，确保后排递增索引连续
for custom_live in MY_CUSTOM_LIVES:
    live_name = custom_live.get("name", "")
    if "🔞" in live_name:
        # 带有 🔞 的线路：不给前排特权，直接融入大池子追加到末尾
        clean_base_lives.append(custom_live)
    else:
        # 普通线路：依然享受原规则，从第 6 位（索引 5）开始正向依序插入
        insert_idx = 5 + inserted_count
        if len(clean_base_lives) >= insert_idx:
            clean_base_lives.insert(insert_idx, custom_live)
        else:
            clean_base_lives.append(custom_live)
        inserted_count += 1

json_cnb["lives"] = clean_base_lives

final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)

final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"')
final_json_text = final_json_text.replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"')

final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '')

path_replacements = {
    './spider.jar': 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar',
    './XBPQ/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/',
    './XYQHiker': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/',
    './js/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/',
    './json/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/',
    './py/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/',
    'http://127.0.0.1:9978/file/TVBox/logo.png': 'https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg'
}
for src, dst in path_replacements.items():
    final_json_text = final_json_text.replace(src, dst)

thanks_warning = "\n\n👑如果遇到失效 or 断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！ "
welcome_notice = "👑 欢迎使用【老杨TV粉丝专属缝合专线】！本接口由老杨TV结合佬&鱼佬的优质核心资源缝合而成，纯净无广告！🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效 or 断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！"

try:
    final_obj = json.loads(final_json_text)
    final_obj["notice"] = welcome_notice + thanks_warning
    if "warningText" in final_obj:
        final_obj.pop("warningText")
    
    ordered_obj = {}
    if "notice" in final_obj: 
        ordered_obj["notice"] = final_obj.pop("notice")
        
    ordered_obj.update(final_obj)
    
    # ====================================================================
    # 🌟【全新深度体验优化区】
    # ====================================================================
    try:
        # --- 1. 去重并保留所有合法的傳統解析站點 ---
        unique_parses = []
        seen_names = set()
        for p in combined_parses:
            name = p.get("name", "")
            if name and name not in seen_names:
                unique_parses.append(p)
                seen_names.add(name)
        ordered_obj["parses"] = unique_parses

        # --- 2. 注入国内高防 AliDNS 到 doh 并修复原有拼写错误 ---
        if "doh" in ordered_obj and isinstance(ordered_obj["doh"], list):
            for doh_item in ordered_obj["doh"]:
                if doh_item.get("url", "").endswith("/dns-quer"):
                    doh_item["url"] = doh_item["url"] + "y"
            
            ali_doh = {
                "name": "AliDNS",
                "url": "https://dns.alidns.com/dns-query",
                "ips": ["223.5.5.5", "223.6.6.6"]
            }
            if not any(d.get("name") == "AliDNS" for d in ordered_obj["doh"]):
                ordered_obj["doh"].insert(0, ali_doh)

        # --- 3. 全面注入通用高级影音防屏蔽去广告 JS 脚本 ---
        custom_js_rules = [
            "console.log('老楊TV高級WebView攔慢器啟動');",
            "window.addEventListener('DOMContentLoaded', function() {",
            "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });",
            "   Function.prototype.__constructor__ = Function.prototype.constructor;",
            "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };",
            "});",
            "setInterval(() => { let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]']; selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); }); }, 400);"
        ]

        current_rules = ordered_obj.get("rules", [])
        if not isinstance(current_rules, list):
            current_rules = []
            
        ad_hosts = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"]
        for rule in current_rules:
            if isinstance(rule, dict) and "hosts" in rule:
                for h in rule["hosts"]:
                    if h not in ad_hosts: ad_hosts.append(h)

        js_injection_rule = {
            "name": "老楊TV·雲端高級去广告JS注入",
            "hosts": ad_hosts,
            "script": custom_js_rules
        }
        ordered_obj["rules"] = [js_injection_rule] + [r for r in current_rules if r.get("name") != "老楊TV·雲端高級去广告JS注入"]

        # --- 4. 彻底移除直播 lives 末尾的无用空对象并统一重写补齐 OkHttp 头部并覆盖手工直播源 ---
        if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list):
            clean_lives = []
            for live in ordered_obj["lives"]:
                if live and isinstance(live, dict):
                    if not live.get("ua") or live.get("ua") == "okhttp":
                        live["ua"] = "okhttp/5.3.2"
                    clean_lives.append(live)
            ordered_obj["lives"] = clean_lives

        # --- 5 & 6. 🏆【核心重写：九大方阵智能归类洗牌 与 热播影视精准置顶长鸣谢算法】 ---
        block_1_rebo = []         # 1. 🏆 热播影视专属置顶方阵 (仅限 key: 热播影视)
        block_2_yingshi = []      # 2. 影视/追剧/APP大类
        block_3_duanju = []       # 3. 短剧/剧场
        block_4_dongman = []      # 4. 动漫类
        block_5_cili = []         # 5. 网盘/磁力/4K (未配Token不加载特性)
        block_6_tiyu = []         # 6. 体育/看球/直播
        block_7_shaoer = []       # 7. 少儿课堂/教育
        block_8_yinyue = []       # 8. 音乐/听书/功能线/DJ
        block_9_fuli = []         # 9. 福利/18禁 (绝对大沉底)

        tg_tail_count = 0

        for site in ordered_obj.get("sites", []):
            if "name" not in site:
                continue
                
            raw_name = site["name"]
            s_key = site.get("key", "")
            s_genre = site.get("genre", "")
            s_api = site.get("api", "")

            # 🛠️ 1. 清浅名称里的脏字符
            for char in ['丨', '┃', ' ']:
                raw_name = raw_name.strip(char)
            raw_name = re.sub(r'\s+', ' ', raw_name)
            
            if "｜Tg：@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg：@huliys9", "").strip()
            elif "｜Tg:@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg:@huliys9", "").strip()

            if "ext" in site and site["ext"] == {}:
                site["ext"] = ""

            # 🛠️ 2. 【核心大招】网盘组件强行去后缀洗白！实现未配Token不展示网盘的特性
            if isinstance(s_api, str) and "PanWebShare" in s_api:
                site["api"] = "csp_PanWebShare"
                if "jar" in site:
                    site.pop("jar")

            # 🛠️ 3. 瓜子靶向保护：防误伤，强力摘出
            is_guazi = "瓜子" in raw_name or "GZ" == s_key

            # 🛠️ 4. 精准捕获福利关键字（排除瓜子后）
            is_nsfw = False if is_guazi else ("🔞" in raw_name or "色播" in raw_name or "av" in s_key.lower() or "瓜" in raw_name or "爆料" in raw_name or "chat" in raw_name.lower() or "cam" in raw_name.lower() or "panda" in raw_name.lower() or "video" in raw_name.lower() or "md" in s_key.lower())

            # 🛠️ 5. 【靶向精准连坐解除】唯一锁定主线 "key": "热播影视"
            is_target_rebo_main = (s_key == "热播影视")

            # 🛠️ 6. 彻底完成洗牌分流与名字特调
            if is_target_rebo_main:
                # 🎯 唯独将“热播影视”注入大长鸣谢声明，推入置顶第一位 block_1
                site["name"] = "热播 • APP｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"
                site["category"] = "综合"
                block_1_rebo.append(site)

            elif "豆瓣" in raw_name and "首页" in raw_name:
                # 豆瓣解绑：恢复其原本清净名，退回普通影视区 block_2
                site["name"] = "🦋 豆瓣 • 首页"
                site["category"] = "综合"
                site["searchable"] = 0
                block_2_yingshi.append(site)

            elif is_nsfw:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "福利"
                block_9_fuli.append(site)
                
            elif "短剧" in raw_name or "剧场" in raw_name:
                # 包含 DJ/dj 关键词的线一律强行分流进入音乐阵营
                if "dj" in raw_name.lower() or "dj" in s_key.lower():
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                    site["name"] = raw_name
                    site["category"] = "音乐"
                    site["searchable"] = 0
                    block_8_yinyue.append(site)
                else:
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                    site["name"] = raw_name
                    site["category"] = "短剧"
                    site["genre"] = "shortdrama"
                    block_3_duanju.append(site)
                
            elif "动漫" in raw_name or "新番" in raw_name or "anime" in s_key.lower() or "a1" in raw_name.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "动漫"
                block_4_dongman.append(site)
                
            elif "磁力" in raw_name or "索" in raw_name or "盘" in raw_name or "云盘" in raw_name or "4k" in raw_name.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "网盘/磁力"
                if "PanWebShare" in site.get("api", ""):
                    site["changeable"] = 1
                block_5_cili.append(site)
                
            elif "体育" in raw_name or "球" in raw_name or "直播" in raw_name:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "体育/直播"
                block_6_tiyu.append(site)
                
            elif "少儿" in raw_name or "课堂" in raw_name or "教学" in raw_name or "教育" in raw_name:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "少儿"
                site["searchable"] = 0
                block_7_shaoer.append(site)
                
            elif "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "唱会" in raw_name or "fm" in raw_name.lower() or "相声" in raw_name or "小品" in raw_name or "戏曲" in raw_name or "推送" in raw_name or "配置" in raw_name or "版本" in raw_name or "本地" in raw_name or "dj" in raw_name.lower() or "dj" in s_key.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                if "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "fm" in raw_name.lower() or "dj" in raw_name.lower() or "dj" in s_key.lower():
                    site["category"] = "音乐"
                else:
                    site["category"] = "综合"
                site["searchable"] = 0
                block_8_yinyue.append(site)
                
            else:
                # 默认影视大类（包含名称带瓜子APP、视频、以及保留原地归类的 "key": "rb" 线路）
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "综合"
                block_2_yingshi.append(site)

            # 🛠️ 7. 补齐非音乐少儿类的全局搜索功能开关
            if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site:
                site["searchable"] = 1

        # 🛠️ 8. 爱奇艺官方名称规格对齐
        for site in block_2_yingshi:
            if site.get("key") == "AQY":
                site["name"] = "🦋 爱奇艺 ｜Tg：@huliys9"

        # 👑 【新首页硬组装】"key": "热播影视" 携长致谢完美置顶（Index 0），另一个热播"key": "rb"正常随大部队在影视区排列
        ordered_obj["sites"] = (
            block_1_rebo +         
            block_2_yingshi +      
            block_3_duanju +       
            block_4_dongman +      
            block_6_tiyu +         
            block_7_shaoer +       
            block_8_yinyue +       
            block_5_cili +         
            block_9_fuli           
        )
        print(f"🚀 【洗牌结算】靶向隔离重排成功！\"key\": \"热播影视\" 已锁定置顶，\"key\": \"rb\" 线路已安稳保留在其原有的影视分类位置。")

    except Exception as inner_e:
        print(f"⚠️ 提示：美化与智能重排阶段跳过，reason: {inner_e}")

    # ====================================================================
    # 🌟【数据安全落盘】
    # ====================================================================
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 全量版更新成功！配置已写出至: {output_path}")

except Exception as e:
    print(f"❌ 严重错误：最后的本地渲染失败，原因: {e}")

if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
