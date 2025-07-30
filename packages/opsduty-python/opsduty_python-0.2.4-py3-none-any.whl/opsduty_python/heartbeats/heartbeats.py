from functools import wraps
from logging import getLogger
from typing import Callable, ParamSpec, TypeVar

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from opsduty_python.settings import settings

logger = getLogger(__name__)


def requests_retry_session(
    *,
    session: requests.Session,
    retries: int = 1,
    backoff_factor: float = 0.4,
    status_forcelist: tuple[int, ...] = (502, 503, 504),
) -> requests.Session:
    """
    Retry on connection failures or bad status codes.
    """

    session = session or requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def send_heartbeat_checkin(
    *,
    heartbeat: str,
    environment: str | None,
    timeout: float | tuple[float, float] | None = None,
) -> bool:
    """Send a heartbeat checkin to OpsDuty."""

    url = f"{settings.OPSDUTY_BASE_URL}/heartbeats/checkin/{heartbeat}/"

    if environment is not None:
        url += f"{environment}/"

    if timeout is None:
        timeout = (3, 3)

    session = requests_retry_session(session=requests.Session(), retries=2)

    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()

        return True
    except requests.RequestException as exc:
        if exc.response is not None and exc.response.status_code == 404:
            logger.warning(
                "Heartbeat with ID: %s and environment: %s was not found.",
                heartbeat,
                environment,
            )
        else:
            logger.warning(
                "Could not send heartbeat (%s:%s) checkin.",
                heartbeat,
                environment,
                exc_info=True,
            )

    return False


Param = ParamSpec("Param")
RetType = TypeVar("RetType")


def heartbeat_checkin(
    *,
    heartbeat: str,
    environment: str | None,
    enabled: bool = True,
    timeout: float | tuple[float, float] | None = None,
) -> Callable[[Callable[Param, RetType]], Callable[Param, RetType]]:
    """Decorator to send a heartbeat checkin when the decorated method succeed."""

    def decorator(func: Callable[Param, RetType]) -> Callable[Param, RetType]:
        @wraps(func)
        def inner(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            result = func(*args, **kwargs)

            logger.debug(
                "Heartbeat checkin heartbeat=%s environment=%s enabled=%s",
                heartbeat,
                environment,
                enabled,
            )

            if enabled:
                send_heartbeat_checkin(
                    heartbeat=heartbeat, environment=environment, timeout=timeout
                )

            return result

        inner.has_heartbeat_checkin = True  # type: ignore
        inner.heartbeat = heartbeat  # type: ignore

        return inner

    return decorator
