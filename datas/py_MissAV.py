# -*- coding: utf-8 -*-
import json
import random
import re
import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup

sys.path.append('..')
try:
    from base.spider import Spider
except ImportError:
    class Spider(object):
        def __init__(self): pass

class Spider(Spider):
    def init(self, extend=""):
        """
        初始化方法：完美同步 51.py 网络代理挂载机制
        """
        try:
            self.proxies = json.loads(extend)
        except:
            self.proxies = {}
            
        self.host = "https://missav.ws"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': f"{self.host}/",
            'Connection': 'keep-alive'
        }

    def getName(self):
        return "🦋 老杨私房 • MissAV女优榜"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def homeContent(self, filter):
        """首页分类设定"""
        result = {
            "class": [
                {"type_id": "ranking", "type_name": "👑 MissAV 女优人气总榜"}
            ]
        }
        return result

    def homeVideoContent(self):
        """首页推荐：默认加载人气榜第一页"""
        return self.categoryContent("ranking", "1", None, None)

    def categoryContent(self, tid, pg, filter, extend):
        """
        分页切换核心：完美複刻 51.py 的第一页自适应逻辑，精精准抓取头像与姓名
        """
        try:
            page_num = int(pg) if pg and pg.isdigit() else 1
            
            # 💡 高阶修正：MissAV 第一页不需要带有 ?page= 缀，否则服务器会返回空数据
            if page_num > 1:
                url = f"{self.host}/actresses/ranking?page={page_num}"
            else:
                url = f"{self.host}/actresses/ranking"

            print(f"MissAV 请求 URL: {url}")
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200:
                return {'list': [], 'page': pg, 'pagecount': 1}
                
            videos = []
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 💡 高阶精准定位：抓取 MissAV 女优网格卡片
            items = soup.find_all('div', class_='text-center')
            for k in items:
                try:
                    a_tag = k.find('a')
                    if not a_tag: continue
                    actress_url = a_tag.get('href', '')
                    if '/actresses/' not in actress_url: continue
                    
                    # 提取女优唯一标识
                    vod_id = actress_url.split('/')[-1]
                    
                    # 提取女优头像并进行 getProxyUrl() 包装防封锁
                    img_tag = k.find('img')
                    img_url = ""
                    if img_tag:
                        img_url = img_tag.get('data-src', '') or img_tag.get('src', '')
                    if not img_url: continue
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    
                    proxy_pic = f"{self.getProxyUrl()}&url={urllib.parse.quote(img_url)}&type=img"
                    
                    # 提取女优姓名
                    name_tag = k.find('h4')
                    title = name_tag.text.strip() if name_tag else "人气女神"
                    
                    # 提取关注人数备忘
                    sub_tag = k.find('p', class_='text-xs')
                    remarks = sub_tag.text.strip() if sub_tag else "巨星"
                    
                    videos.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': proxy_pic,
                        'vod_remarks': remarks,
                        'style': {"type": "rect", "ratio": 1.0} # 完美的正方形头像墙
                    })
                except:
                    continue
                    
            return {
                'list': videos,
                'page': pg,
                'pagecount': page_num + 1,  # 盒子端支持无限滚动翻页
                'limit': 50,
                'total': 500
            }
        except Exception as e:
            print(f"MissAV categoryContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1}

    def detailContent(self, ids):
        """
        点击女优头像时，全自动进入她的个人专页，拉取她的核心番号作品集
        """
        try:
            vod_id = ids[0]
            url = f"{self.host}/actresses/{vod_id}"
            
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200: return {'list': []}
            
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find('h1').text.strip() if soup.find('h1') else vod_id
            
            plist = []
            # 扫描女优主页里的所有影视作品卡片链接
            vod_items = soup.find_all('a', class_='text-secondary')
            for c, v in enumerate(vod_items, start=1):
                v_url = v.get('href', '')
                v_name = v.text.strip().replace('\n', '')
                if v_url and v_name:
                    plist.append(f"封神核心力作 {c}款：{v_name}${v_url}")
            
            if not plist:
                plist.append("⚠️ 暂无线上视频流备份$https://missav.ws")

            vod = {
                "vod_id": vod_id,
                "vod_name": f"👑 女优专題：{title}",
                "vod_pic": "",
                "vod_content": f"当前正在浏览 MissAV 人气榜巨星【{title}】的专属代表作合集。点击下方集数即可直接线上调动内核嗅探播放！",
                "vod_remarks": "MissAV 巨星榜",
                "vod_play_from": "MissAV 旗舰快线",
                "vod_play_url": "#".join(plist)
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"MissAV detailContent error: {e}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        """关键字搜寻女优"""
        try:
            encoded_key = urllib.parse.quote(key)
            url = f"{self.host}/search/{encoded_key}"
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200: return {'list': []}
            
            videos = []
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.find_all('div', class_='text-center')
            for k in items:
                try:
                    a_tag = k.find('a')
                    if not a_tag or '/actresses/' not in a_tag.get('href', ''): continue
                    vod_id = a_tag.get('href', '').split('/')[-1]
                    title = k.find('h4').text.strip() if k.find('h4') else key
                    videos.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': "",
                        'vod_remarks': "搜寻结果"
                    })
                except: continue
            return {'list': videos}
        except Exception as e:
            print(f"MissAV searchContent error: {e}")
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """播放解析：调用电视内置的高级系统WebView去全自动嗅探流媒体网頁中的 m3u8 地址"""
        return {
            'parse': 1,  # 1 代表强制开启 WebView 嗅探，免密秒播
            'url': id,
            'header': self.headers
        }

    def localProxy(self, param):
        """本地反向代理：安全绕过 Cloudflare 防盗链转发海报头像图片"""
        if param.get('type') == 'img':
            target_url = urllib.parse.unquote(param['url'])
            try:
                res = requests.get(target_url, headers=self.headers, proxies=self.proxies, timeout=10)
                return [200, res.headers.get('Content-Type', 'image/jpeg'), res.content]
            except:
                return [404, 'text/plain', b'Not Found']
        return [404, 'text/plain', b'Not Found']
