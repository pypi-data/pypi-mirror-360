import hashlib
import json
from json import JSONDecodeError
from pathlib import Path

from pycopy.logging import log, Color


def hash_file(path: Path) -> str:
    with open(path, 'rb') as file:
        hash_value = hashlib.file_digest(file, "md5")

    return hash_value.hexdigest()


class HashTracker:
    def __init__(self, relative_to: Path):
        self.relative_to = relative_to
        self.hashes = {}

    def get_hash(self, path: Path) -> str:
        try:
            return self.hashes[path]
        except KeyError:
            return None

    def update_hash(self, path: Path, other_tracker):
        self._set_hash(path, other_tracker.get_hash(path))

    def _set_hash(self, path: Path, value: str):
        self.hashes[path] = value

    def _get_combined_hash(self, paths: list) -> str:
        hash_value = hashlib.md5(usedforsecurity=False)
        for path in paths:
            new_value = self.get_hash(path.relative_to(self.relative_to))
            if new_value is None:
                raise RuntimeError("Hash could not be calculated (I apparently forgot to check some file)")
            hash_value.update(new_value.encode("ascii"))
        return hash_value.hexdigest()

    def _scan_file(self, path: Path):
        relative_path = path.relative_to(self.relative_to)

        if path.is_dir():
            subpaths = list(path.iterdir())
            for subpath in subpaths:
                self._scan_file(subpath)
            self._set_hash(relative_path, self._get_combined_hash(subpaths))
        else:
            self._set_hash(relative_path, hash_file(path))

    @classmethod
    def from_file(cls, path: Path):
        log(f"Calculating hashes for {path}")
        tracker = HashTracker(path)
        tracker._scan_file(path)
        return tracker

    @classmethod
    def from_serialized(cls, relative_to: Path, string: str):
        tracker = HashTracker(relative_to)

        try:
            hashes = json.loads(string)
        except JSONDecodeError:
            log(Color(1), "Could not open hashes file. Ignoring it", Color(None), use_color=True)
            return tracker

        for path, hash_value in hashes.items():
            tracker.hashes[Path(path)] = hash_value

        return tracker

    def serialise(self) -> str:
        hashes = {}

        for path, hash_value in self.hashes.items():
            hashes[str(path)] = hash_value

        return json.dumps(hashes, indent=4)
