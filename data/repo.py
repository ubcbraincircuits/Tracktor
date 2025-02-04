from typing import cast, List
import os
import pandas as pd

from .loader import Data

"""
Getters
"""


def get_frame_data(df: pd.DataFrame, frame: int) -> dict:
    row = df[df["frame"] == frame].reset_index(drop=True)
    sort_tracks = cast(List[List[int]], row["sort_tracks"])
    rfid_tracks = cast(List[List[int]], row["RFID_tracks"])

    try:
        sort_tracks = row["sort_tracks"][0]
        rfid_tracks = row["RFID_tracks"][0]
    except Exception:
        return {}

    yolo_to_rfid = {}
    for track in sort_tracks:
        yolo_id = track[-1]

        matched = False
        for rfid_track in rfid_tracks:
            if rfid_track[:4] == track[:4]:
                yolo_to_rfid[yolo_id] = rfid_track[-1]
                matched = True

        if not matched:
            yolo_to_rfid[yolo_id] = None

    return yolo_to_rfid


def get_missing_data(df: pd.DataFrame) -> List[dict]:
    df["rfid_length"] = df["RFID_tracks"].apply(len)
    df["sort_length"] = df["sort_tracks"].apply(len)

    df["length_mismatch"] = df["rfid_length"] != df["sort_length"]

    mismatches = df[
        df["length_mismatch"] & ~df["length_mismatch"].shift(fill_value=False)
    ]

    return [
        {"label": f"Frame {frame}", "frame": frame} for frame in mismatches["frame"]
    ]


def get_rfid_reads(rfid_reads_df: pd.DataFrame) -> List[dict]:
    res = []

    for _, row in rfid_reads_df.iterrows():
        reader = int(row["Reader"])
        rfid = int(row["RFID"])
        frame = int(row["frame"])

        label = f"RFID Reader: {reader} | RFID: {rfid} | Frame: {frame}"

        res.append(
            {
                "label": label,
                "frame": frame,
            }
        )

    return res


"""
Setters
"""


def update_rfid_map(
    df: pd.DataFrame,
    yolo_id: int,
    update_rfid: int,
    from_: int | None = None,
    to_: int | None = None,
) -> None:
    if from_ is None:
        from_ = int(df["frame"].min())
    if to_ is None:
        to_ = int(df["frame"].max())

    contains_yolo_id = df["sort_tracks"].apply(
        lambda tracks: any(track[-1] == yolo_id for track in tracks)
    )

    mask = (df["frame"] >= from_) & (df["frame"] <= to_) & contains_yolo_id

    for idx, row in df[mask].iterrows():
        sort_tracks = cast(List[List[int]], row["sort_tracks"])
        rfid_tracks = cast(List[List[int]], row["RFID_tracks"])

        matching_track = next(
            (track for track in sort_tracks if track[-1] == yolo_id), None
        )

        if matching_track:
            coordinates = matching_track[:4]

            matching_rfid_track = next(
                (track for track in rfid_tracks if track[:4] == coordinates), None
            )

            if matching_rfid_track:
                matching_rfid_track[-1] = update_rfid
            else:
                rfid_tracks.append(coordinates + [update_rfid])

            df.at[idx, "RFID_tracks"] = rfid_tracks


"""
Save Data
"""


def save_rfid_data(data: Data):
    files = os.listdir(data.path)

    next_file = 0

    for file_name in files:
        if (
            Data.TRACKING_RESULTS_FILE_NAME in file_name
            and file_name.split("_")[-1][:-4].isdigit()
        ):
            next_file = max(next_file, int(file_name.split("_")[-1][:-4]) + 1)

    data.df.to_csv(
        f"{data.path}/{Data.TRACKING_RESULTS_FILE_NAME}_{next_file}.csv",
        index=False,
    )
