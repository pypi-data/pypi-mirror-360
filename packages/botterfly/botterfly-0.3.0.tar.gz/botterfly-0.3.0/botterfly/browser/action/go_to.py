from typing import Any

from botterfly.browser.action.base_action import BaseAction


class GoTo(BaseAction):
    async def run(self, page, step: dict) -> Any:
        await page.goto(step["value"])
