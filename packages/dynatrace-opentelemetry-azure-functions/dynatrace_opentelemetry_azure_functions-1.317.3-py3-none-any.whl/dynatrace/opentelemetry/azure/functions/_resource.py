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
import re
from typing import Dict, Optional, Tuple

from azure.functions import Context
from opentelemetry.util.types import AttributeValue

from dynatrace.odin.semconv import v1 as semconv
from dynatrace.opentelemetry.tracing._logging.loggers import azure_logger

_ENV_KEY_FAAS_APP = "WEBSITE_SITE_NAME"
_ENV_KEY_OWNER = "WEBSITE_OWNER_NAME"
_ENV_KEY_RESOURCE_GROUP = "WEBSITE_RESOURCE_GROUP"
_ENV_KEY_REGION = "REGION_NAME"

# example: af7ce8a8-ec27-4b24-af88-324b2712077a+GstHttp1Res-GermanyWestCentralwebspace-Linux
_OWNER_PATTERN = re.compile(
    r"(?P<subscription>[^+]+)\+(?P<group>.+)-(?P<region>[^-]+)webspace(?:-[^-]+)?"
)


def detect_resource(context: Optional[Context]) -> Dict[str, AttributeValue]:
    attributes = {
        semconv.CLOUD_PROVIDER: semconv.CloudProviderValues.AZURE.value,
        semconv.CLOUD_PLATFORM: semconv.CloudPlatformValues.AZURE_FUNCTIONS.value,
    }

    function_name = context and context.function_name
    func_app_name = os.getenv(_ENV_KEY_FAAS_APP)

    if function_name:
        attributes[semconv.FAAS_NAME] = (
            f"{func_app_name}/{function_name}"
            if func_app_name
            else function_name
        )
    else:
        azure_logger.warning("unable to detect '%s'", semconv.FAAS_NAME)

    owner, resource_group, region, subscription_id = _get_faas_id_parts()

    if region:
        attributes[semconv.CLOUD_REGION] = region
    else:
        azure_logger.warning(
            "unable to detect '%s' - owner: %s", semconv.CLOUD_REGION, owner
        )

    if resource_group and subscription_id and function_name and func_app_name:
        attributes[semconv.FAAS_ID] = (
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Web/sites/{func_app_name}"
            f"/functions/{function_name}"
        )
    else:
        azure_logger.warning(
            "unable to detect '%s' - resource_group: %s, subscription_id: %s, "
            "function_app_name: %s, function_name: %s, owner: %s",
            semconv.FAAS_ID,
            resource_group,
            subscription_id,
            func_app_name,
            function_name,
            owner,
        )

    azure_logger.debug("detected resource: %s", attributes)

    return attributes


def _get_faas_id_parts() -> (
    Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]
):
    owner = os.getenv(_ENV_KEY_OWNER)
    resource_group = os.getenv(_ENV_KEY_RESOURCE_GROUP)
    region = os.getenv(_ENV_KEY_REGION)
    subscription_id = None
    if owner:
        match = _OWNER_PATTERN.fullmatch(owner)
        if match:
            subscription_id = match.group("subscription")
            if not resource_group:
                resource_group = match.group("group")
            if not region:
                region = match.group("region")
    else:
        azure_logger.warning("unable to detect owner")

    return owner, resource_group, region, subscription_id
