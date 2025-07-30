from playwright.async_api import async_playwright

from botterfly.config import Config


class RemoteBrowser:
    def __init__(self, config: Config):
        self._cdp_url = config.cdp_url
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None

    async def start(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.connect_over_cdp(
            endpoint_url=str(self._cdp_url)
        )
        self._context = self._browser.contexts[0]
        return self

    async def open_new_page(self):
        if not self._context:
            raise RuntimeError("Browser context not initialized. Call start() first.")
        new_page = await self._context.new_page()
        return new_page

    async def stop(self):
        if self._page and not self._page.is_closed():
            await self._page.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
