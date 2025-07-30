"""This module contains ``TypeVar`` definitions used throughout the TkLife project."""

import typing

if typing.TYPE_CHECKING:
    from tklife.controller import ControllerABC


T_Controller = typing.TypeVar(  # pylint: disable=invalid-name
    "T_Controller", bound="ControllerABC | None"
)
"""A type variable that is bound to a class implementing the
:class:`~tklife.controller.ControllerABC` interface."""
