"""
浏览器控制 MCP Server
提供浏览器自动化功能，符合 MCP 标准
"""

import webbrowser
import urllib.parse
from typing import Dict, Any


class BrowserControlMCPServer:
    """浏览器控制 MCP Server"""
    
    def __init__(self):
        self.name = "browser-control"
        self.version = "1.0.0"
    
    def list_tools(self) -> list:
        """列出可用工具"""
        return [
            {
                "name": "open_url",
                "description": "在默认浏览器中打开指定 URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要打开的 URL"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "open_map_navigation",
                "description": "打开地图导航页面",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_lng": {
                            "type": "number",
                            "description": "起点经度"
                        },
                        "start_lat": {
                            "type": "number",
                            "description": "起点纬度"
                        },
                        "end_lng": {
                            "type": "number",
                            "description": "终点经度"
                        },
                        "end_lat": {
                            "type": "number",
                            "description": "终点纬度"
                        },
                        "map_service": {
                            "type": "string",
                            "description": "地图服务 (amap 或 baidu)",
                            "enum": ["amap", "baidu"]
                        }
                    },
                    "required": ["end_lng", "end_lat"]
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_name == "open_url":
            return self._open_url(arguments["url"])
        
        elif tool_name == "open_map_navigation":
            return self._open_map_navigation(
                start_lng=arguments.get("start_lng"),
                start_lat=arguments.get("start_lat"),
                end_lng=arguments["end_lng"],
                end_lat=arguments["end_lat"],
                map_service=arguments.get("map_service", "amap")
            )
        
        else:
            raise ValueError(f"未知工具: {tool_name}")
    
    def _open_url(self, url: str) -> Dict[str, Any]:
        """打开 URL"""
        try:
            webbrowser.open(url)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ 已打开 URL: {url}"
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ 打开 URL 失败: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    def _open_map_navigation(
        self,
        end_lng: float,
        end_lat: float,
        start_lng: float = None,
        start_lat: float = None,
        map_service: str = "amap"
    ) -> Dict[str, Any]:
        """打开地图导航"""
        try:
            if map_service == "amap":
                url = self._build_amap_url(start_lng, start_lat, end_lng, end_lat)
            elif map_service == "baidu":
                url = self._build_baidu_url(start_lng, start_lat, end_lng, end_lat)
            else:
                raise ValueError(f"不支持的地图服务: {map_service}")
            
            webbrowser.open(url)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ 已打开{map_service.upper()}地图导航\n📍 URL: {url}"
                    }
                ]
            }
        
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ 打开地图导航失败: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    def _build_amap_url(
        self,
        start_lng: float,
        start_lat: float,
        end_lng: float,
        end_lat: float
    ) -> str:
        """构建高德地图导航 URL"""
        if start_lng and start_lat:
            from_param = f"{start_lng},{start_lat}"
        else:
            from_param = ""
        
        to_param = f"{end_lng},{end_lat}"
        
        params = {
            "from": from_param,
            "to": to_param,
            "policy": "1",
            "coordinate": "gaode"
        }
        
        if not from_param:
            del params["from"]
        
        query_string = urllib.parse.urlencode(params)
        return f"https://uri.amap.com/navigation?{query_string}"
    
    def _build_baidu_url(
        self,
        start_lng: float,
        start_lat: float,
        end_lng: float,
        end_lat: float
    ) -> str:
        """构建百度地图导航 URL"""
        if start_lng and start_lat:
            origin = f"latlng:{start_lat},{start_lng}|name:起点"
        else:
            origin = "我的位置"
        
        destination = f"latlng:{end_lat},{end_lng}|name:终点"
        
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "driving",
            "coord_type": "gcj02"
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"http://api.map.baidu.com/direction?{query_string}"


def create_browser_server() -> BrowserControlMCPServer:
    """创建浏览器控制 MCP Server"""
    return BrowserControlMCPServer()
