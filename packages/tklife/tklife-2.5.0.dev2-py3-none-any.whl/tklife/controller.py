"""This module contains the ControllerABC class, which is an abstract base class for
controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from tklife.core import CreatedWidget, SkeletonMixin

T_View = TypeVar("T_View", bound="SkeletonMixin")  # pylint: disable=invalid-name
"""A type variable that is bound to a class implementing the
:class:`~tklife.core.SkeletonMixin` interface."""


class ControllerABC(Generic[T_View]):
    """Abstract base class for controllers.

    Controllers allow for access to created widgets in the view via attribute access.

    """

    view: T_View
    """The view associated with this controller."""

    def set_view(self, view: T_View) -> None:
        """Sets the view associated with this controller.

        Arguments:
            view: An instance that implements SkeletonMixin methods

        """
        self.view: T_View = view

    def __getattr__(self, attr: str) -> CreatedWidget:
        """Gets a created widget in this controller's view's created dictionary.

        Arguments:
            attr: The label of the created widget

        Returns:
            The created widget found

        """
        return self.view.created[attr]
