import aspis.common as A
import tkinter as tk

from cv2.typing import MatLike
from tkinter import filedialog, messagebox

from data import loader, drawer, repo
from ui import video_player, event_nav, edit_data


def main_application(folder_path):
    """Run the main application after folder selection."""
    app = tk.Tk()
    app.title("Tracktor")
    app.geometry("1280x720")
    app.resizable(False, False)

    # Load Data
    cage_data = loader.load_data(folder_path)

    # Configure grid layout for the root window
    app.columnconfigure(0, weight=3)
    app.columnconfigure(1, weight=1)

    # Draw Columns
    left_col = tk.Frame(app, width=730, height=700)
    left_col.grid(row=0, column=0, sticky="", padx=10, pady=5)
    left_col.columnconfigure(0, weight=1)
    left_col.rowconfigure(2, weight=1)
    left_col.grid_propagate(False)

    right_col = tk.Frame(app, width=530, height=700)
    right_col.grid(row=0, column=1, sticky="", padx=10, pady=10)
    right_col.grid_propagate(False)

    # Top controls
    top_controls = tk.Frame(left_col)
    top_controls.grid(row=0, column=0, columnspan=2, sticky="ew")
    top_controls.columnconfigure(0, weight=3)
    top_controls.columnconfigure(1, weight=1)

    # Current Folder
    tk.Label(
        top_controls,
        text=f"Selected Folder:\n{folder_path}",
        wraplength=300,
        anchor="w",
    ).grid(row=0, column=0, sticky="ew")

    # Check Button
    show_rfid_reader_locations = tk.BooleanVar()

    tk.Checkbutton(
        top_controls,
        text="Show RFID Reader Locations",
        variable=show_rfid_reader_locations,
        command=lambda: (
            show_rfid_reader_locations.set(not show_rfid_reader_locations.get())
            or vp.update()
        ),
        justify="center",
    ).grid(row=0, column=1, sticky="ew")

    # Save Button
    tk.Button(
        top_controls,
        text="Save",
        command=lambda: repo.save_rfid_data(cage_data),
    ).grid(row=0, column=2, sticky="ew")

    # Video Player
    def draw(frame: MatLike, frame_number: int):
        if show_rfid_reader_locations.get():
            frame = drawer.draw_rfid_reader_locations(
                cage_data.rfid_reader_locations_df, frame
            )

        frame = drawer.draw_bboxes(cage_data.df, frame, frame_number)
        return frame

    vp = video_player.VideoPlayer(left_col, cage_data.video_path, draw_fn=draw)
    vp.vp_frame.grid(row=2, column=0, sticky="nsew")

    # Editable Table
    edit_frame = edit_data.EditFrame(
        right_col,
        cage_data.rfids,
        A.curry(repo.get_frame_data)(cage_data.df),
        A.compose(lambda _: vp.update(), A.curry(repo.update_rfid_map)(cage_data.df)),
        height=200,
        width=500,
    )
    edit_frame.frame.grid(row=0, column=1, sticky="")
    edit_frame.frame.grid_propagate(False)
    vp.bind_update_callback(edit_frame.update)

    # Event List
    event_navigator = event_nav.EventNavigator(
        right_col,
        {
            "Missing Data": [
                lambda: repo.get_missing_data(cage_data.df),
                lambda k: vp.update(k),
            ],
            "RFID Reads": [
                lambda: repo.get_rfid_reads(cage_data.rfid_reads_df),
                lambda k: vp.update(k),
            ],
        },
        height=470,
        width=490,
    )
    event_navigator.notebook.grid(row=1, column=1, sticky="")
    event_navigator.notebook.grid_propagate(False)
    edit_frame.bind_update_callback(lambda _: event_navigator.update())

    app.mainloop()


def run():
    """Handle folder selection and initialize the main application."""
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Choose date")

    if folder_path:
        main_application(folder_path)
    else:
        messagebox.showwarning("Warning", "Please select a folder to proceed.")
        root.destroy()


if __name__ == "__main__":
    run()
