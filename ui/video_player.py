import aspis.common as A
import cv2
import tkinter as tk

from cv2.typing import MatLike
from PIL import Image, ImageTk
from typing import Callable


def render_frame(canvas, frame):
    height, width, _ = frame.shape
    canvas.config(width=width, height=height)
    img = ImageTk.PhotoImage(master=canvas, image=Image.fromarray(frame))
    canvas.image = img
    canvas.create_image(0, 0, anchor=tk.NW, image=img)


class VideoPlayerState:
    def __init__(self, is_playing: bool = False):
        self._is_playing = is_playing

    def play(self):
        self._is_playing = True

    def pause(self):
        self._is_playing = False

    def is_playing(self):
        return self._is_playing


class VideoPlayerControls:
    def __init__(self, root, video_player, state, from_=0, to_=100):
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=2)

        self.vp = video_player
        self.vp_state = state

        self.draw(from_, to_)

    def play(self):
        if not self.vp_state.is_playing():
            self.vp_state.play()
            self.vp.play()

    def pause(self):
        if self.vp_state.is_playing():
            self.vp_state.pause()
            self.vp.pause()

    def draw(self, from_, to_):
        last_5_frames_button = tk.Button(
            self.control_frame,
            text="-5 Frames",
            command=lambda: (
                self.vp.update(self.vp.get_current_frame() - 5)
                if self.vp.get_current_frame() - 5 >= from_
                and self.vp.get_current_frame() - 5 <= to_
                else None
            ),
        )
        last_5_frames_button.grid(row=0, column=0, padx=0)

        last_frame_button = tk.Button(
            self.control_frame,
            text="-1 Frame",
            command=lambda: (
                self.vp.update(self.vp.get_current_frame() - 1)
                if self.vp.get_current_frame() - 1 >= from_
                and self.vp.get_current_frame() - 1 <= to_
                else None
            ),
        )
        last_frame_button.grid(row=0, column=1, padx=0)

        play_button = tk.Button(
            self.control_frame,
            text="Play",
            command=self.play,
        )
        play_button.grid(row=0, column=2, padx=0)

        pause_button = tk.Button(
            self.control_frame,
            text="Pause",
            command=self.pause,
        )
        pause_button.grid(row=0, column=3, padx=0)

        next_frame_button = tk.Button(
            self.control_frame,
            text="+1 Frame",
            command=lambda: (
                self.vp.update(self.vp.get_current_frame() + 1)
                if self.vp.get_current_frame() + 1 >= from_
                and self.vp.get_current_frame() + 1 <= to_
                else None
            ),
        )
        next_frame_button.grid(row=0, column=4, padx=0)

        next_5_frame_button = tk.Button(
            self.control_frame,
            text="+5 Frames",
            command=lambda: (
                self.vp.update(self.vp.get_current_frame() + 5)
                if self.vp.get_current_frame() + 5 >= from_
                and self.vp.get_current_frame() + 5 <= to_
                else None
            ),
        )
        next_5_frame_button.grid(row=0, column=5, padx=0)


class VideoPlayerFrameEntry:
    def __init__(self, root, video_player, state, from_=0, to_=100):
        self.frame_entry_frame = tk.Frame(root)
        self.frame_entry_frame.pack(pady=2)

        self.vp = video_player
        self.vp_state = state

        self.from_ = from_
        self.to_ = to_

        self.draw()

    def draw(self):
        self.frame_label = tk.Label(self.frame_entry_frame, text="Frame:")
        self.frame_entry = tk.Entry(self.frame_entry_frame, width=10, justify="center")
        self.frame_entry_btn = tk.Button(
            self.frame_entry_frame,
            text="Use Frame",
            command=lambda: self._on_frame_entry(None),
        )

        self.frame_label.grid(row=0, column=0)
        self.frame_entry.grid(row=0, column=1)
        self.frame_entry_btn.grid(row=0, column=2)

        self.frame_entry.bind("<Return>", self._on_frame_entry)

    def update(self, frame_number):
        self.frame_entry.delete(0, tk.END)
        self.frame_entry.insert(0, str(frame_number))

    def _on_frame_entry(self, _):
        try:
            frame_number = int(self.frame_entry.get())

            if frame_number <= self.to_ and frame_number >= self.from_:
                self.vp.update(frame_number)
            else:
                pass
        except ValueError:
            print("Invalid frame number")


class VideoPlayerTimeline:
    def __init__(self, root, video_player, state, width=728, from_=0, to_=100):
        self.timeline_frame = tk.Frame(root)
        self.timeline_frame.pack(pady=2)

        self.vp = video_player
        self.vp_state = state

        self.from_ = from_
        self.to_ = to_
        self.width = width

        self.draw()

    def draw(self):
        self.timeline = tk.Scale(
            self.timeline_frame,
            command=self.on_timeline_change,
            from_=self.from_,
            to=self.to_,
            orient="horizontal",
            length=self.width,
            showvalue=False,
        )
        self.timeline.grid(row=0, column=0, padx=10)

    def update(self, curr_frame):
        self.timeline.configure(command="")
        self.timeline.set(curr_frame)
        self.timeline.configure(command=self.on_timeline_change)

    def on_timeline_change(self, value):
        try:
            frame_number = int(value)
            self.vp.pause()
            self.vp.update(frame_number)
        except ValueError:
            pass


class VideoPlayer:
    def __init__(
        self,
        root: tk.Frame,
        video_path: str,
        width=728,
        height=544,
        draw_fn: Callable[[MatLike, int], MatLike] | None = None,
        update_callback: Callable[[int], None] | None = None,
    ):
        self.vp_frame = tk.Frame(root)

        self.cap = cv2.VideoCapture(video_path)
        self.draw_fn = draw_fn
        self.update_callback = update_callback
        self.process_frame = A.compose(
            A.partial(cv2.cvtColor, code=cv2.COLOR_BGR2RGB),
            A.partial(cv2.resize, dsize=(width, height), interpolation=cv2.INTER_AREA),
        )

        # Range
        self.from_ = 0
        self.to_ = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # State
        self.vp_state = VideoPlayerState(False)

        # Canvas
        self.canvas = tk.Canvas(self.vp_frame, width=width, height=height)
        self.canvas.pack()

        # Controls
        self.frame_entry = VideoPlayerFrameEntry(
            self.vp_frame,
            self,
            self.vp_state,
            from_=self.from_,
            to_=self.to_,
        )
        self.controls = VideoPlayerControls(
            self.vp_frame,
            self,
            self.vp_state,
            from_=self.from_,
            to_=self.to_,
        )
        self.timeline = VideoPlayerTimeline(
            self.vp_frame,
            self,
            self.vp_state,
            from_=self.from_,
            to_=self.to_,
        )

        # Update
        self.update(self.from_)

    def bind_update_callback(self, callback: Callable[[int], None]):
        self.update_callback = callback

    def update(self, frame_number=None):
        if frame_number is not None:
            self.frame_number = frame_number

        if not (self.frame_number <= self.to_ and self.frame_number >= self.from_):
            return

        if self.update_callback is not None:
            self.update_callback(self.frame_number)

        # Update Fields
        self.frame_entry.update(self.frame_number)
        self.timeline.update(self.frame_number)

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)

        ret, frame = self.cap.read()
        if ret:
            frame = self._draw_frame(frame)
            frame = render_frame(self.canvas, frame)

    def play(self):
        self.vp_state.play()
        self._update_frame()

    def pause(self):
        self.vp_state.pause()

    def get_current_frame(self):
        return self.frame_number

    def _draw_frame(self, frame: MatLike):
        if self.draw_fn is not None:
            frame = self.draw_fn(frame, self.frame_number)
        frame = self.process_frame(frame)
        return frame

    def _update_frame(self):
        self.update(self.frame_number)

        if self.vp_state.is_playing():
            self.frame_number += 1
            self.vp_frame.after(30, self._update_frame)
