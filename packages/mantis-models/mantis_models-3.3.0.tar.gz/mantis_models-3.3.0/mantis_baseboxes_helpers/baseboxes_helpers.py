# -*- coding: utf-8 -*-
import tempfile
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from ruamel.yaml import YAML


def validate_yaml_basebox_file(basebox_yaml_file_path: Path) -> None:
    """
    Validate (from a system point of view) a yaml basebox file
    :param yaml_basebox_file_path: path of the file
    :return: None
    """
    if not basebox_yaml_file_path.exists():
        raise Exception(
            "The provided YAML configuration path does not exist: '{}'".format(
                basebox_yaml_file_path
            )
        )

    if not basebox_yaml_file_path.is_file():
        raise Exception(
            "The provided YAML configuration path is not a file: '{}'".format(
                basebox_yaml_file_path
            )
        )

    try:
        with basebox_yaml_file_path.open("r"):
            pass
    except PermissionError as e:
        raise Exception(
            "The provided YAML configuration file is not readable: '{}'".format(
                basebox_yaml_file_path
            )
        ) from e


def validate_basebox_id(expected_basebox_id: str, basebox_yaml: Dict[str, Any]) -> bool:
    """
    Validate that the id of the basebox is correct, according to its path
    Only if the id is present in the yaml file
    :param basebox_subpath: subpath of the basebox (eg AMOSSYS/ubuntu/ubuntu21.04)
    :param content: content of the basebox.yaml file
    :return: True if the id is correct, False otherwise
    """
    if "id" in basebox_yaml:
        basebox_id: str = basebox_yaml["id"]
        if basebox_id != expected_basebox_id:
            raise Exception(
                f"The provided id in the YAML description file of {expected_basebox_id} is not correct"
            )
    return True


def list_baseboxes_yaml(baseboxes_path: Path) -> List[Dict[str, Any]]:
    # check that the directory exists
    if not baseboxes_path.is_dir():
        raise NotADirectoryError(
            f"The provided baseboxes path '{baseboxes_path}' does not exist or is not a folder"
        )

    baseboxes: List[Dict[str, Any]] = []
    invalid_baseboxes: List[str] = []

    # Check that each basebox has a a yaml description
    # Read the YAML file
    for basebox_yaml_file_path in baseboxes_path.rglob("basebox.yaml"):
        # Remove the basebox folder and the basebox.yaml from the path to get the basebox_id
        basebox_relpath = basebox_yaml_file_path.parent.relative_to(baseboxes_path)
        if hasattr(basebox_relpath, "abstract_path"):
            basebox_id = basebox_relpath.abstract_path[1:]  # type: ignore
        else:
            basebox_id = str(basebox_relpath)
        # Check that the file exists and we have the rights to read it
        try:
            validate_yaml_basebox_file(basebox_yaml_file_path)
        except Exception as e:
            invalid_baseboxes.append(str(e))
            continue

        # Load the contents of the file
        basebox_yaml_str = basebox_yaml_file_path.read_text()
        basebox_yaml = YAML().load(basebox_yaml_str)

        # If the id is present, verify it, otherwise add it
        if "id" not in basebox_yaml:
            basebox_yaml["id"] = basebox_id
            with tempfile.NamedTemporaryFile() as tmp:
                YAML().dump(basebox_yaml, tmp)
                tmp_path = Path(tmp.name)
                basebox_yaml_str = tmp_path.read_text()

        # Check coherence between the basebox id and its subpath
        try:
            validate_basebox_id(basebox_id, basebox_yaml)
        except Exception as e:
            invalid_baseboxes.append(str(e))

        baseboxes.append(basebox_yaml)

    if invalid_baseboxes:
        raise Exception(", ".join(invalid_baseboxes))

    return baseboxes


def list_baseboxes_img(baseboxes_path: Path) -> List[str]:
    # check that the directory exists
    if not baseboxes_path.is_dir():
        raise NotADirectoryError(
            f"The provided baseboxes path '{baseboxes_path}' does not exist or is not a folder"
        )

    baseboxes: List[str] = []

    # Check that each basebox has a .img file
    for basebox_img_file_path in baseboxes_path.rglob("basebox.img"):
        # Remove the basebox folder and the basebox.img from the path to get the basebox_id
        basebox_relpath = basebox_img_file_path.parent.relative_to(baseboxes_path)
        if hasattr(basebox_relpath, "abstract_path"):
            basebox_id = basebox_relpath.abstract_path[1:]  # type: ignore
        else:
            basebox_id = str(basebox_relpath)
        baseboxes.append(basebox_id)

    return baseboxes


def retrieve_basebox_yaml(baseboxes_path: Path, basebox_id: str) -> Dict[str, Any]:
    """Retrieve the YAML file associated with a local IMG file, if it
    exist. Those YAML files may exist for custom IMG basebox files.

    """
    # check that the directory exists
    if not baseboxes_path.is_dir():
        raise NotADirectoryError(
            f"The provided baseboxes path '{baseboxes_path}' does not exist or is not a folder"
        )

    basebox_yaml_file_path = baseboxes_path / basebox_id / "basebox.yaml"

    # Check that the file exists and we have the rights to read it
    validate_yaml_basebox_file(basebox_yaml_file_path)

    # Load the contents of the file
    basebox_yaml_str = basebox_yaml_file_path.read_text()
    basebox_yaml = YAML().load(basebox_yaml_str)

    # If the id is present, verify it, otherwise add it
    if "id" not in basebox_yaml:
        basebox_yaml["id"] = basebox_id
        with tempfile.NamedTemporaryFile() as tmp:
            YAML().dump(basebox_yaml, tmp)
            tmp_path = Path(tmp.name)
            basebox_yaml_str = tmp_path.read_text()

    # Check coherence between the basebox id and its subpath
    validate_basebox_id(basebox_id, basebox_yaml)

    return basebox_yaml
