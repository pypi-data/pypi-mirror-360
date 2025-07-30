"""YAML-related functions."""

import io
import logging
from pathlib import Path
from types import UnionType
from typing import Any, Literal, Union, get_args, get_origin

from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError

logger = logging.getLogger(__name__)


def load_yaml(file: Path) -> Any:
    """Load a yaml file and returns its contents.

    Returns an empty dictionary if the file is not found.

    Parameters
    ----------
    file : Path
        file

    Returns
    -------
    Any
        The contents of the yaml file.
    """
    yaml = YAML(typ="safe")
    try:
        with file.open() as f:
            conf = yaml.load(f)
            if conf is None:
                return {}
    except YAMLError as e:
        logger.warning("Error parsing the file '%s': %s", file, str(e))
        raise

    except FileNotFoundError as e:
        logger.warning("File '%s' was not found: %s", file, str(e))
        raise

    return conf


def generate_yaml_template(model: type[BaseModel]) -> str:  # noqa: C901
    """Generate a YAML template from a Pydantic model.

    The generated YAML will include the type and description of each argument as comments.

    Parameters
    ----------
    model : Type[BaseModel]
        The Pydantic model to generate a YAML template from.

    Returns
    -------
    str
        The YAML template as a string.

    Examples
    --------
    >>> from pathlib import Path
    >>> from pydantic import BaseModel, Field
    >>> from typing import Literal
    >>> class NestedModel(BaseModel):
    ...     testing: str = Field(..., description="Nested models...")
    ...     testing2: str = Field(..., description="... work")
    >>> class MyModel(BaseModel):
    ...     field1: str = Field(..., description="Description for field1")
    ...     field2: int = Field(..., description="Description for field2")
    ...     field3: bool = Field(True, description="Using a default value")
    ...     field4: NestedModel
    ...     field_literal: Literal["Literals", "also", "Work"] = Field(
    ...         "Literals", description="This is a literal"
    ...     )
    >>> yaml_template = generate_yaml_template(MyModel)
    >>> print(yaml_template)  # doctest: +NORMALIZE_WHITESPACE
    field1:  # [str] Description for field1
    field2: # [int] Description for field2
    field3: true # [bool] Using a default value
    field4:
        testing:  # [str] Nested models...
        testing2: # [str] ... work
    field_literal: Literals # [Literals, also, Work] This is a literal
    <BLANKLINE>
    """
    yaml = YAML()
    yaml.indent(mapping=4, sequence=4, offset=2)

    def generate_template(model: type[BaseModel]) -> CommentedMap:  # noqa: C901, PLR0912
        """Generate a template from a Pydantic model.

        Parameters
        ----------
        model : Type[BaseModel]
            The Pydantic model to generate a template from.

        Returns
        -------
        CommentedMap
            The template as a CommentedMap.
        """
        template = CommentedMap()
        for name, field in model.__annotations__.items():
            if name[0] == "_":
                continue

            origin = get_origin(field)
            if origin == Union:
                field_types = []
                for arg in get_args(field):
                    if arg.__name__ == "Literal":
                        field_types.append(", ".join(map(str, get_args(arg))))
                    else:
                        field_types.append(arg.__name__)
                field_type = " | ".join(field_types)
            elif origin == Literal:
                field_type = ", ".join(map(str, get_args(field)))
            elif origin == UnionType:
                field_type = ", ".join([arg.__name__ for arg in get_args(field)])
            elif origin is dict:
                key_type, value_type = (
                    t.__name__ if t.__name__ is not None else str(t) for t in get_args(field)
                )
                field_type = f"dict[{key_type}, {value_type}]"
            elif origin is list:
                value_type = get_args(field)[0].__name__
                field_type = f"list[{value_type}]"
            elif issubclass(field, BaseModel):
                template[name] = generate_template(field)
                continue
            else:
                field_type = model.__annotations__[name].__name__

            default_value = model.model_fields[name].default
            if default_value == PydanticUndefined:
                default_value = None

            description = model.model_fields[name].description
            template[name] = default_value

            # TODO Add a '\t' between the field value and the comment (not yet supported by ruamel)
            template.yaml_add_eol_comment(
                f"[{field_type}] {description if description else ''}",
                key=name,
            )
        return template

    template = generate_template(model)
    stream = io.StringIO()
    yaml.dump(template, stream)
    return stream.getvalue()
