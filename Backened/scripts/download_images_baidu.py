import os
import csv
import urllib.request
import urllib.parse
import concurrent.futures
import re
from pathlib import Path

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

# 过滤出已经失败（没有图片）的菜谱
missing = [r for r in recipes if not (frontend_images_dir / f"{r['id']}.jpg").exists() or (frontend_images_dir / f"{r['id']}.jpg").stat().st_size < 5000]
print(f"需要补充下载的: {len(missing)} 道")

def download_from_baidu(recipe):
    id_str = recipe["id"]
    name = recipe["name"]
    target_path = frontend_images_dir / f"{id_str}.jpg"
    
    try:
        # 用百度图片搜索作为备用
        query = urllib.parse.quote(name + " 菜肴 高清")
        url = f"https://image.baidu.com/search/index?tn=baiduimage&word={query}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        
        # 提取 objURL 格式的真实图片链接
        match = re.search(r'"objURL":"(https?://[^"]+?)"', html)
        if match:
            img_url = match.group(1)
            img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(img_req, timeout=15) as res:
                img_data = res.read()
                if len(img_data) < 5000:
                    raise Exception("Image too small")
                with open(target_path, "wb") as img_f:
                    img_f.write(img_data)
            return f"[成功] {id_str}.jpg -> {name}"
        else:
            raise Exception("百度源未找到图片")
    except Exception as e:
        return f"[失败] {id_str}.jpg ({name}): {e}"

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(download_from_baidu, missing))

for r in results:
    print(r)

success = sum(1 for r in results if "[成功]" in r)
print(f"\n✅ 本次补充成功 {success} / {len(missing)} 张")
