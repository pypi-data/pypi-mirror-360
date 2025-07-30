from typing import List, Optional

from truefoundry.deploy.builder.constants import (
    BUILDKIT_SECRET_MOUNT_PIP_CONF_ID,
    BUILDKIT_SECRET_MOUNT_UV_CONF_ID,
)


def _get_id_from_buildkit_secret_value(value: str) -> Optional[str]:
    parts = value.split(",")
    secret_config = {}
    for part in parts:
        kv = part.split("=", 1)
        if len(kv) != 2:
            continue
        key, value = kv
        secret_config[key] = value

    if "id" in secret_config and "src" in secret_config:
        return secret_config["id"]

    return None


def has_python_package_manager_conf_secret(docker_build_extra_args: List[str]) -> bool:
    args = [arg.strip() for arg in docker_build_extra_args]
    for i, arg in enumerate(docker_build_extra_args):
        if (
            arg == "--secret"
            and i + 1 < len(args)
            and (
                _get_id_from_buildkit_secret_value(args[i + 1])
                in (BUILDKIT_SECRET_MOUNT_PIP_CONF_ID, BUILDKIT_SECRET_MOUNT_UV_CONF_ID)
            )
        ):
            return True
    return False
