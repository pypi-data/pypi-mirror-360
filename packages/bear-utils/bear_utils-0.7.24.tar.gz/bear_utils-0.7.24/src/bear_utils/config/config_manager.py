"""Config Manager Module for Bear Utils."""

from collections.abc import Callable
from functools import cached_property
import os
from pathlib import Path
import tomllib
from typing import Any

from pydantic import BaseModel, ValidationError, field_validator


def nullable_string_validator(field_name: str) -> Callable[..., str | None]:
    """Create a validator that converts 'null' strings to None."""

    @field_validator(field_name)
    @classmethod
    def _validate(cls: object, v: str | None) -> str | None:  # noqa: ARG001
        if isinstance(v, str) and v.lower() in ("null", "none", ""):
            return None
        return v

    return _validate


class ConfigManager[ConfigType: BaseModel]:
    """A generic configuration manager with environment-based overrides."""

    def __init__(self, config_model: type[ConfigType], config_path: Path | None = None, env: str = "dev") -> None:
        """Initialize the ConfigManager with a Pydantic model and configuration path."""
        self._model: type[ConfigType] = config_model
        self._config_path: Path = config_path or Path("config")
        self._env: str = env
        self._config: ConfigType | None = None
        self._config_path.mkdir(parents=True, exist_ok=True)

    def _get_env_overrides(self) -> dict[str, Any]:
        """Convert environment variables to nested dictionary structure."""
        env_config: dict[str, Any] = {}

        for key, value in os.environ.items():
            if not key.startswith("APP_"):
                continue

            # Convert APP_DATABASE_HOST to ['database', 'host']
            parts: list[str] = key.lower().replace("app_", "").split("_")

            current: dict[str, Any] = env_config
            for part in parts[:-1]:
                current = current.setdefault(part, {})

            final_value: Any = self._convert_env_value(value)
            current[parts[-1]] = final_value
        return env_config

    def _convert_env_value(self, value: str) -> Any:
        """Convert string environment variables to appropriate types."""
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        if value.isdigit():
            return int(value)

        try:
            if "." in value:
                return float(value)
        except ValueError:
            pass

        if "," in value:
            return [item.strip() for item in value.split(",")]

        return value

    def _load_toml_file(self, file_path: Path) -> dict[str, Any]:
        """Load a TOML file and return its contents."""
        try:
            with open(file_path, "rb") as f:
                return tomllib.load(f)
        except (FileNotFoundError, tomllib.TOMLDecodeError):
            return {}

    @cached_property
    def load(self) -> ConfigType:
        """Load configuration from files and environment variables."""
        # Load order (later overrides earlier):
        # 1. default.toml
        # 2. {env}.toml
        # 3. local.toml (gitignored)
        # 4. environment variables
        config_data: dict[str, Any] = {}

        # TODO: Update this so it looks for it in more than one place
        config_files: list[Path] = [
            self._config_path / "default.toml",
            self._config_path / f"{self._env}.toml",
            self._config_path / "local.toml",
        ]

        for config_file in config_files:
            if config_file.exists():
                file_data = self._load_toml_file(config_file)
                config_data = self._deep_merge(config_data, file_data)

        env_overrides: dict[str, Any] = self._get_env_overrides()
        config_data = self._deep_merge(config_data, env_overrides)

        try:
            return self._model.model_validate(config_data)
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}") from e

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries."""
        result: dict[str, Any] = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @property
    def config(self) -> ConfigType:
        """Get the loaded configuration."""
        if self._config is None:
            self._config = self.load
        return self._config

    def reload(self) -> ConfigType:
        """Force reload the configuration."""
        if "config" in self.__dict__:
            del self.__dict__["config"]
        return self.config

    def create_default_config(self) -> None:
        """Create a default.toml file with example values."""
        default_path = self._config_path / "default.toml"
        if default_path.exists():
            return

        try:
            default_instance: ConfigType = self._model()
            toml_content: str = self._model_to_toml(default_instance)
            default_path.write_text(toml_content)
        except Exception as e:
            print(f"Could not create default config: {e}")

    def _model_to_toml(self, instance: ConfigType) -> str:
        """Convert a Pydantic model to TOML format."""
        lines: list[str] = ["# Default configuration"]

        def _dict_to_toml(data: dict[str, Any], prefix: str = "") -> None:
            for key, value in data.items():
                full_key: str = f"{prefix}.{key}" if prefix else key

                if isinstance(value, dict):
                    lines.append(f"\n[{full_key}]")
                    for sub_key, sub_value in value.items():
                        lines.append(f"{sub_key} = {self._format_toml_value(sub_value)}")
                elif not prefix:
                    lines.append(f"{key} = {self._format_toml_value(value)}")

        _dict_to_toml(instance.model_dump())
        return "\n".join(lines)

    def _format_toml_value(self, value: Any) -> str:
        """Format a value for TOML output."""
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, list):
            formatted_items = [self._format_toml_value(item) for item in value]
            return f"[{', '.join(formatted_items)}]"
        if value is None:
            return '"null"'
        return str(value)


if __name__ == "__main__":
    # Example usage and models
    class DatabaseConfig(BaseModel):
        """Configuration for an example database connection."""

        host: str = "localhost"
        port: int = 5432
        username: str = "app"
        password: str = "secret"  # noqa: S105 This is just an example
        database: str = "myapp"

    class LoggingConfig(BaseModel):
        """Configuration for an example logging setup."""

        level: str = "INFO"
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file: str | None = None

        _validate_file = nullable_string_validator("file")

    class AppConfig(BaseModel):
        """Example application configuration model."""

        database: DatabaseConfig = DatabaseConfig()
        logging: LoggingConfig = LoggingConfig()
        environment: str = "development"
        debug: bool = False
        api_key: str = "your-api-key-here"
        allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    def get_config_manager(env: str = "dev") -> ConfigManager[AppConfig]:
        """Get a configured ConfigManager instance."""
        return ConfigManager[AppConfig](
            config_model=AppConfig,
            config_path=Path("config"),
            env=env,
        )

    config_manager: ConfigManager[AppConfig] = get_config_manager("development")
    config_manager.create_default_config()
    config: AppConfig = config_manager.config

    print(f"Database host: {config.database.host}")
    print(f"Debug mode: {config.debug}")
    print(f"Environment: {config.environment}")

    # Test environment variable override
    # Set: APP_DATABASE_HOST=production-db.example.com
    # Set: APP_DEBUG=true
