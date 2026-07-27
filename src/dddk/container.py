from duckdi import (
    register,
)

from dddk.envs.adapters import (
    EnvsToml,
)

register(EnvsToml, "toml", True)
