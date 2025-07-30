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

from types import SimpleNamespace

HTTP = 'http'
BATCH = 'batch'

DEPLOYMENT_TYPES = SimpleNamespace(
    http=HTTP,
    batch=BATCH
)

DEFAULT_POLLING_TIMEOUT = 3600
DEFAULT_PAGE_SIZE = 100

MAX_BODY_SIZE = 30 * 1024 * 1024

POLLING_INTERVAL = 10

DISABLE_SSL_VERIFICATION = 'DISABLE_SSL_VERIFICATION'
