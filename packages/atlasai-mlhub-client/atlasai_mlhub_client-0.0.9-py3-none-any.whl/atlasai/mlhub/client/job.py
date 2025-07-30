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
from .requests import paginate
from .response import JobInfoResponse
from .utils import get_model_url


logger = logging.getLogger(__name__)

def get_jobs(model, version, limit=DEFAULT_PAGE_SIZE, offset=0, tabular=True):
    url = f"{get_model_url(model, version)}/jobs"

    for result in paginate(url, limit, offset):
        yield JobInfoResponse(**result, tabular=tabular)
