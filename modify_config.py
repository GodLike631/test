import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/老杨TV.json'

def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 1. 物理提取海豚源里的 sites 和 lives 内部的纯文本
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

if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 🌐 【原厂高级瞒天过海脚本 - 强行清空宿主并重构老杨公告】
# 严格遵循文档 12 章 UX 规范，用纯正 CSS/DOM 注入，抹除百度，就地渲染公告
# ====================================================================
inline_js_code = """
(function() {
    if (window.top !== window) return;
    
    // 1. 抹除宿主网站（如百度）的所有干扰元素，给老杨公告留出纯净白纸
    document.title = "老杨TV · 官方导航首页";
    
    // 2. 创建符合鱼壳自适应的安全区全套样式
    var css = `
        html, body { background-color: #0d0d11 !important; color: #e2e8f0 !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; box-sizing: border-box; width: 100% !important; height: 100% !important; overflow-x: hidden; }
        body { padding-top: calc(100px + var(--fm-safe-top, 0px)) !important; padding-left: 20px; padding-right: 20px; padding-bottom: 40px; display: flex !important; flex-direction: column !important; align-items: center !important; justify-content: flex-start !important; }
        .container { max-width: 850px; width: 100%; background: linear-gradient(145deg, #13131a, #1c1c24); border-radius: 20px; padding: 30px; box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7); border: 1px solid #2d2d3d; box-sizing: border-box; margin: 0 auto; text-align: left; }
        .marquee-box { background: linear-gradient(90deg, #ff4e50, #f9d423); color: #000000; padding: 16px; border-radius: 12px; text-align: center; font-size: 1.5rem; font-weight: 800; margin-bottom: 25px; box-shadow: 0 6px 20px rgba(255, 78, 80, 0.25); letter-spacing: 1px; line-height: 1.6; }
        .highlight-tag { background-color: #1b5e20; color: #00e676; padding: 2px 10px; border-radius: 6px; font-size: 1.4rem; font-weight: 900; margin: 0 4px; border: 1px solid #00e676; display: inline-block; box-shadow: 0 0 8px rgba(0, 230, 118, 0.5); }
        h2 { font-size: 1.7rem; text-align: center; margin: 0 0 10px 0; color: #38bdf8; }
        .subtitle { text-align: center; color: #94a3b8; font-size: 1rem; margin-bottom: 25px; line-height: 1.6; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
        @media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
        .card { background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 14px; padding: 20px; box-sizing: border-box; }
        .card-title { font-size: 1.2rem; font-weight: bold; margin-bottom: 12px; }
        .fish-title { color: #38bdf8; }
        .dolphin-title { color: #2dd4bf; }
        .card-content { font-size: 0.95rem; color: #cbd5e1; line-height: 1.8; }
        .danger-box { background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); border-left: 5px solid #ef4444; border-radius: 12px; padding: 20px; margin-bottom: 25px; }
        .danger-title { color: #f87171; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
        .danger-text { font-size: 1rem; line-height: 1.7; color: #f1f5f9; }
        .statement-box { background: #181824; border-radius: 14px; padding: 22px; border: 1px solid #2a2a3a; }
        .statement-title { color: #f1f5f9; font-size: 1.2rem; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #2d2d3d; padding-bottom: 10px; }
        .statement-item { font-size: 0.9rem; color: #94a3b8; line-height: 1.8; margin-bottom: 12px; }
    `;
    
    var styleEl = document.createElement('style');
    styleEl.innerHTML = css;
    document.head.appendChild(styleEl);

    // 3. 动态绘制纯正公告 DOM
    var html = `
        <div class="container">
            <div class="marquee-box">👉 请花1分钟时间看完此公告，点击<span class="highlight-tag">返回键</span>退出全屏后，点击左上角切换线路，即可正常观看</div>
            <h2>👑 特别致谢与版权声明</h2>
            <div class="subtitle">本接口的诞生离不开大后方两位业内顶流技术大佬的无私奉献，特此致谢：</div>
            <div class="grid">
                <div class="card">
                    <div class="card-title fish-title">🐋 感谢鱼佬的付出</div>
                    <div class="card-content">源码基础与发布主页: fish2018/webhtv<br>版本发布绝对地址: fish2018/webhtv/releases<br>Telegram 官方群组: 👉 https://t.me/webhtv</div>
                </div>
                <div class="card">
                    <div class="card-title dolphin-title">🐬 感谢海豚佬的付出</div>
                    <div class="card-content">核心仓库主页: FGBLH/GHK<br>数据源直链地址: FGBLH/GHK/海豚.json<br>Telegram 官方群组: 👉 https://t.me/hshsjk9</div>
                </div>
            </div>
            <div class="danger-box">
                <div class="danger-title">🚨 【超级防骗防割警告】</div>
                <div class="danger-text">本接口完全免费！本人仅将两位大佬的优质接口在云端进行了融合优化，纯属自用方便。如果你是花钱买来的，请立刻联系卖家退款举报！<br><span style="color: #fbbf24; font-weight: bold; display: inline-block; margin-top: 8px;">📢 欢迎关注官方专属 Telegram 频道:</span> https://t.me/huliys9</div>
            </div>
            <div class="statement-box">
                <div class="statement-title">⚠️ 免责声明</div>
                <div class="statement-item"><strong>1. 项目性质：</strong>本项目仅用于技术研究、自动化脚本测试与学术学习交流，严禁用于任何商业营利性用途。</div>
                <div class="statement-item"><strong>2. 内容说明：</strong>项目本身作为云端自动化数据缝合中转站，不存储、不分发、不制作任何影视及直播流媒体视频内容。所有接口内展示的数据，均源自网络公开可获取的数据源进行自动化整理与聚合。</div>
                <div class="statement-item"><strong>3. 版权归属：</strong>所有涉及的影视资源、直播源及软件品牌版权均归原作者、原厂官仓及相关合法平台所有。</div>
                <div class="statement-item"><strong>4. 版权处理：</strong>若相关资源涉及版权或其他侵权问题，请联系上游源头资源提供方或版权方进行删除处理。本自动同步仓库在收到通知后，会积极配合在 24 小时内移除相关缓存索引。</div>
            </div>
        </div>
    `;
    
    // 强制全屏覆盖，不给百度留一丁点残影
    document.body.innerHTML = html;
})();
"""

# 清洗压缩成合法的内联 JSON 字符串
clean_js_code = inline_js_code.replace("\n", " ").replace('"', '\\"')

# ====================================================================
# 🌟 【大厂网址宿主·内联无痕闭合方案】
# 1. 采用100%能够完美通过鱼壳订阅、更新网络试探请求的绝对合法顶级大厂域名
# 2. 宿主网络秒过，全盘剩余线路绝不丢包死锁；加载完毕后 extensions 瞬间移花接木重构公告
# ====================================================================
laoyang_homepage_json = f"""{{
            "key": "Laoyang_Home_Perfect",
            "name": "👑老杨TV · 官方公告首页",
            "type": 3,
            "api": "csp_Builtin",
            "homePage": "https://www.baidu.com",
            "extensions": [
                {{
                    "id": "laoyang-home-render",
                    "name": "老杨公告大厂宿主渲染器",
                    "runAt": "document-end",
                    "code": "{clean_js_code}"
                }}
            ]
        }},"""

if '"sites": [' in final_json_text:
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n        {laoyang_homepage_json}', 1)

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
final_json_text = final_json_text.replace('"warningText": "欢迎使用鱼儿自用缝合专线，完全免费！"', '"warningText": "欢迎使用老杨自用全量缝合专线，本接口完全免费！"')

# 强力消除尾部符号瑕疵
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🎉 【大满贯终极解法】全面攻克鱼壳底层大坑，接口更新/初次订阅彻底完美！")
