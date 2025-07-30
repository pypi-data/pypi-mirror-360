import os
from pathlib import Path
from typing import List, Tuple, Literal, Dict, Any, ClassVar, Type

from pydantic import AnyHttpUrl, HttpUrl, AfterValidator
from typing_extensions import Annotated

from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

from sources import MultiDotEnvSettingsSource, SSMSettingsSource, SecretsManagerSettingsSource

AnyHttpUrlString = Annotated[AnyHttpUrl, AfterValidator(lambda v: str(v))]
HttpUrlString = Annotated[HttpUrl, AfterValidator(lambda v: str(v))]

SettingsSourceType = Literal[
    "init",
    "env",
    "dotenv",
    "ssm",
    "secrets",
    "file_secrets"
]


class Settings(BaseSettings):
    """ Common configuration parameters shared between all environments.

    Read configuration parameters defined in this class, and from
    ENVIRONMENT variables and from the .env file.

    The source priority is changed (from default) to the following
    order (from highest to lowest)::
      - init_settings
      - dotenv_settings
      - env_settings
      - file_secret_settings
      - AWS Parameter Store (if available)
      - AWS Secrets Manager (if available)

    The following environment variables should already be defined::
      - HOSTNAME (on Linux servers only - set by OS)
      - COMPUTERNAME (on Windows servers only - set by OS)
      - ENVIRONMENT (on all servers - "dev" is default when missing)

    Path where your <environment>.env file should be placed::
      - linux: /home/<user>/.local
      - darwin: /home/<user>/.local
      - win32: C:\\Users\\<user>\\AppData\\Roaming\\Python'

    Path where your secret files should be placed::
      - linux: /home/<user>/.local/secrets
      - darwin: /home/<user>/.local/secrets
      - win32: C:\\Users\\<user>\\AppData\\Roaming\\Python\\secrets'

    You know you are running in Docker when the "/.dockerenv" file exists.

    Sources: You can configure the sources and order of priority for settings loading.
                    sources = configureSources(
                        DevSettings,
                        env_files=["config/.env", "config/.env.dev"],
                        ssm_prefixes=["/myapp/dev/"],
                        secret_ids=["myapp/dev/secret1", "myapp/dev/secret2"],
                    )

    You can also setup multiple settings variables and pick the one based on the environment.
    For example, you can have `DefaultSettings` class for common settings and derive `DevSettings`, `ProdSettings`
    to override the sources_config for each.

    Finally, you can use:
             _setup: dict[str, Type[LocalSettings | DevSettings | QASettings | ProdSettings]] = dict(
                    local=LocalSettings or DefaultSettings,
                    dev=DevSettings,
                    qa=QASettings,
                    prod=ProdSettings
            )

            ENVIRONMENT = os.getenv('ENVIRONMENT', MISSING_ENV)
            print(f"Loading Environment: {ENVIRONMENT}")
            settings = _setup[ENVIRONMENT]()

    """

    sources_config: ClassVar[List[Dict[str, Any]]] = [
        {"type": "init"},
        {"type": "dotenv", "env_files": ["config/.env"]},
        {"type": "env"},
        {"type": "file_secrets", "secrets_dir": None},  # None means default auto-detection
    ]

    model_config = SettingsConfigDict(
        extra='ignore',  # Allow/ignore/forbid extra fields here
    )

    @classmethod
    def configureSources(cls, settings_cls: Type[BaseSettings]) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Configure settings sources explicitly in the desired priority order."""
        sources: List[PydanticBaseSettingsSource] = []
        for src in cls.sources_config:
            src_type = src["type"]
            if src_type == "dotenv":
                env_files = [Path(f) for f in src["env_files"]]
                sources.append(MultiDotEnvSettingsSource(settings_cls, env_files))
            elif src_type == "ssm":
                sources.append(SSMSettingsSource(
                    cls, prefixes=src["prefixes"], region=src.get("region", "us-west-2")
                ))
            elif src_type == "secrets":
                sources.append(SecretsManagerSettingsSource(
                    cls, secret_ids=src["secret_ids"], region=src.get("region", "us-west-2")
                ))
            else:
                raise ValueError(f"Unknown source type: {src_type}")
        return tuple(sources)

    @classmethod
    def settings_customise_sources(cls,
                                   settings_cls: Type[BaseSettings],
                                   init_settings: PydanticBaseSettingsSource,
                                   env_settings: PydanticBaseSettingsSource,
                                   dotenv_settings: PydanticBaseSettingsSource,
                                   file_secret_settings: PydanticBaseSettingsSource
                                   ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Customize loading order, adding custom sources before env/dotenv/secret defaults."""
        return cls.configureSources(settings_cls) + (
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    @staticmethod
    def getSecretsDir() -> str:
        """Determine secrets directory based on Docker/non-Docker context."""
        if os.path.exists('/.dockerenv'):
            return '/run/secrets'
        else:
            secrets_dir = 'config/secrets'
            os.makedirs(secrets_dir, exist_ok=True)
            return secrets_dir
