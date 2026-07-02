# coding=utf-8
# !/usr/bin/python
import sys
import base64
import hashlib
import json
import requests
from typing import Tuple
from base.spider import Spider
from datetime import datetime, timedelta
from urllib.parse import quote, unquote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
sys.path.append('..')

class Spider(Spider):

    def init(self, extend="{}"):
        origin = 'https://zh.pikpedcams.com'
        self.host = origin
        # 【方案二·移动端伪装】使用 iPad 浏览器的 User-Agent，这是最容易触发“免解密流”的特征
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Origin': origin,
            'Referer': f"{origin}/",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.stripchat_key = self.decode_key_compact()
        self._hash_cache = {}
        self.create_session_with_retry()

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def homeContent(self, filter):
        result = {}
        classes = [{'type_name': '女主播g', 'type_id': 'girls'}, {'type_name': '情侣c', 'type_id': 'couples'}, {'type_name': '男主播m', 'type_id': 'men'}, {'type_name': '跨性别t', 'type_id': 'trans'}]
        filters = {}
        value = [{'n': '中国', 'v': 'tagLanguageChinese'}, {'n': '亚洲', 'v': 'ethnicityAsian'}, {'n': '白人', 'v': 'ethnicityWhite'}, {'n': '拉丁', 'v': 'ethnicityLatino'}, {'n': '混血', 'v': 'ethnicityMultiracial'}, {'n': '印度', 'v': 'ethnicityIndian'}, {'n': '阿拉伯', 'v': 'ethnicityMiddleEastern'}, {'n': '黑人', 'v': 'ethnicityEbony'}]
        value_gay = [{'n': '情侣', 'v': 'sexGayCouples'}, {'n': '直男', 'v': 'orientationStraight'}]
        for tid in ['girls', 'couples', 'men', 'trans']:
            c_value = value[:]
            if tid == 'men':
                c_value += value_gay
            filters[tid] = [{'key': 'tag', 'value': c_value}]
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, tid, pg, filter, extend):
        if isinstance(extend, str):
            try:
                extend = json.loads(extend)
            except:
                extend = {}
        limit = 60
        offset = limit * (int(pg) - 1)
        domain = f"{self.host}/api/front/models?improveTs=false&removeShows=false&limit={limit}&offset={offset}&primaryTag={tid}&sortBy=stripRanking&rcmGrp=A&rbCnGr=true&prxCnGr=false&nic=false"
        if extend and 'tag' in extend:
            domain += "&filterGroupTags=%5B%5B%22" + extend['tag'] + "%22%5D%5D"
        
        rsp = self.session.get(domain, headers=self.headers).json()
        vodList = rsp.get('models', [])
        videos = []
        for vod in vodList:
            id = str(vod['id'])
            name = str(vod['username']).strip()
            stamp = vod['snapshotTimestamp']
            country = str(vod['country']).strip()
            flag = self.country_code_to_flag(country)
            remark = "🎫" if vod['status'] == "groupShow" else ""
            videos.append({
                "vod_id": name,
                "vod_name": f"{flag}{name}",
                "vod_pic": f"https://img.doppiocdn.net/thumbs/{stamp}/{id}",
                "vod_remarks": remark
            })
        total = int(rsp.get('filteredCount', 0))
        result = {}
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = (total + limit - 1) // limit if total > 0 else 1
        result['limit'] = limit
        result['total'] = total
        return result

    def detailContent(self, array):
        username = array[0]
        domain = f"{self.host}/api/front/v2/models/username/{username}/cam"
        rsp = self.session.get(domain, headers=self.headers).json()
        info = rsp['cam']
        user = rsp['user']['user']
        id = str(user['id'])
        country = str(user['country']).strip()
        isLive = "" if user['isLive'] else " 已下播"
        flag = self.country_code_to_flag(country)
        remark = ''
        if info.get('show'):
            show = info['show']['details']['groupShow']
            BJtime = (datetime.strptime(show["startAt"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)).strftime("%m月%d日 %H:%M")
            remark = f"🎫 始于 {BJtime}"
        
        # 记录真实数据，以便调试
        vod = [{
            "vod_id": id,
            "vod_name": str(info.get('topic', '')).strip(), 
            "vod_pic": str(user['avatarUrl']),
            "vod_director": f"{flag}{username}{isLive}",
            "vod_remarks": remark,
            'vod_play_from': 'StripChat',
            'vod_play_url': f"{id}${id}"
        }]
        result = {}
        result['list'] = vod
        return result

    def playerContent(self, flag, id, vipFlags):
        # 依然请求 master 索引，但现在整个会话都是 iPad 移动端特征
        domain = f"https://edge-hls.doppiocdn.net/hls/{id}/master/{id}_auto.m3u8?playlistType=lowLatency"
        rsp = self.session.get(domain, headers=self.headers).text
        lines = rsp.strip().split('\n')
        
        psch_list = []
        for line in lines:
            if line.startswith('#EXT-X-MOUFLON:PSCH:v2:'):
                parts = line.split(':')
                if len(parts) >= 4:
                    psch_list.append(parts[3].strip())
                    
        url = []
        stream_count = 0
        
        for i, line in enumerate(lines):
            if '#EXT-X-STREAM-INF' in line:
                name_start = line.find('NAME="') + 6
                name_end = line.find('"', name_start)
                qn = line[name_start:name_end]
                url_base = lines[i + 1]
                
                # 如果是移动端特供流，可能不需要复杂的 psch
                current_psch = psch_list[stream_count] if stream_count < len(psch_list) else ""
                full_url = f"{url_base}&psch={current_psch}"
                
                # 再次注入移动端伪装，防止 CDN 二次校验播放器
                proxy_url = f"{self.getProxyUrl()}&url={quote(full_url)}"
                
                url.append(qn)
                url.append(proxy_url)
                stream_count += 1
                
        result = {}
        result["url"] = url
        result["parse"] = '0'
        result["contentType"] = ''
        result["header"] = self.headers
        return result

    def localProxy(self, param):
        url = unquote(param['url'])
        # 关键：这里必须带上和上面 init 里面完全一致的 Headers，模拟移动端行为
        data = self.session.get(url, headers=self.headers, timeout=10)
        if data.status_code != 200:
            return [404, "text/plain", ""]
        data = data.text
        
        # 兼容性匹配：如果服务器返回的是原生流（没加密），直接放行
        if "#EXT-X-MOUFLON:" in data:
            data = self.process_m3u8_content_v2(data)
        return [200, "application/vnd.apple.mpegur", data]

    def process_m3u8_content_v2(self, m3u8_content):
        lines = m3u8_content.strip().split('\n')
        for i, line in enumerate(lines):
            # 这里的特征匹配必须是 EXT-REF 或 FILE，不能漏掉
            if (line.startswith('#EXT-X-MOUFLON:EXT-REF:') or line.startswith('#EXT-X-MOUFLON:FILE:')) and 'media.mp4' in lines[i + 1]:
                encrypted_data = line.split(':', 2)[2].strip()
                try:
                    decrypted_data = self.decrypt(encrypted_data, self.stripchat_key)
                except Exception as e:
                    try:
                        decrypted_data = self.decrypt(encrypted_data, "Zokee2OhPh9kugh4")
                    except:
                        continue
                lines[i + 1] = lines[i + 1].replace('media.mp4', decrypted_data)
        return '\n'.join(lines)

    def country_code_to_flag(self, country_code):
        if len(country_code) != 2 or not country_code.isalpha():
            return country_code
        flag_emoji = ''.join([chr(ord(c.upper()) - ord('A') + 0x1F1E6) for c in country_code])
        return flag_emoji

    def decode_key_compact(self):
        base64_str = "NTEgNzUgNjUgNjEgNmUgMzQgNjMgNjEgNjkgMzkgNjIgNmYgNGEgNjEgMzUgNjE="
        decoded = base64.b64decode(base64_str).decode('utf-8')
        key_bytes = bytes(int(hex_str, 16) for hex_str in decoded.split(" "))
        return key_bytes.decode('utf-8')

    def compute_hash(self, key: str) -> bytes:
        if key not in self._hash_cache:
            sha256 = hashlib.sha256()
            sha256.update(key.encode('utf-8'))
            self._hash_cache[key] = sha256.digest()
        return self._hash_cache[key]

    def decrypt(self, encrypted_b64: str, key: str) -> str:
        padding = len(encrypted_b64) % 4
        if padding:
            encrypted_b64 += '=' * (4 - padding)
        hash_bytes = self.compute_hash(key)
        encrypted_data = base64.b64decode(encrypted_b64)
        decrypted_bytes = bytearray()
        for i, cipher_byte in enumerate(encrypted_data):
            key_byte = hash_bytes[i % len(hash_bytes)]
            decrypted_bytes.append(cipher_byte ^ key_byte)
        return decrypted_bytes.decode('utf-8')

    def create_session_with_retry(self, retries=3, backoff_factor=0.3):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
