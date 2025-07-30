#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /// script
# dependencies = [
#   "requests",
# ]
# ///

"""
Script for outputting athe PYPI token, compare
<https://stefan.sofa-rockers.org/2024/11/14/gitlab-trusted-publisher/>
but eliminating the need for curl in the container image

Run using "uv run tools/ci_get_pypi_token.py"
"""

import os

import requests


if __name__ == "__main__":
    response = requests.post(
        os.environ.get("PYPI_OIDC_URL"),
        json={"token": os.environ.get("PYPI_ID_TOKEN")},
        timeout=10,
    )
    print(response.json()["token"])
