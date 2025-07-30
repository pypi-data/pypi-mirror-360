from botterfly.browser.action.base_action import BaseAction
from botterfly.browser.get_element import get_element


class Extract(BaseAction):
    async def run(self, page, step: dict):
        selector = step["selector"]
        key = step["key"]
        attr = step.get("attribute")

        element = get_element(page, selector)

        match attr:
            case "value":
                value = await element.input_value()
            case "inner_html":
                value = await element.inner_html()
            case "outer_html":
                value = await element.evaluate("el => el.outerHTML")
            case _:
                value = await element.text_content()

        return {key: value}
