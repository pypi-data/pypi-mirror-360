from pathlib import Path
from typing import Optional, Union

import yaml
from jinja2 import Environment, Undefined


class TemplateRenderer:
    def __init__(self):
        self.env = Environment(undefined=Undefined)

    def render(
        self,
        context: dict,
        file: Optional[Union[str, Path]] = None,
        template_str: Optional[str] = None,
    ):
        if file:
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"Template file not found: {file_path}")
            if file_path.suffix not in {".yml", ".yaml"}:
                raise ValueError(f"Unsupported template file type: {file_path.suffix}")
            template = self.env.from_string(file_path.read_text(encoding="utf-8"))
        elif template_str:
            template = self.env.from_string(template_str)
        else:
            raise ValueError("You must provide either a `file` or `template_str`.")

        rendered = template.render(**context)
        try:
            return yaml.safe_load(rendered)
        except yaml.YAMLError as e:
            raise ValueError(f"Rendered template is not valid YAML: {e}") from e
