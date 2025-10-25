import json
from openai import AsyncOpenAI
from typing import Dict, Optional
from pydantic import BaseModel
import config


class NavigationIntent(BaseModel):
    origin: str = "我的位置"
    destination: str
    mode: str = "driving"
    policy: int = 0
    preferences: list[str] = []


class AIIntentParser:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL
        )
        
        self.system_prompt = """你是一个导航指令解析助手。请从用户输入中提取以下结构化信息：
- 起点(origin)：如未指定则默认为"我的位置"
- 终点(destination)：必须提取
- 导航模式(mode)：driving(驾车)/walking(步行)/bicycling(骑行)
- 路径策略(policy)：0(速度优先)/1(费用优先)/2(距离优先)/4(躲避拥堵)
- 其他偏好(preferences)：如"避开高速"、"最短距离"等

请返回JSON格式，示例：
{
  "origin": "北京西站",
  "destination": "颐和园", 
  "mode": "driving",
  "policy": 4,
  "preferences": ["避开拥堵"]
}

注意：
1. mode只能是: driving, walking, bicycling 之一
2. policy只能是: 0, 1, 2, 4 之一
3. 如果用户说"开车"、"自驾"，mode应为driving
4. 如果用户说"走路"、"步行"，mode应为walking
5. 如果用户说"骑车"、"骑行"，mode应为bicycling
6. 如果用户提到"快一点"、"速度优先"，policy应为0
7. 如果用户提到"便宜"、"省钱"，policy应为1
8. 如果用户提到"近一点"、"最短距离"，policy应为2
9. 如果用户提到"不堵车"、"避开拥堵"，policy应为4"""

    async def parse(self, user_input: str) -> NavigationIntent:
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return NavigationIntent(**result)
            
        except Exception as e:
            raise Exception(f"AI解析失败: {str(e)}")
