"""
新闻服务模块 - 从 RSS 源获取健康养生新闻
"""

import feedparser
import re
from html import unescape

RSS_URLS = [
    "https://www.chinanews.com.cn/rss/jk.xml",
    "https://www.chinanews.com.cn/rss/life.xml",
    "http://www.chinadaily.com.cn/rss/lifestyle_rss.xml"
]


import concurrent.futures
import requests

def fetch_feed(url):
    """单独抓取一个源，带超时逻辑"""
    try:
        response = requests.get(url, timeout=3.5)
        if response.status_code == 200:
            return feedparser.parse(response.content)
    except Exception as e:
        print(f"[News] 抓取源失败 {url}: {e}")
    return None

def get_food_news():
    """
    并发从 RSS 源获取健康养生新闻
    
    Returns:
        list: 新闻列表，每条新闻包含 title, link, summary, source, image
    """
    news_list = []
    seen_links = set()

    try:
        # 使用线程池并发抓取，极大缩短总等待时间
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(RSS_URLS)) as executor:
            future_to_url = {executor.submit(fetch_feed, url): url for url in RSS_URLS}
            
            for future in concurrent.futures.as_completed(future_to_url):
                feed = future.result()
                if not feed:
                    continue
                
                try:
                    for entry in feed.entries[:5]:
                        if hasattr(entry, 'link') and entry.link in seen_links:
                            continue
                        
                        # 提取图片 URL (复用原有逻辑)
                        image_url = ""
                        if hasattr(entry, 'media_content') and entry.media_content:
                            for media in entry.media_content:
                                if 'url' in media:
                                    image_url = media['url']
                                    break
                        
                        if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
                            for enclosure in entry.enclosures:
                                if 'url' in enclosure and enclosure.get('type', '').startswith('image/'):
                                    image_url = enclosure['url']
                                    break
                        
                        # 创建新闻对象
                        news = {
                            "title": entry.title if hasattr(entry, 'title') else "无标题",
                            "link": entry.link if hasattr(entry, 'link') else "",
                            "summary": unescape(re.sub(r'<[^>]+>', '', entry.summary)) if hasattr(entry, 'summary') and entry.summary else "",
                            "source": feed.feed.title if hasattr(feed.feed, 'title') and feed.feed.title else "新闻",
                            "image": image_url
                        }
                        
                        news_list.append(news)
                        seen_links.add(entry.link)
                except Exception as e:
                    print(f"[News] 处理条目失败: {e}")
                    continue
    except Exception as e:
        print(f"[News] 获取新闻服务失败: {e}")
    
    return news_list
