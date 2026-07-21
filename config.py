# -*- coding: utf-8 -*-
"""
核心配置文件
"""
from pathlib import Path

# ====================================================================
# 🆔 【零、工程版本与全局控制参数定义】
# ====================================================================
VERSION = "3.1.0"
BUILD_DATE = "2026.07.20"

# 🎯 专属外层大总包 Jar 远程绝对路径
GLOBAL_SPIDER_JAR = "https://cnb.cool/fish2035/xs/-/git/raw/main/spider.jar"

# 统一提取的 Magic Number
DEFAULT_TIMEOUT = 10     # 默认网络请求超时时间 (秒)
TG_TIMEOUT = 15          # Telegram 通知专用超时时间 (秒)
TOKEN_LENGTH = 3         # 动态密码锁随机字符长度
TG_MAX_DISPLAY = 15      # 变动明细单次最大展示行数
INSERT_POS = 5           # 手工非福利直播源的正向插入起始位置
SITE_INSERT_POS = 0      # 手工点播源的插入位置 (1 表示插入到第 2 位)

# ====================================================================
# 🌐 【一、全局核心路径与网络代理配置区】
# ====================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "datas"

CNB_PATH = DATA_DIR / "cnb.json"
HAITUN_PATH = DATA_DIR / "haitun.json"
LZ_PATH = DATA_DIR / "lz.json"

LOCK_FILE_PATH = DATA_DIR / "控制开关.txt"
TRACKER_PATH = DATA_DIR / "最新接口文件名.txt"

GITHUB_PROXY = "https://gh-proxy.org/"
DEFAULT_LOGO_URL = "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"

# ====================================================================
# 🚫 【二、双版本过滤依据、广告拦截与恶意杂质直接清洗区】
# ====================================================================
BLOCK_KEYWORDS = ("羊壳", "弹幕", "不可用")
UPSTREAM_DIRTY_WORDS = ('🐬', '海豚影视', '海豚', '完全免费，如有收费的都是骗子', '交流群 TG：@hshsjk9')
AD_HOSTS_LIST = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"]

# 纯净版敏感词分流
NSFW_KEYWORDS = ("🔞", "福利", "探花", "约炮", "色播", "av", "爆料", "蜜桃", "三级片")
# 上游全线杂质强力永久丢弃词
BLOCK_MALICIOUS_KEYWORDS = ("日本女优", "日本女友")

# ====================================================================
# 👑 【三、专属品牌与视觉定制区】
# ====================================================================
MY_QQ_GROUP = "532637640"
MY_PROMO_CHANNEL = "@huliys9"
MY_TG_SUFFIX = "｜Tg：@huliys9"
LOGO_PREFIX = "🦋"

WALLPAPER_FULL = "https://img.naixiai.cn/2026/wallpapers/full_vip.jpg"
WALLPAPER_CLEAN = "https://img.naixiai.cn/2026/wallpapers/home_clean.jpg"

HOT_VIDEO_KEY = "js_douban"
HOT_VIDEO_SITE_NAME = f"豆瓣(js),该接口完全免费，如有收费都是骗子｜{MY_TG_SUFFIX.strip('｜')}"

MY_NAME_REPLACEMENTS = {
    # 示例: "原词": "目标新词",
}

# ====================================================================
# 🗂️ 【🎯 点播自动类目分组与正则映射配置面板】
# ====================================================================
CATEGORY_RULES = {
    "短剧": ["短剧", "剧场"],
    "动漫": ["动漫", "新番", "anime", "a1"],
    "网盘/磁力": ["磁力", "索", "盘", "云盘", "4k"],
    "体育/直播": ["体育", "球", "直播"],
    "少儿": ["少儿", "课堂", "教学", "教育"],
    "音乐": ["音乐", "网易云", "听书", "唱会", "fm", "相声", "小品", "戏曲", "dj"]
}

# 核心路径与图标的正则/精准替换映射表
PATH_REPLACEMENTS = {
    r'\./spider\.jar': 'https://cnb.cool/fish2035/xs/-/git/raw/main/spider.jar',
    r'\./XBPQ/': 'https://cnb.cool/fish2035/xs/-/git/raw/main/XBPQ/',
    r'\./XYQHiker': 'https://cnb.cool/fish2035/xs/-/git/raw/main/XYQHiker',  # 🎯 砍掉末尾斜杠，防止与底包自带的斜杠冲突
    r'\./js/': 'https://cnb.cool/fish2035/xs/-/git/raw/main/js/',
    r'\./json/': 'https://cnb.cool/fish2035/xs/-/git/raw/main/json/',
    r'\./py/': 'https://cnb.cool/fish2035/xs/-/git/raw/main/py/',
    r'http://127\.0\.0\.1:9978/file/TVBox/logo\.png': DEFAULT_LOGO_URL
}

# ====================================================================
# 🔒 【四、双版本输出控制与“金蝉脱壳”大轰炸配置区】
# ====================================================================
BASE_OUTPUT_FULL = "老杨TV全量版"
BASE_OUTPUT_CLEAN = "老杨TV纯净版"

TRAP_NOTICE_TEXT = f"⚠️ 警告：当前专线已过期断流！老链接已彻底作废！\n\n最新全量/纯净矩阵链接或当前密码请加QQ群“{MY_QQ_GROUP}”获取"
TRAP_SITE_NAME_1 = f"🚨 请前往QQ群“{MY_QQ_GROUP}”获取最新密码🚨 当前专线密码已过期断流！"
TRAP_SITE_NAME_2 = f"🚨 请前往QQ群“{MY_QQ_GROUP}”获取最新订阅链接矩阵"
TRAP_LIVE_GROUP = "🚨 接口过期断流 ｜ 提示"
TRAP_LIVE_CHANNEL = f"👉 线路已过期 ➡️ 加QQ群“{MY_QQ_GROUP}”获取最新订阅密码"

# ====================================================================
# 📡 【五、客户端通知弹窗与 DOH/JS 注入高级规则配置区】
# ====================================================================
THANKS_WARNING = f"\n\n👑如果遇到失效 or 断流，请及时回 Telegram 频道（{MY_PROMO_CHANNEL}）或微信群获取当前最新密码锁！"
WELCOME_NOTICE_FULL = "欢迎使用【老杨TV粉丝专属全量专线】！本接口结合佬&鱼佬的优质核心资源缝合而成，纯净无广告！重要提示：本接口密码不定期全自动更换！"
WELCOME_NOTICE_CLEAN = "欢迎使用【老杨TV专属绿色客厅专线】！本接口已全面过滤敏感、擦边 and 福利内容，全家老少看电视更安全、更绿色！"

ALI_DOH_CONFIG = {"name": "AliDNS", "url": "https://dns.alidns.com/dns-query", "ips": ["223.5.5.5", "223.6.6.6"]}

CUSTOM_AD_BLOCK_JS = [
    "console.log('老楊TV高級WebView攔確器啟動');",
    "window.addEventListener('DOMContentLoaded', function() {",
    "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });",
    "   Function.prototype.__constructor__ = Function.prototype.constructor;",
    "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };",
    "});",
    "setInterval(() => { let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]']; selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); }); }, 400);"
]

# Telegram 消息模板定义
TG_PWD_MSG_TEMPLATE = (
    "🔔 *老杨TV · 全新硬核双通道密码锁发布* 🔔\n\n"
    "📅 *生效时间*：`{current_time}` (北京时间)\n"
    "🔑 *全新专线密锁*：`{current_token}`\n\n"
    "🚀 *重要提示*：\n密码锁已成功交替！旧接口已全线开启【金蝉脱壳】大轰炸，老链接彻底作废，请及时复制下方对应通道的最新链接！\n\n"
    "🔞 *最新【老杨TV全量版】矩阵订阅*：\n`{full_sub_url}`\n\n"
    "🏡 *最新【老杨TV纯净版】客厅订阅*：\n`{clean_sub_url}`\n\n"
    f"👑 全量版与纯净版已在后台全自动换锁，请及时前往电视端更新。若电视端遇到断流请尝试重启软件或前往TG频道（{MY_PROMO_CHANNEL}）获取支持！"
)

# 变动消息模板定义
TG_UPDATE_MSG_TEMPLATE = (
    "🔔 *老杨TV 缝合矩阵接口变更通知* 🔔\n\n"
    "📅 *更新时间*：{current_time} (北京时间)\n"
    "🚀 *变动说明*：检测到上游数据源更新或手工区调整，双版本配置已全自动编译上链！\n\n"
    "{detail_msg}\n\n"
    "📡 *【 最新多版本订阅矩阵 (点击可自动复制)】*：\n\n"
    "🔞 *1. 老杨TV全量版* (包含全部线路):\n`{full_sub_url}`\n\n"
    "🏡 *2. 老杨TV纯净版* (已自动全面过滤敏感内容):\n`{clean_sub_url}`\n\n"
    f"👑 全量版与纯净版已在后台无缝更新。更新配置即可，若遇到断流请尝试重启软件或及时前往TG频道（{MY_PROMO_CHANNEL}）获取当前最新密码锁！"
)

# ====================================================================
# ✍️ 【通道一：老杨专属点播手工加线区】
# ====================================================================
MY_CUSTOM_SITES = [
    {
			"key": "采集合集py",
			"name": f"🦋采集合集(py)｜{MY_TG_SUFFIX.strip('｜')}",
			"type": 3,
			"api": "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/py/采集合集.py",
			"searchable": 1,
			"quickSearch": 1,
			"filterable": 1,
			"changeable": 1,
			"playerType": 2,
			"ext": "0"
	},
	{
			"key": "js_douban",
			"name": "🦋豆瓣(js)",
			"type": 3,
			"api": "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/douban_min.js",
			"searchable": 0,
			"quickSearch": 0,
			"filterable": 1,
			"changeable": 0
	}
]

# ====================================================================
# 📺 【通道二：老杨专属直播手工加线区】
# ====================================================================
MY_CUSTOM_LIVES = [
    {"name": "乡村电视", "type": 0, "playerType": 2, "ua": "okhttp/5.3.2", "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"},
    {"name": "锋云直播", "type": 3, "url": "https://gh-proxy.org/https://raw.githubusercontent.com/807080747/zv/refs/heads/main/suale.txt", "ua": "okhttp/5.3.2", "timeout": 10, "playerType": 2},
    {"name": "最新电影", "type": 0, "ua": "okhttp/5.3.2", "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/Ly_18/refs/heads/main/datas/%E6%9C%80%E6%96%B0%E7%94%B5%E5%BD%B1.m3u"},
    {"name": "Kimentanm", "type": 0, "url": "https://ghfast.top/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u", "playerType": 2},
    {"name": "综合直播", "type": 0, "playerType": 2, "url": "https://ghfast.top/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt", "ua": "bingcha/1.1 (mianfeifenxiang) "},
    {"name": "央卫TV", "type": 0, "ua": "okhttp/5.3.2", "url": "http://47.120.41.246:8025/vip/jar/zb.php"},
    {"name": "超稳定流畅", "type": 0, "ua": "okhttp/5.3.2", "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E8%B6%85%E7%A8%B3%E5%AE%9A%E6%B5%81%E7%95%85.txt"},
    {"name": "国产直播🔞", "type": 0, "ua": "okhttp/5.3.2", "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%9B%B4%E6%92%AD_20260417_024507.m3u"},
    {"name": "国产精品🔞", "type": 0, "ua": "okhttp/5.3.2", "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%B2%BE%E5%93%81_20260417_024507.m3u"},
    {"name": "4K福利🔞", "type": 0, "ua": "okhttp/5.3.2", "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/4k%E7%A6%8F%E5%88%A9.m3u"},
    {"name": "探花🔞", "type": 0, "ua": "okhttp/5.3.2", "url": "https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E6%8E%A2%E8%8A%B1%E7%BA%A6%E7%82%AE_20260417_024507.m3u"},
    {"name": "咪咕", "type": 0, "ua": "okhttp/5.3.2", "url": "https://develop202.github.io/migu_video/interface.txt"},
    {"name": "Gather「IPTV」", "type": 3, "url": "https://iptv.yang-1989.xyz/playlist.m3u", "epg": "https://material.yang-1989.xyz/epg.xml.gz", "ua": "okhttp/5.3.2", "timeout": 10, "playerType": 2},
    {"name": "Live「直播」", "type": 3, "url": "https://live.yang-1989.eu.org/Live.m3u", "ua": "okhttp/5.3.2", "timeout": 10, "playerType": 2},
    {"name": "myTV「香港」1", "type": 3, "url": "https://iptv.yang-1989.xyz/myTV/playlist.m3u", "epg": "https://material.yang-1989.xyz/epg.xml.gz", "ua": "okhttp/5.3.2", "timeout": 10, "playerType": 2}
]
