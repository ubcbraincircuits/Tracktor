import cv2
import pandas as pd

from cv2.typing import MatLike


UNKNOWN_BBOX_COLOR = (0, 0, 255)
KNOWN_BBOX_COLOR = (0, 255, 0)
BBOX_THICKNESS = 2

READER_BOX_COLOR = (255, 0, 0)


def draw_bboxes(df: pd.DataFrame, frame: MatLike, frame_number: int) -> MatLike:
    row = df.loc[df["frame"] == frame_number].reset_index(drop=True)

    try:
        all_bboxes = row["sort_tracks"][0]
        labeled_bboxes = row["RFID_tracks"][0]

        all_bboxes.sort()
        labeled_bboxes.sort()
    except Exception:
        return frame

    j = 0

    for i in range(len(all_bboxes)):
        x1, y1, x2, y2 = all_bboxes[i][0:4]
        yolo_id = all_bboxes[i][4]

        # If they reference the same bounding box
        if j < len(labeled_bboxes) and all_bboxes[i][0:4] == labeled_bboxes[j][0:4]:
            rfid = labeled_bboxes[j][4]
            frame = cv2.rectangle(
                frame, (x1, y1), (x2, y2), KNOWN_BBOX_COLOR, BBOX_THICKNESS
            )
            frame = cv2.putText(
                frame,
                f"YOLO ID: {yolo_id}",
                (x1, y1 - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                KNOWN_BBOX_COLOR,
                2,
            )
            frame = cv2.putText(
                frame,
                f"RFID: {rfid}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                KNOWN_BBOX_COLOR,
                2,
            )
            j += 1

        # Else
        else:
            frame = cv2.rectangle(
                frame, (x1, y1), (x2, y2), UNKNOWN_BBOX_COLOR, BBOX_THICKNESS
            )
            frame = cv2.putText(
                frame,
                f"YOLO ID: {yolo_id}",
                (x1, y1 - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                UNKNOWN_BBOX_COLOR,
                2,
            )
            frame = cv2.putText(
                frame,
                "Unknown",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                UNKNOWN_BBOX_COLOR,
                2,
            )

    return frame


def draw_rfid_reader_locations(rfid_reader_locations: pd.DataFrame, frame: MatLike):
    for _, row in rfid_reader_locations.iterrows():
        reader_id = str(row["reader_id"])
        x1, y1, x2, y2 = int(row["x1"]), int(row["y1"]), int(row["x2"]), int(row["y2"])

        frame = cv2.rectangle(
            frame, (x1, y1), (x2, y2), READER_BOX_COLOR, BBOX_THICKNESS
        )

        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        text_size = cv2.getTextSize(
            f"Reader ID: {reader_id}", cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2
        )
        text_width, text_height = text_size[0]

        text_x = center_x - (text_width // 2)
        text_y = center_y + (text_height // 2)

        frame = cv2.putText(
            frame,
            f"Reader ID: {reader_id}",
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            READER_BOX_COLOR,
            2,
        )

    return frame
