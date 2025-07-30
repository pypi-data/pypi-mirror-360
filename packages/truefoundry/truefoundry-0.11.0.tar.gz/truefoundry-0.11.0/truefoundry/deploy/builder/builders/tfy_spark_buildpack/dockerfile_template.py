import shlex
from typing import List, Optional

from mako.template import Template

from truefoundry.common.constants import ENV_VARS, PythonPackageManager
from truefoundry.deploy._autogen.models import SparkBuild
from truefoundry.deploy.builder.constants import (
    PIP_CONF_BUILDKIT_SECRET_MOUNT,
    PIP_CONF_SECRET_MOUNT_AS_ENV,
    UV_CONF_BUILDKIT_SECRET_MOUNT,
    UV_CONF_SECRET_MOUNT_AS_ENV,
)
from truefoundry.deploy.v2.lib.patched_models import (
    _resolve_requirements_path,
)

# TODO (chiragjn): Switch to a non-root user inside the container

_POST_PYTHON_INSTALL_TEMPLATE = """
% if requirements_path is not None:
COPY ${requirements_path} ${requirements_destination_path}
% endif
% if python_packages_install_command is not None:
RUN ${package_manager_config_secret_mount} ${python_packages_install_command}
% endif
ENV PYTHONDONTWRITEBYTECODE=1
ENV IPYTHONDIR=/tmp/.ipython
RUN groupadd --system --gid 1001 spark && useradd --system --uid 1001 --gid spark --no-create-home spark
USER spark
COPY . /app
"""

_POST_USER_TEMPLATE = """
COPY tfy_execute_notebook.py /app/tfy_execute_notebook.py
"""

DOCKERFILE_TEMPLATE = Template(
    """
FROM ${spark_image_repo}:${spark_version}
USER root
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*
"""
    + _POST_PYTHON_INSTALL_TEMPLATE
    + _POST_USER_TEMPLATE
)

ADDITIONAL_PIP_PACKAGES = [
    "papermill>=2.6.0,<2.7.0",
    "ipykernel>=6.0.0,<7.0.0",
    "nbconvert>=7.16.6,<7.17.0",
    "boto3>=1.38.43,<1.40.0",
]


def generate_pip_install_command(
    requirements_path: Optional[str],
    pip_packages: Optional[List[str]],
    mount_pip_conf_secret: bool = False,
) -> Optional[str]:
    upgrade_pip_command = "python3 -m pip install -U pip setuptools wheel"
    envs = []
    if mount_pip_conf_secret:
        envs.append(PIP_CONF_SECRET_MOUNT_AS_ENV)

    command = ["python3", "-m", "pip", "install", "--use-pep517", "--no-cache-dir"]
    args = []
    if requirements_path:
        args.append("-r")
        args.append(requirements_path)

    if pip_packages:
        args.extend(pip_packages)

    if not args:
        return None

    final_pip_install_command = shlex.join(envs + command + args)
    final_docker_run_command = " && ".join(
        [upgrade_pip_command, final_pip_install_command]
    )
    return final_docker_run_command


def generate_uv_pip_install_command(
    requirements_path: Optional[str],
    pip_packages: Optional[List[str]],
    mount_uv_conf_secret: bool = False,
) -> Optional[str]:
    upgrade_pip_command = "python3 -m pip install -U pip setuptools wheel"
    uv_mount = f"--mount=from={ENV_VARS.TFY_PYTHON_BUILD_UV_IMAGE_URI},source=/uv,target=/usr/local/bin/uv"
    envs = [
        "UV_LINK_MODE=copy",
        "UV_PYTHON_DOWNLOADS=never",
        "UV_INDEX_STRATEGY=unsafe-best-match",
    ]
    if mount_uv_conf_secret:
        envs.append(UV_CONF_SECRET_MOUNT_AS_ENV)

    command = ["uv", "pip", "install", "--no-cache-dir"]

    args = []

    if requirements_path:
        args.append("-r")
        args.append(requirements_path)

    if pip_packages:
        args.extend(pip_packages)

    if not args:
        return None

    uv_pip_install_command = shlex.join(envs + command + args)
    shell_commands = " && ".join([upgrade_pip_command, uv_pip_install_command])
    final_docker_run_command = " ".join([uv_mount, shell_commands])

    return final_docker_run_command


def generate_dockerfile_content(
    build_configuration: SparkBuild,
    package_manager: str = ENV_VARS.TFY_PYTHON_BUILD_PACKAGE_MANAGER,
    mount_python_package_manager_conf_secret: bool = False,
) -> str:
    # TODO (chiragjn): Handle recursive references to other requirements files e.g. `-r requirements-gpu.txt`
    requirements_path = _resolve_requirements_path(
        build_context_path=build_configuration.build_context_path,
        requirements_path=build_configuration.requirements_path,
    )
    requirements_destination_path = (
        "/tmp/requirements.txt" if requirements_path else None
    )
    if not build_configuration.spark_version:
        raise ValueError(
            "`spark_version` is required for `tfy-spark-buildpack` builder"
        )

    if package_manager == PythonPackageManager.PIP.value:
        python_packages_install_command = generate_pip_install_command(
            requirements_path=requirements_destination_path,
            pip_packages=ADDITIONAL_PIP_PACKAGES,
            mount_pip_conf_secret=mount_python_package_manager_conf_secret,
        )
    elif package_manager == PythonPackageManager.UV.value:
        python_packages_install_command = generate_uv_pip_install_command(
            requirements_path=requirements_destination_path,
            pip_packages=ADDITIONAL_PIP_PACKAGES,
            mount_uv_conf_secret=mount_python_package_manager_conf_secret,
        )
    else:
        raise ValueError(f"Unsupported package manager: {package_manager}")

    template_args = {
        "spark_image_repo": ENV_VARS.TFY_SPARK_BUILD_SPARK_IMAGE_REPO,
        "spark_version": build_configuration.spark_version,
        "requirements_path": requirements_path,
        "requirements_destination_path": requirements_destination_path,
        "python_packages_install_command": python_packages_install_command,
    }

    if mount_python_package_manager_conf_secret:
        if package_manager == PythonPackageManager.PIP.value:
            template_args["package_manager_config_secret_mount"] = (
                PIP_CONF_BUILDKIT_SECRET_MOUNT
            )
        elif package_manager == PythonPackageManager.UV.value:
            template_args["package_manager_config_secret_mount"] = (
                UV_CONF_BUILDKIT_SECRET_MOUNT
            )
        else:
            raise ValueError(f"Unsupported package manager: {package_manager}")
    else:
        template_args["package_manager_config_secret_mount"] = ""

    dockerfile_content = DOCKERFILE_TEMPLATE.render(**template_args)
    return dockerfile_content
