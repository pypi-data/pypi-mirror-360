import logging

import grpc
from grpc.aio import ServerInterceptor
from jose.exceptions import JWTError

from delphai_utils.keycloak import PublicKeyFetchError, decode_token

logger = logging.getLogger(__name__)


class AuthenticationInterceptor(ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        metadata = dict(handler_call_details.invocation_metadata)
        authorization_header = metadata.get("authorization")

        if not authorization_header:
            logger.warning("authorization header not specified")

        else:
            error_message = None

            if "Bearer " not in authorization_header:
                error_message = "Authorization header has the wrong format."

            else:
                access_token = authorization_header.split("Bearer ")[1]
                try:
                    await decode_token(access_token)
                except JWTError as ex:
                    error_message = f"Error decoding the token: {ex}"
                except PublicKeyFetchError as ex:
                    error_message = f"Error fetching jwk from keycloak: {ex}"

            if error_message is not None:

                @grpc.unary_unary_rpc_method_handler
                async def abort(ignored_request, context):
                    logger.error(error_message)
                    await context.abort(grpc.StatusCode.UNAUTHENTICATED, error_message)

                return abort

        return await continuation(handler_call_details)
