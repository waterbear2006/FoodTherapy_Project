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


def get_food_news():
    """
    从 RSS 源获取健康养生新闻
    
    Returns:
        list: 新闻列表，每条新闻包含 title, link, summary, source, image
    """
    news_list = []
    seen_links = set()  # 用于存储已存在的新闻链接

    try:
        for url in RSS_URLS:
            try:
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:5]:
                    # 去重：检查新闻链接是否已存在
                    if hasattr(entry, 'link') and entry.link in seen_links:
                        continue  # 跳过重复的新闻
                    
                    # 提取图片 URL
                    image_url = ""
                    
                    # 方法 1: 尝试从 media_content 中获取图片
                    if hasattr(entry, 'media_content') and entry.media_content:
                        for media in entry.media_content:
                            if 'url' in media:
                                image_url = media['url']
                                break
                    
                    # 方法 2: 尝试从 enclosures 中获取图片
                    if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
                        for enclosure in entry.enclosures:
                            if 'url' in enclosure and enclosure.get('type', '').startswith('image/'):
                                image_url = enclosure['url']
                                break
                    
                    # 方法 3: 从 content 或 summary 中提取图片
                    if not image_url:
                        content = ""
                        if hasattr(entry, 'content') and entry.content:
                            content = entry.content[0].get('value', '')
                        elif hasattr(entry, 'summary'):
                            content = entry.summary
                        
                        # 使用正则表达式提取 img 标签的 src
                        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
                        match = re.search(img_pattern, content, re.IGNORECASE)
                        if match:
                            image_url = match.group(1)
                    
                    # 方法 4: 从 media_thumbnail 中获取
                    if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                        for thumb in entry.media_thumbnail:
                            if 'url' in thumb:
                                image_url = thumb['url']
                                break
                    
                    # 方法 5: 从 links 中查找图片链接
                    if not image_url and hasattr(entry, 'links') and entry.links:
                        for link in entry.links:
                            if hasattr(link, 'type') and link.type and link.type.startswith('image/'):
                                image_url = link.href
                                break
                    
                    # 创建新闻对象
                    news = {
                        "title": entry.title if hasattr(entry, 'title') else "无标题",
                        "link": entry.link if hasattr(entry, 'link') else "",
                        "summary": unescape(re.sub(r'<[^>]+>', '', entry.summary)) if hasattr(entry, 'summary') and entry.summary else "",
                        "source": feed.feed.title if hasattr(feed.feed, 'title') and feed.feed.title else "新闻",
                        "image": image_url
                    }
                    
                    # 添加到列表和已见集合
                    news_list.append(news)
                    seen_links.add(entry.link)
            except Exception as e:
                print(f"[News] 解析 RSS 源失败 {url}: {e}")
                continue
    except Exception as e:
        print(f"[News] 获取新闻失败: {e}")
    
    return news_list
