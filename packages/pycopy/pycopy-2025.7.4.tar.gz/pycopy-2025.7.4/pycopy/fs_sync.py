import os.path as path
import shutil
from pathlib import Path

from pycopy import logging
from pycopy import terminal_formatting


def sync(src, dest, verbose=True, do_delete=False, check_metadata=True,
         advanced_output_features=True):
    """
    Sync the src and dest paths (can be files)
    :param src: The path dictating what should be at dest
    :param dest: The path that will be modified
    :param verbose: Print output when deleting files
    :param do_delete: Whether files should be deleted
    :param check_metadata: Whether to check the modification date and the file size to determine whether the file needs to be updated
    :param advanced_output_features: Whether to use ANSI color codes in the output and print the current position in the file system
    """

    src = to_path(src)
    dest = to_path(dest)

    if not verbose:
        advanced_output_features = False

    if not src.exists():
        if not do_delete: return

        if advanced_output_features:
            terminal_formatting.hide_temp()
        if verbose:
            logging.log("Deleting ", logging.Color(1), dest, use_color=advanced_output_features)
        delete_path(dest)
        return

    if src.is_dir():
        if advanced_output_features:
            terminal_formatting.print_temp(src)

        if dest.exists() and not dest.is_dir():
            if not do_delete:
                return

            if advanced_output_features:
                terminal_formatting.hide_temp()

            if verbose:
                logging.log("Deleting ", logging.Color(1), dest, use_color=advanced_output_features)
            delete_path(dest)

        dest.mkdir(parents=True, exist_ok=True)

        kwargs = {
            "verbose": verbose,
            "do_delete": do_delete,
            "check_metadata": check_metadata,
            "advanced_output_features": advanced_output_features
        }

        if do_delete:
            for item in dest.iterdir():
                sub_path = item.relative_to(dest)
                sync(src / sub_path, dest / sub_path, **kwargs)

        for item in src.iterdir():
            sub_path = item.relative_to(src)
            sync(src / sub_path, dest / sub_path, **kwargs)

        if advanced_output_features:
            terminal_formatting.hide_temp()
        return

    if advanced_output_features:
        terminal_formatting.print_temp(src)

    if not check_metadata:
        if dest.is_dir():
            if advanced_output_features:
                terminal_formatting.hide_temp()

            if verbose:
                logging.log("Deleting ", logging.Color(1), dest)
            delete_path(dest)

        copy_file(src, dest)

        return

    if not dest.exists():
        dest_mod = -1
        dest_size = -1
    elif dest.is_dir():
        if advanced_output_features:
            terminal_formatting.hide_temp()

        if verbose:
            logging.log("Deleting ", logging.Color(1), dest)
        delete_path(dest)
        dest_mod = -1
        dest_size = -1
    else:
        dest_mod = path.getmtime(dest)
        dest_size = path.getsize(dest)

    src_mod = path.getmtime(src)
    src_size = path.getsize(src)

    if src_mod <= dest_mod and src_size == dest_size:
        return

    copy_file(src, dest)


def copy_file(src: Path, dest: Path):
    """
    This method exists to delete files if they might be copied over.
    This MIGHT help with certain mounted file systems being buggy
    """
    dest.unlink(missing_ok=True)
    shutil.copyfile(src, dest)


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


def to_path(file):
    if isinstance(file, Path):
        return file

    return Path(file)
