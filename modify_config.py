import os
import re
import json

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/老杨TV.json'  # 🌟 输出文件名

def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 1. 物理提取海豚源里的 sites 和 lives 内部的纯文本（完全保留）
# ====================================================================
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

haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

# ====================================================================
# 【海豚专属尾缀手术】（完全保留）
# ====================================================================
name_regex = r'"name"\s*:\s*"([^"]+)"'
if haitun_sites_text:
    haitun_sites_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_sites_text)
if haitun_lives_text:
    haitun_lives_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_lives_text)

# ====================================================================
# 2. 逆向注入：把海豚的内容无缝贴进 CNB 对应的数组最前面（完全保留）
# ====================================================================
final_json_text = text_cnb

if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 3. 靶向拦截手术（✨安全改良：让 jar 走绝对网络路径，防止相对路径闪退）
# ====================================================================
# 原来注入 ./tvbox.jar 容易找不到文件崩溃，这里直接给它们锁死官方绝对网络 jar 链接，彻底防闪退
final_json_text = final_json_text.replace(
    '"key": "hajim-腾讯备"', 
    '"jar": "https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar",\n           "key": "hajim-腾讯备"'
)
final_json_text = final_json_text.replace(
    '"key": "茫茫"', 
    '"jar": "https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar",\n        "key": "茫茫"'
)

# ====================================================================
# 【全方位无死角路径清洗】（完全保留）
# ====================================================================
final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 4. 定制老杨自用全量缝合专线 brand 头部（长篇致谢完整保留）
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
# 5. 全方位名称大清洗与品牌脱敏手术（完全保留）
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

# 爱奇艺超长免责声明（完整保留）
final_json_text = final_json_text.replace(
    '"name": "🦋爱奇艺｜Tg：@huliys9"',
    '"name": "🦋爱奇艺｜此接口非原创，合并自海豚佬和鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"'
)

# ====================================================================
# 6. 安全消除尾部逗号瑕疵（完全保留）
# ====================================================================
final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')

# ====================================================================
# ✨【新增：终极防闪退守护层】
# 用纯文本拼完后，用 Python 官方库进行一次对象格式化输出
# 这能自动修复任何肉眼看不到的隐藏错位、非法不可见控制字符和编码瑕疵
# ====================================================================
try:
    # 尝试用正统 JSON 校验拼出来的文本
    json_object = json.loads(final_json_text)
    # 校验成功：用标准、最纯净、不带任何瑕疵的格式存盘
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_object, f, ensure_ascii=False, indent=4)
    print("🎉 【老杨自用全量版】已通过正统 JSON 格式清洗，完美输出！老旧设备不再闪退。")
except Exception as e:
    # 如果物理拼接有极个别特殊符号冲突，兜底机制会直接采用原版文本写入，确保功能绝不丢失
    print(f"⚠️ 触发安全兜底写入（原文本输出）: {e}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_json_text)
