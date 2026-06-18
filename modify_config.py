import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/老杨TV.json'  # 🌟 如需修改输出文件名，改这里即可

def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 1. 物理提取海豚源里的 sites（视频站）和 lives（直播源）内部的纯文本
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
# 【海豚专属尾缀手术】在合并前，单独为海豚的线路名称末尾加上 ｜Tg：@huliys9
# ====================================================================
name_regex = r'"name"\s*:\s*"([^"]+)"'
if haitun_sites_text:
    haitun_sites_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_sites_text)
if haitun_lives_text:
    haitun_lives_text = re.sub(name_regex, r'"name": "\1｜Tg：@huliys9"', haitun_lives_text)

# ====================================================================
# 2. 逆向注入：把海豚的内容，无缝贴进 CNB 对应的数组最前面
# ====================================================================
final_json_text = text_cnb

# 注入视频站点
if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

# 注入直播源
if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 3. 靶向拦截手术：揪出这两个瘫痪的 4K 线路，强行切断 CNB 依赖，锁死海豚核心
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
# 【全方位无死角路径清洗】：让 CNB 的其余线路走官方绝对 network 链接
# ====================================================================
final_json_text = final_json_text.replace('./spider.jar', 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar')
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 4. 定制老杨自用全量缝合专线 brand 头部
# ====================================================================
# 1. 精准锁定头部唯一图片，替换为你的专属蝴蝶 Logo 链接
final_json_text = final_json_text.replace(
    '"logo": "http://127.0.0.1:9978/file/TVBox/logo.png"', 
    '"logo": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"'
)

# 2. 锁定 JSON 唯一的开头首行，精准插入专属长篇致谢声明
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
# 5. 全方位名称大清洗与品牌脱敏手术
# ====================================================================
# 1. 批量拔除各种旧品牌的残留和无关话术
final_json_text = final_json_text.replace('🐬', '')
final_json_text = final_json_text.replace('海豚影视', '')
final_json_text = final_json_text.replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '')
final_json_text = final_json_text.replace('交流群 TG：@hshsjk9', '')

# 2. 精准格式化与全线路 🦋 前缀注入
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

# 3. 🎯【精准拦截替换】单独将爱奇艺线路名称升级为长篇免责声明版本
final_json_text = final_json_text.replace(
    '"name": "🦋爱奇艺｜Tg：@huliys9"',
    '"name": "🦋爱奇艺｜此接口非原创，合并自海豚佬和鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"'
)

# ====================================================================
# 6. 安全、高效地消除尾部逗号瑕疵（摒弃危险的正则回溯）
# ====================================================================
final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')

# 写入本地文件存盘
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🎉 【全能无暇版】已完美输出！爱奇艺长声明已单独生效。")
