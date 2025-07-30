"""Menu functionality for ``tkinter.Tk`` and ``tkinter.Toplevel`` widgets that are used
with the ``tklife.skel.SkeletonMixin``."""

from __future__ import annotations

import tkinter
from functools import partial
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from typing import Any, Optional


MenuCommand = Callable[[tkinter.Menu], None]


class MenuMixin:
    """Mixin to allow for a menu to be configured.

    Must appear after SkeletonMixin, but before the tkinter Widget. Must implement the
    menu_template() property method.

    """

    def __init__(self, master: Optional[tkinter.Misc] = None, **kwargs: Any) -> None:
        # Init the frame or the menu mixin... or not
        super().__init__(master, **kwargs)  # type: ignore
        self._create_menu()

    @property
    def menu_template(self) -> dict:
        """Returns a dict that is used to create the menu. **Must be declared as
        @property**

        Returns:
            The menu template

        """
        return {}

    def _create_menu(self):
        def submenu(template: dict):
            menu = tkinter.Menu(self.winfo_toplevel())  # type: ignore
            for menu_partial, data in template.items():
                if menu_partial.func == tkinter.Menu.add_command:
                    menu_partial(menu, command=data)
                elif menu_partial.func == tkinter.Menu.add_cascade:
                    if not isinstance(data, dict):
                        raise ValueError(
                            f"{menu_partial.func.__name__} must have dict for value"
                        )
                    menu_partial(menu, menu=submenu(data))
                elif menu_partial.func == tkinter.Menu.add:
                    menu_partial(menu, data)
            return menu

        self.option_add("*tearOff", 0)
        main_menu = submenu(self.menu_template)
        self["menu"] = main_menu


class Menu:
    """Class methods are used to define a menu template."""

    def __new__(cls):
        raise ValueError("Cannot instantiate instance, use class methods instead")

    @classmethod
    def add(cls, **opts: Any) -> MenuCommand:
        """Use to add a separator, radiobutton, or checkbutton menu item.

        >>> {Menu.add(**opts): 'separator'|'radiobutton'|'checkbutton'}

        Returns:
            Partial function that will be called to create item

        """
        return partial(tkinter.Menu.add, **opts)

    @classmethod
    def command(cls, label: str, **opts: Any) -> MenuCommand:
        """Use to add a command menu item.

        >>> {Menu.command("labeltext", **opts): command_function}

        Returns:
            Partial function that will be called to create item

        """
        nf = partial(tkinter.Menu.add_command, label=label, **opts)
        return nf

    @classmethod
    def cascade(
        cls,
        label: str,
        **opts,
    ) -> MenuCommand:
        """Use to add a submenu to a menu.

        >>> {
        ...     Menu.cascade("labeltext", **opts): {
        ...         # ...
        ...     }
        ... }

        Keyword Args:
            accelerator: Shortcut key
            activebackground: Background color when active
            activeforeground: Foreground color when active
            background: Background color
            bitmap: Bitmap to display
            columnbreak: Column to break to
            command: Command to call when item is selected
            compound: Compound style
            font: Font to use
            foreground: Foreground color
            hidemargin: Hide margin
            image: Image to display
            state: State of item
            underline: Underline index

        Returns:
            Partial function that will be called to create submenu

        """
        nf = partial(tkinter.Menu.add_cascade, label=label, **opts)

        return nf
