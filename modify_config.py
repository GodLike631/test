import os
import re
import random
import string
import glob
import datetime

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'

# 控制开关和追踪器的文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# ⏰ 【安全阀门升级：绿色版方案 A 确保 1 号早晚双跑只洗一次牌】
# ====================================================================
today = datetime.datetime.now()
is_reset_day = (today.day == 1)  # 🌟 默认每月 1 号全自动定时洗牌

current_token = ""

# 1. 优先读取现有的控制开关
if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        current_token = f.read().strip()

# 🌟【核心纠偏】：如果发现旧暗号长度不是严格的 3 位，强行作废重抽
if len(current_token) != 3:
    current_token = ""

# 🌟【安全闭环阀门拦截】
if is_reset_day and len(current_token) == 3:
    print(f"🔒 【安全阀拦截】今日 1 号已在早晨完成大洗牌，晚上保持原暗号不再重复抽签: {current_token}")
else:
    # 2. 抽签新密锁
    if is_reset_day or not current_token:
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(current_token)
        print(f"⏰ 【密锁自动生成】已生成绿色版严格 3 位新密锁: {current_token}")

# 👑 固定的品牌前缀 + 3位乱码尾缀
output_filename = f"老杨TV无18{current_token}.json"
output_path = f"datas/{output_filename}"

# ====================================================================
# 🛡️ 【黑科技：绿色版过期全屏背景大弹窗重塑雷达】
# ====================================================================
old_configs = glob.glob('datas/老杨TV无18*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
        try:
            # 🌟【特制绿色纯净版二维码全屏强显 JSON 代码】
            trap_json = {
                "spider": "",
                "wallpaper": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg",
                "warningText": "⚠️ 警告：当前【老杨TV无18绿色纯净版】已洗牌变幻新密码！\n老订阅链接已全线物理断流！\n\n请立刻打开手机微信，扫描屏幕背景上的【二维码】，重新进入【老杨官方核心铁粉群】获取今日最新 3 位后缀通关密码！\n退群或失联将永久断流！\n\n\n\n\n",
                "sites": [
                    {
                        "key": "老杨提示",
                        "name": "🦋 请看电视背景墙二维码 ｜ 微信扫码进群拿新密码",
                        "type": 3,
                        "api": "csp_Push",
                        "searchable": 0,
                        "quickSearch": 0,
                        "filterable": 0,
                        "ext": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"
                    }
                ]
            }
            import json
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
            print(f"📡 【金蝉脱壳】已成功将绿色版过期旧线调包为背景强显弹窗: {old_file}")
        except Exception as e:
            pass

# 顺手全面清理历史可能遗留的无关垃圾
for garbage in ['datas/local_config.json', *glob.glob('datas/config_*.json')]:
    try: os.remove(garbage)
    except: pass


def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 1. 精准提取海豚源（利用括号抵消原理，100% 完整提取不截断）
# ====================================================================
def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    
    start_idx = content.find(split_key) + len(split_key)
    bracket_count = 1
    end_idx = start_idx
    
    while end_idx < len(content):
        if content[end_idx] == '[':
            bracket_count += 1
        elif content[end_idx] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                break
        end_idx += 1
        
    return content[start_idx:end_idx].strip()

haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

# ====================================================================
# 【海豚专属尾缀手术】
# ====================================================================
name_regex = r'"name"\s*:\s*"([^"]+)"'
if haitun_sites_text:
    haitun_sites_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_sites_text)
if haitun_lives_text:
    haitun_lives_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_lives_text)

# ====================================================================
# 2. 逆向无缝注入
# ====================================================================
final_json_text = text_cnb

if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 3. 🛡️ 【全局上帝视角净网】：彻底剿灭 🔞 和 18+
# ====================================================================
raw_lines = final_json_text.splitlines()
skip_indices = set()

for i, line in enumerate(raw_lines):
    if "🔞" in line or "18+" in line:
        if "{" in line and "}" in line:
            skip_indices.add(i)
        else:
            start = i
            while start >= 0 and "{" not in raw_lines[start]:
                start -= 1
            end = i
            while end < len(raw_lines) and "}" not in raw_lines[end]:
                end += 1
            
            if start >= 0 and end < len(raw_lines):
                for r in range(start, end + 1):
                    skip_indices.add(r)

clean_lines = [line for i, line in enumerate(raw_lines) if i not in skip_indices]
final_json_text = '\n'.join(clean_lines)

# ====================================================================
# 4. 靶向拦截手术
# ====================================================================
final_json_text = final_json_text.replace(
    '"key": "hajim-腾讯备"', 
    '"spider": "./tvbox.jar",\n           "key": "hajim-腾讯备"'
)
final_json_text = final_json_text.replace(
    '"key": "茫茫"', 
    '"spider": "./tvbox.jar",\n        "key": "茫茫"'
)

# ====================================================================
# 5. 全方位无死角路径清洗
# ====================================================================
final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 6. 定制老杨自用全量缝合专线 brand 头部
# ====================================================================
final_json_text = final_json_text.replace(
    '"logo": "http://127.0.0.1:9978/file/TVBox/logo.png"', 
    '"logo": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"'
)

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
    final_json_text = final_json_text.replace(
        '{\n    "spider":',
        f'{{\n    "warningText": "{thanks_warning}",\n    "spider":'
    )

# ====================================================================
# 7. 全方位名称大清洗与品牌脱敏手术
# ====================================================================
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
    '"name": "🦋爱奇艺｜Tg：@huliys9"',
    '"name": "🦋爱奇艺｜此接口非原创，合并自海豚佬和鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"'
)

# 🎯 【精细化脱敏】
final_json_text = final_json_text.replace('有三级片', 'SP')

# ====================================================================
# 8. 安全、高效地消除尾部及多余逗号瑕疵
# ====================================================================
final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 写入带有品牌特征的乱码绿色版文件
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

# 登记在追踪器里
with open(tracker_path, 'w', encoding='utf-8') as f:
    f.write(output_filename)

print(f"🎉 【绿色版二维码大弹窗定版成功】同步成功！当前出库配置名: {output_path}")
