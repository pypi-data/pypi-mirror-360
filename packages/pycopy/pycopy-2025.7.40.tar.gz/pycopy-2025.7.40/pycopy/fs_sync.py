import os.path
import shutil
import time
from pathlib import Path

from pycopy import logging
from pycopy import terminal_formatting
from pycopy.hashing import HashTracker


class Syncer:
    def __init__(self, src: Path, dst: Path, verbose, do_delete, check_metadata,
                 advanced_output_features, use_hash: bool):
        if not verbose:
            advanced_output_features = False

        self.src = src
        self.dst = dst
        self.use_hashes = use_hash
        self.advanced_output_features = advanced_output_features
        self.check_metadata = check_metadata
        self.do_delete = do_delete
        self.verbose = verbose
        self.force = (not check_metadata) and (not use_hash)
        self.last_autosave_time = time.time()

        if use_hash:
            self.hash_file = dst / ".hashes.json"
            self.src_hashes = HashTracker.from_file(src)
            if self.hash_file.exists():
                self.dst_hashes = HashTracker.from_serialized(dst, self.hash_file.read_text())
                logging.log(f"Reading hashes from {self.hash_file}")
            else:
                self.dst_hashes = HashTracker(dst)
                self.hash_file.write_text(self.dst_hashes.serialise())
                logging.log(f"Creating empty hashes file at {self.hash_file}")

    def _check_wrong_file_type(self, dst: Path, should_be_dir: bool) -> bool:
        if dst.exists() and (dst.is_dir() != should_be_dir):
            if not self.do_delete:
                return True

            if self.is_protected(dst):
                return False

            if self.advanced_output_features:
                terminal_formatting.hide_temp()

            if self.verbose:
                logging.log("Deleting ", logging.Color(1), dst, use_color=self.advanced_output_features)
            self.delete_path(dst)

        return False

    def visit_dir(self, path: Path):
        if self.use_hashes:
            if not self.check_hashes(path):
                return

        src = self.src / path
        dst = self.dst / path

        if self._check_wrong_file_type(dst, True):
            return

        dst.mkdir(parents=True, exist_ok=True)

        if self.do_delete:
            for item in os.listdir(dst):
                self.visit(path / item)

        for item in os.listdir(src):
            self.visit(path / item)

        self.update_hashes(path)

    def update_hashes(self, path: Path):
        if self.use_hashes:
            self.dst_hashes.update_hash(path, self.src_hashes)

    def check_hashes(self, path: Path) -> bool:
        return (self.src_hashes.get_hash(path)
                != self.dst_hashes.get_hash(path))

    def should_copy(self, path: Path) -> bool:
        src = self.src / path
        dst = self.dst / path

        if not dst.exists():
            return True

        if self.use_hashes:
            if self.check_hashes(path):
                return True

        if self.check_metadata:
            if os.path.getsize(src) != os.path.getsize(dst):
                return True
            if os.path.getmtime(src) > os.path.getmtime(dst):
                return True

        return self.force

    def autosave_hashes(self, force=False):
        if not self.use_hashes:
            return
        if not (force or time.time() - self.last_autosave_time >= 2):
            return

        self.last_autosave_time = time.time()

        terminal_formatting.print_temp(f"Saving hashes to {self.hash_file}")
        self.hash_file.write_text(self.dst_hashes.serialise())

    def visit_file(self, path: Path):
        src = self.src / path
        dst = self.dst / path

        if self._check_wrong_file_type(dst, False):
            return

        if self.should_copy(path):
            self.copy_file(src, dst)
            self.update_hashes(path)

    def visit(self, path: Path):
        self.autosave_hashes()

        src = self.src / path

        if not src.exists():
            if not self.do_delete: return

            dst = self.dst / path
            if self.is_protected(dst):
                return

            if self.advanced_output_features:
                terminal_formatting.hide_temp()
            if self.verbose:
                logging.log("Deleting ", logging.Color(1), dst, use_color=self.advanced_output_features)
            self.delete_path(dst)
            return

        if self.advanced_output_features:
            terminal_formatting.print_temp(src)

        if src.is_dir():
            self.visit_dir(path)
        else:
            self.visit_file(path)

        if self.advanced_output_features:
            terminal_formatting.hide_temp()

    def is_protected(self, path: Path):
        return not self.use_hashes or path == self.hash_file

    @staticmethod
    def copy_file(src: Path, dest: Path):
        """
        This method exists to delete files if they might be copied over.
        This MIGHT help with certain mounted file systems being buggy
        """
        dest.unlink(missing_ok=True)
        shutil.copyfile(src, dest)

    @staticmethod
    def delete_path(file: Path):
        """
        Deletes this file if path is a folder or the folder and all subdirectories
        """
        if not file.exists():
            return

        if file.is_dir():
            for item in file.iterdir():
                delete_path(item)
            file.rmdir()
            return

        file.unlink(missing_ok=True)

    def finish(self):
        self.autosave_hashes(force=True)
        terminal_formatting.hide_temp()


def sync(src, dest, verbose=True, do_delete=False, check_metadata=True,
         advanced_output_features=True, use_hash: bool = False):
    """
    Sync the src and dest paths (can be files)
    :param src: The path dictating what should be at dest
    :param dest: The path that will be modified
    :param verbose: Print output when deleting files
    :param do_delete: Whether files should be deleted
    :param check_metadata: Whether to check the modification date and the file size to determine whether the file needs to be updated
    :param advanced_output_features: Whether to use ANSI color codes in the output and print the current position in the file system
    :param use_hash: Whether to store the hashes of the copied files in a small file in the destination
    """

    syncer = Syncer(Path(src), Path(dest), verbose, do_delete, check_metadata, advanced_output_features, use_hash)
    syncer.visit(Path("."))
    syncer.finish()
