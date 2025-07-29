

from typing import Optional

import os
import tarfile


def load_from_package(basedir: str, package: str, version: str,
                      resourcepath: str) -> Optional[bytes]:
    srcpath = f"{basedir}/{package}-{version}.tgz"
    if not os.path.exists(srcpath):
        return None  # scriptkiddie noise
    try:
        return load_from_tarball(srcpath, f"package/{resourcepath}")
    except KeyError:
        return None  # file not in archive


def load_from_tarball(tarball: str, path: str) -> bytes:
    with tarfile.open(tarball, "r:gz") as archive:
        src = archive.extractfile(path)
        assert src is not None
        return src.read()


def guess_mime_type(path: str) -> str:
    if path.endswith(".js"):
        return "text/javascript"
    if path.endswith(".css"):
        return "text/css"  # firefox won't load without this set
    return "text/html"  # is there a better default?!?
