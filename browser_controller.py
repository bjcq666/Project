import asyncio
from playwright.async_api import async_playwright, Browser, Page


class BrowserController:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.playwright = None
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )
        context = await self.browser.new_context(
            viewport=None,
            no_viewport=True
        )
        self.page = await context.new_page()
    
    async def close(self):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def open_amap_navigation(self, url: str, wait_time: int = 5) -> bool:
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            
            await asyncio.sleep(wait_time)
            
            await self.page.bring_to_front()
            
            return True
            
        except Exception as e:
            raise Exception(f"打开高德地图失败: {str(e)}")
