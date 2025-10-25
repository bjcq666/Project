import asyncio
from ai_parser import AIIntentParser, NavigationIntent
from amap_mcp_client import AmapMCPClient
from browser_controller import BrowserController


async def main():
    print("=" * 60)
    print("欢迎使用 AI 智能导航系统")
    print("=" * 60)
    print()
    
    user_input = input("请输入导航指令（例如：我要从北京西站开车去颐和园，避开拥堵）: ")
    
    if not user_input.strip():
        print("错误: 输入不能为空")
        return
    
    print()
    print("正在解析您的导航需求...")
    
    try:
        parser = AIIntentParser()
        nav_intent = await parser.parse(user_input)
        
        print(f"\n✓ 解析成功!")
        print(f"  起点: {nav_intent.origin}")
        print(f"  终点: {nav_intent.destination}")
        print(f"  模式: {nav_intent.mode}")
        print(f"  策略: {nav_intent.policy}")
        if nav_intent.preferences:
            print(f"  偏好: {', '.join(nav_intent.preferences)}")
        
        print("\n正在连接高德地图服务...")
        
        async with AmapMCPClient() as mcp_client:
            print("✓ 已连接到高德地图 MCP 服务")
            
            print(f"\n正在获取起点 '{nav_intent.origin}' 的坐标...")
            origin_coord = await mcp_client.get_geocode(nav_intent.origin)
            
            if not origin_coord:
                print(f"错误: 无法找到起点 '{nav_intent.origin}' 的位置")
                return
            
            print(f"✓ 起点坐标: {origin_coord}")
            
            print(f"\n正在获取终点 '{nav_intent.destination}' 的坐标...")
            dest_coord = await mcp_client.get_geocode(nav_intent.destination)
            
            if not dest_coord:
                print(f"错误: 无法找到终点 '{nav_intent.destination}' 的位置")
                return
            
            print(f"✓ 终点坐标: {dest_coord}")
            
            print("\n正在规划路线...")
            route_data = await mcp_client.get_route_plan(
                origin_coord,
                dest_coord,
                nav_intent.mode,
                nav_intent.policy
            )
            
            print("✓ 路线规划完成")
            
            print("\n正在生成导航 URL...")
            amap_url = await mcp_client.generate_web_url(
                origin_coord,
                dest_coord,
                nav_intent.mode,
                nav_intent.policy
            )
            
            print(f"✓ 导航 URL: {amap_url}")
            
            print("\n正在打开浏览器并显示导航路线...")
            
            async with BrowserController() as browser:
                success = await browser.open_amap_navigation(amap_url)
                
                if success:
                    print("\n✓ 导航路线已在浏览器中打开!")
                    print("\n提示: 请在浏览器中查看并开始导航")
                    print("按 Ctrl+C 退出程序...")
                    
                    try:
                        await asyncio.Event().wait()
                    except KeyboardInterrupt:
                        print("\n\n程序已退出")
                else:
                    print("\n错误: 无法打开导航页面")
    
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
