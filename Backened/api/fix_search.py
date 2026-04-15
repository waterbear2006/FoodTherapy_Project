# 读取原始文件
with open('search.py', 'rb') as f:
    content = f.read()

print(f'Original size: {len(content)} bytes')

# 找到最后一个正常的行（news 接口结束）
# 搜索 "return {" 并截断到这里
search_marker = b'return {\n        "status": "success",\n        "data": news_data,\n        "total": len(news_data)\n    }\n}'
last_good_pos = content.rfind(search_marker)

if last_good_pos != -1:
    # 找到结束位置
    end_pos = last_good_pos + len(search_marker)
    clean_content = content[:end_pos]
    
    with open('search_fixed.py', 'wb') as f:
        f.write(clean_content)
    
    print(f'Created search_fixed.py with {len(clean_content)} bytes')
    print(f'Removed {len(content) - len(clean_content)} bytes')
else:
    print('Marker not found, trying alternative approach...')
    # 尝试找到第 378 行左右
    lines = content.split(b'\n')
    good_lines = []
    for i, line in enumerate(lines):
        if b'\x00' in line or i > 380:
            break
        good_lines.append(line)
    
    clean_content = b'\n'.join(good_lines)
    with open('search_fixed.py', 'wb') as f:
        f.write(clean_content)
    
    print(f'Created search_fixed.py with {len(clean_content)} bytes')
