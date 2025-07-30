import inspect

from delphai_utils.keycloak import decode_token
from functools import wraps
from grpc import StatusCode
from grpc.aio import ServicerContext
from typing import Dict, List, Tuple, Union


def get_authorization_token(context: ServicerContext) -> str:
    """
    Get user access token.
    :param grpc.aio.ServicerContext context: context passed to grpc endpoints
    :return access token.
      More information: https://wiki.delphai.dev/wiki/Authorization
    :rtype: str
    """

    metadata = dict(context.invocation_metadata())
    if "authorization" not in metadata:
        return None

    authorization_header = metadata["authorization"]
    access_token = authorization_header.split("Bearer ")[1]

    return access_token


async def get_user(context: ServicerContext) -> Dict:
    """
    Get x-delphai-user information.
    :param grpc.aio.ServicerContext context: context passed to grpc endpoints
    :raises: KeyError
    :return x-delphai-user dictionary.
      More information: https://wiki.delphai.dev/wiki/Authorization
    :rtype: Dict
    """

    access_token = get_authorization_token(context)
    if not access_token:
        return {}
    decoded_access_token = await decode_token(access_token)
    user = {
        "https://delphai.com/mongo_user_id": decoded_access_token.get("mongo_user_id"),
        "https://delphai.com/client_id": decoded_access_token.get("mongo_client_id"),
        "user_id": decoded_access_token.get("sub"),
    }
    if "realm_access" in decoded_access_token and "roles" in decoded_access_token.get(
        "realm_access"
    ):
        roles = decoded_access_token.get("realm_access").get("roles")
        user["roles"] = roles
    if "group_membership" in decoded_access_token:
        user["groups"] = decoded_access_token["group_membership"]
    if "limited_dataset_group_name" in decoded_access_token:
        user["limited_dataset_group_name"] = decoded_access_token[
            "limited_dataset_group_name"
        ]
    if "name" in decoded_access_token:
        user["name"] = decoded_access_token["name"]
    if decoded_access_token.get("groups"):
        user_groups = decoded_access_token["groups"][0]
        user["customer_id"] = user_groups[0]["id"]
        if len(user_groups) > 1:
            user["department_id"] = user_groups[-1]["id"]
    if decoded_access_token.get("preferred_currency"):
        user["preferred_currency"] = decoded_access_token["preferred_currency"]

    return user


async def get_user_and_client_ids(context: ServicerContext) -> Tuple[str, str]:
    """
    Get user_id and client_id.
    :param grpc.aio.ServicerContext context: context passed to grpc endpoints
    :return user_id and client_id.
      More information: https://wiki.delphai.dev/wiki/Authorization
    :rtype: Tuple[str, str]
    """
    try:
        user = await get_user(context)
        user_id = user.get("https://delphai.com/mongo_user_id")
        client_id = user.get("https://delphai.com/client_id")
    except Exception:
        return "", ""
    return user_id, client_id


async def get_roles(context: ServicerContext):
    """
    Utility function to retrieve roles from grpc context.
    :param Union[List[str], grpc.aio.ServicerContext] context:
      a list of roles or the grpc context passed to class methods
    :return list of roles
    :rtype List[str]
    """

    try:
        user = await get_user(context)
        return user.get("roles") or []
    except KeyError:
        return []


async def get_groups(context: ServicerContext) -> List[str]:
    """
    Gets groups of calling identity
    :param grpc.aio.ServicerContext context: context passed to grpc endpoints
    :return raw roles passed from keycloak.
      For example this can be ["/delphai/Development"]
    :rtype List[str]
    """

    assert isinstance(context, object)
    try:
        user = await get_user(context)
    except KeyError:
        return []
    return user.get("groups") or []


async def get_affiliation(
    context: ServicerContext,
) -> Tuple[Union[str, None], Union[str, None]]:
    """
    Gets organization and department of user
    :param grpc.aio.ServicerContext context: context passed to grpc endpoints
    :return organization and department as a tuple or None if not affiliated
    :rtype Union[Tuple[str, None], Tuple[str, None]]
    """

    raw_groups = await get_groups(context)
    if len(raw_groups) == 0:
        return None, None
    else:
        group_hirarchy = raw_groups[0].split("/")[1:3]
        if len(group_hirarchy) == 1:
            return group_hirarchy.pop(), None
        elif len(group_hirarchy) == 2:
            return tuple(group_hirarchy)
        else:
            return None, None


async def is_authorized(
    provided_roles: Union[List[str], ServicerContext],
    required_roles: List[str],
    decision_logic: str = "all",
    abort: bool = False,
):
    """
    Makes a decision if user is authorized based on intersection of roles.
    :param Union[List[str], grpc.aio.ServicerContext] provided_roles:
      a list of roles or the grpc context passed to class methods
    :param List[str] required_roles: roles the request must pass
    :param str decision_logic: one of 'all' or 'some'. Default: 'all'
    :param bool abort: if set to true grpc call will abort with PERMISSION_DENIED. Default: False
    :rtype: bool
    """

    assert len(required_roles) != 0
    assert type(required_roles) == list
    assert any([allowed == decision_logic for allowed in ["all", "some"]])
    resolved_roles = await get_roles(provided_roles)

    required_roles = set(required_roles)  # in case same role is passed mulitple times
    role_intersection = required_roles.intersection(resolved_roles)
    all_intersects = len(role_intersection) == len(required_roles)
    some_intersects = len(role_intersection) > 0
    _is_authorized = (decision_logic == "all" and all_intersects) or (
        decision_logic == "some" and some_intersects
    )
    is_grpc_context = type(provided_roles) is not list
    if abort and not _is_authorized and is_grpc_context:
        details = f"Provided roles {resolved_roles} don't intersect with required roles {required_roles}."
        provided_roles.abort(StatusCode.PERMISSION_DENIED, details)
    return _is_authorized


def authorize(required_roles: List[str], decision_logic: str = "all"):
    """
    Decorator for grpc endpoints to restrict role-based access.
    :param List[str] required_roles: list of strings which roles are required
    :param str decision_logic: one of 'all' or 'some'. Default: 'all'
    :return: wraped function
    :rtype: func
    """

    def wrap(func):
        assert inspect.iscoroutinefunction(func)

        @wraps(func)
        async def wrapped_func(self, request, context, *args, **kwargs):
            if await is_authorized(context, required_roles, decision_logic):
                return await func(self, request, context, *args, **kwargs)
            else:
                details = f"Given roles don't intersect with {required_roles} using decission logic '{decision_logic}'"
                await context.abort(StatusCode.PERMISSION_DENIED, details)

        return wrapped_func

    return wrap
