with open('search.py', 'rb') as f:
    content = f.read()
    
clean_content = content.replace(b'\x00', b'')

with open('search.py', 'wb') as f:
    f.write(clean_content)
    
print(f'Cleaned! Removed {content.count(b"\x00")} null bytes')
