"""Enterprise utilities for Reflex CLI."""

from typing import ClassVar

from reflex.config import Config


class ConfigEnterprise(Config):
    """Enterprise configuration class."""

    show_built_with_reflex: bool | None = None

    use_single_port: bool | None = None

    _prefixes: ClassVar[list[str]] = ["REFLEX_", "REFLEX_ENTERPRISE_"]


Config = ConfigEnterprise
