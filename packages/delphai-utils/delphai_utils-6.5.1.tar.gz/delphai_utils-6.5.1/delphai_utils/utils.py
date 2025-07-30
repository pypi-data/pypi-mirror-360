import logging
import socket

logger = logging.getLogger(__name__)


def generate_default_message(message_descriptor, lvls: int = 10):
    """
    Returns descriptive template for message.
    """
    if lvls == 0:
        return "..."
    res = {}
    for fld in message_descriptor.fields:
        if fld.message_type:
            fld_content = generate_default_message(fld.message_type, lvls - 1)
        else:
            fld_content = fld.default_value

        if fld.default_value == []:
            if fld.message_type:
                fld_content = [
                    fld_content,
                ]
            elif fld.type == 9:  # string
                fld_content = [
                    "",
                ]
            elif fld.type == 2:  # float
                fld_content = [
                    0.0,
                ]
            elif fld.type == 8:  # boolean
                fld_content = [
                    False,
                ]
            elif fld.type in [3, 5]:  # int32, int64
                fld_content = [
                    0,
                ]
        res[fld.name] = fld_content
    return res


def _is_port_free(host, port):
    """
    determine whether `host` has the `port` free

    From: https://www.thepythoncode.com/article/make-port-scanner-python
    """
    s = socket.socket()
    try:
        s.connect((host, port))
    except Exception:
        return True
    else:
        return False


class NoPortFoundError(Exception):
    ...


def find_free_port(start: int, host="127.0.0.1", num_tries=4) -> int:
    for port in range(start, start + num_tries):
        if _is_port_free(host, port):
            return port
        else:
            logger.info(f"Port {port} already in use.")
    message = f"No free port found in range [{start}, {start + num_tries - 1}]"
    raise NoPortFoundError(message)
