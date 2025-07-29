from __future__ import annotations as _annotations
from typing import Literal as _Literal, TYPE_CHECKING as _TYPE_CHECKING
from pathlib import Path as _Path
import json as _json
import ruamel.yaml as _yaml
from ruamel.yaml import scalarstring as _yaml_scalar_string
import tomlkit as _tomlkit

if _TYPE_CHECKING:
    from typing import Callable, Any


def to_string(
    data: dict | list | str | int | float | bool | _yaml.CommentedMap | _yaml.CommentedSeq,
    data_type: _Literal["json", "yaml", "toml"],
    sort_keys: bool = False,
    indent: int | None = None,
    default: Callable[[Any], Any] | None = None,
    end_of_file_newline: bool = True,
    indent_mapping: int = 2,
    indent_sequence: int = 4,
    indent_sequence_offset: int = 2,
    multiline_string_to_block: bool = True,
    remove_top_level_indent: bool = True
):
    if data_type == "json":
        return to_json_string(data, sort_keys=sort_keys, indent=indent, default=default, end_of_file_newline=end_of_file_newline)
    if data_type == "yaml":
        return to_yaml_string(
            data,
            end_of_file_newline=end_of_file_newline,
            indent_mapping=indent_mapping,
            indent_sequence=indent_sequence,
            indent_sequence_offset=indent_sequence_offset,
            multiline_string_to_block=multiline_string_to_block,
            remove_top_level_indent=remove_top_level_indent
        )
    return to_toml_string(data, sort_keys=sort_keys, end_of_file_newline=end_of_file_newline)


def to_yaml_string(
    data: dict | list | str | int | float | bool | _yaml.CommentedMap | _yaml.CommentedSeq,
    end_of_file_newline: bool = True,
    indent_mapping: int = 2,
    indent_sequence: int = 4,
    indent_sequence_offset: int = 2,
    multiline_string_to_block: bool = True,
    remove_top_level_indent: bool = True
) -> str:
    yaml = _yaml.YAML(typ=["rt", "string"])
    yaml.indent(mapping=indent_mapping, sequence=indent_sequence, offset=indent_sequence_offset)
    if multiline_string_to_block:
        _yaml_scalar_string.walk_tree(data)
    yaml_syntax = yaml.dumps(data, add_final_eol=False).removesuffix("\n...")
    if remove_top_level_indent:
        yaml_lines = yaml_syntax.splitlines()
        count_leading_spaces = len(yaml_lines[0]) - len(yaml_lines[0].lstrip(" "))
        if count_leading_spaces:
            yaml_syntax = "\n".join(yaml_line.removeprefix(" " * count_leading_spaces) for yaml_line in yaml_lines)
    return f"{yaml_syntax}\n" if end_of_file_newline else yaml_syntax


def to_toml_string(
    data: dict | list | str | int | float | bool | _yaml.CommentedMap | _yaml.CommentedSeq,
    sort_keys: bool = False,
    end_of_file_newline: bool = True,
) -> str:
    string = _tomlkit.dumps(data, sort_keys=sort_keys)
    return f"{string.rstrip("\n")}\n" if end_of_file_newline else string


def to_json_string(
    data: dict | list | str | int | float | bool | _yaml.CommentedMap | _yaml.CommentedSeq,
    sort_keys: bool = False,
    indent: int | None = None,
    default: Callable[[Any], Any] | None = None,
    end_of_file_newline: bool = True,
) -> str:
    string = _json.dumps(data, indent=indent, sort_keys=sort_keys, default=default)
    return f"{string.rstrip("\n")}\n" if end_of_file_newline else string


def to_json_file(
    data: dict | list | str | int | float | bool | _yaml.CommentedMap | _yaml.CommentedSeq,
    path: str | _Path,
    sort_keys: bool = False,
    indent: int | None = None,
    default: Callable[[Any], Any] | None = None,
    end_of_file_newline: bool = True,
    make_dirs: bool = True,
) -> None:
    json_string = to_json_string(
        data,
        sort_keys=sort_keys,
        indent=indent,
        default=default,
        end_of_file_newline=end_of_file_newline,
    )
    path = _Path(path).resolve()
    if make_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_string)
    return


def to_yaml_file(
    data: dict | list | str | int | float | bool | _yaml.CommentedMap | _yaml.CommentedSeq,
    path: str | _Path,
    make_dirs: bool = True,
    indent_mapping: int = 2,
    indent_sequence: int = 4,
    indent_sequence_offset: int = 2,
    multiline_string_to_block: bool = True,
):
    path = _Path(path).resolve()
    if make_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    yaml = _yaml.YAML()
    yaml.indent(mapping=indent_mapping, sequence=indent_sequence, offset=indent_sequence_offset)
    if multiline_string_to_block:
        _yaml_scalar_string.walk_tree(data)
    yaml.dump(data, path)
    return
