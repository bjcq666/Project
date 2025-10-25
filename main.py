"""
AI 驱动的地图导航系统 - 主程序
支持文字和语音输入，基于 MCP 架构实现
"""

import json
import asyncio
import argparse
from typing import Dict, Any, Optional
import httpx

from amap_mcp_client import create_amap_client
from voice_input import create_voice_recognizer, LocalMicrophoneRecorder
from mcp_browser_server import create_browser_server


class AINavigationSystem:
    """AI 导航系统主类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化导航系统
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.amap_client = None
        self.voice_recognizer = None
        self.browser_server = create_browser_server()
        self.ai_client = self._create_ai_client()
    
    def _create_ai_client(self):
        """创建 AI 客户端（支持多种提供商）"""
        ai_config = self.config.get("ai", {})
        provider = ai_config.get("provider", "qiniu")
        
        if provider == "anthropic":
            try:
                from anthropic import AsyncAnthropic
                api_key = ai_config.get("anthropic", {}).get("apiKey", "")
                if api_key and "YOUR_" not in api_key:
                    print("✅ 使用 Anthropic Claude AI")
                    return AsyncAnthropic(api_key=api_key)
            except ImportError:
                print("⚠️  anthropic 库未安装")
        
        elif provider == "qiniu":
            qiniu_config = ai_config.get("qiniu", {})
            api_url = qiniu_config.get("apiUrl", "")
            model = qiniu_config.get("model", "gpt-3.5-turbo")
            print(f"✅ 使用七牛 AI 推理服务 (模型: {model})")
            return {
                "type": "openai_compatible",
                "api_url": api_url,
                "model": model
            }
        
        print("⚠️  未配置 AI 服务，使用简单文本解析")
        return None
    
    async def parse_navigation_intent(self, user_input: str) -> Dict[str, Any]:
        """
        使用 AI 解析用户导航意图
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            解析结果: {"origin": str, "destination": str, "map_service": str}
        """
        print(f"\n🤖 AI 正在解析: \"{user_input}\"")
        
        if self.ai_client:
            if isinstance(self.ai_client, dict) and self.ai_client.get("type") == "openai_compatible":
                return await self._parse_with_openai_compatible(user_input)
            else:
                return await self._parse_with_anthropic(user_input)
        else:
            return self._parse_with_regex(user_input)
    
    async def _parse_with_anthropic(self, user_input: str) -> Dict[str, Any]:
        """使用 Anthropic Claude 解析"""
        try:
            prompt = f"""请分析以下导航请求，提取起点和终点。如果没有明确起点，返回 null。

用户输入: {user_input}

请以 JSON 格式返回，例如:
{{"origin": "北京", "destination": "上海", "map_service": "amap"}}

如果用户指定了地图服务（百度或高德），请在 map_service 字段中指定（baidu 或 amap）。
如果没有指定，默认使用 amap。

只返回 JSON，不要其他解释。"""

            message = await self.ai_client.messages.create(
                model=self.config.get("ai", {}).get("anthropic", {}).get("model", "claude-3-5-sonnet-20241022"),
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = message.content[0].text.strip()
            
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            result = json.loads(result_text)
            print(f"✅ AI 解析结果: {result}")
            return result
        
        except Exception as e:
            print(f"⚠️  AI 解析失败: {e}，回退到简单解析")
            return self._parse_with_regex(user_input)
    
    async def _parse_with_openai_compatible(self, user_input: str) -> Dict[str, Any]:
        """使用 OpenAI 兼容 API 解析（七牛）"""
        try:
            qiniu_config = self.config.get("qiniu", {})
            access_key = qiniu_config.get("accessKey", "")
            secret_key = qiniu_config.get("secretKey", "")
            
            if not access_key or "YOUR_" in access_key:
                print("⚠️  未配置七牛密钥，回退到简单解析")
                return self._parse_with_regex(user_input)
            
            import base64
            import hmac
            import hashlib
            
            api_url = self.ai_client["api_url"]
            model = self.ai_client["model"]
            
            prompt = f"""请分析以下导航请求，提取起点和终点。如果没有明确起点，返回 null。

用户输入: {user_input}

请以 JSON 格式返回，例如:
{{"origin": "北京", "destination": "上海", "map_service": "amap"}}

只返回 JSON，不要其他解释。"""

            request_body = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200
            }
            
            body_bytes = json.dumps(request_body).encode("utf-8")
            
            path = "/v1/ai/inference"
            data = f"POST {path}\nHost: api.qiniu.com\nContent-Type: application/json\n\n"
            data += body_bytes.decode("utf-8")
            
            sign = hmac.new(
                secret_key.encode("utf-8"),
                data.encode("utf-8"),
                hashlib.sha1
            ).digest()
            encoded_sign = base64.urlsafe_b64encode(sign).decode("utf-8")
            token = f"Qiniu {access_key}:{encoded_sign}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    content=body_bytes,
                    headers={
                        "Authorization": token,
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                result_data = response.json()
            
            result_text = result_data["choices"][0]["message"]["content"].strip()
            
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            result = json.loads(result_text)
            print(f"✅ AI 解析结果: {result}")
            return result
        
        except Exception as e:
            print(f"⚠️  AI 解析失败: {e}，回退到简单解析")
            return self._parse_with_regex(user_input)
    
    def _parse_with_regex(self, user_input: str) -> Dict[str, Any]:
        """使用正则表达式简单解析"""
        import re
        
        result = {
            "origin": None,
            "destination": None,
            "map_service": "amap"
        }
        
        if "百度" in user_input or "baidu" in user_input.lower():
            result["map_service"] = "baidu"
        
        patterns = [
            r"从(.+?)到(.+?)$",
            r"从(.+?)去(.+?)$",
            r"(.+?)到(.+?)$",
            r"(.+?)去(.+?)$",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                result["origin"] = match.group(1).strip()
                result["destination"] = match.group(2).strip()
                break
        
        if not result["destination"]:
            match = re.search(r"(?:去|到|导航到|导航去)(.+?)$", user_input)
            if match:
                result["destination"] = match.group(1).strip()
        
        for keyword in ["百度", "高德", "地图", "导航", "用", "帮我", "请"]:
            if result["origin"]:
                result["origin"] = result["origin"].replace(keyword, "").strip()
            if result["destination"]:
                result["destination"] = result["destination"].replace(keyword, "").strip()
        
        print(f"✅ 简单解析结果: {result}")
        return result
    
    async def navigate(self, user_input: str):
        """
        执行导航
        
        Args:
            user_input: 用户输入（文字或语音识别后的文字）
        """
        print("\n" + "="*60)
        print("🚀 开始导航流程")
        print("="*60)
        
        parsed = await self.parse_navigation_intent(user_input)
        
        origin = parsed.get("origin")
        destination = parsed.get("destination")
        map_service = parsed.get("map_service", "amap")
        
        if not destination:
            print("❌ 无法识别目的地，请重新输入")
            return
        
        print(f"\n📍 导航信息:")
        print(f"   起点: {origin or '当前位置'}")
        print(f"   终点: {destination}")
        print(f"   地图: {map_service.upper()}")
        
        self.amap_client = create_amap_client(self.config)
        
        async with self.amap_client:
            try:
                if origin:
                    print(f"\n[1/3] 🔍 查询起点坐标: {origin}")
                    origin_coords = await self.amap_client.geocode(origin)
                    print(f"   ✅ {origin}: ({origin_coords['longitude']}, {origin_coords['latitude']})")
                    start_lng = origin_coords['longitude']
                    start_lat = origin_coords['latitude']
                else:
                    print("\n[1/3] 📍 起点: 当前位置")
                    start_lng = None
                    start_lat = None
                
                print(f"\n[2/3] 🔍 查询终点坐标: {destination}")
                dest_coords = await self.amap_client.geocode(destination)
                print(f"   ✅ {destination}: ({dest_coords['longitude']}, {dest_coords['latitude']})")
                
                print(f"\n[3/3] 🌐 打开浏览器导航...")
                result = self.browser_server.call_tool(
                    "open_map_navigation",
                    {
                        "start_lng": start_lng,
                        "start_lat": start_lat,
                        "end_lng": dest_coords['longitude'],
                        "end_lat": dest_coords['latitude'],
                        "map_service": map_service
                    }
                )
                
                print(f"\n{result['content'][0]['text']}")
                print("\n✅ 导航启动完成!")
            
            except Exception as e:
                print(f"\n❌ 导航失败: {str(e)}")
    
    async def process_text_input(self, text: str):
        """处理文字输入"""
        await self.navigate(text)
    
    async def process_voice_input(self, duration: int = 5):
        """处理语音输入"""
        try:
            recorder = LocalMicrophoneRecorder()
            audio_data = recorder.record_audio(duration)
            
            self.voice_recognizer = create_voice_recognizer(self.config)
            
            print("\n🎤 正在识别语音...")
            async with self.voice_recognizer:
                text = await self.voice_recognizer.recognize_audio_file(audio_data)
                print(f"✅ 识别结果: \"{text}\"")
                
                await self.navigate(text)
        
        except Exception as e:
            print(f"❌ 语音处理失败: {str(e)}")


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  配置文件 {config_path} 不存在，使用默认配置")
        return {
            "mcpServers": {},
            "qiniu": {},
            "ai": {"provider": "qiniu"},
            "defaultMapService": "amap"
        }


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI 驱动的地图导航系统")
    parser.add_argument("--text", "-t", action="store_true", help="文字输入模式")
    parser.add_argument("--voice", "-v", action="store_true", help="语音输入模式")
    parser.add_argument("--duration", "-d", type=int, default=5, help="语音录制时长（秒）")
    parser.add_argument("--config", "-c", default="config.json", help="配置文件路径")
    
    args = parser.parse_args()
    
    print("="*60)
    print("🗺️  AI 地图导航系统")
    print("="*60)
    
    config = load_config(args.config)
    system = AINavigationSystem(config)
    
    if args.voice:
        print("\n🎤 语音输入模式")
        await system.process_voice_input(args.duration)
    
    elif args.text:
        print("\n⌨️  文字输入模式")
        user_input = input("\n请输入导航指令 (例如: 从北京到上海): ").strip()
        if user_input:
            await system.process_text_input(user_input)
        else:
            print("❌ 输入不能为空")
    
    else:
        print("\n⌨️  默认文字输入模式 (使用 --voice 切换到语音模式)")
        while True:
            user_input = input("\n请输入导航指令 (输入 'quit' 退出): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见!")
                break
            
            if user_input:
                await system.process_text_input(user_input)
            else:
                print("❌ 输入不能为空")


if __name__ == "__main__":
    asyncio.run(main())
