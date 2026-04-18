import os
import csv
import urllib.request
import urllib.parse
import concurrent.futures
import re
import time
from pathlib import Path

# 取出所有的菜谱名
csv_path = Path(__file__).resolve().parent.parent / "data" / "caipu.csv"
frontend_images_dir = Path(__file__).resolve().parent.parent.parent / "diet-health-frontend" / "public" / "images" / "recipes"
frontend_images_dir.mkdir(parents=True, exist_ok=True)

recipes = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader, None)
    for row in reader:
        if row and row[0].isdigit():
            recipes.append({"id": row[0], "name": row[1]})

def download_image(recipe):
    id_str = recipe["id"]
    name = recipe["name"]
    target_path = frontend_images_dir / f"{id_str}.jpg"
    
    # 支持断点续传
    if target_path.exists() and target_path.stat().st_size > 5000:
        return f"[跳过] {id_str}.jpg 已存在"
        
    try:
        # 为了极度准确性，放弃 AI 并采用真实搜索引擎抓取高质量实拍美食图
        query = urllib.parse.quote(name + " 高清 美食")
        url = f"https://cn.bing.com/images/search?q={query}"
        
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        )
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        
        # 提取 Bing 图库中第一原图链接
        match = re.search(r'murl&quot;:&quot;(.*?)&quot;', html)
        if match:
            img_url = match.group(1)
            img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(img_req, timeout=15) as res:
                img_data = res.read()
                if len(img_data) < 5000:
                   raise Exception("Image too small")
                with open(target_path, "wb") as img_f:
                    img_f.write(img_data)
            return f"[成功] 下载图片 {id_str}.jpg -> {name}"
        else:
            raise Exception("未能提取到有效的图片链接")
    except Exception as e:
        return f"[失败] 下载 {id_str}.jpg ({name}) 出错: {e}"

print(f"🚀 开始为 {len(recipes)} 道菜谱请求真实实拍配图...")
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(download_image, recipes))

success_count = sum(1 for r in results if "[成功]" in r or "[跳过]" in r)
print(f"🎉 全部跑完！成功获取了 {success_count} / {len(recipes)} 张精准高图。")
