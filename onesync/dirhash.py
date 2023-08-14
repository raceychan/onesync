import re
import os
import hashlib
from pathlib import Path

EMPTY_HASH: str = hashlib.md5().hexdigest()


def _reduce_hash(hashlist: list[str]):
    hasher = hashlib.md5()
    for hashvalue in sorted(hashlist):
        hasher.update(hashvalue.encode("utf-8"))
    return hasher.hexdigest()


def filehash(filepath: Path):
    hasher = hashlib.md5()
    blocksize = 64 * 1024  # 64kb

    if not filepath.exists():
        return EMPTY_HASH

    with open(filepath, "rb") as fp:
        while True:
            data = fp.read(blocksize)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def dirhash(
    dirname: Path,
    *,
    excluded_files: list[str] = [],
    excluded_extensions: list[str] = [],
    ignore_hidden: bool = False,
    followlinks: bool = False,
    include_paths: bool = False,
):
    hashvalues = []
    for root, dirs, files in os.walk(dirname, topdown=True, followlinks=followlinks):
        if ignore_hidden and re.search(r"/\.", root):
            continue

        dirs.sort()
        files.sort()

        for fname in files:
            if ignore_hidden and fname.startswith("."):
                continue

            if fname.split(".")[-1:][0] in excluded_extensions:
                continue

            if fname in excluded_files:
                continue

            fpath = Path(os.path.join(root, fname))
            hash_list = filehash(fpath)

            hashvalues.append(hash_list)

            if include_paths:
                # NOTE: this calculates the name of files, not just the contents
                hasher = hashlib.md5()
                # get the resulting relative path into array of elements
                path_list = os.path.relpath(os.path.join(root, fname)).split(os.sep)
                # compute the hash on joined list, removes all os specific separators
                hasher.update("".join(path_list).encode("utf-8"))
                hashvalues.append(hasher.hexdigest())

    return _reduce_hash(hashvalues)


def md5sum(path: Path):
    return dirhash(path) if path.is_dir() else filehash(path)