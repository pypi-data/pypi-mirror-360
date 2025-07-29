# Copyright 2022 Dynatrace LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from http.client import HTTPConnection
from typing import Dict, Optional, Tuple

from opentelemetry.util.types import AttributeValue

from dynatrace.odin.semconv import v1 as semconv
from dynatrace.opentelemetry.tracing._logging.loggers import gcf_logger

# some resource attributes are only available via the GCP internal metadata server
# which can be queried via HTTP, see: https://cloud.google.com/compute/docs/metadata/overview
# see also gcp-metadata Node.Js package: https://github.com/googleapis/gcp-metadata/blob/v5.0.0/src/index.ts
_GCP_HOST = "169.254.169.254"
_GCP_BASE_PATH = "/computeMetadata/v1"
_GCP_TIMEOUT = 0.3
_GCP_HEADERS = {"Metadata-Flavor": "Google"}


def detect_resource() -> Dict[str, AttributeValue]:
    function_name = get_function_name()
    attrs = {
        semconv.CLOUD_PROVIDER: semconv.CloudProviderValues.GCP.value,
        semconv.CLOUD_PLATFORM: semconv.CloudPlatformValues.GCP_CLOUD_FUNCTIONS.value,
    }

    project_id, region = _query_gcp_metadata()

    _add_attr(attrs, semconv.FAAS_NAME, function_name)
    _add_attr(attrs, semconv.GCP_INSTANCE_NAME, function_name)

    function_version = os.getenv("K_REVISION")
    if function_version:
        attrs[semconv.FAAS_VERSION] = function_version

    _add_attr(attrs, semconv.CLOUD_ACCOUNT_ID, project_id)
    _add_attr(attrs, semconv.GCP_PROJECT_ID, project_id)

    _add_attr(attrs, semconv.CLOUD_REGION, region)
    _add_attr(attrs, semconv.GCP_REGION, region)

    _add_faas_id(attrs, function_name, project_id, region)

    return attrs


def get_function_name() -> Optional[str]:
    return os.getenv("K_SERVICE") or os.getenv("FUNCTION_NAME")


def _add_attr(
    attrs: Dict[str, AttributeValue], key: str, value: Optional[AttributeValue]
) -> None:
    if not value:
        gcf_logger.warning("Could not detect resource '%s'", key)
    else:
        attrs[key] = value


def _add_faas_id(
    attrs: Dict[str, AttributeValue],
    function_name: Optional[str],
    project_id: Optional[str],
    region: Optional[str],
) -> None:
    key = semconv.FAAS_ID
    if function_name and project_id and region:
        # ID in resource name format: https://cloud.google.com/asset-inventory/docs/resource-name-format
        attrs[key] = (
            "//cloudfunctions.googleapis.com/projects"
            f"/{project_id}/locations/{region}/functions/{function_name}"
        )
    else:
        gcf_logger.warning(
            "Could not detect resource '%s' (func-name=%s, project-id=%s, region=%s)",
            key,
            function_name,
            project_id,
            region,
        )


def _query_gcp_metadata() -> Tuple[Optional[str], Optional[str]]:
    project_id = os.getenv("GCP_PROJECT")
    region = os.getenv("FUNCTION_REGION")
    # legacy py 3.7 runtime have these env vars set
    if project_id and region:
        return project_id, region

    # for newer runtimes query the metadata server
    conn = HTTPConnection(_GCP_HOST, timeout=_GCP_TIMEOUT)
    try:
        if not project_id:
            project_id = _request_project_id(conn)
        if not region:
            region = _request_region(conn)
    finally:
        conn.close()
    return project_id, region


def _request_project_id(conn: HTTPConnection) -> Optional[str]:
    try:
        return _request_metadata(conn, f"{_GCP_BASE_PATH}/project/project-id")
    except Exception as ex:  # pylint:disable=broad-except
        gcf_logger.warning("Error when requesting 'project-id': %s", ex)
        return None


def _request_region(conn: HTTPConnection) -> Optional[str]:
    try:
        region = _request_metadata(conn, f"{_GCP_BASE_PATH}/instance/region")
        # should be in the form "projects/<numeric-project-id>/regions/<region>"
        return region.rsplit("/", 1)[-1]
    except Exception as ex:  # pylint:disable=broad-except
        gcf_logger.warning("Error when requesting 'region': %s", ex)
        return None


def _request_metadata(conn: HTTPConnection, path: str) -> str:
    conn.request("GET", path, headers=_GCP_HEADERS)
    response = conn.getresponse()

    if response.status < 200 or response.status > 299:
        return ""

    data = response.read()
    if data is None:
        return ""

    return data.decode("utf-8")
