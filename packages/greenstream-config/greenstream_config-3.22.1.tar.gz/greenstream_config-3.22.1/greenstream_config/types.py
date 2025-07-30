from typing import List, Literal, Optional

from pydantic import BaseModel, model_validator


class Offsets(BaseModel):
    # in radians in FLU
    roll: Optional[float] = None
    pitch: Optional[float] = None
    yaw: Optional[float] = None
    forward: Optional[float] = None
    left: Optional[float] = None
    up: Optional[float] = None


class PTZOffsets(Offsets):
    type: Literal["pan", "tilt"]


class Camera(BaseModel):
    # This will become the name of frame-id, ros topic and webrtc stream
    name: str
    # Used to order the stream in the UI
    order: int
    # The camera type, eg. color, ir
    type: str = "color"
    # launch the camera info node
    publish_camera_info: bool = True
    # Whether we should start the PTZ driver
    ptz: bool = False
    # The offsets from the base-link to the camera
    camera_offsets: Optional[Offsets] = None
    # The offsets from the camera to the optical frame if PTZ
    ptz_offsets: List[PTZOffsets] = []

    # Ensure that ptz_offsets is set when ptz is True
    @model_validator(mode="after")
    def validate_ptz_with_offsets(cls, model):
        if model.ptz and not model.ptz_offsets:
            raise ValueError("ptz_offsets cannot be empty when ptz is set to True")
        return model


class GreenstreamConfig(BaseModel):
    cameras: List[Camera]
    signalling_server_port: int = 8443
    namespace_vessel: str = "vessel_1"
    namespace_application: str = "greenstream"
    ui_port: int = 8000
    debug: bool = False
    diagnostics_topic: str = "diagnostics"
    cert_path: Optional[str] = None
    cert_password: Optional[str] = None
