# -*- coding: utf-8 -*-
#
# Copyright 2021-2022, 2025 NXP
#
# SPDX-License-Identifier: MIT


import pathlib
from importlib.metadata import version


def get_package_version():
    root = pathlib.Path(__file__) / ".."
    root = root.resolve()

    return (root / "VERSION").read_text(encoding="utf-8").rstrip()


def get_runtime_version(pkg):
    """
    `fc_common` including `VERSION` maybe upgraded by other caller packages,
    so internal package version is the most reliable item,
    fallback to `VERSION` only when in docker release
    """

    try:
        version_str = version(pkg)
    except Exception:  # pylint: disable=broad-except
        version_str = get_package_version()

    return version_str
