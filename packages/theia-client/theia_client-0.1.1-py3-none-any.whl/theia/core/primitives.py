from __future__ import annotations

import dataclasses
import enum


@dataclasses.dataclass
class SafetyConfig:
    """Safety parameters used in determining whether a pedestrian has been detected."""

    close_bbox_diagonal: int
    min_stopping_confidence: float
    min_throughput_hz: float
    monitor_window_s: int


@dataclasses.dataclass(frozen=True)
class BoundingBox:
    """Represents a 2D bounding on the image plane defined by its top left and bottom
    right corners. The coordinates are expressed in pixels with the X coordinates
    measured from the image's left edge, and the Y coordinates are measured from the top
    of the image.

    p0 -------
    | |__O__| |
    |    |    |
    |  _/|_   |
     ------- p1

    Where: p0 = (x0, y0), p1 = (x1, y1)
    """

    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def diagonal(self) -> float:
        """Length of the diagonal of this bounding box in pixels."""
        return (self.width**2 + self.height**2) ** 0.5

    @property
    def area(self) -> int:
        return self.width * self.height

    def intersection(self, other: BoundingBox) -> int:
        intersect_w = min(self.x1, other.x1) - max(self.x0, other.x0)
        intersect_h = min(self.y1, other.y1) - max(self.y0, other.y0)
        if intersect_w < 0 or intersect_h < 0:
            return 0
        else:
            return intersect_w * intersect_h


@dataclasses.dataclass(frozen=True)
class Detection:
    """A detected object within an image."""

    bounding_box: BoundingBox
    confidence: float


@dataclasses.dataclass(frozen=True)
class EvaluatedDetection:
    """A detection evaluated on whether the object is close and/or confident."""

    detection: Detection
    is_close: bool
    is_confident: bool


@dataclasses.dataclass
class StreamUpdate:
    """An update that happens after a frame is processed."""

    detections: list[Detection]
    jpeg: bytes
    pts: int


class SafetyState(enum.IntEnum):
    """A state that reflects safety conditions in a stream."""

    HEALTHY = enum.auto()
    LOW_THROUGHPUT = enum.auto()
    PEDESTRIAN_PRESENT = enum.auto()


@dataclasses.dataclass
class StreamStatus:
    """Comprises the current status of a stream, including detections and PTS of the
    latest frame processed in the stream.
    """

    evaluated_detections: list[EvaluatedDetection]
    fps: float
    pts: int
    safety_state: SafetyState


@dataclasses.dataclass
class SystemStatus:
    """Aggregates individual stream statuses with an overall system stafety state."""

    safety_state: SafetyState
    stream_statuses: dict[str, StreamStatus]

    @classmethod
    def from_stream_statuses(
        cls, stream_statuses: dict[str, StreamStatus]
    ) -> SystemStatus:
        safety_state = _calc_system_safety_state(stream_statuses)
        return cls(safety_state=safety_state, stream_statuses=stream_statuses)

    @classmethod
    def from_dict(cls, status_dict: dict) -> SystemStatus:
        stream_status_dicts = status_dict["stream_statuses"]
        stream_statuses = {
            stream_id: StreamStatus(**stream_status_dict)
            for stream_id, stream_status_dict in stream_status_dicts.items()
        }
        status_dict["stream_statuses"] = stream_statuses
        return cls(**status_dict)


def _calc_system_safety_state(stream_statuses: dict[str, StreamStatus]) -> SafetyState:
    """Determines the most critical safety state from all stream statuses."""
    stream_safety_states = [
        stream_status.safety_state for stream_status in stream_statuses.values()
    ]
    if any(
        safety_state == SafetyState.LOW_THROUGHPUT
        for safety_state in stream_safety_states
    ):
        return SafetyState.LOW_THROUGHPUT
    elif any(
        safety_state == SafetyState.PEDESTRIAN_PRESENT
        for safety_state in stream_safety_states
    ):
        return SafetyState.PEDESTRIAN_PRESENT
    else:
        return SafetyState.HEALTHY
