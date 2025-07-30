# Introduction

Tklife is an opinionated framework for the development of Tkinter applications.

## Installation

```bash
pip install tklife
```

## Why Tklife?

Tklife is a framework that aims to make the development of Tkinter applications more structured as well as correct the following issues Python 3 has with Tkinter:

- Event unbinding does not work properly for events appended with "+" argument to the bind method. See [tklife.event.BaseEvent.unbind()](api.html#tklife.event.BaseEvent.unbind) for more information on how this is corrected.

- The tearoff attribute of the Menu widget is outdated and should not be used. The MenuMixin automatically removes the tearoff attribute from all Menus.
