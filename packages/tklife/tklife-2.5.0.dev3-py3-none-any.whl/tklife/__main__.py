"""Shows an example of a skeleton window."""

from __future__ import annotations

import dataclasses
import tkinter as tk
from random import random
from tkinter import EW, NSEW, E, Misc, StringVar, Tk, Toplevel, W, ttk
from tkinter.messagebox import showinfo
from typing import Iterable, Optional

from tklife import SkeletonMixin, SkelEventDef, SkelWidget, style
from tklife.behaviors import commands
from tklife.constants import (
    COLUMNSPAN,
    COMMAND,
    PADX,
    PADY,
    STICKY,
    STYLE,
    TEXT,
    TEXTVARIABLE,
    VALUES,
    WEIGHT,
    WIDTH,
)
from tklife.controller import ControllerABC
from tklife.core import GridColConfig, GridRowConfig
from tklife.dynamic import AppendableMixin
from tklife.event import TkEvent, TkEventMod
from tklife.menu import Menu, MenuMixin
from tklife.widgets import AutoSearchCombobox, ModalDialog, ScrolledFrame

# pylint: disable=all


class GreenLabelStyle(style.TLabel):
    configure = {"foreground": "green"}


class GreenScrollbar(style.scrollbar.Horizontal):
    configure = {"troughcolor": "green"}


class ExampleModal(ModalDialog[str, None]):
    def __init__(self, master, **kwargs):
        super().__init__(master, global_grid_args={PADX: 3, PADY: 3}, **kwargs)

    def __after_init__(self):
        self.title("Example Modal")

    @property
    def template(self):
        return (
            [
                SkelWidget(ttk.Label).init(text="Enter Data:"),
                SkelWidget(
                    AutoSearchCombobox,
                    {TEXTVARIABLE: StringVar, VALUES: ["test", "value"]},
                    {},
                    label="entry",
                ),
            ],
            [
                SkelWidget(ttk.Button, {TEXT: "Okay", COMMAND: self.destroy}).grid(
                    sticky=W
                ),
                SkelWidget(
                    ttk.Button, {TEXT: "Cancel", COMMAND: self.cancel}, {STICKY: E}
                ),
            ],
        )

    def set_return_values(self):
        self.return_value = self.created["entry"][TEXTVARIABLE].get()


class AppendExampleScrolledFrame(SkeletonMixin, AppendableMixin, ScrolledFrame):
    def __after_init__(self):
        GreenScrollbar.set_style(self.h_scroll)
        super().__after_init__()


class ExampleController(ControllerABC["ExampleView"]):
    @dataclasses.dataclass()
    class AddRowCommand(commands.Command):
        appendable_frame: AppendExampleScrolledFrame
        controller: ExampleController
        id: str = dataclasses.field(default_factory=lambda: f"{random():.8f}")
        entry_text: str = dataclasses.field(default="")
        insert_at: int = dataclasses.field(default=-1)

        def add_row(self) -> None:
            id = self.id
            add_to = self.appendable_frame
            new_row = [
                SkelWidget(ttk.Label, {TEXT: f"Appended Row {id}"}, {STICKY: EW}),
                SkelWidget(ttk.Entry, {}, {STICKY: EW}),
                SkelWidget(
                    ttk.Button,
                    {
                        TEXT: "x",
                        COMMAND: self.controller.get_delete_this_row_command(id),
                        WIDTH: 2,
                    },
                    {STICKY: EW},
                    label=id,
                ),
            ]
            if self.insert_at == -1:
                added_row = add_to.append_row(new_row)
                add_to.widget_cache[added_row, 1].widget.insert(0, self.entry_text)  # type: ignore
            else:
                try:
                    added_row = add_to.insert_row_at(self.insert_at, new_row)
                    add_to.widget_cache[added_row, 1].widget.insert(0, self.entry_text)  # type: ignore
                except KeyError:
                    added_row = add_to.append_row(new_row)
                    add_to.widget_cache[added_row, 1].widget.insert(0, self.entry_text)  # type: ignore

        def _get_delete_this_row_command(self):
            def delete_this_row():
                destroy_row = self.appendable_frame.find_row_of(self.id)
                self.entry_text = self.appendable_frame.widget_cache[
                    destroy_row, 1
                ].widget.get()
                self.appendable_frame.destroy_row(destroy_row)
                self.insert_at = destroy_row

            return delete_this_row

        def delete_row(self) -> None:
            return self._get_delete_this_row_command()()

        def execute(self) -> None:
            self.add_row()

        def reverse(self) -> None:
            self.delete_row()

    class DeleteRowCommand(AddRowCommand):
        def execute(self) -> None:
            self.delete_row()

        def reverse(self) -> None:
            self.add_row()

    @dataclasses.dataclass()
    class DeleteLastRowCommand(DeleteRowCommand):
        def execute(self) -> None:
            destroy_row = int(len(self.appendable_frame.widget_cache) / 3) - 1
            self.entry_text = self.appendable_frame.widget_cache[  # type: ignore
                destroy_row, 1
            ].widget.get()
            self.id = next(
                lbl_
                for lbl_, cr_w in self.appendable_frame.created.items()
                if cr_w.widget
                == self.appendable_frame.widget_cache[destroy_row, 2].widget
            )
            self.appendable_frame.destroy_row(destroy_row)

    view: ExampleView
    command_history: commands.CommandHistory

    def __init__(self, command_history: commands.CommandHistory | None = None) -> None:
        self.command_history = (
            commands.CommandHistory() if command_history is None else command_history
        )
        super().__init__()

    def button_a_command(self, *__):
        showinfo(
            title="Information",
            message=self.entry_a["textvariable"].get(),
            parent=self.view,
        )

    def button_b_command(self, *__):
        showinfo(
            title="Information",
            message=self.entry_b["textvariable"].get(),
            parent=self.view,
        )

    def button_c_command(self, *__):
        d = ExampleModal.create(self.view)
        showinfo(title="Information", message=f"{d}", parent=self.view)

    def add_row_command(self, *__):
        command = self.AddRowCommand(self.appendable_frame.widget, self)
        self.command_history.add_history(command)

    def get_delete_this_row_command(self, last_label: str):
        def delete_this_row():
            command = self.DeleteRowCommand(
                self.appendable_frame.widget, self, last_label
            )
            self.command_history.add_history(command)

        return delete_this_row

    def delete_last_row_command(self, *__):
        if not self.appendable_frame.widget.widget_cache:
            return
        command = self.DeleteLastRowCommand(self.appendable_frame.widget, self)
        self.command_history.add_history(command)

    def control_z_event_handler(self, *__):
        self.command_history.undo()

    def control_y_event_handler(self, *__):
        self.command_history.redo()


class ExampleView(SkeletonMixin[ExampleController], MenuMixin, Toplevel):
    def __init__(
        self,
        master: Optional[Misc] = None,
        example_controller: Optional[ExampleController] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master, example_controller, global_grid_args={PADX: 3, PADY: 3}, **kwargs
        )

    def __after_init__(self):
        self.title("TkLife Example")

    @property
    def events(self) -> Iterable[SkelEventDef]:
        return [
            {
                "event": TkEvent.ESCAPE,
                "action": lambda __: self.destroy(),
            },
            {
                "event": TkEventMod.CONTROL + TkEvent.RETURN,
                "action": lambda __: self.destroy(),
            },
            {
                "event": TkEvent.MAP,
                "action": lambda event: print("Mapped", event.widget),
                "widget": self.created["entry_a"].widget,
            },
            {
                "event": TkEventMod.CONTROL + TkEvent.KEYPRESS + "<z>",
                "action": self.controller.control_z_event_handler,
                "widget": self.winfo_toplevel(),
            },
            {
                "event": TkEventMod.CONTROL + TkEvent.KEYPRESS + "<y>",
                "action": self.controller.control_y_event_handler,
                "widget": self.winfo_toplevel(),
            },
        ]

    @property
    def grid_config(self) -> tuple[Iterable[GridRowConfig], Iterable[GridColConfig]]:
        return [
            {WEIGHT: 1},
            {WEIGHT: 1},
            {WEIGHT: 1},
            {WEIGHT: 1},
            {WEIGHT: 1},
        ], [
            {WEIGHT: 1},
            {WEIGHT: 1},
            {WEIGHT: 1},
        ]

    @property
    def template(self):
        return (
            [
                SkelWidget(ttk.Label).init(text="Label A:"),
                SkelWidget(ttk.Entry)
                .init(textvariable=tk.StringVar)
                .grid(sticky=tk.EW)
                .set_label("entry_a"),
                SkelWidget(
                    ttk.Button,
                    {TEXT: "Print contents", COMMAND: self.controller.button_a_command},
                    {},
                ),
            ],
            [
                SkelWidget(
                    ttk.Label, {TEXT: "Label B:", STYLE: GreenLabelStyle.ttk_style}, {}
                ),
                SkelWidget(
                    AutoSearchCombobox,
                    {
                        TEXTVARIABLE: StringVar(value="Default value"),
                        "values": ["Default value", "other", "a thing to test"],
                    },
                    {STICKY: E + W},
                    label="entry_b",
                ),
                SkelWidget(
                    ttk.Button,
                    {TEXT: "Print contents", COMMAND: self.controller.button_b_command},
                    {},
                ),
            ],
            [
                None,
                SkelWidget(
                    ttk.Button,
                    {TEXT: "Dialog", COMMAND: self.controller.button_c_command},
                    {},
                ),
                None,
            ],
            [
                SkelWidget(
                    AppendExampleScrolledFrame,
                    {"show_hscroll": True},
                    {COLUMNSPAN: 3, STICKY: NSEW},
                    label="appendable_frame",
                )
            ],
            [
                SkelWidget(
                    ttk.Button,
                    {TEXT: "Add Row", COMMAND: self.controller.add_row_command},
                    {},
                ),
                None,
                SkelWidget(
                    ttk.Button,
                    {
                        TEXT: "Delete Row",
                        COMMAND: self.controller.delete_last_row_command,
                    },
                    {},
                ),
            ],
        )

    @property
    def menu_template(self):
        return {
            Menu.cascade(label="File", underline=0): {
                Menu.command(
                    label="Show Dialog", underline=0
                ): self.controller.button_c_command,
                Menu.add(): "separator",
                Menu.command(label="Exit", underline=1): self.destroy,
            },
            Menu.cascade(label="Edit", underline=0): {
                Menu.command(
                    label="Undo", underline=0, accelerator="Ctrl+Z"
                ): self.controller.control_z_event_handler,
                Menu.command(
                    label="Redo", underline=0, accelerator="Ctrl+Y"
                ): self.controller.control_y_event_handler,
            },
        }


if __name__ == "__main__":
    master = Tk()
    style.BaseStyle.define_all()
    example_view = ExampleView(master)
    example_view.controller = ExampleController()
    master.withdraw()
    example_view.wait_window()
    master.quit()
