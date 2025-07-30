from botterfly.browser.action.check import Check
from botterfly.browser.action.click import Click
from botterfly.browser.action.extract import Extract
from botterfly.browser.action.fill import Fill
from botterfly.browser.action.go_back import GoBack
from botterfly.browser.action.go_to import GoTo
from botterfly.browser.action.wait import Wait


class ActionRegistry:
    def __init__(self):
        self._registry = {}
        self._init_registry()

    def _init_registry(self):
        if self._registry == {}:
            self._add("goto", GoTo())
            self._add("goback", GoBack())
            self._add("fill", Fill())
            self._add("click", Click())
            self._add("check", Check())
            self._add("wait", Wait())
            self._add("extract", Extract())

    def get(self, name: str):
        if name not in self._registry:
            raise ValueError(f"'{name}' is not registered")

        return self._registry[name]

    def _add(self, name, action):
        self._registry[name] = action
