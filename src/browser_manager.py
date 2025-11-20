import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

class BrowserManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    async def start(self):
        """Starts the Playwright browser session."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir="captured_workflows/videos/" # Record video for debugging/Loom
        )
        self.page = await self.context.new_page()

    async def navigate(self, url: str):
        """Navigates to a specific URL."""
        if not self.page:
            raise Exception("Browser not started. Call start() first.")
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")

    async def click(self, selector: str):
        """Clicks an element specified by the selector."""
        if not self.page:
            raise Exception("Browser not started.")
        await self.page.click(selector)
        # Wait a bit for potential animations or navigation
        await self.page.wait_for_load_state("domcontentloaded")

    async def type(self, selector: str, text: str):
        """Types text into an element."""
        if not self.page:
            raise Exception("Browser not started.")
        await self.page.fill(selector, text)

    async def press(self, key: str):
        """Presses a key."""
        if not self.page:
            raise Exception("Browser not started.")
        await self.page.keyboard.press(key)

    async def get_current_url(self) -> str:
        """Returns the current URL."""
        if not self.page:
            raise Exception("Browser not started.")
        return self.page.url

    async def stop(self):
        """Stops the browser session."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
