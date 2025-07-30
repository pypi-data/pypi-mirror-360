# Copyright 2024 Superlinked, Inc.
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

import json
import os

import structlog
from beartype.typing import Any

logger = structlog.getLogger(__name__)


class OpenApiDescriptionUtil:
    @staticmethod
    def get_open_api_description_by_key(key: str, file_path: str | None = None) -> dict[str, Any]:
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), "..", "openapi", "static_endpoint_descriptor.json")
        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)
            open_api_description = data.get(key)
            if open_api_description is None:
                logger.warning("no OpenAPI description was found for the provided key", key=key)
            return open_api_description
