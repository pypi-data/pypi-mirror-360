import copy
import time
import logging
from enum import Enum
from collections import namedtuple
import json
import random
from typing import Any, Dict
import statistics
import os

CONFIG = dict(
    save_monitoring_logs=None,
    save_monitoring_stats=None,
    SUBPATH_PREFIXES=[],
    default_pipeline_id=None,
    SLIDING_WINDOW_WIDTH=3600,  # = 1hr
)

logger = logging.getLogger(__name__)


def configure(**updates: Dict[str, Any]) -> Dict[str, Any]:
    CONFIG.update(updates)
    return CONFIG


"""
control_point_timing is 2-level structure like
{ path1 : { request_id1: RequestCheckIn( ... ), request_id1: RequestCheckIn( ... ), ... } }
Definitely, the token is a dict key.
path1 is 
"""
control_point_timing = dict()


RequestCheckIn = namedtuple(
    "RequestCheckIn", ["request_id", "timestamp", "elapsed_time"]
)
RequestFootstep = namedtuple(
    "RequestFootstep", ["path", "timestamp", "status", "message"]
)


class Status(str, Enum):
    SUCCESS = "SUCCESS"
    PROGRESS = "PROGRESS"
    ERROR = "ERROR"


try:
    import faust

    class RecordWithMetadata(faust.Record):
        metadata: Any = None

        def __init__(self, **kwargs):
            metadata = kwargs.pop("metadata", None)
            super(faust.Record, self).__init__(**kwargs)
            self.metadata = metadata

        async def trace(self, path, message="", status=Status.PROGRESS):
            if not self.metadata:
                return None
            return await update_metadata(
                path=path,
                status=status,
                metadata=self.metadata,
                message=message,
            )

        async def done(self, path, message="", status=Status.SUCCESS):
            if not self.metadata:
                return
            await update_metadata(
                path=path,
                status=status,
                metadata=self.metadata,
                message=message,
            )
            await post_statistics(self.metadata)

except ImportError:
    logger.warning(
        "cannot define class RecordWithMetadata because the faust package is not installed,"
    )


def update_control_point_timings(
    request_id: str, path: str, message_timestamp: float, elapsed_time: float
):
    """
    Extend message timings
    Meaningful paths are
    1) full message path

    2) minimal suffix that starts with one of SUBPATH_ROOTS

    /scraping/start/end/write-to-blob/start/end/translation/start/end/write-to-blob/start/end
    => /write-to-blob/start/end

    """

    # select meaningful suffixes from the path
    positions = list(
        filter(
            lambda x: x >= 0,
            [
                path.find(subpath_prefix, 0)
                for subpath_prefix in CONFIG["SUBPATH_PREFIXES"]
            ],
        )
    )
    if positions:
        _update_subpath_timing(
            request_id, path[max(positions) :], message_timestamp, elapsed_time
        )


def _update_subpath_timing(
    request_id: str, path: str, message_timestamp: float, elapsed_time: float
):
    min_timestamp = time.time() - CONFIG["SLIDING_WINDOW_WIDTH"]
    control_point_timing.setdefault(path, dict())
    control_point_timing[path][request_id] = RequestCheckIn(
        timestamp=message_timestamp, elapsed_time=elapsed_time, request_id=request_id
    )

    old_request_ids = [
        _request_id
        for _request_id, message_check_in in control_point_timing[path].items()
        if message_check_in.timestamp < min_timestamp
    ]
    for old_request_id in old_request_ids:
        control_point_timing[path].pop(old_request_id)


def new_metadata(request_id, pipeline_id=None, prototype={}):
    """
    Creates empty metadata structure
    """
    metadata = copy.deepcopy(prototype)
    metadata["request_id"] = f"{request_id}[{time.time()+0.001*random.random()}]"
    metadata["pipeline_id"] = pipeline_id or CONFIG["default_pipeline_id"]
    metadata["timings"] = list()
    metadata["updated_at"] = time.time()
    return metadata


def copy_metadata(metadata):
    return copy.deepcopy(metadata)


async def update_metadata(*, path, status, metadata, message=""):
    """
    Call this when existing request is processed
    """
    current_time = time.time()

    path_old = get_metadata_path(metadata)
    path_new = os.path.normpath(os.path.join(path_old, path))

    current_footstep = RequestFootstep(
        path=path_new, timestamp=current_time, status=status, message=message
    )

    parent_path = path_new.rsplit("/", 1)[0]
    elapsed_time = 0
    if parent_path:
        for i_footstep in range(len(metadata["timings"]) - 1, -1, -1):
            parent_footstep = metadata["timings"][i_footstep]
            if not isinstance(parent_footstep, RequestFootstep):
                metadata["timings"][i_footstep] = RequestFootstep(*parent_footstep)
                parent_footstep = metadata["timings"][i_footstep]
            if parent_footstep.path == parent_path:
                elapsed_time = current_footstep.timestamp - parent_footstep.timestamp

    metadata["timings"].append(current_footstep)
    metadata["updated_at"] = current_time

    update_control_point_timings(
        metadata["request_id"], path_new, current_time, elapsed_time
    )

    try:
        await CONFIG["save_monitoring_logs"](
            pipeline=metadata["pipeline_id"],
            metadata=json.dumps(
                dict(
                    request_id=metadata["request_id"],
                    pipeline_id=metadata["pipeline_id"],
                    timings=[current_footstep],
                    updated_at=metadata["updated_at"],
                )
            ),
        )
    except Exception as ex:
        logger.error(f"[log_metadata] {ex} {type(ex)}")

    return metadata


def get_metadata_path(metadata):
    if metadata and metadata["timings"]:
        footstep = metadata["timings"][-1]
        if isinstance(footstep, RequestFootstep):
            path_old = footstep.path
        else:
            path_old = RequestFootstep(*footstep).path
    else:
        path_old = ""
    return path_old


async def on_done(*, control_point_id, status, metadata, message=""):
    if not metadata:
        return
    await update_metadata(
        path=control_point_id,
        status=status,
        metadata=metadata,
        message=message,
    )
    await post_statistics(metadata)


async def post_statistics(metadata):
    report_stats = dict()
    min_timestamp = time.time() - CONFIG["SLIDING_WINDOW_WIDTH"]

    for path in control_point_timing:
        mean_elapsed_time = 0

        arrival_rate = len(control_point_timing[path])

        if arrival_rate > 0:
            elapsed_times = [
                message_check_in.elapsed_time
                for message_check_in in control_point_timing[path].values()
                if message_check_in.timestamp >= min_timestamp
            ]
            if elapsed_times:
                mean_elapsed_time = statistics.mean(elapsed_times)
            else:
                mean_elapsed_time = 0
        report_stats[path] = {
            "arrival_rate": arrival_rate,
            "elapsed_time": mean_elapsed_time,
        }

    try:
        await CONFIG["save_monitoring_stats"](
            pipeline=metadata["pipeline_id"],
            updated_at=int(metadata["updated_at"]),
            stats=report_stats,
        )
    except Exception as ex:
        logger.error(f"[on_done] {ex}")
