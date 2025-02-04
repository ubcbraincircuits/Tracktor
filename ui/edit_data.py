import tkinter as tk

from collections.abc import Callable
from typing import Dict


class EditFrame:
    def __init__(
        self,
        root: tk.Frame,
        rfids: list[int],
        get_data_fn: Callable[[int], Dict[int, int]],
        set_data_fn: Callable,
        update_callback: Callable[[int], None] | None = None,
        width: int = 640,
        height: int = 360,
    ) -> None:
        self.root = root
        self.rfids = rfids
        self.get_data_fn = get_data_fn
        self.set_data_fn = set_data_fn
        self.update_callback = update_callback

        self.frame = tk.Frame(root, width=width, height=height)
        self.frame.pack(fill="both", expand=True)

        self.update(0)

    def bind_update_callback(self, callback: Callable[[int], None]) -> None:
        self.update_callback = callback

    def update(self, frame_number: int) -> None:
        data = self.get_data_fn(frame_number)

        for widget in self.frame.winfo_children():
            widget.destroy()

        self.entry_widgets = {}
        self.change_mode_widgets = {}

        row_idx = 0

        for yolo, rfid in sorted(data.items()):
            row1 = tk.Frame(self.frame)
            row1.grid(row=row_idx, column=0, sticky="w", padx=0, pady=2)
            row_idx += 1

            # YOLO Label
            yolo_label = tk.Label(row1, text=f"YOLO {yolo}")
            yolo_label.grid(row=0, column=0)

            # RFID Entry
            rfid_var = tk.StringVar(row1, value=str(rfid))
            rfid_dropdown = tk.OptionMenu(
                row1,
                rfid_var,
                *list(map(str, self.rfids)),
            )
            rfid_dropdown.grid(row=0, column=1, padx=5)

            row2 = tk.Frame(self.frame)
            row2.grid(row=row_idx, column=0, sticky="w", pady=2)
            row_idx += 1

            # From Frame Entry
            from_label = tk.Label(row2, text="From Frame:")
            from_label.grid(row=0, column=0)
            from_entry = tk.Entry(row2, width=10)
            from_entry.grid(row=0, column=1)

            # To Frame Entry
            to_label = tk.Label(row2, text="To Frame:")
            to_label.grid(row=0, column=2)
            to_entry = tk.Entry(row2, width=10)
            to_entry.grid(row=0, column=3)

            self.entry_widgets[yolo] = {
                "rfid": rfid_var,
                "to": to_entry,
                "from": from_entry,
            }

            # Submit Button
            submit_button = tk.Button(
                row2,
                text="Submit",
                command=lambda y=yolo: self._submit_changes(frame_number, int(y)),
            )
            submit_button.grid(row=0, column=4, padx=5, pady=2, sticky="w")

    def _submit_changes(self, frame_number: int, yolo_id: int) -> None:
        if not self.entry_widgets[yolo_id]["rfid"].get():
            return

        rfid = int(self.entry_widgets[yolo_id]["rfid"].get())

        from_frame = None
        if self.entry_widgets[yolo_id]["from"].get():
            from_frame = int(self.entry_widgets[yolo_id]["from"].get())

        to_frame = None
        if self.entry_widgets[yolo_id]["to"].get():
            to_frame = int(self.entry_widgets[yolo_id]["to"].get())

        self.set_data_fn(yolo_id, rfid, from_frame, to_frame)

        if self.update_callback:
            self.update_callback(frame_number)
