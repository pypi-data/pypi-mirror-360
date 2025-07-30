import os
from pathlib import Path

import yaml
from jinja2 import Environment, Undefined

from botterfly.context.vault_wrapper import VaultWrapper


class ContextParser:
    def __init__(self):
        self.vault = VaultWrapper()
        self.env = Environment(undefined=Undefined)

    def parse(self, file_path: Path = None) -> dict:
        context = self.env.from_string(file_path.read_text(encoding="utf-8"))
        rendered = context.render(
            env=os.environ,
            vault=self.vault,
        )

        return yaml.safe_load(rendered)
