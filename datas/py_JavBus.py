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
        支援在 JSON 配置中的 site.ext 傳入代理字串 (例如 '{"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}')
        """
        try:
            self.proxies = json.loads(extend)
        except:
            self.proxies = {}
            
        self.host = "https://www.javbus.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': f"{self.host}/",
            'Connection': 'keep-alive'
        }

    def getName(self):
        return "🔞 老楊私房 • JavBus旗艦專線"

    def isVideoFormat(self, url):
        return any(ext in (url or '') for ext in ['.m3u8', '.mp4', '.ts', 'magnet:?'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def homeContent(self, filter):
        """首頁分類設定：採用標準 Class 物件規範"""
        result = {
            "class": [
                {"type_id": "genre", "type_name": "🦋 亞洲有碼"},
                {"type_id": "uncensored", "type_name": "🦋 亞洲無碼"},
                {"type_id": "stars", "type_name": "🦋 女優企劃總覽"}
            ]
        }
        return result

    def homeVideoContent(self):
        """首頁推薦：抓取瀑布流最新卡片，並透過 getProxyUrl() 代理轉發海報圖片"""
        try:
            res = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200: return {'list': []}
            return {'list': self.get_video_list(res.text)}
        except Exception as e:
            print(f"JavBus homeVideoContent error: {e}")
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        """分頁切換核心：適應無限加載與分頁拼接"""
        try:
            page_num = int(pg) if pg and pg.isdigit() else 1
            if tid == "genre":
                url = f"{self.host}/page/{page_num}"
            elif tid == "uncensored":
                url = f"{self.host}/uncensored/page/{page_num}"
            else:
                url = f"{self.host}/page/{page_num}"

            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200:
                return {'list': [], 'page': pg, 'pagecount': 1}
                
            videos = self.get_video_list(res.text)
            return {
                'list': videos,
                'page': pg,
                'pagecount': page_num + 1,  # 盒子端無限滾動
                'limit': 30,
                'total': 9999
            }
        except Exception as e:
            print(f"JavBus categoryContent error: {e}")
            return {'list': [], 'page': pg, 'pagecount': 1}

    def detailContent(self, ids):
        """
        影片詳情核心解析：解開 Ajax 異步加載的磁力數據表
        將多個磁力下載地址轉化為電視盒子的播放集數（vod_play_url）
        """
        try:
            vod_id = ids[0]
            url = f"{self.host}/{vod_id}" if not vod_id.startswith('http') else vod_id
            
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200:
                return {'list': []}
                
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            
            title = soup.find('h3').text.strip() if soup.find('h3') else "未知影片"
            img_div = soup.find('a', class_='bigImage')
            img_url = img_div.get('href', '') if img_div else ""
            if img_url.startswith("//"): img_url = "https:" + img_url
            
            # 海報圖片也進行本地代理包裝，防屏蔽
            proxy_img = f"{self.getProxyUrl()}&url={urllib.parse.quote(img_url)}&type=img"
            
            info_div = soup.find('div', class_='col-md-3 info')
            vod_content = info_div.text.strip().replace('\n', ' ') if info_div else title
            
            # 🔔 二次進擊：解析 Ajax 動態渲染的磁力連結
            plist = []
            gid_match = re.search(r'var gid = (\d+);', html)
            uc_match = re.search(r'var uc = (\d+);', html)
            img_match = re.search(r'var img = \'(.*?)\';', html)
            
            if gid_match:
                gid = gid_match.group(1)
                uc = uc_match.group(1) if uc_match else "0"
                img = img_match.group(1) if img_match else ""
                
                ajax_url = f"{self.host}/ajax/uncensoredmod.php?gid={gid}&lang=zh&img={img}&uc={uc}"
                ajax_headers = dict(self.headers)
                ajax_headers["Referer"] = url
                
                ajax_res = requests.get(ajax_url, headers=ajax_headers, proxies=self.proxies, timeout=10)
                if ajax_res.status_code == 200 and ajax_res.text.strip():
                    ajax_soup = BeautifulSoup(ajax_res.text, 'html.parser')
                    tr_items = ajax_soup.find_all('tr')
                    
                    for tr in tr_items:
                        td_link = tr.find('a')
                        if td_link and 'magnet:?' in td_link.get('href', ''):
                            mag_url = td_link.get('href', '')
                            mag_name = td_link.text.strip().replace('\n', '').replace('\t', '')
                            
                            size_td = tr.find_all('td')[1] if len(tr.find_all('td')) > 1 else None
                            size_str = size_td.text.strip() if size_td else "未知大小"
                            
                            # 拼裝格式符合：名稱[大小]$磁力連結
                            plist.append(f"{mag_name}[{size_str}]${mag_url}")

            if not plist:
                plist.append("⚠️ 暫無磁力備份(請更換線路)$magnet:?xt=urn:btih:000000000000")

            vod = {
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": proxy_img,
                "vod_content": vod_content,
                "vod_remarks": "老楊私房合集",
                "vod_play_from": "老楊磁力快線",
                "vod_play_url": "#".join(plist)
            }
            return {'list': [vod]}
        except Exception as e:
            print(f"JavBus detailContent error: {e}")
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        """搜尋功能：自動將繁體字轉成簡體關鍵字去發送請求"""
        try:
            encoded_key = urllib.parse.quote(key)
            url = f"{self.host}/search/{encoded_key}&type=1"
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=12)
            if res.status_code != 200: return {'list': []}
            return {'list': self.get_video_list(res.text)}
        except Exception as e:
            print(f"JavBus searchContent error: {e}")
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        """播放解析：直接把磁力連結（Magnet）交付給電視內核調用 P2P 下載內核邊下邊播"""
        return {'parse': 0, 'url': id, 'header': self.headers}

    def localProxy(self, param):
        """本地代理：轉發海報圖片，阻斷防盜鏈干擾"""
        if param.get('type') == 'img':
            target_url = urllib.parse.unquote(param['url'])
            try:
                res = requests.get(target_url, headers=self.headers, proxies=self.proxies, timeout=10)
                return [200, res.headers.get('Content-Type', 'image/jpeg'), res.content]
            except:
                return [404, 'text/plain', b'Not Found']
        return [404, 'text/plain', b'Not Found']

    def get_video_list(self, html):
        """解析瀑布流卡片列表"""
        videos = []
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('a', class_='movie-box')
        for k in items:
            try:
                href = k.get('href', '')
                if not href: continue
                vod_id = href.split('/')[-1]
                
                img_div = k.find('div', class_='photo-frame')
                img_url = img_div.find('img').get('src', '') if img_div else ""
                if img_url.startswith("//"): img_url = "https:" + img_url
                
                title = img_div.find('img').get('title', '未知番號') if img_div else "未知番號"
                
                date_tags = k.find_all('date')
                remarks = date_tags[0].text.strip() if len(date_tags) > 0 else "HD"
                
                # 包裝圖片地址，走電視本地代理轉發防封
                proxy_pic = f"{self.getProxyUrl()}&url={urllib.parse.quote(img_url)}&type=img"
                
                videos.append({
                    'vod_id': vod_id,
                    'vod_name': title,
                    'vod_pic': proxy_pic,
                    'vod_remarks': f"番號: {remarks}",
                    'style': {"type": "rect", "ratio": 1.33}
                })
            except:
                continue
        return videos
