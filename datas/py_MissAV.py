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
        初始化方法：完美同步 51.py 網絡代理掛載機制
        支援在配置檔案的 site.ext 中傳入自訂代理參數
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
        return "🦋 老楊私房 • MissAV女優人氣榜"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def homeContent(self, filter):
        """首頁分類設定：採用標準 Class 物件規範"""
        result = {
            "class": [
                {"type_id": "ranking", "type_name": "👑 MissAV 女優人氣總榜"}
            ]
        }
        return result

    def homeVideoContent(self):
        """首頁推薦：預設加載人氣榜第一頁"""
        return self.categoryContent("ranking", "1", None, None)

    def categoryContent(self, tid, pg, filter, extend):
        """分頁切換核心：精準抓取女優頭像、姓名、以及粉絲關注數"""
        try:
            page_num = int(pg) if pg and pg.isdigit() else 1
            # 拼接 MissAV 女優排行榜官方直鏈網址
            url = f"{self.host}/actresses/ranking?page={page_num}"

            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200:
                return {'list': [], 'page': pg, 'pagecount': 1}
                
            videos = []
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 尋找女優卡片網格元素
            items = soup.find_all('div', class_='text-center')
            for k in items:
                try:
                    # 提取女優作品專頁的 URL
                    a_tag = k.find('a')
                    if not a_tag: continue
                    actress_url = a_tag.get('href', '')
                    # 拿女優的唯一英文代號名字作為唯一 ID
                    vod_id = actress_url.split('/')[-1]
                    
                    # 提取頭像地址
                    img_tag = k.find('img')
                    img_url = img_tag.get('data-src', '') or img_tag.get('src', '') if img_tag else ""
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    
                    # 提取姓名與排行關注數
                    name_tag = k.find('h4')
                    title = name_tag.text.strip() if name_tag else "未知人氣女神"
                    
                    sub_tag = k.find('p', class_='text-xs')
                    remarks = sub_tag.text.strip() if sub_tag else "人氣巨星"
                    
                    # 🌟 核心安全防護：頭像圖片全部走 getProxyUrl() 進行盒子本地中轉發，防止 Cloudflare 擋圖
                    proxy_pic = f"{self.getProxyUrl()}&url={urllib.parse.quote(img_url)}&type=img"
                    
                    videos.append({
                        'vod_id': vod_id,
                        'vod_name': title,
                        'vod_pic': proxy_pic,
                        'vod_remarks': remarks,
                        'style': {"type": "rect", "ratio": 1.0} # 正方形女神頭像牆
                    })
                except:
                    continue
                    
            return {
                'list': videos,
                'page': pg,
                'pagecount': page_num + 1,  # 支持滾動無限翻頁
                'limit': 50,
                'total': 500
            }
        except Exception as e:
            print(f"MissAV categoryContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1}

    def detailContent(self, ids):
        """
        高階動態交互：點擊女優頭像時，全自動將其轉換為「該女優的作品專題合集」！
        """
        try:
            vod_id = ids[0]
            # 拼接該女優的作品專頁連結
            url = f"{self.host}/actresses/{vod_id}"
            
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200: return {'list': []}
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 抓取女優真實名字
            title = soup.find('h1').text.strip() if soup.find('h1') else vod_id
            
            plist = []
            # 掃描專頁裡該女優的所有影片作品卡片
            vod_items = soup.find_all('a', class_='text-secondary')
            for c, v in enumerate(vod_items, start=1):
                v_url = v.get('href', '')
                v_name = v.text.strip().replace('\n', '')
                if v_url and v_name:
                    # 轉換為格式：作品名$影片網頁網址
                    plist.append(f"番號作品 {c}款：{v_name}${v_url}")
            
            if not plist:
                plist.append("⚠️ 暫無線上流媒體備份$https://missav.ws")

            vod = {
                "vod_id": vod_id,
                "vod_name": f"👑 女優專題合集：{title}",
                "vod_pic": "",
                "vod_content": f"當前正在瀏覽 MissAV 人氣榜巨星【{title}】的專屬影視海報牆。下方已為您全自動解鎖拉取該女神的全部核心代表作，點擊即可直接線上免密碼嗅探播放！",
                "vod_remarks": "MissAV 巨星專區",
                "vod_play_from": "MissAV 旗艦快線",
                "vod_play_url": "#".join(plist) # 用 # 分隔每一款作品
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"MissAV detailContent error: {e}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        """關鍵字搜尋"""
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
                        'vod_remarks': "搜尋結果"
                    })
                except: continue
            return {'list': videos}
        except Exception as e:
            print(f"MissAV searchContent error: {e}")
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """播放解析：將影片網址交付給電視端，FongMi 內核會自動調用核心 WebView 進行高級流媒體嗅探"""
        return {
            'parse': 1,  # 1 代表調用內置嗅探內核，自動抓取網頁內部的真實 m3u8 播放地址
            'url': id,
            'header': self.headers
        }

    def localProxy(self, param):
        """本地代理反向代理：安全繞過 Cloudflare 防盜鏈轉發頭像與封面圖片"""
        if param.get('type') == 'img':
            target_url = urllib.parse.unquote(param['url'])
            try:
                res = requests.get(target_url, headers=self.headers, proxies=self.proxies, timeout=10)
                return [200, res.headers.get('Content-Type', 'image/jpeg'), res.content]
            except:
                return [404, 'text/plain', b'Not Found']
        return [404, 'text/plain', b'Not Found']

    def destroy(self):
        pass
