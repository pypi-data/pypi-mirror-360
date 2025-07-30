from __future__ import annotations

import os

from pathlib import Path

home = str(Path.home())
s1_cns_dir = f"{home}/.s1cns"
s1_cns_file = f"{s1_cns_dir}/credentials"


def persist_key(key: str) -> None:
    if not os.path.exists(s1_cns_dir):
        os.makedirs(s1_cns_dir)
    with open(s1_cns_file, "w") as f:
        f.write(key)


def read_key() -> str | None:
    key = None
    if os.path.exists(s1_cns_file):
        with open(s1_cns_file, "r") as f:
            key = f.readline()
    return key
