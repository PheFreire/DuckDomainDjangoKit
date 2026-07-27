from duckdi import (
    Get,
)

import dddk.container  # noqa: F401 - side-effect import: registers the "toml" adapter
from dddk.envs.interfaces.i_envs import (
    IEnvs,
)
from dddk.envs.adapters.envs_toml import (
    EnvsToml,
)


def test_container_registers_envs_toml_under_toml_label():
    instance = Get(IEnvs, label="env", adapter="toml")
    assert isinstance(instance, EnvsToml)


def test_container_registration_is_a_singleton():
    first = Get(IEnvs, label="env", adapter="toml")
    second = Get(IEnvs, label="env", adapter="toml")
    assert first is second
