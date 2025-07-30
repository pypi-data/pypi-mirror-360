from greenstream_config.types import Camera


def camera_topic(namespace_vessel: str, camera_name: str, camera_type: str):
    return f"/{namespace_vessel}/sensors/cameras/{camera_name}_{camera_type}"


def camera_topic_from_camera(namespace_vessel: str, camera: Camera):
    return camera_topic(namespace_vessel, camera.name, camera.type)


def frame_id(namespace_vessel: str, camera_name: str, camera_type: str):
    return f"{namespace_vessel}_{camera_name}_{camera_type}_optical_frame"


def frame_id_from_camera(namespace_vessel: str, camera: Camera):
    return frame_id(namespace_vessel, camera.name, camera.type)


def camera_namespace(namespace_full: str, camera_name: str):
    return f"{namespace_full}/cameras/{camera_name}"


def camera_namespace_from_camera(namespace_full: str, camera: Camera):
    return camera_namespace(namespace_full, camera.name)


def camera_node_name(node_type: str, camera_name: str, camera_type: str):
    return f"{node_type}_{camera_name}_{camera_type}"


def camera_node_name_from_camera(node_type: str, camera: Camera):
    return camera_node_name(node_type, camera.name, camera.type)


def camera_frame_topic(namespace_vessel: str, camera_name: str, camera_type: str):
    if namespace_vessel == "":
        return f"perception/frames/{camera_name}_{camera_type}"
    else:
        return f"/{namespace_vessel}/perception/frames/{camera_name}_{camera_type}"


def camera_frame_topic_from_camera(namespace_vessel: str, camera: Camera):
    return camera_frame_topic(namespace_vessel, camera.name, camera.type)
