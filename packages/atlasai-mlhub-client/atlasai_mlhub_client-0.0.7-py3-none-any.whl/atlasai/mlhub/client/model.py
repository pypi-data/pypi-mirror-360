# Copyright 2024 AtlasAI PBC. All Rights Reserved.
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

import logging

from .constants import DEFAULT_PAGE_SIZE
from .requests import get_session, paginate
from .response import ModelResponse
from .utils import get_base_url, get_headers, get_model_url

logger = logging.getLogger(__name__)


def get_models(limit=DEFAULT_PAGE_SIZE, offset=0, search=None, tabular=True):
    url = f"{get_base_url()}/models"

    for result in paginate(url, limit, offset, search):
        yield ModelResponse(**result, tabular=tabular)


def get_model_info(model, version, tabular=True):
    url = get_model_url(model, version)

    session = get_session()

    response = session.get(url, headers=get_headers())
    response.raise_for_status()

    return ModelResponse(**response.json(), tabular=tabular)
