import sys
import io
import time
import pandas as pd
import requests  # 换成了最稳定的 requests 库

# 强制 UTF-8 环境
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ================= 配置区 =================
# 请确保这里填入了正确的 DeepSeek API Key
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" 
URL = "https://api.deepseek.com/v1/chat/completions"

INPUT_CSV = "caipu_enriched.csv"
OUTPUT_CSV = "caipu_enriched.csv"

# ================= 核心请求逻辑 =================
def get_ancient_quote(name, ingredients, effect):
    prompt = f"""
    你是一位精通中医典籍的老中医。我现在要为一款中医食疗 APP 生成古籍考证数据。
    
    菜谱名称：{name}
    主要食材：{ingredients}
    主要功效：{effect}
    
    请你帮我从《本草纲目》、《伤寒论》、《千金方》等著名中医古籍中，寻找一段能佐证该菜谱或其核心食材功效的原文，并配上一句白话文解释。
    
    【输出格式严格要求】：
    1. 必须包含书名号《》。
    2. 格式范例：“《本草纲目》记载：‘黄芪补气固表’。此膳用以益气固表，最适合体虚之人。”
    3. 严禁输出任何多余的问候语、直接输出纯文本段落！
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个严谨的中医古籍数据生成引擎。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 150
    }
    
    try:
        # 直接发送 HTTP POST 请求，设置 30 秒超时
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        
        # 检查 HTTP 状态码
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        else:
            print(f"❌ API 报错了！状态码: {response.status_code}, 错误信息: {response.text}")
            return ""
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时！可能是网络连接 DeepSeek 较慢。")
        return ""
    except Exception as e:
        # 这里即使报错也不会引发 ASCII 崩溃
        print(f"❌ 网络请求异常，请检查是否开启了代理。")
        return ""

# ================= 主运行逻辑 =================
def main():
    print("🚀 开启中医古籍 RAG 富化进程 (底层通信版)...")
    
    try:
        df = pd.read_csv(INPUT_CSV, encoding='utf-8')
    except Exception as e:
        print(f"读取 CSV 失败: {e}")
        return

    if 'ancient_quote' not in df.columns:
        df['ancient_quote'] = ""

    total_rows = len(df)
    
    for index, row in df.iterrows():
        # 断点续传逻辑
        if pd.notna(row.get('ancient_quote')) and str(row.get('ancient_quote')).strip() != "":
            print(f"⏭️ [{index+1}/{total_rows}] {row['name']} 已有古籍，跳过。")
            continue
            
        print(f"⏳ [{index+1}/{total_rows}] 正在为 {row['name']} 检索古籍...")
        
        quote = get_ancient_quote(
            name=row['name'], 
            ingredients=row['ingredients'], 
            effect=row['effect']
        )
        
        if quote:
            df.at[index, 'ancient_quote'] = quote
            # 成功一条存一条
            df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
            print(f"   ✅ 成功获取！")
        
        time.sleep(1.5) # 降低请求频率

    print(f"🎉 全部富化完成！请刷新您的前端页面！")

if __name__ == "__main__":
    main()