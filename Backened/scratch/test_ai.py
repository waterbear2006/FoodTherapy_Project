import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_deepseek():
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    print(f"Testing DeepSeek with API_KEY: {api_key[:8]}... and BASE_URL: {base_url}")
    
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "你好"}
            ],
            max_tokens=10
        )
        print("✅ Success!")
        print(f"Reply: {response.choices[0].message.content}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepseek())
