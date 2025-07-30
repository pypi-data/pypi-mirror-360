import asyncio
import collections.abc
import functools
import logging
from typing import Iterable, Optional, Union

from google.protobuf.descriptor import FileDescriptor
from grpc import Server, StatusCode, aio
from grpc.aio import AioRpcError
from grpc_health.v1 import health, health_pb2_grpc
from grpc_health.v1.health_pb2 import _HEALTH
from grpc_reflection.v1alpha import reflection
from prometheus_client import start_http_server

from delphai_utils.gateway import start_gateway
from delphai_utils.interceptors.authentication import AuthenticationInterceptor
from delphai_utils.interceptors.metrics import MetricsInterceptor
from delphai_utils.keycloak import update_public_keys
from delphai_utils.utils import find_free_port

logger = logging.getLogger(__name__)


GRPC_MAX_MESSAGE_LENGTH = 512 * 1024 * 1024

GRPC_OPTIONS = [
    ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_LENGTH),
    ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_LENGTH),
    ("grpc.max_metadata_size", GRPC_MAX_MESSAGE_LENGTH),
]

shutdown_event = asyncio.Event()


def grpc_error(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        context = args[2]
        try:
            result = await func(*args, **kwargs)
            return result
        except AioRpcError as ex:
            await context.abort(ex.code(), ex.details())
        except Exception as ex:
            await context.abort(StatusCode.INTERNAL, str(ex))

    return wrapper


def create_grpc_server(
    descriptors: Union[FileDescriptor, Iterable[FileDescriptor]],
    server: Optional[aio.Server] = None,
) -> aio.Server:
    """Configures a grpc server based on one or multiple proto file descriptors.

    A existing grpc server can be passed as configuration base. If not the
    default configured grpc.aio.Server will be used.
    """
    if not isinstance(descriptors, collections.abc.Iterable):
        descriptors = [descriptors]

    server = server or aio.server(
        options=GRPC_OPTIONS,
        interceptors=(
            AuthenticationInterceptor(),
            MetricsInterceptor(),
        ),
    )

    health_servicer = health.HealthServicer(experimental_non_blocking=True)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    service_names = [
        service.full_name
        for descriptor in descriptors
        for service in descriptor.services_by_name.values()
    ] + [
        _HEALTH.full_name,
        reflection.SERVICE_NAME,
    ]

    reflection.enable_server_reflection(service_names, server)
    server.descriptors = descriptors
    return server


def start_server(
    server: Server,
    gateway: bool = True,
    grpc_port: Optional[int] = None,
    http_port: Optional[int] = None,
    metrics_port: Optional[int] = None,
):
    """Start a grpc server including gateway and background tasks."""
    logger.info("starting grpc server...")

    if not grpc_port:
        grpc_port = find_free_port(8080)

    server.add_insecure_port(f"[::]:{grpc_port}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.start())
    logger.info(f"started grpc server on port {grpc_port}")

    if not metrics_port:
        metrics_port = find_free_port(9191)
    start_http_server(metrics_port)
    logger.info(f"started metrics server on port {metrics_port}")

    tasks = [loop.create_task(server.wait_for_termination())]
    if gateway:
        tasks.append(start_gateway(server, grpc_port, http_port))

    tasks.append(loop.create_task(update_public_keys()))

    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    except KeyboardInterrupt:
        logger.info("stopped server (keyboard interrupt)")
