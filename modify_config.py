import os
import re
import glob
import json

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
lz_path = 'datas/lz.json'

# 控制开关和追踪器文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# 🎛️ 【控制开关动态读取与文件名拼接逻辑】
# ====================================================================
# 默认配置
current_token = "全量版" 

if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        config_content = f.read().strip()
        if config_content:
            current_token = config_content

# 🎯 根据控制开关里的内容，决定输出的文件名（固定带上“全量版”）
if current_token == "全量版":
    output_filename = "老杨TV全量版.json"
else:
    output_filename = f"老杨TV全量版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 当前控制开关模式为：[{current_token}] -> 目标输出：{output_filename}")

# ====================================================================
# 🛡️ 【金蝉脱壳：全量/暗号版本过期旧线一键调包大轰炸】
# ====================================================================
old_configs = glob.glob('datas/老杨TV*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            trap_json = {
                "spider": "", 
                "notice": f"⚠️ 警告：当前线路已过期断流！老链接已彻底作废！\n\n最新全量版链接或密码请加QQ群“532637640”获取",
                "warningText": "👑 特别提示：加QQ群“532637640”获取最新接口",
                "sites": [
                    {"key": "老杨纯文字提示", "name": "🚨 当前专线密码已过期断流！", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
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
# 🧠 【核心重构：正统 JSON 对象读取与合并逻辑】
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

# 1. 载入标准 JSON 对象
json_cnb = load_json_safe(cnb_path)
json_haitun = load_json_safe(haitun_path)
json_lz = load_json_safe(lz_path)

# 获取各自的 sites 和 lives 列表
haitun_sites = json_haitun.get("sites", [])
haitun_lives = json_haitun.get("lives", [])
lz_sites = json_lz.get("sites", [])

# 2. 过滤老张源里的 🔞 站点并转换为绝对路径
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

# 3. 给海豚源打上后缀标签
for item in haitun_sites:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"

# 4. 精准插入“乡村电视”到直播数组索引 5（第 6 位）
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
# 🚀 数组大合并
# ====================================================================
json_cnb["sites"] = haitun_sites + lz_nsfw_list
json_cnb["lives"] = haitun_lives

# ====================================================================
# 📝 转换为文本后进行清洗与特调
# ====================================================================
final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)

# 针对特定 key 补充 jar 包依赖
final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"')
final_json_text = final_json_text.replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"')

# 净化海豚残留词
final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '')

# 替换本地路径为绝对网络路径
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
# 🎯 开机大公告栏提示注入
# ====================================================================
thanks_warning = "👑 特别致谢与版权声明\n本接口的诞生离不开大后方几位业内顶流技术大佬的无私奉献，特此致谢：\n🐋 感谢鱼佬的付出\n源码基础与发布主页: fish2018/webhtv\n版本发布绝对地址: fish2018/webhtv/releases\nTelegram 官方群组: 👉 https://t.me/webhtv\n 感谢佬的付出\n核心仓库主页: FGBLH/GHK\n数据源直链地址: FGBLH/GHK/.json\nTelegram 官方群组: 👉 https://t.me/hshsjk9"
welcome_notice = "👑 欢迎使用【老杨TV粉丝专属缝合专线】！本接口由老杨TV结合佬&老张特调&鱼佬的优质核心资源缝合而成，纯净无广告！🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（@huliys9）或微信群获取当前最新密码！"

try:
    final_obj = json.loads(final_json_text)
    final_obj["notice"] = welcome_notice
    final_obj["warningText"] = thanks_warning
    
    ordered_obj = {}
    if "notice" in final_obj: ordered_obj["notice"] = final_obj.pop("notice")
    if "warningText" in final_obj: ordered_obj["warningText"] = final_obj.pop("warningText")
    ordered_obj.update(final_obj)
    
    # 🦋 【高级加蝴蝶逻辑】：只加在 sites 里面
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

    # 写出最终文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    # 把当前最新文件名写入追踪器文件
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 更新成功！配置已写出至: {output_path}")

except Exception as e:
    print(f"❌ 严重错误：最后的本地渲染失败，原因: {e}")
