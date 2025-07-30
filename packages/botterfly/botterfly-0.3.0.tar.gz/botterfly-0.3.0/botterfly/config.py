from pathlib import Path
from typing import Annotated

from dynaconf import Dynaconf
from pydantic import AnyUrl, BaseModel, UrlConstraints


class ConfigSchema(BaseModel):
    name: str
    cdp_url: Annotated[
        AnyUrl,
        UrlConstraints(
            allowed_schemes=["http", "ws"],
            host_required=True,
            default_host="localhost",
            default_port=9222,
            default_path=None,
        ),
    ]
    plan: Path
    context: Path


class Config:
    def __init__(self, path: Path, env: str = "default") -> None:
        if path is None:
            raise ValueError("No config path provided")
        if not path.exists():
            raise FileNotFoundError(f"Config file not found at: {path}")

        settings = Dynaconf(
            settings_files=[path.resolve()],
            environments=True,
            envvar_prefix="BOTTERFLY",
            env=env,
            # dynaconf uppercases all keys by design to make them compatible with env variables
            # this turn of this behavior and keep the case sensitivity so the schema validation work
            case_sensitive=True,
        )

        self._schema = ConfigSchema(
            name=settings.get("name"),
            cdp_url=settings.get("cdp_url"),
            plan=Path(settings.get("plan")),
            context=Path(settings.get("context")),
        )

    def __getattr__(self, key):
        return getattr(self._schema, key)
