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
        chosen_url = HAITUN_MANUAL_URL.strip()
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
# ✍️ 【通道一：老杨专属点播手工加线区】 [cite: 1]
# 提示：想单独加点播爬虫线贴在这里，如果上游有同 key 线路，脚本会自动蒸发上游、以此处为准。 [cite: 1]
# ====================================================================
MY_CUSTOM_SITES = [
    {
        "key": "山楂影视", [cite: 1]
        "name": "山楂影视.py",  [cite: 1]
        "type": 3, [cite: 1]
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E5%B1%B1%E6%A5%82%E5%BD%B1%E8%A7%86.py", [cite: 1]
        "searchable": 1, [cite: 1]
        "quickSearch": 1 [cite: 1]
    },
    {
        "key": "红果短剧", [cite: 2]
        "name": "红果短剧.py",  [cite: 2]
        "type": 3, [cite: 2]
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E7%BA%A2%E6%9E%9C%E7%9F%AD%E5%89%A7.py", [cite: 2]
        "searchable": 1, [cite: 2]
        "quickSearch": 1 [cite: 2]
    }
]

# ====================================================================
# 📺 【通道二：老杨专属直播手工加线区（从第 6 位开始正向依序后排）】 [cite: 2]
# 提示：乡村电视已完美收录！第一个手工源(乡村电视)占第 6 位，第二个(最新电影)自动顺延排第 7 位！ [cite: 2]
# 如果手工加的直播线路名字与上游重复，脚本会自动触发“特权锁”全自动蒸发上游同名源！ [cite: 2]
# 🌟 特别规则：若线路名称中含有 🔞，则放弃前排特权，自动融入大池子并追加到末尾进行沉底。 [cite: 2]
# ====================================================================
MY_CUSTOM_LIVES = [
    {
        "name": "乡村电视 ｜Tg：@huliys9", [cite: 2]
        "type": 0, [cite: 2]
        "playerType": 2, [cite: 3]
        "ua": "okhttp/5.3.2", [cite: 3]
        "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt" [cite: 3]
    },
    {
        "name": "最新电影｜Tg：@huliys9", [cite: 3]
        "type": 0, [cite: 3]
        "ua": "okhttp/5.3.2", [cite: 3]
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/Ly_18/refs/heads/main/datas/%E6%9C%80%E6%96%B0%E7%94%B5%E5%BD%B1.m3u" [cite: 3]
    },
    {
        "name": "Kimentanm", [cite: 3]
        "type": 0, [cite: 3]
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u", [cite: 4]
        "playerType": 2 [cite: 4]
    },
    {
      "name": "综合直播", [cite: 4]
      "type": 0, [cite: 4]
      "playerType": 2, [cite: 4]
      "url": "https://ghfast.top/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt", [cite: 4]
      "ua": "bingcha/1.1 (mianfeifenxiang) " [cite: 4]
    },
    {
        "name": "央卫TV｜Tg：@huliys9", [cite: 4]
        "type": 0, [cite: 4]
        "ua": "okhttp/5.3.2", [cite: 4]
        "url": "http://47.120.41.246:8025/vip/jar/zb.php" [cite: 4]
    },
    {
        "name": "超稳定流畅｜Tg：@huliys9", [cite: 5]
        "type": 0, [cite: 5]
        "ua": "okhttp/5.3.2", [cite: 5]
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E8%B6%85%E7%A8%B3%E5%AE%9A%E6%B5%81%E7%95%85.txt" [cite: 5]
    },
    {
        "name": "国产直播🔞｜Tg：@huliys9", [cite: 5]
        "type": 0, [cite: 5]
        "ua": "okhttp/5.3.2", [cite: 5]
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%9B%B4%E6%92%AD_20260417_024507.m3u" [cite: 5]
    },
    {
        "name": "国产精品🔞｜Tg：@huliys9", [cite: 6]
        "type": 0, [cite: 6]
        "ua": "okhttp/5.3.2", [cite: 6]
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%B2%BE%E5%93%81_20260417_024507.m3u" [cite: 6]
    },
    {
        "name": "4K福利🔞｜Tg：@huliys9", [cite: 6]
        "type": 0, [cite: 6]
        "ua": "okhttp/5.3.2", [cite: 6]
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/4k%E7%A6%8F%E5%88%A9.m3u" [cite: 6]
    },
    {
        "name": "探花🔞｜Tg：@huliys9", [cite: 6]
        "type": 0, [cite: 6]
        "ua": "okhttp/5.3.2", [cite: 7]
        "url": "https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E6%8E%A2%E8%8A%B1%E7%BA%A6%E7%82%AE_20260417_024507.m3u" [cite: 7]
    },
    {
        "name": "欧美🔞｜Tg：@huliys9", [cite: 7]
        "type": 0, [cite: 7]
        "ua": "okhttp/5.3.2", [cite: 7]
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/%E6%AC%A7%E7%BE%8E%E9%A2%91%E9%81%93.m3u" [cite: 7]
    },
    {
        "name": "咪咕｜Tg：@huliys9", [cite: 7]
        "type": 0, [cite: 7]
        "ua": "okhttp/5.3.2", [cite: 7]
        "url": "https://develop202.github.io/migu_video/interface.txt" [cite: 8]
    }
]

# ====================================================================
# ⏰ 【每月 1 号自动大洗牌与控制开关自动生成逻辑】 (原汁原味保留) [cite: 8]
# ====================================================================
today = datetime.datetime.now() [cite: 8]
current_month = str(today.month)  [cite: 8]
is_reset_day = (today.day == 1) [cite: 8]

saved_month = "" [cite: 8]
saved_code = "" [cite: 8]

if os.path.exists(lock_file_path): [cite: 8]
    with open(lock_file_path, 'r', encoding='utf-8') as f: [cite: 8]
        content = f.read().strip() [cite: 8]
        if "-" in content: [cite: 8]
            saved_month, saved_code = content.split("-", 1) [cite: 8]
        else: [cite: 8]
            saved_code = content [cite: 8, 9]

if is_reset_day and saved_month != current_month: [cite: 9]
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3)) [cite: 9]
    with open(lock_file_path, 'w', encoding='utf-8') as f: [cite: 9]
        f.write(f"{current_month}-{current_token}") [cite: 9]
    print(f"⏰ 【每月1号全新硬核洗牌】检测到进入新月份 {current_month} 月！已全自动抽签生成本月新密锁: {current_token}") [cite: 9]
elif is_reset_day and saved_month == current_month: [cite: 9]
    current_token = saved_code [cite: 9]
    print(f"🔒 【安全阀拦截】今日 1号已经是当月第二次运行，保持原暗号: {current_token}") [cite: 9]
else: [cite: 9]
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""): [cite: 9]
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3)) [cite: 9]
        with open(lock_file_path, 'w', encoding='utf-8') as f: [cite: 9, 10]
            f.write(f"{current_month}-{current_token}") [cite: 10]
    else: [cite: 10]
        current_token = saved_code [cite: 10]
    print(f"📡 正常沿用本月密锁: {current_token}") [cite: 10]

if current_token in ["全量版", "纯净版"]: [cite: 10]
    output_filename = "老杨TV全量版.json" [cite: 10]
else: [cite: 10]
    output_filename = f"老杨TV全量版{current_token}.json" [cite: 10]

output_path = f"datas/{output_filename}" [cite: 10]
print(f"🎯 最终结算 -> 目标输出：{output_filename}") [cite: 10]

# ====================================================================
# 🛡️ 【金蝉脱壳：全量版过期旧线自动全文字大轰炸】 (原汁原味保留) [cite: 10]
# ====================================================================
old_configs = glob.glob('datas/老杨TV全量版*.json') + glob.glob('datas/老杨TV*.json') [cite: 10]
for old_file in old_configs: [cite: 10]
    if os.path.basename(old_file) != output_filename: [cite: 10]
        try: [cite: 10]
            trap_json = { [cite: 10]
                "spider": "",  [cite: 11]
                "notice": f"⚠️ 警告：当前专线已过期断流！老链接已彻底作废！\n\n最新全量版链接或当前密码请加QQ群“532637640”获取", [cite: 11]
                "sites": [ [cite: 11]
                    {"key": "老杨纯文字提示", "name": "🚨 请前往QQ群“532637640”获取最新密码🚨 当前专线密码已过期断流！", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}, [cite: 11]
                    {"key": "老杨纯文字提示2", "name": "🚨 请前往QQ群“532637640”获取最新全量版链接", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0} [cite: 12]
                ], [cite: 12]
                "lives": [ [cite: 12]
                    {"group": "🚨 接口过期断流 ｜ 提示", "channels": [{"name": "👉 线路已过期 ➡️ 加QQ群“532637640”获取最新全量版密码", "urls": ["http://127.0.0.1"]}]} [cite: 12]
                ] [cite: 12]
            } [cite: 13]
            with open(old_file, 'w', encoding='utf-8') as f: [cite: 13]
                json.dump(trap_json, f, ensure_ascii=False, indent=4) [cite: 13]
            print(f"📡 【金蝉脱壳】已成功将过期旧线调包为纯文字大轰炸: {old_file}") [cite: 13]
        except: [cite: 13]
            pass [cite: 13]

for garbage in glob.glob('datas/config_*.json'): [cite: 13]
    try: os.remove(garbage) [cite: 13]
    except: pass [cite: 13]


# ====================================================================
# 🧠 【核心逻辑：正统 JSON 对象读取与合并逻辑】 [cite: 13, 14]
# ====================================================================
def load_json_safe(path): [cite: 14]
    if not os.path.exists(path): [cite: 14]
        return {} [cite: 14]
    with open(path, 'r', encoding='utf-8') as f: [cite: 14]
        try: [cite: 14]
            return json.load(f) [cite: 14]
        except Exception as e: [cite: 14]
            print(f"❌ 错误：{path} JSON 格式不正确！无法解析。") [cite: 14]
            return {} [cite: 14]

# 常规且路径固定的上游加载
json_cnb = load_json_safe(cnb_path) [cite: 14]
json_lz = load_json_safe(lz_path) [cite: 14, 15]

# 🚀 海豚接口：直接调用全新升级的智能化 API 检索与历史兜底加载器
json_haitun = load_haitun_with_smart_fallback(haitun_path)

haitun_sites = json_haitun.get("sites", []) [cite: 14]
haitun_lives = json_haitun.get("lives", []) [cite: 14]
lz_sites = json_lz.get("sites", []) [cite: 14, 15]

lz_nsfw_list = [] [cite: 15]
for item in lz_sites: [cite: 15]
    if "🔞" in item.get("name", ""): [cite: 15]
        raw_name = item["name"].replace("🔞", "").strip() [cite: 15]
        item["name"] = f"{raw_name}｜🔞" [cite: 15]
        
        if "api" in item and isinstance(item["api"], str): [cite: 15]
            if item["api"].startswith("./py/"): [cite: 15]
                item["api"] = item["api"].replace("./py/", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/py/") [cite: 15]
            elif item["api"].startswith("./js/"): [cite: 15, 16]
                item["api"] = item["api"].replace("./js/", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/js/") [cite: 16]
            elif item["api"].startswith("./"): [cite: 16]
                item["api"] = item["api"].replace("./", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/") [cite: 16]
        lz_nsfw_list.append(item) [cite: 16]

for item in haitun_sites: [cite: 16]
    if "name" in item: [cite: 16]
        item["name"] = f"{item['name']}｜Tg：@huliys9" [cite: 16]
for item in haitun_lives: [cite: 16]
    if "name" in item: [cite: 16]
        item["name"] = f"{item['name']}｜Tg：@huliys9" [cite: 16, 17]

cnb_sites = json_cnb.get("sites", []) [cite: 17]
cnb_lives = json_cnb.get("lives", []) [cite: 17]

# 🎯 直接安全地收集上游所有原本的解析器（parses）
combined_parses = json_haitun.get("parses", []) + json_lz.get("parses", []) + json_cnb.get("parses", []) [cite: 17]

# ➕ 【手工特权点播去重锁】智能检测上游，若有冲突，物理蒸发上游重名 key 线路
custom_keys = {site.get("key") for site in MY_CUSTOM_SITES if site.get("key")} [cite: 17]
upstream_sites = haitun_sites + lz_nsfw_list + cnb_sites [cite: 17]
clean_upstream_sites = [site for site in upstream_sites if site.get("key") not in custom_keys] [cite: 17]
json_cnb["sites"] = clean_upstream_sites + MY_CUSTOM_SITES [cite: 17]

# ➕ 【手工特权直播去重锁 & 从第6位正向依序后排核心算法】
custom_live_names = {live.get("name") for live in MY_CUSTOM_LIVES if live.get("name")} [cite: 17]
base_lives = haitun_lives + cnb_lives [cite: 17]

# 🛠️ 核心修改：同时清洗并剔除名称中带有“日本女优”或“日本女友”的上游直播线路
clean_base_lives = [ [cite: 17]
    live for live in base_lives  [cite: 17]
    if live.get("name") not in custom_live_names  [cite: 17]
    and "日本女优" not in live.get("name", "")  [cite: 17]
    and "日本女友" not in live.get("name", "") [cite: 17, 18]
]

# 🛠️ 核心修改：使用正向切片递增算法。如果手工直播源带 🔞 则不占前排，直接归入大池子末尾。
inserted_count = 0  # 追踪真正插入前排的手工源数量，确保后排递增索引连续 [cite: 18]
for custom_live in MY_CUSTOM_LIVES: [cite: 18]
    live_name = custom_live.get("name", "") [cite: 18]
    if "🔞" in live_name: [cite: 18]
        # 带有 🔞 的线路：不给前排特权，直接融入大池子追加到末尾
        clean_base_lives.append(custom_live) [cite: 18]
    else: [cite: 18]
        # 普通线路：依然享受原规则，从第 6 位（索引 5）开始正向依序插入
        insert_idx = 5 + inserted_count [cite: 18]
        if len(clean_base_lives) >= insert_idx: [cite: 18]
            clean_base_lives.insert(insert_idx, custom_live) [cite: 18, 19]
        else: [cite: 19]
            clean_base_lives.append(custom_live) [cite: 19]
        inserted_count += 1 [cite: 19]

json_cnb["lives"] = clean_base_lives [cite: 19]

final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4) [cite: 19]

final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"') [cite: 19]
final_json_text = final_json_text.replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"') [cite: 19]

final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '') [cite: 19]
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '') [cite: 19]

path_replacements = { [cite: 19]
    './spider.jar': 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar', [cite: 19]
    './XBPQ/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/', [cite: 19]
    './XYQHiker': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/', [cite: 20]
    './js/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/', [cite: 20]
    './json/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/', [cite: 20]
    './py/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/', [cite: 20]
    'http://127.0.0.1:9978/file/TVBox/logo.png': 'https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg' [cite: 20]
}
for src, dst in path_replacements.items(): [cite: 20]
    final_json_text = final_json_text.replace(src, dst) [cite: 20]

thanks_warning = "\n\n👑如果遇到失效 or 断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！ " [cite: 20]
welcome_notice = "👑 欢迎使用【老杨TV粉丝专属缝合专线】！本接口由老杨TV结合佬&鱼佬的优质核心资源缝合而成，纯净无广告！🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效 or 断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！" [cite: 20]

try: [cite: 20]
    final_obj = json.loads(final_json_text) [cite: 20]
    final_obj["notice"] = welcome_notice + thanks_warning [cite: 20]
    if "warningText" in final_obj: [cite: 20]
        final_obj.pop("warningText") [cite: 20]
    
    ordered_obj = {} [cite: 20]
    if "notice" in final_obj:  [cite: 20]
        ordered_obj["notice"] = final_obj.pop("notice") [cite: 21]
        
    ordered_obj.update(final_obj) [cite: 21]
    
    # ====================================================================
    # 🌟【全新深度体验优化区】 [cite: 21]
    # ====================================================================
    try: [cite: 21]
        # --- 1. 去重并保留所有合法的傳統解析站點 ---
        unique_parses = [] [cite: 21]
        seen_names = set() [cite: 21]
        for p in combined_parses: [cite: 21]
            name = p.get("name", "") [cite: 21, 22]
            if name and name not in seen_names: [cite: 22]
                unique_parses.append(p) [cite: 22]
                seen_names.add(name) [cite: 22]
        ordered_obj["parses"] = unique_parses [cite: 22]

        # --- 2. 注入国内高防 AliDNS 到 doh 并修复原有拼写错误 ---
        if "doh" in ordered_obj and isinstance(ordered_obj["doh"], list): [cite: 22]
            for doh_item in ordered_obj["doh"]: [cite: 22, 23]
                if doh_item.get("url", "").endswith("/dns-quer"): [cite: 23]
                    doh_item["url"] = doh_item["url"] + "y" [cite: 23]
            
            ali_doh = { [cite: 23]
                "name": "AliDNS", [cite: 23]
                "url": "https://dns.alidns.com/dns-query", [cite: 24]
                "ips": ["223.5.5.5", "223.6.6.6"] [cite: 24]
            } [cite: 24]
            if not any(d.get("name") == "AliDNS" for d in ordered_obj["doh"]): [cite: 24]
                ordered_obj["doh"].insert(0, ali_doh) [cite: 24]

        # --- 3. 全面注入通用高级影音防屏蔽去广告 JS 脚本 ---
        custom_js_rules = [ [cite: 24]
            "console.log('老楊TV高級WebView攔截器啟動');", [cite: 25]
            "window.addEventListener('DOMContentLoaded', function() {", [cite: 25]
            "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });", [cite: 25, 26]
            "   Function.prototype.__constructor__ = Function.prototype.constructor;", [cite: 26]
            "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };", [cite: 26, 27]
            "});", [cite: 27]
            "setInterval(() => { let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]']; selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); }); }, 400);" [cite: 27]
        ]

        current_rules = ordered_obj.get("rules", []) [cite: 27]
        if not isinstance(current_rules, list): [cite: 27]
            current_rules = [] [cite: 27]
            
        ad_hosts = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"] [cite: 28]
        for rule in current_rules: [cite: 28]
            if isinstance(rule, dict) and "hosts" in rule: [cite: 28]
                for h in rule["hosts"]: [cite: 28]
                    if h not in ad_hosts: ad_hosts.append(h) [cite: 28]

        js_injection_rule = { [cite: 29]
            "name": "老楊TV·雲端高級去广告JS注入", [cite: 29]
            "hosts": ad_hosts, [cite: 29]
            "script": custom_js_rules [cite: 29]
        } [cite: 29]
        ordered_obj["rules"] = [js_injection_rule] + [r for r in current_rules if r.get("name") != "老楊TV·雲端高級去广告JS注入"] [cite: 29]

        # --- 4. 彻底移除直播 lives 末尾的无用空对象并统一重写补齐 OkHttp 头部并覆盖手工直播源 ---
        if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list): [cite: 29, 30]
            clean_lives = [] [cite: 30]
            for live in ordered_obj["lives"]: [cite: 30]
                if live and isinstance(live, dict): [cite: 30]
                    if not live.get("ua") or live.get("ua") == "okhttp": [cite: 30]
                        live["ua"] = "okhttp/5.3.2" [cite: 31]
                    clean_lives.append(live) [cite: 31]
            ordered_obj["lives"] = clean_lives [cite: 31]

        # --- 5 & 6. 🏆【核心重写：九大方阵智能归类洗牌 与 热播影视精准置顶长鸣谢算法】 ---
        block_1_rebo = []         # 1. 🏆 热播影视专属置顶方阵 (仅限 key: 热播影视) [cite: 31]
        block_2_yingshi = []      # 2. 影视/追剧/APP大类 [cite: 31]
        block_3_duanju = []       # 3. 短剧/剧场 [cite: 32]
        block_4_dongman = []      # 4. 动漫类 [cite: 32]
        block_5_cili = []         # 5. 网盘/磁力/4K (未配Token不加载特性) [cite: 32]
        block_6_tiyu = []         # 6. 体育/看球/直播 [cite: 32]
        block_7_shaoer = []       # 7. 少儿课堂/教育 [cite: 32]
        block_8_yinyue = []       # 8. 音乐/听书/功能线/DJ [cite: 33]
        block_9_fuli = []         # 9. 福利/18禁 (绝对大沉底) [cite: 33]

        tg_tail_count = 0 [cite: 33]

        for site in ordered_obj.get("sites", []): [cite: 33]
            if "name" not in site: [cite: 33]
                continue [cite: 33]
                
            raw_name = site["name"] [cite: 34]
            s_key = site.get("key", "") [cite: 34]
            s_genre = site.get("genre", "") [cite: 34]
            s_api = site.get("api", "") [cite: 34]

            # 🛠️ 1. 清洗名称里的脏字符
            for char in ['丨', '┃', ' ']: [cite: 34]
                raw_name = raw_name.strip(char) [cite: 35]
            raw_name = re.sub(r'\s+', ' ', raw_name) [cite: 35]
            
            if "｜Tg：@huliys9" in raw_name: [cite: 35]
                tg_tail_count += 1 [cite: 35]
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg：@huliys9", "").strip() [cite: 35, 36]
            elif "｜Tg:@huliys9" in raw_name: [cite: 36]
                tg_tail_count += 1 [cite: 36]
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg:@huliys9", "").strip() [cite: 36]

            if "ext" in site and site["ext"] == {}: [cite: 36]
                site["ext"] = "" [cite: 36]

            # 🛠️ 2. 【核心大招】网盘组件强行去后缀洗白！实现未配Token不展示网盘的特性
            if isinstance(s_api, str) and "PanWebShare" in s_api: [cite: 37]
                site["api"] = "csp_PanWebShare" [cite: 37]
                if "jar" in site: [cite: 37]
                    site.pop("jar") [cite: 37]

            # 🛠️ 3. 瓜子靶向保护：防误伤，强力摘出
            is_guazi = "瓜子" in raw_name or "GZ" == s_key [cite: 38]

            # 🛠️ 4. 精准捕获福利关键字（排除瓜子后）
            is_nsfw = False if is_guazi else ("🔞" in raw_name or "色播" in raw_name or "av" in s_key.lower() or "瓜" in raw_name or "爆料" in raw_name or "chat" in raw_name.lower() or "cam" in raw_name.lower() or "panda" in raw_name.lower() or "video" in raw_name.lower() or "md" in s_key.lower()) [cite: 38]

            # 🛠️ 5. 【靶向精准连坐解除】唯一锁定主线 "key": "热播影视"
            is_target_rebo_main = (s_key == "热播影视") [cite: 39]

            # 🛠️ 6. 彻底完成洗牌分流与名字特调
            if is_target_rebo_main: [cite: 39]
                # 🎯 唯独将“热播影视”注入大长鸣谢声明，推入置顶第一位 block_1
                site["name"] = "热播 • APP｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9" [cite: 39]
                site["category"] = "综合" [cite: 40]
                block_1_rebo.append(site) [cite: 40]

            elif "豆瓣" in raw_name and "首页" in raw_name: [cite: 40]
                # 豆瓣解绑：恢复其原本清净名，退回普通影视区 block_2
                site["name"] = "🦋 豆瓣 • 首页" [cite: 40]
                site["category"] = "综合" [cite: 40, 41]
                site["searchable"] = 0 [cite: 41]
                block_2_yingshi.append(site) [cite: 41]

            elif is_nsfw: [cite: 41]
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 41]
                site["name"] = raw_name [cite: 41]
                site["category"] = "福利" [cite: 42]
                block_9_fuli.append(site) [cite: 42]
                
            elif "短剧" in raw_name or "剧场" in raw_name: [cite: 42]
                # 包含 DJ/dj 关键词的线一律强行分流进入音乐阵营
                if "dj" in raw_name.lower() or "dj" in s_key.lower(): [cite: 42, 43]
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 43]
                    site["name"] = raw_name [cite: 43]
                    site["category"] = "音乐" [cite: 43]
                    site["searchable"] = 0 [cite: 43]
                    block_8_yinyue.append(site) [cite: 44]
                else: [cite: 44]
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 44]
                    site["name"] = raw_name [cite: 44]
                    site["category"] = "短剧" [cite: 44]
                    site["genre"] = "shortdrama" [cite: 45]
                    block_3_duanju.append(site) [cite: 45]
                
            elif "动漫" in raw_name or "新番" in raw_name or "anime" in s_key.lower() or "a1" in raw_name.lower(): [cite: 45]
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 45, 46]
                site["name"] = raw_name [cite: 46]
                site["category"] = "动漫" [cite: 46]
                block_4_dongman.append(site) [cite: 46]
                
            elif "磁力" in raw_name or "索" in raw_name or "盘" in raw_name or "云盘" in raw_name or "4k" in raw_name.lower(): [cite: 46, 47]
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 47]
                site["name"] = raw_name [cite: 47]
                site["category"] = "网盘/磁力" [cite: 47]
                if "PanWebShare" in site.get("api", ""): [cite: 47]
                    site["changeable"] = 1 [cite: 48]
                block_5_cili.append(site) [cite: 48]
                
            elif "体育" in raw_name or "球" in raw_name or "直播" in raw_name: [cite: 48]
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 48]
                site["name"] = raw_name [cite: 48]
                site["category"] = "体育/直播" [cite: 49]
                block_6_tiyu.append(site) [cite: 49]
                
            elif "少儿" in raw_name or "课堂" in raw_name or "教学" in raw_name or "教育" in raw_name: [cite: 49]
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 49]
                site["name"] = raw_name [cite: 50]
                site["category"] = "少儿" [cite: 50]
                site["searchable"] = 0 [cite: 50]
                block_7_shaoer.append(site) [cite: 50]
                
            elif "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "唱会" in raw_name or "fm" in raw_name.lower() or "相声" in raw_name or "小品" in raw_name or "戏曲" in raw_name or "推送" in raw_name or "配置" in raw_name or "版本" in raw_name or "本地" in raw_name or "dj" in raw_name.lower() or "dj" in s_key.lower(): [cite: 50, 51]
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 51]
                site["name"] = raw_name [cite: 51]
                if "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "fm" in raw_name.lower() or "dj" in raw_name.lower() or "dj" in s_key.lower(): [cite: 52]
                    site["category"] = "音乐" [cite: 52]
                else: [cite: 52]
                    site["category"] = "综合" [cite: 52]
                site["searchable"] = 0 [cite: 53]
                block_8_yinyue.append(site) [cite: 53]
                
            else: [cite: 53]
                # 默认影视大类（包含名称带瓜子APP、视频、以及保留原地归类的 "key": "rb" 线路）
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}" [cite: 53]
                site["name"] = raw_name [cite: 54]
                site["category"] = "综合" [cite: 54]
                block_2_yingshi.append(site) [cite: 54]

            # 🛠️ 7. 补齐非音乐少儿类的全局搜索功能开关
            if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site: [cite: 54]
                site["searchable"] = 1 [cite: 54, 55]

        # 🛠️ 8. 爱奇艺官方名称规格对齐
        for site in block_2_yingshi: [cite: 55]
            if site.get("key") == "AQY": [cite: 55]
                site["name"] = "🦋 爱奇艺 ｜Tg：@huliys9" [cite: 55]

        # 👑 【新首页硬组装】"key": "热播影视" 携长致谢完美置顶（Index 0），另一个热播"key": "rb"正常随大部队在影视区排列
        ordered_obj["sites"] = ( [cite: 55]
            block_1_rebo +      [cite: 55]
            block_2_yingshi +      # 2. 传统综合影视单线路 (包含回归的豆瓣首页 and 原本就在此的 key: rb 线路) [cite: 56]
            block_3_duanju +       # 3. 独立短剧 [cite: 56]
            block_4_dongman +      # 4. 动漫新番 [cite: 56]
            block_6_tiyu +         # 5. 体育直播 [cite: 56, 57]
            block_7_shaoer +       # 6. 少儿课堂 [cite: 57]
            block_8_yinyue +       # 7. 音乐/听书/功能辅助线 [cite: 57]
            block_5_cili +         # 8. 网盘/磁力/4K降权区 [cite: 57]
            block_9_fuli           # 9. 福利18禁安全坠尾 [cite: 57]
        ) [cite: 58]
        print(f"🚀 【洗牌结算】靶向隔离重排成功！\"key\": \"热播影视\" 已锁定置顶，\"key\": \"rb\" 线路已安稳保留在其原有的影视分类位置。") [cite: 58]

    except Exception as inner_e: [cite: 58]
        print(f"⚠️ 提示：美化与智能重排阶段跳过，reason: {inner_e}") [cite: 58]

    # ====================================================================
    # 🌟【数据安全落盘】 [cite: 58]
    # ====================================================================
    with open(output_path, 'w', encoding='utf-8') as f: [cite: 58]
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4) [cite: 58]
        
    with open(tracker_path, 'w', encoding='utf-8') as f: [cite: 58]
        f.write(output_filename) [cite: 58]
     
    print(f"🎉 全量版更新成功！配置已写出至: {output_path}") [cite: 59]

except Exception as e: [cite: 59]
    print(f"❌ 严重错误：最后的本地渲染失败，原因: {e}") [cite: 59]

if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""): [cite: 59]
    with open(lock_file_path, 'w', encoding='utf-8') as f: [cite: 59]
        f.write(f"{current_month}-{current_token}") [cite: 59]
