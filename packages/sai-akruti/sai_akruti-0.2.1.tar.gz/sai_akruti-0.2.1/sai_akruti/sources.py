import boto3
import botocore.exceptions
import json

from abc import ABC
from pathlib import Path
from typing import Any, Dict, List, Type

from dotenv import dotenv_values
from pydantic_settings import PydanticBaseSettingsSource, BaseSettings


class MultiDotEnvSettingsSource(PydanticBaseSettingsSource, ABC):
    """Load from multiple .env files in order."""
    env_files: List[Path]

    def __init__(self,  settings_cls: Type[BaseSettings], env_files: List[Path]):
        super().__init__(settings_cls)
        self.env_files = env_files

    def __call__(self) -> Dict[str, Any]:
        data = {}
        for env_file in self.env_files:
            if env_file.exists():
                data.update(dotenv_values(env_file))
        return data


class SSMSettingsSource(PydanticBaseSettingsSource, ABC):
    """Load from AWS SSM Parameter Store, supporting multiple prefixes."""
    def __init__(self,  settings_cls: Type[BaseSettings], prefixes: List[str], region: str = "us-west-2"):
        super().__init__(settings_cls)
        self.prefixes = prefixes
        self.client = boto3.client("ssm", region_name=region)

    def __call__(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for prefix in self.prefixes:
            paginator = self.client.get_paginator("get_parameters_by_path")
            for page in paginator.paginate(Path=prefix, Recursive=True, WithDecryption=True):
                for param in page.get("Parameters", []):
                    key = param["Name"].replace(prefix, "").strip("/").replace("/", "_")
                    data[key] = param["Value"]
        return data


class SecretsManagerSettingsSource(PydanticBaseSettingsSource, ABC):
    """Load from AWS Secrets Manager, supporting multiple secrets."""
    def __init__(self, settings_cls: Type[BaseSettings], secret_ids: List[str], region: str = "us-west-2"):
        super().__init__(settings_cls)
        self.secret_ids = secret_ids
        self.client = boto3.client("secretsmanager", region_name=region)

    def __call__(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for secret_id in self.secret_ids:
            try:
                response = self.client.get_secret_value(SecretId=secret_id)
                secret_string = response.get("SecretString")
                if secret_string:
                    secret_data = json.loads(secret_string)
                    if isinstance(secret_data, dict):
                        data.update(secret_data)
            except botocore.exceptions.BotoCoreError as e:
                raise e
        return data
