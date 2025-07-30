from typing import Any

from botterfly.browser.action.base_action import BaseAction
from botterfly.browser.get_element import get_element


class Check(BaseAction):
    async def run(self, page, step: dict) -> Any:
        locator = get_element(page=page, selector=step["selector"])
        await locator.check()
