#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron

"""Git utility functions to clone model repositories."""

from dataclasses import dataclass


@dataclass
class Repository:
    """Remote git repository.

    Attributes:
        cache_path: Path to clone the repository to in the local cache.
        commit: Commit ID or tag to checkout after cloning.
        url: URL to the remote git repository.
    """

    cache_path: str
    commit: str
    url: str


REPOSITORIES: dict[str, Repository] = {
    "fourier_grx_descriptions_cn": Repository(
        url="https://gitee.com/FourierIntelligence/wiki-grx-models.git",
        commit="57d720db14d62524e50d8abf7919ab07e0123f08",
        cache_path="fourier_grx_descriptions",
    ),
    "fourier_grx_descriptions": Repository(
        url="https://github.com/FFTAI/Wiki-GRx-Models.git",
        commit="57d720db14d62524e50d8abf7919ab07e0123f08",
        cache_path="fourier_grx_descriptions",
    ),
    "fourier_grx_descriptions_private": Repository(
        url="https://gitee.com/FourierIntelligence/Fourier_Models.git",
        commit="6d944d86940317a9a1b48f4d5ef238fbde6d402f",
        cache_path="fourier_grx_descriptions_private",
    ),
}
