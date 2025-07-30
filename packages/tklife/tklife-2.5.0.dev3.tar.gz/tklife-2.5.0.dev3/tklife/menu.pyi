import tkinter
from typing import Any, Callable, Literal, NoReturn, Optional

MenuCommand = Callable[[tkinter.Menu], None]

class MenuMixin:
    def __init__(self, master: Optional[tkinter.Misc] = ..., **kwargs: Any) -> None: ...
    @property
    def menu_template(self) -> dict: ...

class Menu:
    def __new__(cls) -> NoReturn: ...
    @classmethod
    def add(cls, **opts: Any) -> MenuCommand: ...
    @classmethod
    def command(
        cls,
        label: str,
        accelerator: str = ...,
        activebackground: str = ...,
        activeforeground: str = ...,
        background: str = ...,
        bitmap: str = ...,
        columnbreak: int = ...,
        compound: Any = ...,
        font: Any = ...,
        foreground: str = ...,
        hidemargin: bool = ...,
        image: Any = ...,
        state: Literal["normal", "active", "disabled"] = ...,
        underline: int = ...,
    ) -> MenuCommand: ...
    @classmethod
    def cascade(
        cls,
        label: str,
        accelerator: str = ...,
        activebackground: str = ...,
        activeforeground: str = ...,
        background: str = ...,
        bitmap: str = ...,
        columnbreak: int = ...,
        command: str = ...,
        compound: Any = ...,
        font: Any = ...,
        foreground: str = ...,
        hidemargin: bool = ...,
        image: Any = ...,
        state: Literal["normal", "active", "disabled"] = ...,
        underline: int = ...,
    ) -> MenuCommand: ...
