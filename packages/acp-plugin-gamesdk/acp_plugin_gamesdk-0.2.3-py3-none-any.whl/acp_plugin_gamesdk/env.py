from typing import Optional
from virtuals_acp.env import EnvSettings
from pydantic import field_validator

class PluginEnvSettings(EnvSettings):
    GAME_DEV_API_KEY: str
    GAME_API_KEY: str
    BUYER_AGENT_GAME_TWITTER_ACCESS_TOKEN: str
    SELLER_AGENT_GAME_TWITTER_ACCESS_TOKEN: str
    WHITELISTED_WALLET_ENTITY_ID: Optional[int] = None
    # BUYER_AGENT_TWITTER_BEARER_TOKEN: str
    # BUYER_AGENT_TWITTER_API_KEY: str
    # BUYER_AGENT_TWITTER_API_SECRET_KEY: str
    # BUYER_AGENT_TWITTER_ACCESS_TOKEN: str
    # BUYER_AGENT_TWITTER_ACCESS_TOKEN_SECRET: str
    # SELLER_AGENT_TWITTER_BEARER_TOKEN: str
    # SELLER_AGENT_TWITTER_API_KEY: str
    # SELLER_AGENT_TWITTER_API_SECRET_KEY: str
    # SELLER_AGENT_TWITTER_ACCESS_TOKEN: str
    # SELLER_AGENT_TWITTER_ACCESS_TOKEN_SECRET: str

    @field_validator("GAME_DEV_API_KEY", "GAME_API_KEY")
    @classmethod
    def check_apt_prefix(cls, v: str) -> str:
        if v and not v.startswith("apt-"):
            raise ValueError("GAME key must start with 'apt-'")
        return v

    @field_validator("BUYER_AGENT_GAME_TWITTER_ACCESS_TOKEN", "SELLER_AGENT_GAME_TWITTER_ACCESS_TOKEN")
    @classmethod
    def check_apx_prefix(cls, v: str) -> str:
        if v and not v.startswith("apx-"):
            raise ValueError("SELLER_AGENT_GAME_TWITTER_ACCESS_TOKEN must start with 'apx-'")
        return v
    