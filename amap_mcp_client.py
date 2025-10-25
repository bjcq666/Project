import asyncio
import json
from typing import Dict, Optional, Tuple
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import config


class AmapMCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@masx200/amap-maps-mcp-server"],
            env={
                "AMAP_MAPS_API_KEY": config.AMAP_API_KEY
            }
        )
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
    
    async def connect(self):
        self.stdio_transport = await stdio_client(self.server_params)
        self.stdio, self.write = self.stdio_transport.__enter__()
        self.session = ClientSession(self.stdio, self.write)
        await self.session.__aenter__()
        await self.session.initialize()
    
    async def disconnect(self):
        if self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'stdio_transport'):
            self.stdio_transport.__exit__(None, None, None)
    
    async def get_geocode(self, address: str) -> Optional[Tuple[float, float]]:
        try:
            result = await self.session.call_tool(
                "maps_geo",
                arguments={"address": address}
            )
            
            if result.content and len(result.content) > 0:
                data = json.loads(result.content[0].text)
                if data.get("status") == "1" and data.get("geocodes"):
                    location = data["geocodes"][0].get("location", "")
                    if location:
                        lon, lat = map(float, location.split(","))
                        return (lon, lat)
            return None
        except Exception as e:
            raise Exception(f"地理编码失败: {str(e)}")
    
    async def get_route_plan(
        self, 
        origin: Tuple[float, float], 
        destination: Tuple[float, float],
        mode: str = "driving",
        policy: int = 0
    ) -> Dict:
        origin_str = f"{origin[0]},{origin[1]}"
        destination_str = f"{destination[0]},{destination[1]}"
        
        try:
            if mode == "driving":
                tool_name = "maps_direction_driving"
                arguments = {
                    "origin": origin_str,
                    "destination": destination_str,
                    "strategy": str(policy)
                }
            elif mode == "walking":
                tool_name = "maps_direction_walking"
                arguments = {
                    "origin": origin_str,
                    "destination": destination_str
                }
            elif mode == "bicycling":
                tool_name = "maps_bicycling"
                arguments = {
                    "origin": origin_str,
                    "destination": destination_str
                }
            else:
                raise ValueError(f"不支持的导航模式: {mode}")
            
            result = await self.session.call_tool(tool_name, arguments=arguments)
            
            if result.content and len(result.content) > 0:
                data = json.loads(result.content[0].text)
                return data
            return {}
            
        except Exception as e:
            raise Exception(f"路线规划失败: {str(e)}")
    
    async def generate_web_url(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "driving",
        policy: int = 0
    ) -> str:
        mode_map = {
            "driving": "car",
            "walking": "walk",
            "bicycling": "bike"
        }
        
        amap_mode = mode_map.get(mode, "car")
        
        origin_str = f"{origin[0]},{origin[1]}"
        destination_str = f"{destination[0]},{destination[1]}"
        
        url = (
            f"https://uri.amap.com/navigation?"
            f"from={origin_str}&"
            f"to={destination_str}&"
            f"mode={amap_mode}&"
            f"policy={policy}&"
            f"src=ai_navigation&"
            f"callnative=0"
        )
        
        return url
