from collections.abc import Callable
import tkinter as tk
from tkinter import ttk
from typing import Any, List, Dict


class EventListbox:
    def __init__(
        self,
        root,
        get_data: Callable[[], List[Dict[str, int]]],
        on_click: Callable[[int], Any],
        height=360,
        width=640,
    ) -> None:
        self.on_click = on_click
        self.get_data = get_data
        self.data = get_data()

        self.listbox = tk.Listbox(
            root, selectmode="SINGLE", exportselection=False, height=height, width=width
        )
        self.listbox.pack(fill="both", expand=False)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        self.update()

    def update(self) -> None:
        self.data = self.get_data()
        self.listbox.delete(0, tk.END)

        for event in self.data:
            self.listbox.insert(tk.END, event["label"])

    def _on_select(self, _):
        selected_idx = self.listbox.curselection()
        if selected_idx:
            selected_event = self.data[selected_idx[0]]
            self.on_click(selected_event["frame"])


class EventNavigator:
    def __init__(
        self,
        root: tk.Frame,
        tabs_setting: Dict[str, List[Callable]],
        width: int = 640,
        height: int = 360,
    ):
        self.notebook = ttk.Notebook(root, width=width, height=height)

        self.listboxes = {}
        for tab_name, callables in tabs_setting.items():
            get_data = callables[0]
            on_click = callables[1]

            tab_frame = ttk.Frame(self.notebook)
            tab_frame.pack_propagate(False)
            tab_frame.pack(fill="both", expand=True)

            current_eventlist = EventListbox(
                tab_frame,
                get_data,
                on_click,
                height=height,
                width=width,
            )

            self.notebook.add(tab_frame, text=tab_name)
            self.listboxes[tab_name] = current_eventlist

    def update(self):
        for listbox in self.listboxes.values():
            listbox.update()
