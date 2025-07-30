import asyncio
import hypercorn
import json
import logging
import os

from typing import Optional
from urllib.parse import urlparse

from google.protobuf import symbol_database
from google.protobuf.json_format import MessageToDict
from grpc import Server, StatusCode
from grpc.experimental.aio import AioRpcError, insecure_channel
from hypercorn.asyncio import serve as hypercorn_serve
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from delphai_utils.utils import find_free_port, generate_default_message

logger = logging.getLogger(__name__)

SUPPORTED_METHODS = ["get", "put", "post", "delete", "patch"]
STATUS_MAP = {
    StatusCode.OK: 200,
    StatusCode.CANCELLED: 499,
    StatusCode.UNKNOWN: 500,
    StatusCode.INVALID_ARGUMENT: 400,
    StatusCode.DEADLINE_EXCEEDED: 504,
    StatusCode.NOT_FOUND: 404,
    StatusCode.ALREADY_EXISTS: 409,
    StatusCode.PERMISSION_DENIED: 403,
    StatusCode.UNAUTHENTICATED: 401,
    StatusCode.RESOURCE_EXHAUSTED: 429,
    StatusCode.FAILED_PRECONDITION: 412,
    StatusCode.ABORTED: 499,
    StatusCode.OUT_OF_RANGE: 416,
    StatusCode.UNIMPLEMENTED: 501,
    StatusCode.INTERNAL: 500,
    StatusCode.UNAVAILABLE: 503,
    StatusCode.DATA_LOSS: 420,
}
status_map = STATUS_MAP  # for backward compatibility, don't use it


async def http_exception_handler(request, exc):
    if "/favicon.ico" in request.url.path:
        detail = "Not Found"
        status_code = 404
    else:
        path = urlparse(str(request.url)).path
        logger.error(f"[{exc.status_code}] {request.method} {path} - {exc.detail}")
        detail = exc.detail
        status_code = exc.status_code
    return JSONResponse(
        {"detail": detail, "status": exc.status_code}, status_code=status_code
    )


def _add_method_handlers(method_descriptor, app, channel):
    logger.info(f"  processing {method_descriptor.name}")

    async def method_get_handler(request: Request):
        return JSONResponse(
            {
                "function_name": method_descriptor.full_name,
                "input": generate_default_message(method_descriptor.input_type),
                "output": generate_default_message(method_descriptor.output_type),
            }
        )

    async def method_post_handler(request: Request):
        metadata = request.headers.items()

        body = await request.body()
        body_params = json.loads(body) if body else {}

        input = {**request.path_params, **request.query_params, **body_params}

        try:
            input_prototype = symbol_database.Default().GetPrototype(
                method_descriptor.input_type
            )
            output_prototype = symbol_database.Default().GetPrototype(
                method_descriptor.output_type
            )
            method_callable = channel.unary_unary(
                f"/{method_descriptor.containing_service.full_name}/{method_descriptor.name}",
                request_serializer=input_prototype.SerializeToString,
                response_deserializer=output_prototype.FromString,
            )
            response = await method_callable(
                input_prototype(**input), metadata=metadata
            )

            output = MessageToDict(
                response,
                preserving_proto_field_name=True,
                including_default_value_fields=True,
            )
            return JSONResponse(output)

        except AioRpcError as ex:
            detail = ex.details()
            grpc_status = ex.code()
            http_status_code = STATUS_MAP[grpc_status]
            raise HTTPException(http_status_code, detail=detail)

        except Exception as ex:
            detail = str(ex).replace("\n", " ")
            http_status_code = 500
            raise HTTPException(http_status_code, detail=detail)

    app.add_route(
        f"/{method_descriptor.full_name}",
        route=method_get_handler,
        methods=["get"],
    )
    app.add_route(
        f"/{method_descriptor.full_name}",
        route=method_post_handler,
        methods=["post"],
    )

    for field_descriptor, http_rule in method_descriptor.GetOptions().ListFields():
        if field_descriptor.full_name != "google.api.http":
            continue

        for method in SUPPORTED_METHODS:
            http_path = getattr(http_rule, method)
            if http_path:
                app.add_route(
                    http_path,
                    route=method_post_handler,
                    methods=[method],
                )


def start_gateway(
    server: Server,
    grpc_port: int,
    http_port: Optional[int] = None,
    app: Optional[Starlette] = None,  # main application to add GRPC routes to it
    public_api: Optional[Starlette] = None,
):
    if not app:
        debug = os.environ.get("DELPHAI_ENVIRONMENT") == "development"
        app = Starlette(debug=debug)

        # This module registers its metrics on import
        # Import it only if we need it
        from starlette_prometheus import PrometheusMiddleware

        app.add_middleware(PrometheusMiddleware)

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    from .grpc_server import GRPC_OPTIONS

    channel = insecure_channel(f"localhost:{grpc_port}", options=GRPC_OPTIONS)

    if not hasattr(server, "descriptors"):
        raise RuntimeError(
            "Server instance does not include the proto file descriptors. Make sure you instantiate it with 'create_grpc_server'"
        )
    for file_descriptor in server.descriptors:
        for service_descriptor in file_descriptor.services_by_name.values():
            if service_descriptor.full_name.startswith("grpc."):
                logger.info(f"skipping service {service_descriptor.name}")
                continue

            logger.info(f"processing service {service_descriptor.name}")
            for method_descriptor in service_descriptor.methods_by_name.values():
                logger.info(f"  processing {method_descriptor.name}")
                _add_method_handlers(method_descriptor, app, channel)

    if not http_port:
        http_port = find_free_port(7070)

    logger.info(f"starting gateway on port {http_port}")
    config = hypercorn.Config()
    config.bind = [f"0.0.0.0:{int(http_port)}"]
    config.accesslog = logger
    config.access_log_format = '[%(s)s] %(m)s %(U)s?%(q)s [%(L)ss] %(b)s "%(h)s"'
    config.errorlog = logger

    if public_api:
        app = app.with_public_api(public_api)

    return asyncio.get_event_loop().create_task(hypercorn_serve(app, config))
