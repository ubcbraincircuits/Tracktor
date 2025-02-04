import ast
import os
import pandas as pd

from typing import cast


def parse_tracking_data(df: pd.DataFrame) -> pd.DataFrame:
    df = cast(pd.DataFrame, df[Data.TRACKING_COLS])
    df["frame"] = df["frame"].astype(int) - 1
    df["sort_tracks"] = df["sort_tracks"].apply(ast.literal_eval)
    df["RFID_tracks"] = df["RFID_tracks"].apply(ast.literal_eval)
    return df


def parse_rfid_readings(
    rfid_reads_df: pd.DataFrame, tracking_df: pd.DataFrame
) -> pd.DataFrame:
    rfid_reads_df = cast(pd.DataFrame, rfid_reads_df)
    rfid_reads_df["frame"] = rfid_reads_df["Timestamp"].apply(
        lambda x: tracking_df.iloc[(tracking_df["Time"] - x).abs().idxmin()]["frame"]
    )
    rfid_reads_df["Reader"] = rfid_reads_df["Reader"].astype(int)
    rfid_reads_df["RFID"] = rfid_reads_df["RFID"].astype(int)
    rfid_reads_df["frame"] = rfid_reads_df["frame"].astype(int)
    return rfid_reads_df


def get_rfids(path) -> list[int]:
    with open(f"{path}/logs.txt") as f:
        f.readline()
        tags = f.read()
        tags = tags[tags.find(":") + 1 :]
        return list(map(int, tags.split(",")))


class Data:
    VIDEO_FILE_NAME = "raw"
    TRACKING_RESULTS_FILE_NAME = "tracking_results"

    TRACKING_COLS = ["frame", "Time", "sort_tracks", "RFID_tracks"]

    def __init__(self, path):
        self.path = path
        self.files = os.listdir(path)
        self.video_path = f"{path}/{Data.VIDEO_FILE_NAME}.mp4"

        # Parse data
        self.df = parse_tracking_data(
            pd.read_csv(f"{path}/{Data.TRACKING_RESULTS_FILE_NAME}.csv")
        )
        self.rfids = get_rfids(path)
        self.rfid_reader_locations_df = pd.read_csv(f"{path}/rfid_locations.csv")
        self.rfid_reads_df = parse_rfid_readings(
            pd.read_csv(f"{path}/rfid_reads.csv"),
            self.df,
        )


def load_data(path):
    return Data(path)
