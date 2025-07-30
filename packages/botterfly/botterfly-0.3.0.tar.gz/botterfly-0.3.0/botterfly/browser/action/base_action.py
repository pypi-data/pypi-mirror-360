from typing import Any


class BaseAction:
    async def run(self, page, step) -> Any:
        raise NotImplementedError
