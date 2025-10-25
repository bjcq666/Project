#!/usr/bin/env python3
"""
Location Service Module
Provides current geographic location functionality
"""

import asyncio
import json
import os
from typing import Optional, Dict
import httpx


class LocationService:
    def __init__(self, provider: str = "auto"):
        """
        初始化位置服务
        
        Args:
            provider: 位置服务提供商 ('ip', 'amap', 'auto')
                     'ip' - 基于IP地址获取位置
                     'amap' - 使用高德地图IP定位API
                     'auto' - 自动选择可用服务
        """
        self.provider = provider
        self.amap_api_key = os.getenv("AMAP_API_KEY")
    
    async def get_current_location(self) -> Optional[Dict[str, any]]:
        """
        获取当前地理位置
        
        Returns:
            包含位置信息的字典，格式：
            {
                "name": "城市名称",
                "longitude": 经度,
                "latitude": 纬度,
                "province": "省份",
                "city": "城市",
                "formatted_address": "格式化地址"
            }
        """
        if self.provider == "amap" or (self.provider == "auto" and self.amap_api_key):
            location = await self._get_location_from_amap()
            if location:
                return location
        
        return await self._get_location_from_ip()
    
    async def _get_location_from_amap(self) -> Optional[Dict[str, any]]:
        """使用高德地图IP定位API获取当前位置"""
        if not self.amap_api_key:
            return None
        
        try:
            url = "https://restapi.amap.com/v3/ip"
            params = {
                "key": self.amap_api_key,
                "output": "json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == "1" and data.get("rectangle"):
                        rectangle = data["rectangle"].split(";")
                        if len(rectangle) >= 2:
                            coords = rectangle[0].split(",")
                            if len(coords) >= 2:
                                return {
                                    "name": data.get("city", "当前位置"),
                                    "longitude": float(coords[0]),
                                    "latitude": float(coords[1]),
                                    "province": data.get("province", ""),
                                    "city": data.get("city", ""),
                                    "formatted_address": f"{data.get('province', '')}{data.get('city', '')}"
                                }
        except Exception as e:
            print(f"高德地图IP定位失败: {e}")
        
        return None
    
    async def _get_location_from_ip(self) -> Optional[Dict[str, any]]:
        """基于IP地址获取大致位置（备用方案）"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://ipapi.co/json/")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    city = data.get("city", "")
                    if not city:
                        city = data.get("region", "当前位置")
                    
                    return {
                        "name": city,
                        "longitude": float(data.get("longitude", 116.397128)),
                        "latitude": float(data.get("latitude", 39.916527)),
                        "province": data.get("region", ""),
                        "city": city,
                        "formatted_address": f"{data.get('country_name', '')}{data.get('region', '')}{city}"
                    }
        except Exception as e:
            print(f"IP定位失败: {e}")
        
        return {
            "name": "当前位置",
            "longitude": 116.397128,
            "latitude": 39.916527,
            "province": "",
            "city": "",
            "formatted_address": "当前位置"
        }


async def get_current_location() -> Optional[Dict[str, any]]:
    """
    便捷函数：获取当前位置
    
    Returns:
        包含位置信息的字典
    """
    service = LocationService(provider="auto")
    return await service.get_current_location()
