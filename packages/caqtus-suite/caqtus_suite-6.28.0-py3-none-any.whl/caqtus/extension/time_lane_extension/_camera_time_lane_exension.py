from caqtus.gui.condetrol.timelanes_editor import TimeLaneModel
from caqtus.gui.condetrol.timelanes_editor.camera_lane_editor import CameraTimeLaneModel
from caqtus.types.timelane import CameraTimeLane
from caqtus.utils import serialization
from caqtus.utils.serialization import JSON
from ._extension import TimeLaneExtension


def create_camera_lane(number_steps: int) -> CameraTimeLane:
    return CameraTimeLane([None] * number_steps)


def create_lane_model(lane, lane_name: str) -> TimeLaneModel:
    model = CameraTimeLaneModel(lane_name)
    model.set_lane(lane)
    return model


def create_lane_delegate(lane, lane_name: str) -> None:
    return None


def dump_camera_lane(time_lane: CameraTimeLane):
    return serialization.converters["json"].unstructure(time_lane, CameraTimeLane)


def load_camera_lane(content: JSON):
    return serialization.converters["json"].structure(content, CameraTimeLane)


camera_time_lane_extension = TimeLaneExtension(
    label="Camera",
    lane_type=CameraTimeLane,
    dumper=dump_camera_lane,
    loader=load_camera_lane,
    lane_factory=create_camera_lane,
    lane_model_factory=create_lane_model,
    lane_delegate_factory=create_lane_delegate,
    type_tag="camera",
)
