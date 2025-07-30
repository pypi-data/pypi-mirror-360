from typing import Any

from botterfly.browser.action.base_action import BaseAction


class GoBack(BaseAction):
    async def run(self, page, step) -> Any:
        await page.go_back()
