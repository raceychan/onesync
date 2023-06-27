import hashlib
import pytest
from pathlib import Path
from onesync.dirhash import _reduce_hash, filehash, dirhash

EMPTY_HASH = "empty_hash"


def test_reduce_hash():
    hashlist = ["abc", "def", "ghi"]
    expected_result = hashlib.md5("abcdefghi".encode("utf-8")).hexdigest()
    result = _reduce_hash(hashlist)
    assert result == expected_result


# @pytest.fixture
# def tmp_path(tmp_path: Path):
#     f = tmp_path / "text_file.txt"
#     f.write_text("This is a test file.")
#     return f


def test_filehash(tmp_path: Path):
    f = tmp_path / "text_file.txt"
    f.write_text("This is a test file.")
    expected_result = hashlib.md5("This is a test file.".encode("utf-8")).hexdigest()
    result = filehash(f)
    assert result == expected_result


def test_dirhash(tmp_path: Path):
    fs = []
    for i in range(1, 4):
        f_cont = f"File {i} content"
        f = tmp_path / f"file{i}.txt"
        f.write_text(f_cont)
        fs.append(f)

    excluded_files = ["file3.txt"]
    excluded_extensions = ["png"]
    include_paths = False

    hashs = [filehash(f) for f in fs[:-1]]

    expected_result = _reduce_hash(hashs)
    # NOTE: this expected_result is incorrect

    result = dirhash(
        tmp_path,
        excluded_files=excluded_files,
        excluded_extensions=excluded_extensions,
        include_paths=include_paths,
    )

    assert result == expected_result
