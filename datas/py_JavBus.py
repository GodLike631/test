#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

# 導入 FongMi 影視官方自帶的 Spider 基類
# 基類路徑符合官方抽象層定位
try:
    from com.github.catvod.crawler.Spider import Spider
except ImportError:
    # 本地調試相容性基類
    class Spider(object):
        def __init__(self): pass

class Spider(Spider):
    def __init__(self):
        super(Spider, self).__init__()
        self.siteUrl = "https://www.javbus.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.javbus.com/",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        self.proxy_url = None

    def init(self, context, extend):
        """
        初始化方法：只執行一次。
        支援在配置檔案的 Site.ext 中傳入自訂代理（例如 "http://127.0.0.1:7890"）
        """
        print(f"JavBus Spider Init, ext: {extend}")
        if extend:
            # 支援 ext 傳入代理網址，解決部分盒子需要翻牆的問題
            if extend.startswith("http"):
                self.proxy_url = extend
                print(f"JavBus 已掛載自訂網路代理: {self.proxy_url}")

    def fetch(self, url, headers=None):
        """強健的自適應網路請求工具"""
        if not headers:
            headers = self.headers
        try:
            req = urllib.request.Request(url, headers=headers)
            if self.proxy_url:
                # 動態注入代理攔截
                proxy_handler = urllib.request.ProxyHandler({'http': self.proxy_url, 'https': self.proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
                return opener.open(req, timeout=15).read().decode('utf-8', errors='ignore')
            else:
                return urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"JavBus 網路請求報錯: {url}, 原因: {e}")
            return ""

    def homeContent(self, filter):
        """首頁分類設定：嚴格遵循 Class 物件規範"""
        result = {}
        # 定義高階分類列表
        result["class"] = [
            {"type_id": "genre", "type_name": "有碼影片"},
            {"type_id": "uncensored", "type_name": "無碼影片"},
            {"type_id": "stars", "type_name": "女優企劃"}
        ]
        return json.dumps(result, ensure_ascii=False)

    def homeVideoContent(self):
        """首頁推薦：抓取 JavBus 首頁最新的瀑布流卡片"""
        result = {}
        videos = []
        html = self.fetch(self.siteUrl)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            # 瀑布流元素
            items = soup.find_all('a', class_='movie-box')
            for item in items:
                try:
                    url = item.get('href', '')
                    vod_id = url.split('/')[-1] # 使用番號或唯一標識作為 ID
                    img_div = item.find('div', class_='photo-frame')
                    img_url = img_div.find('img').get('src', '') if img_div else ""
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    
                    title_span = item.find('span')
                    title = title_span.text.strip() if title_span else "未知番號"
                    
                    # 提取番號和日期做成標籤
                    date_div = item.find_all('date')
                    remarks = date_div[0].text.strip() if len(date_div) > 0 else "HD"
                    
                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": title,
                        "vod_pic": img_url,
                        "vod_remarks": f"番號: {remarks}"
                    })
                except:
                    continue
        result["list"] = videos
        return json.dumps(result, ensure_ascii=False)

    def categoryContent(self, tid, pg, filter, extend):
        """分頁與條件切換核心瀏覽頁面"""
        result = {}
        videos = []
        page = int(pg)
        
        # 拼接分頁網址
        if tid == "genre":
            url = f"{self.siteUrl}/page/{page}"
        elif tid == "uncensored":
            url = f"{self.siteUrl}/uncensored/page/{page}"
        else:
            url = f"{self.siteUrl}/page/{page}"
            
        html = self.fetch(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            items = soup.find_all('a', class_='movie-box')
            for item in items:
                try:
                    vod_url = item.get('href', '')
                    vod_id = vod_url.split('/')[-1]
                    img_url = item.find('img').get('src', '')
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    title = item.find('img').get('title', '未知番號')
                    
                    date_div = item.find_all('date')
                    remarks = date_div[0].text.strip() if len(date_div) > 0 else "HD"
                    
                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": title,
                        "vod_pic": img_url,
                        "vod_remarks": remarks
                    })
                except:
                    continue
        result["list"] = videos
        result["pagecount"] = page + 1 # 動態無限加載分頁
        return json.dumps(result, ensure_ascii=False)

    def detailContent(self, ids):
        """
        影片詳情解析：極其重要！
        將網頁內的「多個磁力連結（Magnet）」轉化為播放集數格式！
        """
        result = {}
        vod_id = ids[0]
        url = f"{self.siteUrl}/{vod_id}"
        
        html = self.fetch(url)
        if not html:
            return json.dumps({"list": []})
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. 抓取基本數據
        title = soup.find('h3').text.strip() if soup.find('h3') else "未知番號"
        img_div = soup.find('a', class_='bigImage')
        img_url = img_div.get('href', '') if img_div else ""
        if img_url.startswith("//"): img_url = "https:" + img_url
        
        # 2. 提取簡介與標籤
        info_div = soup.find('div', class_='col-md-3 info')
        content_text = info_div.text.strip() if info_div else "暫無簡介"
        
        # 3. 高級核心：二次解析異步加載的磁力數據表
        # JavBus的磁力連結是靠 Ajax 請求動態渲染的，必須抓取對應腳本參數
        magnet_lines = []
        try:
            script_text = html
            gid_match = re.search(r'var gid = (\d+);', script_text)
            uc_match = re.search(r'var uc = (\d+);', script_text)
            img_match = re.search(r'var img = \'(.*?)\';', script_text)
            
            if gid_match:
                gid = gid_match.group(1)
                uc = uc_match.group(1) if uc_match else "0"
                img = img_match.group(1) if img_match else ""
                
                # 拼接異步磁力 API 接口
                ajax_url = f"{self.siteUrl}/ajax/uncensoredmod.php?gid={gid}&lang=zh&img={img}&uc={uc}"
                ajax_headers = dict(self.headers)
                ajax_headers["Referer"] = url
                
                ajax_html = self.fetch(ajax_url, headers=ajax_headers)
                if ajax_html:
                    ajax_soup = BeautifulSoup(ajax_html, 'html.parser')
                    tr_items = ajax_soup.find_all('tr')
                    
                    # 遍歷磁力下載列表
                    for tr in tr_items:
                        td_links = tr.find('a')
                        if td_links and 'magnet:?' in td_links.get('href', ''):
                            mag_url = td_links.get('href', '')
                            # 拿名稱和檔案大小作為集數名字
                            mag_name = td_links.text.strip().replace('\n', '').replace('\t', '')
                            size_td = tr.find_all('td')[1] if len(tr.find_all('td')) > 1 else None
                            size_str = size_td.text.strip() if size_td else "未知大小"
                            
                            # 拼裝格式符合：集數名$磁力網址
                            magnet_lines.append(f"{mag_name}[{size_str}]${mag_url}")
        except Exception as e:
            print(f"JavBus 磁力解析失敗: {e}")

        # 如果沒抓到磁力，提供一個提示線路
        if not magnet_lines:
            magnet_lines.append("⚠️暫無可用磁力備份$magnet:?xt=urn:btih:000000000000")

        # 4. 完美打包符合 SPIDER 規範的雙 $ 分隔符物件
        vod_item = {
            "vod_id": vod_id,
            "vod_name": title,
            "vod_pic": img_url,
            "vod_content": content_text,
            "vod_remarks": "老楊私房合集",
            "vod_play_from": "磁力下載專線",
            "vod_play_url": "#".join(magnet_lines) # 使用 # 分隔每一集
        }
        
        result["list"] = [vod_item]
        return json.dumps(result, ensure_ascii=False)

    def searchContent(self, key, quick):
        """搜尋功能：框架會自動繁轉簡，我們將關鍵字編碼後發起 GET 請求"""
        result = {}
        videos = []
        encoded_key = urllib.parse.quote(key)
        url = f"{self.siteUrl}/search/{encoded_key}&type=1"
        
        html = self.fetch(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            items = soup.find_all('a', class_='movie-box')
            for item in items:
                try:
                    vod_url = item.get('href', '')
                    vod_id = vod_url.split('/')[-1]
                    img_url = item.find('img').get('src', '')
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    title = item.find('img').get('title', '未知番號')
                    
                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": title,
                        "vod_pic": img_url,
                        "vod_remarks": "搜尋結果"
                    })
                except:
                    continue
        result["list"] = videos
        return json.dumps(result, ensure_ascii=False)

    def playerContent(self, flag, id, vipFlags):
        """播放解析：直接把 Magnet 網址丟給內核，調用電視自帶的 P2P 引擎播放"""
        result = {
            "parse": 0,    # 0 代表直接播放，不需要二級網頁嗅探
            "url": id,     # 這裡的 id 就是集數裡的 magnet:? 網址
            "format": "application/x-mpegURL" # 跳過格式檢測
        }
        return json.dumps(result, ensure_ascii=False)

    def destroy(self):
        print("JavBus Spider Destroyed")