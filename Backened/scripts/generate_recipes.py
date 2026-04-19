import asyncio
import os
import csv
import json
import urllib.parse
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

# 加载 .env 环境变量
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("AI_API_KEY")
base_url = os.getenv("AI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

if not api_key:
    print("错误: 找不到 AI_API_KEY")
    exit(1)

client = AsyncOpenAI(api_key=api_key, base_url=base_url)

# 9种体质
CONSTITUTIONS = [
    '平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质'
]

async def generate_for_constitution(constitution: str, count: int = 15):
    prompt = f"""
    任务: 作为资深中医食疗专家，请为【{constitution}】体质的人群，推荐 {count} 道高质量、临床有效、且日常可操作的药膳/食疗菜谱。
    注意：
    - 切勿输出 markdown 代码块标志 (` ```json `)。直接返回纯 JSON！
    - 不需要额外的话语，仅仅返回一个 JSON 数组，数组格式如下：
    [
        {{
            "name": "菜名",
            "ingredients": "食材1、食材2、食材3",
            "effect": "功效描述",
            "suitable": "{constitution}",
            "steps": "简单的一到两句话步骤"
        }}
    ]
    每一道菜的具体选材要符合 {constitution} 的调理原则。
    """
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        # DeepSeek 有时会忽略 json_object 或者返回包裹在外层的内容，我们尝试解析
        content = response.choices[0].message.content.strip()
        # 兼容处理: 如果它返回的对象包裹着 list 字典 (如 {"recipes": [...]})
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            # 找到第一个 list 字段
            for k, v in parsed.items():
                if isinstance(v, list):
                    return v
            return []
        elif isinstance(parsed, list):
            return parsed
        return []
    except Exception as e:
        print(f"❌ 生成 {constitution} 菜谱时出错: {e}")
        return []

async def main():
    print(f"🚀 开始为 9 种中医体质生成食疗库数据，预计 135 条...")
    tasks = [generate_for_constitution(c, 15) for c in CONSTITUTIONS]
    results = await asyncio.gather(*tasks)
    
    all_recipes = []
    for batch in results:
        all_recipes.extend(batch)
        
    print(f"✅ AI 联合生成了 {len(all_recipes)} 条食谱！正在进行清洗和合并...")
    
    csv_path = Path(__file__).resolve().parent.parent / "data" / "caipu.csv"
    
    # 获取目前的 ID 最大值
    max_id = 0
    existing_recipes = []
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                existing_recipes.append(row)
                if row and row[0].isdigit():
                    max_id = max(max_id, int(row[0]))
    
    # 写入文件
    added_count = 0
    with open(csv_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for r in all_recipes:
            max_id += 1
            name = r.get("name", "未命名").strip()
            # 自动利用 pollinations.ai 生成精准中医食疗配图
            prompt_str = f"中医养生 药膳 食疗 美食 高清照 {name}"
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt_str)}?width=400&height=300&nologo=true"
            
            row = [
                str(max_id),
                name,
                r.get("ingredients", "").replace(",", "、"),
                r.get("effect", ""),
                r.get("suitable", ""),
                r.get("steps", ""),
                img_url
            ]
            writer.writerow(row)
            added_count += 1
            
    print(f"🎉 成功向 caipu.csv 中追加了 {added_count} 条高质量菜谱！目前库中总共 {len(existing_recipes) + added_count} 条数据。")

if __name__ == '__main__':
    asyncio.run(main())
