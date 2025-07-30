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
import os

from furl import furl
import requests

from . import discovery

logger = logging.getLogger(__name__)


def authenticate(env_name='ATLASAI_TOKEN'):
    """
     Authenticate with Discovery

     Returns an OAuth2 Access Token

     If `env_name` provided, the Access Token will be saved
     to the named environment variable

     #### Usage

     ```python
     from atlasai.mlhub import client

     token = client.authenticate(<OPTIONAL_ENV_VARIABLE_NAME>)
     ```
     """

    f = furl(discovery.get_url())
    f.path = 'token'
    url = f.url
    headers = {}
    discovery.include_authorization(url, headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    token = data['access_token']

    if env_name:
        os.environ[env_name] = token

    user_id = data.get('email') or data.get('sub') or 'AtlasAI Employee'
    os.environ['LOGNAME'] = user_id

    return token
