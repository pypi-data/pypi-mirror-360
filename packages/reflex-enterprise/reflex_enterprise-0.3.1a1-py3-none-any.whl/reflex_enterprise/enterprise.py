"""Enterprise utilities for Reflex CLI."""

from typing import Any

from reflex.config import get_config
from reflex.utils import console, prerequisites

SHOW_BUILT_WITH_REFLEX_INFO = "https://reflex.dev/docs/hosting/reflex-branding/"


def check_config_option_in_tier(
    option_name: str,
    allowed_tiers: list[str],
    fallback_value: Any,
    help_link: str | None = None,
):
    """Check if a config option is allowed for the authenticated user's current tier.

    Args:
        option_name: The name of the option to check.
        allowed_tiers: The tiers that are allowed to use the option.
        fallback_value: The fallback value if the option is not allowed.
        help_link: The help link to show to a user that is authenticated.
    """
    config = get_config()
    current_tier = prerequisites.get_user_tier()

    if current_tier == "anonymous":
        the_remedy = (
            "You are currently logged out. Run `reflex login` to access this option."
        )
    else:
        the_remedy = (
            f"Your current subscription tier is `{current_tier}`. "
            f"Please upgrade to {allowed_tiers} to access this option. "
        )
        if help_link:
            the_remedy += f"See {help_link} for more information."

    if current_tier not in allowed_tiers:
        console.warn(f"Config option `{option_name}` is restricted. {the_remedy}")
        setattr(config, option_name, fallback_value)
        config._set_persistent(**{option_name: fallback_value})
