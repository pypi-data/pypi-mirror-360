from pathlib import Path

from botterfly.browser.action.action_registry import ActionRegistry
from botterfly.browser.remote_browser import RemoteBrowser
from botterfly.config import Config
from botterfly.context.context_parser import ContextParser
from botterfly.context.template_renderer import TemplateRenderer
from botterfly.plan import Plan


class Bot:
    def __init__(
        self,
        template_renderer: TemplateRenderer,
        context_parser: ContextParser,
        remote_browser: RemoteBrowser,
        registry: ActionRegistry,
    ):
        self._template_renderer = template_renderer
        self._context_parser = context_parser
        self._remote_browser = remote_browser
        self._registry = registry

    def _load_plan(self, config: Config) -> str:
        with Path.open(config.plan.resolve(), "r") as f:
            return f.read()

    def _load_context(self, config: Config) -> dict:
        return self._context_parser.parse(config.context.resolve())

    async def execute(self, config: Config):
        context = self._load_context(config)
        plan_template_str = self._load_plan(config)

        result = {}
        executor = Plan(self._template_renderer, plan_template_str, context, result)

        try:
            await self._remote_browser.start()
            page = await self._remote_browser.open_new_page()

            for step, result in executor:
                action = self._registry.get(step["action"])
                action_result = await action.run(page=page, step=step)
                if isinstance(action_result, dict):
                    result.update(action_result)

        except Exception as e:
            print(e)
        finally:
            await self._remote_browser.stop()

        return result
