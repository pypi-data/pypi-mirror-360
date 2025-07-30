import json
import re
from pathlib import Path
from typing import cast, final
from urllib.parse import urlsplit

import flask
import requests
import structlog

from .types import AdapterRequest, RequestInterceptor


def _get_base_url(url: str) -> str:
    r = urlsplit(url)
    netloc = r.netloc
    # NOTE(dfridman): if the NVCF URL is of the form https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/{function_id}/...
    # replace with invocation.api.nvcf.nvidia.com url
    # the old endpoint gives 503 error if the request contains ```python
    # see https://nvidia.slack.com/archives/C04NQTZ9RDZ/p1746127244783519
    nvcf_pattern = (
        "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/([a-zA-Z0-9_-]+)"
    )
    m = re.match(nvcf_pattern, url)
    if m:
        function_id = m.group(1)
        netloc = f"{function_id}.invocation.api.nvcf.nvidia.com"
    return f"{r.scheme}://{netloc}"


@final
class OmniInfoInterceptor(RequestInterceptor):
    """Makes a call to the endpoint `/omni/info` and if there's a return, writes to `<output dir>/omni-info`

    Usecase:
        * recognize if the endpoint is deployed by us -- i.e. using OmniEndpoint containers

    """

    _FILE_NAME: str = "omni-info.json.txt"
    _MAX_RETRIES: int = 3

    _logger: structlog.BoundLogger
    _retries_remaining: int = _MAX_RETRIES
    _omni_info_dir: Path

    def __init__(self, api_url: str, output_dir: str):
        self._logger = structlog.get_logger(__name__)
        self._omni_info_dir = Path(output_dir) / "omni-info"
        if not self._omni_info_dir.exists():
            self._omni_info_dir.mkdir(parents=True, exist_ok=True)
        self._api_url = api_url

    @final
    def intercept_request(self, ar: AdapterRequest) -> AdapterRequest:

        # We intercept request with some retries but do this without blocking the request:
        # that is, we don't retry within the same request, but let it go and try gracefully the next
        # time.
        if self._retries_remaining <= 0:
            return ar

        try:
            response = requests.get(
                url=_get_base_url(self._api_url) + "/omni/info",
                headers={k: v for k, v in ar.r.headers if k.lower() != "host"},
                json={},  # NOTE(dfridman): we don't need to send any json
                cookies=ar.r.cookies,
                allow_redirects=False,
            )
            response.raise_for_status()
            data = response.json()

            with open(self._omni_info_dir / self._FILE_NAME, "w") as file:
                json.dump(data, file, indent=4)

            self._logger.info(
                "JSON omni-info data successfully written to 'omni-info.json'"
            )
            self._retries_remaining = 0  # no need to query any more

        except requests.exceptions.RequestException as e:
            self._logger.warning(
                "No information could be obtained from the `/omni/info` endpoint",
                attempts_remaining=self._retries_remaining,
            )
            with open(self._omni_info_dir / self._FILE_NAME, "w") as file:
                json.dump({"error": str(e)}, file, indent=4)

        finally:
            self._retries_remaining -= 1

        return ar
