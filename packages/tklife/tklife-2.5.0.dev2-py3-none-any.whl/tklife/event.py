"""Module containing classes for generating and binding tkinter events."""

from __future__ import annotations

import re
from enum import Enum
from tkinter import BaseWidget, Tk, Toplevel
from typing import Any, Callable, Literal, Union

__all__ = [
    "BaseEvent",
    "EventsEnum",
    "CompositeEvent",
    "TkEventMod",
    "TkEvent",
    "TkVirtualEvents",
    "TtkNotebookEvents",
    "TtkPanedWindowEvents",
    "TtkSpinboxEvents",
    "TtkComboboxEvents",
    "TtkTreeviewEvents",
]

ActionCallable = Callable[..., Any]
"""A callable that can be used as a tkinter event callback."""

Widget = Union[BaseWidget, Tk, Toplevel]
"""A tkinter widget, or the root Tk instance."""

FuncId = str
"""A tkinter callback id."""


class BaseEvent:
    """Class representing a tkinter event.

    Can be used to generate events, bind events, and unbind events. This class should
    not be instantiated directly.

    Note:
        This class implements the composite pattern, and can be used to create composite
        events. See the ``__add__`` method.

    """

    value: str

    def generate(self, widget: Widget, **kwargs) -> ActionCallable:
        """Returns a callable that will generate this event on a widget.

        Args:
            widget: The widget to generate the event on

        Returns:
            The callable that actually generates the event

        """

        def generator(*__, widget=widget, kwargs={**kwargs}):
            widget.event_generate(self.value, **kwargs)

        return generator

    def bind(
        self,
        widget: Widget,
        action: ActionCallable,
        add: Literal["", "+"] = "",
        classname: str | None = None,
    ) -> FuncId:
        """Binds a callback to an event on given widget. Kwargs are passed to the bind
        method.

        Args:
            widget: The widget the bind is on or called on
            action: The callable called when the event is triggered

        Keyword Args:
            add: If set to "+" the callback is added to the existing callbacks (default:
                "")
            classname: The classname to bind on, or None for widget (default: None); use
                `"all"` to bind to all widgets or `"tag_name"` to bind to a specific
                tag.

        Returns:
            The event callback id, used to unbind events

        """
        if not classname:
            return widget.bind(self.value, action, add=add)
        return widget.bind_class(classname, self.value, action, add=add)

    def unbind(
        self,
        widget: Widget,
        funcid: FuncId | None = None,
        classname: str | None = None,
    ) -> None:
        """Unbinds callback(s) on the event for the given widget.

        Note:
            Based on code found on Stack Overflow, see:
            http://stackoverflow.com/questions/6433369/deleting-and-changing-a-tkinter-event-binding-in-python

        Args:
            widget: The widget that will call unbind

        Keyword Args:
            funcid: The callback id to remove, or None for all (default: None)
            classname: The classname to unbind on, or None for widget

        Raises:
            KeyError: If the provided funcid is not found in the current bindings

        """
        if not funcid:
            widget.tk.call("bind", classname or str(widget), self.value, "")
            return
        func_callbacks = self.get_bindings(widget, classname=classname)
        if funcid not in func_callbacks:
            raise KeyError(f"Function ID '{funcid}' not found in bindings")
        new_callbacks = [v for k, v in func_callbacks.items() if k != funcid]
        widget.tk.call(
            "bind", classname or str(widget), self.value, "\n".join(new_callbacks)
        )
        widget.deletecommand(funcid)

    def get_bindings(
        self, widget: Widget, classname: str | None = None
    ) -> dict[FuncId, str]:
        """Returns a dict of all bindings for this event on the given widget (if
        applicable) and classname, if specified.

        Args:
            widget: The widget to get bindings for

        Keyword Args:
            classname: The classname to get bindings for, or None for widget (default:
                widget name)

        Returns:
            A dict of callback ids to callbacks

        """
        func_id_re = re.compile(r"^[\w<>]+")
        func_callbacks = (
            widget.tk.call(  # type: ignore
                "bind",
                classname or str(widget),
                self.value,
                None,
            )
            .strip()
            .split("\n")
        )

        def get_match(v):
            match = func_id_re.match(v[6:])
            if match:
                return match.group()
            return None

        return {match: v for v in func_callbacks if (match := get_match(v))}

    def __add__(self, arg: BaseEvent | str) -> CompositeEvent:
        """Creates a composite event from this event and another.

        Args:
            arg: The event to append to this one. Either should be an event type, or
                string like: "<Event>"

        Returns:
            The new event, having value like <self-event>

        """
        return CompositeEvent.factory(self, arg)


class EventsEnum(BaseEvent, Enum):
    """Use to define custom tkinter events."""


class CompositeEvent(BaseEvent):
    """An event composed of other events/event mods."""

    value: str

    def __init__(self, value: str) -> None:
        """Create a new CompositeEvent instance.

        Args:
            value: The event. Should be formatted like: <event>

        """
        self.value = value

    @classmethod
    def factory(
        cls, modifier: Union[BaseEvent, str], event: Union[BaseEvent, str]
    ) -> CompositeEvent:
        """Creates a composite event from two events.

        Args:
            modifier: Prepends to the new event. Either should be an event type, or
                string like: "<Event>"
            event: Appends to the new event. Either should be an event type, or string
                like: "<Event>"

        Returns:
            The new event, having value like <modifier-event>

        """
        mod_value = modifier.value if not isinstance(modifier, str) else modifier
        event_value = event.value if not isinstance(event, str) else event
        return cls(f"{mod_value[0:-1]}-{event_value[1:]}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.value}>"


class TkEventMod(EventsEnum):
    """Standard tkinter event modifiers.

    Note:
        These are not used to generate events, but are used to create composite events.

    """

    ALT = "<Alt>"
    ANY = "<Any>"
    CONTROL = "<Control>"
    DOUBLE = "<Double>"
    LOCK = "<Lock>"
    SHIFT = "<Shift>"
    TRIPLE = "<Triple>"


class TkEvent(EventsEnum):
    """Standard tkinter events."""

    ACTIVATE = "<Activate>"
    BUTTON = "<Button>"
    BUTTONRELEASE = "<ButtonRelease>"
    CONFIGURE = "<Configure>"
    DEACTIVATE = "<Deactivate>"
    DESTROY = "<Destroy>"
    ENTER = "<Enter>"
    EXPOSE = "<Expose>"
    FOCUSIN = "<FocusIn>"
    FOCUSOUT = "<FocusOut>"
    KEYPRESS = "<KeyPress>"
    KEYRELEASE = "<KeyRelease>"
    LEAVE = "<Leave>"
    MAP = "<Map>"
    MOTION = "<Motion>"
    MOUSEWHEEL = "<MouseWheel>"
    UNMAP = "<Unmap>"
    VISIBILITY = "<Visibility>"
    ALT_L = "<Alt_L>"
    ALT_R = "<Alt_R>"
    BACKSPACE = "<BackSpace>"
    CANCEL = "<Cancel>"
    CAPS_LOCK = "<Caps_Lock>"
    CONTROL_L = "<Control_L>"
    CONTROL_R = "<Control_R>"
    DELETE = "<Delete>"
    DOWN = "<Down>"
    END = "<End>"
    ESCAPE = "<Escape>"
    EXECUTE = "<Execute>"
    F1 = "<F1>"
    F2 = "<F2>"
    FI = "<Fi>"
    F12 = "<F12>"
    HOME = "<Home>"
    INSERT = "<Insert>"
    LEFT = "<Left>"
    LINEFEED = "<Linefeed>"
    KP_0 = "<KP_0>"
    KP_1 = "<KP_1>"
    KP_2 = "<KP_2>"
    KP_3 = "<KP_3>"
    KP_4 = "<KP_4>"
    KP_5 = "<KP_5>"
    KP_6 = "<KP_6>"
    KP_7 = "<KP_7>"
    KP_8 = "<KP_8>"
    KP_9 = "<KP_9>"
    KP_ADD = "<KP_Add>"
    KP_BEGIN = "<KP_Begin>"
    KP_DECIMAL = "<KP_Decimal>"
    KP_DELETE = "<KP_Delete>"
    KP_DIVIDE = "<KP_Divide>"
    KP_DOWN = "<KP_Down>"
    KP_END = "<KP_End>"
    KP_ENTER = "<KP_Enter>"
    KP_HOME = "<KP_Home>"
    KP_INSERT = "<KP_Insert>"
    KP_LEFT = "<KP_Left>"
    KP_MULTIPLY = "<KP_Multiply>"
    KP_NEXT = "<KP_Next>"
    KP_PRIOR = "<KP_Prior>"
    KP_RIGHT = "<KP_Right>"
    KP_SUBTRACT = "<KP_Subtract>"
    KP_UP = "<KP_Up>"
    NEXT = "<Next>"
    NUM_LOCK = "<Num_Lock>"
    PAUSE = "<Pause>"
    PRINT = "<Print>"
    PRIOR = "<Prior>"
    RETURN = "<Return>"
    RIGHT = "<Right>"
    SCROLL_LOCK = "<Scroll_Lock>"
    SHIFT_L = "<Shift_L>"
    SHIFT_R = "<Shift_R>"
    TAB = "<Tab>"
    UP = "<Up>"


class TkVirtualEvents(EventsEnum):
    """Standard tkinter virtual events."""

    ALT_UNDERLINED = "<<AltUnderlined>>"
    INVOKE = "<<Invoke>>"
    LISTBOX_SELECT = "<<ListboxSelect>>"
    MENU_SELECT = "<<MenuSelect>>"
    MODIFIED = "<<Modified>>"
    SELECTION = "<<Selection>>"
    THEME_CHANGED = "<<ThemeChanged>>"
    TK_WORLD_CHANGED = "<<TkWorldChanged>>"
    TRAVERSE_IN = "<<TraverseIn>>"
    TRAVERSE_OUT = "<<TraverseOut>>"
    UNDO_STACK = "<<UndoStack>>"
    WIDGET_VIEW_SYNC = "<<WidgetViewSync>>"
    CLEAR = "<<Clear>>"
    COPY = "<<Copy>>"
    CUT = "<<Cut>>"
    LINE_END = "<<LineEnd>>"
    LINE_START = "<<LineStart>>"
    NEXT_CHAR = "<<NextChar>>"
    NEXT_LINE = "<<NextLine>>"
    NEXT_PARA = "<<NextPara>>"
    NEXT_WORD = "<<NextWord>>"
    PASTE = "<<Paste>>"
    PASTE_SELECTION = "<<PasteSelection>>"
    PREV_CHAR = "<<PrevChar>>"
    PREV_LINE = "<<PrevLine>>"
    PREV_PARA = "<<PrevPara>>"
    PREV_WINDOW = "<<PrevWindow>>"
    PREV_WORD = "<<PrevWord>>"
    REDO = "<<Redo>>"
    SELECT_ALL = "<<SelectAll>>"
    SELECT_LINE_END = "<<SelectLineEnd>>"
    SELECT_LINE_START = "<<SelectLineStart>>"
    SELECT_NEXT_CHAR = "<<SelectNextChar>>"
    SELECT_NEXT_LINE = "<<SelectNextLine>>"
    SELECT_NEXT_PARA = "<<SelectNextPara>>"
    SELECT_NEXT_WORD = "<<SelectNextWord>>"
    SELECT_NONE = "<<SelectNone>>"
    SELECT_PREV_CHAR = "<<SelectPrevChar>>"
    SELECT_PREV_LINE = "<<SelectPrevLine>>"
    SELECT_PREV_PARA = "<<SelectPrevPara>>"
    SELECT_PREV_WORD = "<<SelectPrevWord>>"
    TOGGLE_SELECTION = "<<ToggleSelection>>"
    UNDO = "<<Undo>>"


class TtkNotebookEvents(EventsEnum):
    """Events for the ttk.Notebook widget."""

    NOTEBOOK_TAB_CHANGED = "<<NotebookTabChanged>>"


class TtkPanedWindowEvents(EventsEnum):
    """Events for the ttk.PanedWindow widget."""

    ENTERED_CHILD = "<<EnteredChild>>"


class TtkSpinboxEvents(EventsEnum):
    """Events for the ttk.Spinbox widget."""

    INCREMENT = "<<Increment>>"
    DECREMENT = "<<Decrement>>"


class TtkComboboxEvents(EventsEnum):
    """Events for the ttk.Combobox widget."""

    COMBOBOX_SELECTED = "<<ComboboxSelected>>"


class TtkTreeviewEvents(EventsEnum):
    """Events for the ttk.Treeview widget."""

    TREEVIEW_SELECT = "<<TreeviewSelect>>"
    TREEVIEW_OPEN = "<<TreeviewOpen>>"
    TREEVIEW_CLOSE = "<<TreeviewClose>>"
