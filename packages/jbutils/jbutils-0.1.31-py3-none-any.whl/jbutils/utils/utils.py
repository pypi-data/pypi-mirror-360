"""Collection of common utils functions for personal repeated use"""

import argparse
import csv
import json
import io
import os
import re
import shlex
import subprocess
import sys
import traceback
import fnmatch

from pathlib import Path
from platform import platform

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from jbutils.types import CommandArg, T, Patterns, DataPath, DataPathList, SubReturn

yaml = YAML()
yaml.indent = 2

Predicate = Callable[[T], bool]


class Consts:
    encoding: str = "UTF-8"


# pylint: disable=C0103
@dataclass
class SubReturns:
    """Enum class for SubReturn values"""

    OUT: SubReturn = "out"
    ERR: SubReturn = "err"
    BOTH: SubReturn = "both"


# pylint: enable=C0103


def set_encoding(enc: str) -> None:
    Consts.encoding = enc


def set_yaml_indent(indent: int) -> None:
    yaml.indent = 2


def read_file(
    path: str,
    mode: str = "r",
    encoding: str | None = Consts.encoding,
    as_lines: bool = False,
    default_val: Any = None,
    as_dicts: bool = False,
) -> str | dict | list:
    """Read data from a file

    Args:
        path (str): The path to the file
        mode (str, optional): IO mode to use. Defaults to "r".
        encoding (str, optional): Encoding format to use.
            Defaults to "latin-1".
        as_lines (bool, optional): If reading a regular text file,
            True will return the value of readlines() instead of read().
            Defaults to False.
        default_val (Any, optional): Value to return if the file is not found.
            Defaults to None.

    Returns:
        str | dict | list: The data read from the file. If the file is
            not found, returns an empty dict
    """

    default_val = default_val or {}

    if not os.path.exists(path):
        print(f"Warning: Path '{path}' does not exist")
        return default_val

    _, ext = os.path.splitext(path)

    with open(path, mode, encoding=encoding) as fs:
        match ext.lower():
            case ".yaml" | ".yml":
                return yaml.load(stream=fs)
            case ".json":
                return json.load(fs)
            case ".csv":
                data = list(csv.reader(fs))
                if as_dicts:
                    if not data:
                        return []

                    cols = data.pop(0)

                    if not data:
                        return []

                    return [dict(zip(cols, vals)) for vals in data]
                return data
            case _:
                if as_lines:
                    return fs.readlines()
                else:
                    return fs.read()


def write_file(
    path: str,
    data: Any,
    mode: str = "w",
    encoding: str | None = Consts.encoding,
    indent: int = 4,
) -> None:
    """Write text to a file

    Args:
        path (str): The path to the file
        data (Any): The data to write
        mode (str, optional): Read/write mode. Defaults to "w".
        encoding (str, optional): Encoding to write with. Defaults to ENCODING.
        indent (int, optional): Indent to apply if JSON. Defaults to 4.
        sort_keys (bool, optional): Whether to sort the output keys for YAML.
            Defaults to False.
    """

    _, ext = os.path.splitext(path)

    with open(path, mode, encoding=encoding) as fs:
        match ext.lower():
            case ".yml" | ".yaml":
                yaml.dump(data, fs)
            case ".json":
                json.dump(data, fs, indent=indent)
            case _:
                if isinstance(data, list):
                    fs.writelines(data)
                else:
                    fs.write(str(data))


def get_ext(path: str) -> str:
    """Get the file extension from a path

    Args:
        path (str): The path to the file

    Returns:
        str: The file extension including the dot, or an empty string if no extension exists
    """

    return os.path.splitext(path)[1]


def replace_ext(path: str, ext: str) -> str:
    """Replace the file extension in a path with a new one
    Args:
        path (str): The path to the file
        ext (str): The new file extension, including the dot
    Returns:
        str: The path with the new file extension
    """

    return os.path.splitext(path)[0] + ext


def strip_ext(path: str) -> str:
    """Get the file name without the extension from a path

    Args:
        path (str): The path to the file

    Returns:
        str: The file name without the extension, or an empty string if no name exists
    """

    return os.path.splitext(os.path.basename(path))[0]


def get_os_sep() -> str:
    if platform() == "Windows":
        return "\\"
    else:
        return "/"


def split_path(path: str, keep_ext: bool = True) -> list[str]:
    path_split = []
    head, tail = os.path.split(path)
    if not tail:
        return [head.replace(get_os_sep(), "")]

    if not keep_ext:
        tail = strip_ext(tail)

    path_split.append(tail)
    max_depth = 32
    count = 0
    while tail and count < max_depth:
        head, tail = os.path.split(head)
        if tail:
            path_split.insert(0, tail)
        count += 1
    return path_split


def find(items: list, value: Any) -> int:
    """A 'not in list' safe version of list.index()

    Args:
        items (list): List to search
        value (Any): Value to search for

    Returns:
        int: Index of the first instance of value, or -1 if not found
    """

    try:
        return items.index(value)
    except ValueError:
        return -1


def update_list_values(
    items: list[Any],
    new_items: list[Any],
    sort: bool = False,
    sort_func: Optional[Predicate[Any]] = None,
    reverse: bool = False,
) -> list[Any]:
    """Add new items to a list and sort it

    Args:
        items (list[Any]): Items to add to
        new_items (list[Any]): Items to add
        sort (Callable[[Any], bool], optional): Custom sort function. Defaults to None.
        reverse (bool, optional): If true, sort order is reversed. Defaults to False.

    Returns:
        list[Any]: The updated list
    """

    for item in new_items:
        if item not in items:
            items.append(item)

    if sort:
        if sort_func:
            items.sort(key=sort_func, reverse=reverse)
        else:
            items.sort(reverse=reverse)

    return items


def remove_list_values(
    items: list[Any],
    del_items: list[Any],
    sort: bool = False,
    sort_func: Optional[Predicate[Any]] = None,
    reverse: bool = False,
) -> list[Any]:
    """Remove items from a list and sort it

    Args:
        items (list[Any]): Items to remove from
        del_items (list[Any]): Items to remove
        sort (Callable[[Any], bool], optional): Custom sort function. Defaults to None.
        reverse (bool, optional): If true, sort order is reversed. Defaults to False.

    Returns:
        list[Any]: The updated list
    """

    for item in del_items:
        if item in items:
            items.remove(item)
    if sort:
        if sort_func:
            items.sort(key=sort_func, reverse=reverse)
        else:
            items.sort(reverse=reverse)

    return items


def print_stack_trace():
    # Get the current stack frame
    stack = traceback.format_stack()

    print("\n".join(stack[:-2]))


def debug_print(*args):
    """Print debug statements with a newline before and after"""

    strings = list(args)
    strings.insert(0, "\n")
    strings.append("\n")
    print(*strings)


def pretty_print(obj: Any) -> None:
    """Prints a JSON serializable object with indentation"""

    print(json.dumps(obj, indent=4))


def copy_to_clipboard(text):
    process = subprocess.Popen(
        ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE
    )
    process.communicate(input=text.encode("utf-8"))


def dedupe_list(items: list) -> list:
    new_list = []
    for item in items:
        if item not in new_list:
            new_list.append(item)
    return new_list


def dedupe_in_place(items: list) -> list:
    uniques = []
    dupes = []

    for item in items:
        if item not in uniques:
            uniques.append(item)
        else:
            dupes.append(item)

    for item in dupes:
        items.remove(item)

    return dupes


def get_keys(obj: dict, keys: Optional[list[str]] = None) -> Any:
    if not isinstance(obj, dict):
        return keys

    keys = keys or []
    keys.extend(obj.keys())
    for value in obj.values():
        get_keys(value, keys)

    return keys


def parse_cfg_key(key: list[str] | str, trim_exts: bool = True) -> list[str]:
    if isinstance(key, str):
        key = key.split(".")
        if not trim_exts:
            if len(key) >= 2:
                ext = key.pop()
                fname = key.pop()
                key.append(f"{fname}{ext}")

    return key


def parse_data_path(
    key: DataPath, sep: str = ".", split_exts: bool = True
) -> DataPathList:

    if isinstance(key, int):
        return [key]
    if isinstance(key, str):
        key = key.split(sep)
        if not split_exts and len(key) >= 2:
            ext = key.pop()
            fname = key.pop()
            key.append(f"{fname}.{ext}")
    return key


def parse_int(value: Any) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


IDX_RE = re.compile(r"\[\s*(-?\d+)\s*\]")


def is_idx_key(key_part: str | int) -> bool:
    if isinstance(key_part, int):
        return False
    return IDX_RE.search(key_part) is not None or key_part == "+"


def get_idx_key(key_part: str | int) -> str | int:
    key_part = str(key_part)
    matches = IDX_RE.findall(key_part)
    if matches:
        key_part = int(matches[0])

    return key_part


def get_nested(
    obj: dict | list, path: DataPath, default: Any = None, sep: str = "."
) -> Any:
    """Get a nested value from a dictionary or list

    Args:
        obj (dict | list): The object to get the value from
        path (list[str] | str): The path to the value
        default (Any, optional): The default value to return if the path is not found.
            Defaults to None.
        sep (str, optional): Separator to split string with if path is str.
            Defaults to "."

    Returns:
        Any: The value at the path or the default value
    """

    """ if isinstance(path, str):
        path = path.split(sep) """
    path = parse_data_path(path, sep)

    if not path:
        return default

    if len(path) == 1:
        result = None
        key = get_idx_key(path[0])
        is_int = isinstance(key, int)
        if isinstance(obj, dict):
            result = obj.get(str(key), obj.get(key, default))

        elif isinstance(obj, list) and is_int:
            item = None
            if key < len(obj):
                item = obj[key]
            if item is None:
                item = default

            result = item
        return result

    next_key = get_idx_key(path.pop(0))

    if isinstance(obj, list):
        if obj and isinstance(next_key, int):
            if next_key < len(obj):
                return get_nested(obj[next_key], path, default)
        return default

    if str(next_key) not in obj and next_key not in obj:
        return default

    return get_nested(obj[next_key], path, default)


def delete_nested(obj: dict | list, path: DataPath, sep: str = ".") -> None:
    """Delete a nested value from a dictionary or list

    Args:
        obj (dict | list): The object to delete the value from
        path (list[str] | str): The path to the value
        sep (str, optional): Separator to split string with if path is str.
            Defaults to "."
    """

    """ if isinstance(path, str):
        path = path.split(sep) """
    path = parse_data_path(path, sep)

    if not path:
        return

    if len(path) == 1:
        debug_print(obj)

        key = get_idx_key(path[0])

        if isinstance(obj, (dict, CommentedMap)):
            obj.pop(key, None)
        elif isinstance(obj, (list, CommentedSeq)):
            if obj and isinstance(key, int):
                if key < len(obj):
                    obj.pop(key)
            """ elif path[0] in obj:
                debug_print("removing", path[0])
                obj.remove(path[0]) """
    else:
        next_key = get_idx_key(path.pop(0))
        if isinstance(obj, list):
            if isinstance(next_key, int):
                if next_key < len(obj):
                    delete_nested(obj[next_key], path)
        elif next_key in obj or str(next_key) in obj:
            delete_nested(obj[next_key], path)


def _set_next_append(
    obj: list,
    path: DataPathList,
    value: Any,
    debug: bool = False,
    overwrite: bool = False,
) -> None:
    """Set a value in a nested object when the index is out of bounds

    Args:
        obj (list): Object to set the value in
        path (list[str]): Path to the value
        key (str | int): Key to set the value at
        value (Any): Value to set
        debug (bool, optional): Flag to enable debug statements. Defaults to False.
        overwrite (bool, optional): Flag to overwite existing data along path.
            Defaults to False.
    """
    if debug:
        debug_print("out of bounds", "inserting new value", f"path[0] = {path[0]}")

    new_val = [] if is_idx_key(path[0]) else {}
    obj.append(new_val)

    if debug:
        debug_print("blank inserted", obj)

    set_nested(
        obj=obj[-1], path=path, value=value, debug=debug, overwrite=overwrite
    )


def _set_next_list_item(
    obj: list,
    path: DataPathList,
    key: int,
    value: Any,
    debug: bool = False,
    overwrite: bool = False,
) -> None:
    """Iterate through the next item in a list or dictionary

    Args:
        obj (list): Object to set the value in
        path (list[str]): Path to the value
        key (str | int): Key to set the value at
        value (Any): Value to set
        debug (bool, optional): Flag to enable debug statements. Defaults to False.
        overwrite (bool, optional): Flag to overwite existing data along path.
            Defaults to False.
    """

    if not path:
        return

    sub = obj[key]

    if not sub or not isinstance(sub, (dict, list)):
        if debug:
            debug_print("sub is None or not an object", "creating new sub")
        if overwrite:
            if is_idx_key(path[0]):
                obj[int(key)] = []
            else:
                obj[int(key)] = {}
        else:
            return

    set_nested(
        obj=obj[key],
        path=path,
        value=value,
        debug=debug,
        overwrite=overwrite,
    )


def _set_final_prop(obj: dict | list, path: DataPathList, value: Any) -> None:
    """Set a value in a nested object at the final path

    Args:
        obj (dict | list): Object to set the value in
        path (list[str]): Path to the value
        value (Any): Value to set
    """

    key = get_idx_key(path[0])

    if isinstance(obj, dict):
        obj[key] = value
    elif isinstance(obj, list):
        if isinstance(key, int) and key < len(obj):
            obj[key] = value
        else:
            obj.append(value)


def _set_next_nested(
    obj: dict,
    path: DataPathList,
    value: Any,
    key: str | int,
    debug: bool = False,
    overwrite: bool = False,
) -> None:
    """Set a value in a nested object

    Args:
        obj (dict | list): Object to set the value in
        path (list[str]): Path to the value
        value (Any): Value to set
        key (str | int): Key to set the value at
        debug (bool, optional): Flag to enable debug statements. Defaults to False.
        overwrite (bool, optional): Flag to overwite existing data along path.
            Defaults to False.
    """

    sub = obj.get(key)

    if debug:
        debug_print("obj is dict", "sub:", sub)

    if not sub or not isinstance(sub, (dict, list)):
        if debug:
            debug_print("sub is None or not an object", "creating new sub")

        if is_idx_key(path[0]):  # and create_lists:
            obj[key] = []
        else:
            obj[key] = {}

        if debug:
            debug_print("new sub created", obj)

    prop = obj.get(key)
    if isinstance(prop, (list | dict)):
        set_nested(
            obj=prop,
            path=path,
            value=value,
            debug=debug,
            overwrite=overwrite,
        )


def set_nested(
    obj: dict | list,
    path: DataPath,
    value: Any,
    debug: bool = False,
    overwrite: bool = False,
    sep: str = ".",
) -> None:
    """Set a nested value in a dictionary or list

    Args:
        obj (dict | list): The object to set the value in
        path (list[str] | str): The path to the value
        value (Any): The value to set
        debug (bool, optional): Flag to enable debug statements. Defaults to False.
        overwrite (bool, optional): Flag to overwite existing data along path.
            Defaults to False.
    """

    path = parse_data_path(path, sep)

    if debug:
        print_stack_trace()
        debug_print("starting function")
        pretty_print({"obj": obj, "path": path, "value": value})

    if not path:
        return

    if len(path) == 1:
        _set_final_prop(obj, path, value)
    else:
        key = get_idx_key(path.pop(0))

        if debug:
            debug_print("key", key)

        if isinstance(obj, list):
            if debug:
                debug_print("obj is list", "key < len", int(key) < len(obj))
            if obj and isinstance(key, int) and key < len(obj):
                _set_next_list_item(
                    obj=obj,
                    path=path,
                    key=key,
                    value=value,
                    debug=debug,
                    overwrite=overwrite,
                )
            elif isinstance(key, int) or key == "+":
                _set_next_append(
                    obj=obj,
                    path=path,
                    value=value,
                    debug=debug,
                    overwrite=overwrite,
                )
        elif isinstance(obj, dict):
            _set_next_nested(
                obj=obj,
                path=path,
                value=value,
                key=key,
                debug=debug,
                overwrite=overwrite,
            )


def cmdx(
    cmd: list[str] | str, rtrn: SubReturn = "out", print_out: bool = True
) -> str | tuple[str, str]:
    """Executes a command and returns the output or error

    Args:
        cmd (list[str] | str): - A list of strings that make up the command or a string
            that will be split by spaces
        rtrn (SubReturn, optional): What outputs to return. If both, it will return a
            tuple of (stdout, stderr)Defaults to 'out'.

    Returns:
        str | tuple[str, str]: The output of the command or a tuple of (stdout, stderr)
    """

    if isinstance(cmd, str):
        cmd = shlex.split(cmd)

    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            check=True,
        )
    except subprocess.CalledProcessError as e:
        # Print and handle the errors here if needed
        process = e

    stdout = process.stdout
    stderr = process.stderr
    if print_out:
        if stdout:
            print(stdout)
        if stderr:
            print("\nERROR:\n", stderr)

    if rtrn == "out":
        return process.stdout
    if rtrn == "err":
        return process.stderr

    return process.stdout, process.stderr


def join_paths(root: str, paths: list[str]) -> list[str]:
    """Join each path in paths with the root str

    Args:
        root (str): Directory root path
        paths (list[str]): list of paths to join with root

    Returns:
        list[str]: List of os.path.join(root, path) for all paths
    """

    return [os.path.join(root, path) for path in paths]


def list_paths(path: str, *predicates: Predicate[str]) -> list[str]:
    """Extension of os.listdir(path) that allows you to pre-filter the
        results with a list of predicate functions

    Args:
        path (str): Path to inspect
        predicates ([list[Predicate[str]]  |  Predicate[str]], optional):
            A function or list of functions used to filter the returned
            path names. Defaults to [].

    Returns:
        list[str]: List of files/directories at the location that pass
            all predicates, returns [] if path is invalid
    """

    if not os.path.exists(path) or not os.path.isdir(path):
        return []

    fnames = os.listdir(path)
    fullpaths = join_paths(path, fnames)
    match_paths: list[str] = []
    for i, fpath in enumerate(fullpaths):
        if all(predicate(fpath) for predicate in predicates):
            match_paths.append(fnames[i])
    return match_paths


def rm_dirs(
    dir_path: str | Path,
    ignored: Patterns | None = None,
    use_glob: bool = True,
) -> None:
    """
    Deletes all contents of a directory, optionally ignoring files or directories
    matching any of the given patterns.

    Args:
        dir_path (str): The path to the directory whose contents will be
            deleted.
        ignored (Patterns, optional): A list of glob patterns or compiled
            regexes to skip. Defaults to []
        use_glob (bool, optional): If True, treat patterns as glob-style
            strings. If False, treat them as regex. Defaults to True
    """
    dir_path = Path(dir_path)
    ignored = ignored or []

    def should_ignore(path: Path) -> bool:
        rel_path = str(path.relative_to(dir_path))
        for pattern in ignored:
            if isinstance(pattern, str) and use_glob:
                if fnmatch.fnmatch(rel_path, pattern):
                    return True
            elif isinstance(pattern, re.Pattern):
                if pattern.search(rel_path):
                    return True
        return False

    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            full_path = Path(root) / name
            if not should_ignore(full_path):
                full_path.unlink()
        for name in dirs:
            full_path = Path(root) / name
            if not should_ignore(full_path):
                try:
                    full_path.rmdir()  # only removes if empty
                except OSError:
                    pass  # ignore non-empty directories


def get_local_funcs(tgt_cls: type, *base_classes: type) -> list[str]:
    """Get all local functions of a class that are not inherited from its
        base classes. This function retrieves all callable attributes of
        the target class that do not start with an underscore and are not
        present in the base classes.

    Args:
        tgt_cls (type): The target class from which to retrieve functions.
        *base_classes (type): Base classes to exclude inherited functions from.

    Returns:
        list[str]: A list of function names that are defined in the target class
            and not inherited from the base classes.
    """

    base_funcs = set()

    for base_cls in base_classes:
        base_funcs.update(
            [
                name
                for name in dir(base_cls)
                if callable(getattr(base_cls, name)) and not name.startswith("_")
            ]
        )

    return [
        name
        for name in dir(tgt_cls)
        if callable(getattr(tgt_cls, name))
        and not name.startswith("_")
        and name not in base_funcs
    ]


def parse_csv_line(csv_str: str) -> list[str]:
    """Parses a single-line CSV string into a list of strings using ISO-like rules."""
    reader = csv.reader(io.StringIO(csv_str))
    return next(reader)


def to_csv_line(items: list[str]) -> str:
    """Serializes a list of strings into a single CSV-formatted string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(items)
    return output.getvalue().strip("\r\n")


def add_common_args(
    parser: argparse.ArgumentParser,
    proj_path: str,
    overrides: dict[str, CommandArg] | None = None,
) -> Callable[...]:
    overrides = overrides or {}

    cmd_args: list[CommandArg] = [
        overrides.get(
            "code",
            CommandArg(
                "--code",
                "-c",
                "store_true",
                help="Open the source file for this tool in VS Code",
            ),
        ),
        overrides.get(
            "cd",
            CommandArg(
                "--cd",
                "-C",
                "store_true",
                help="Copy a cd command to the project directory to the clipboard",
            ),
        ),
    ]

    for arg in cmd_args:

        parser.add_argument(*arg.name_or_flags, action=arg.action, help=arg.help)

    def handle_common() -> None:
        code, cd = cmd_args
        args = vars(parser.parse_args())
        if args.get(code.arg_name):
            cmdx(f"code {proj_path}")
            sys.exit(0)
        if args.get(cd.arg_name):
            path = os.path.dirname(proj_path)
            copy_to_clipboard(f"cd {path}")
            sys.exit(0)

    return handle_common
