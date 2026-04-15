"""
针对失败的菜谱，使用 Bing 国际版搜图作为备用，
同时也尝试使用微博相关图片来源
"""
import os
import csv
import urllib.request
import urllib.parse
import re
from pathlib import Path

csv_path = Path(__file__).resolve().parent.parent / "data" / "caipu.csv"
frontend_images_dir = Path(__file__).resolve().parent.parent.parent / "diet-health-frontend" / "public" / "images" / "recipes"

# 需要补充的菜名
missing_ids = [12, 20, 47, 56, 65, 68, 69, 71, 76, 84, 89, 95, 96, 98, 101, 105, 110, 116, 122, 134]

id_to_name = {}
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if row and row[0].isdigit():
            id_to_name[int(row[0])] = row[1]

# 要搜索的菜单列表
targets = [{"id": str(i), "name": id_to_name.get(i, "")} for i in missing_ids if id_to_name.get(i)]

def download_with_bing_intl(recipe):
    id_str = recipe["id"]
    name = recipe["name"]
    target_path = frontend_images_dir / f"{id_str}.jpg"
    
    try:
        # 使用 Bing 国际版搜索
        query = urllib.parse.quote(name + " food recipe")
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        url = f"https://www.bing.com/images/search?q={query}&first=1"
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        
        # 搜索 murl 格式的真实图片链接
        match = re.search(r'murl&quot;:&quot;(https?://[^&"]+)&quot;', html)
        if match:
            img_url = match.group(1)
            img_req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(img_req, timeout=15) as res:
                img_data = res.read()
                if len(img_data) < 5000:
                    raise Exception("Image too small")
                with open(target_path, "wb") as f:
                    f.write(img_data)
            return f"[成功] {id_str}.jpg -> {name}"
        else:
            raise Exception("Bing 国际版未找到图片")
    except Exception as e:
        return f"[失败] {id_str}.jpg ({name}): {e}"

print(f"📸 尝试为 {len(targets)} 道菜补充真实配图（Bing 国际版）...")
for recipe in targets:
    result = download_with_bing_intl(recipe)
    print(result)
    
final_count = sum(1 for r in [frontend_images_dir / f"{r['id']}.jpg" for r in targets] if r.exists() and r.stat().st_size > 5000)
print(f"\n✅ 本次补充成功下载 {final_count} / {len(targets)} 张")
