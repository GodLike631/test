import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/老杨TV.json'  # 🌟 专属后缀文件名

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
# 1. 将无法显示的本地 logo 替换为你上传到图床上的在线蝴蝶版 Logo 链接
# 💡 请把下面的 https://你的图床地址/老杨TV_logo.png 替换成你真实的图床链接
final_json_text = final_json_text.replace(
    '"logo": "http://127.0.0.1:9978/file/TVBox/logo.png"', 
    '"logo": "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"'
)

# 2. 强行在头部注入你专属的欢迎语（因为 CNB 原始文件里没有 warningText 字段）
if '"logo":' in final_json_text and '"warningText":' not in final_json_text:
    final_json_text = final_json_text.replace(
        '    "logo":',
        '    "warningText": "👑 特别致谢与版权声明
本接口的诞生离不开大后方两位业内顶流技术大佬的无私奉献，特此致谢：
🐋 感谢鱼佬的付出
源码基础与发布主页: fish2018/webhtv
版本发布绝对地址: fish2018/webhtv/releases
Telegram 官方群组: 👉 https://t.me/webhtv
🐬 感谢海豚佬的付出
核心仓库主页: FGBLH/GHK
数据源直链地址: FGBLH/GHK/海豚.json
Telegram 官方群组: 👉 https://t.me/hshsjk9",\n    "logo":'
    )

# ====================================================================
# 5. 全方位名称大清洗与品牌脱敏手术
# ====================================================================
# 1. 靶向切除“🐬”、“海豚影视”、“海豚”
final_json_text = final_json_text.replace('🐬', '')
final_json_text = final_json_text.replace('海豚影视', '')
final_json_text = final_json_text.replace('海豚', '')

# 2. 自动修正因为删掉品牌词后，名字前缀残留的“｜”或“丨”等符号
final_json_text = final_json_text.replace('"name": "｜', '"name": "')
final_json_text = final_json_text.replace('"name": "丨', '"name": "')
final_json_text = final_json_text.replace('"name": " ', '"name": "')

# 3. 靶向替换特定的广告词和联系方式，锁定你的全新 Tg 频道链接
final_json_text = final_json_text.replace('@hshsjk9', '@huliys9')
final_json_text = final_json_text.replace('交流群', 'Tg频道')

# ====================================================================
# 6. 安全、高效地消除尾部逗号瑕疵（摒弃危险的正则回溯）
# ====================================================================
# 用安全的精准字符串替换来消除可能由于注入引起的 `[,` 或者 `, ]` 问题
final_json_text = final_json_text.replace('[\n    ,', '[')
final_json_text = final_json_text.replace('[\n,', '[')
final_json_text = final_json_text.replace(',\n    ]', '\n    ]')
final_json_text = final_json_text.replace(',\n  ]', '\n  ]')

# 写入本地文件存盘
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🎉 【专属定制版】已经完成秒级清洗，成功输出为 老杨TV.json！")
