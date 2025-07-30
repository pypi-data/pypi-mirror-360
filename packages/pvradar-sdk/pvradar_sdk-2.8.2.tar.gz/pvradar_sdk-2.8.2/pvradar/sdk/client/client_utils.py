from httpx import Timeout

from ..common.settings import SdkSettings


def make_timeout_object():
    s = SdkSettings.instance()
    return Timeout(s.httpx_timeout, connect=s.httpx_connect_timeout)
