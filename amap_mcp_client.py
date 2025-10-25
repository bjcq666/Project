"""
高德地图 MCP 客户端 - Streamable HTTP 接入方式
基于高德官方 MCP Server 实现地理编码功能
文档: https://lbs.amap.com/api/mcp-server/gettingstarted
"""

import json
import httpx
from typing import Dict, Any, Optional


class AmapMCPClient:
    """高德地图 MCP 客户端 - Streamable HTTP"""
    
    def __init__(self, mcp_url: str):
        """
        初始化高德 MCP 客户端
        
        Args:
            mcp_url: MCP Server URL，格式: https://mcp.amap.com/mcp?key=YOUR_KEY
        """
        self.mcp_url = mcp_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用 MCP Server 工具
        
        Args:
            tool_name: 工具名称 (如 "geocode", "regeo", "poi_search")
            arguments: 工具参数
            
        Returns:
            工具调用结果
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.client.post(
                self.mcp_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"MCP Error: {result['error']}")
            
            return result.get("result", {})
        
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"MCP call failed: {str(e)}")
    
    async def geocode(self, address: str, city: Optional[str] = None) -> Dict[str, Any]:
        """
        地理编码 - 将地址转换为坐标
        
        Args:
            address: 地址名称
            city: 城市名称（可选，提高准确度）
            
        Returns:
            包含经纬度的字典: {"name": str, "longitude": float, "latitude": float}
        """
        arguments = {"address": address}
        if city:
            arguments["city"] = city
        
        result = await self.call_tool("geocode", arguments)
        
        if not result or "content" not in result:
            raise Exception(f"无法获取 '{address}' 的坐标信息")
        
        content = result["content"][0] if isinstance(result["content"], list) else result["content"]
        
        if isinstance(content, dict) and "text" in content:
            data = json.loads(content["text"])
        else:
            data = content
        
        if not data or "location" not in data:
            raise Exception(f"地理编码失败: {address}")
        
        location = data["location"]
        if isinstance(location, str):
            lng, lat = map(float, location.split(","))
        else:
            lng = float(location.get("lng") or location.get("longitude"))
            lat = float(location.get("lat") or location.get("latitude"))
        
        return {
            "name": address,
            "longitude": lng,
            "latitude": lat
        }
    
    async def reverse_geocode(self, longitude: float, latitude: float) -> Dict[str, Any]:
        """
        逆地理编码 - 将坐标转换为地址
        
        Args:
            longitude: 经度
            latitude: 纬度
            
        Returns:
            地址信息字典
        """
        arguments = {
            "location": f"{longitude},{latitude}"
        }
        
        result = await self.call_tool("regeo", arguments)
        
        if not result or "content" not in result:
            raise Exception(f"无法获取坐标 ({longitude}, {latitude}) 的地址信息")
        
        content = result["content"][0] if isinstance(result["content"], list) else result["content"]
        
        if isinstance(content, dict) and "text" in content:
            data = json.loads(content["text"])
        else:
            data = content
        
        return data
    
    async def search_poi(self, keywords: str, city: Optional[str] = None) -> Dict[str, Any]:
        """
        POI 搜索
        
        Args:
            keywords: 搜索关键词
            city: 城市名称（可选）
            
        Returns:
            POI 搜索结果
        """
        arguments = {"keywords": keywords}
        if city:
            arguments["city"] = city
        
        result = await self.call_tool("poi_search", arguments)
        
        if not result or "content" not in result:
            raise Exception(f"POI 搜索失败: {keywords}")
        
        content = result["content"][0] if isinstance(result["content"], list) else result["content"]
        
        if isinstance(content, dict) and "text" in content:
            data = json.loads(content["text"])
        else:
            data = content
        
        return data


class MockAmapMCPClient:
    """模拟高德 MCP 客户端 - 用于开发测试"""
    
    MOCK_LOCATIONS = {
        "北京": {"longitude": 116.397128, "latitude": 39.916527},
        "上海": {"longitude": 121.473701, "latitude": 31.230416},
        "广州": {"longitude": 113.264385, "latitude": 23.129163},
        "深圳": {"longitude": 114.057868, "latitude": 22.543099},
        "杭州": {"longitude": 120.155070, "latitude": 30.274085},
        "成都": {"longitude": 104.065735, "latitude": 30.659462},
        "西安": {"longitude": 108.940175, "latitude": 34.341568},
        "重庆": {"longitude": 106.551557, "latitude": 29.563010},
        "南京": {"longitude": 118.796877, "latitude": 32.060255},
        "武汉": {"longitude": 114.305393, "latitude": 30.593099},
    }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def geocode(self, address: str, city: Optional[str] = None) -> Dict[str, Any]:
        """模拟地理编码"""
        for city_name, coords in self.MOCK_LOCATIONS.items():
            if city_name in address:
                return {
                    "name": address,
                    "longitude": coords["longitude"],
                    "latitude": coords["latitude"]
                }
        
        raise Exception(f"Mock 模式下不支持地址: {address}。支持的城市: {', '.join(self.MOCK_LOCATIONS.keys())}")
    
    async def reverse_geocode(self, longitude: float, latitude: float) -> Dict[str, Any]:
        """模拟逆地理编码"""
        return {
            "formatted_address": f"模拟地址 ({longitude}, {latitude})",
            "location": {"longitude": longitude, "latitude": latitude}
        }
    
    async def search_poi(self, keywords: str, city: Optional[str] = None) -> Dict[str, Any]:
        """模拟 POI 搜索"""
        return {
            "pois": [
                {"name": keywords, "location": {"longitude": 116.397128, "latitude": 39.916527}}
            ]
        }


def create_amap_client(config: Dict[str, Any]) -> AmapMCPClient:
    """
    创建高德 MCP 客户端
    
    Args:
        config: 配置字典
        
    Returns:
        AmapMCPClient 或 MockAmapMCPClient 实例
    """
    mcp_config = config.get("mcpServers", {}).get("amap-maps-streamableHTTP", {})
    mcp_url = mcp_config.get("url", "")
    
    if not mcp_url or "YOUR_AMAP_API_KEY" in mcp_url:
        print("⚠️  未配置高德 API Key，使用 Mock 模式")
        return MockAmapMCPClient()
    
    print(f"✅ 连接到高德 MCP Server: {mcp_url.split('?')[0]}...")
    return AmapMCPClient(mcp_url)
