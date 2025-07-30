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

"""
## Helpers for Requests package
"""

import os

import requests
from requests.adapters import HTTPAdapter, Retry
from .constants import DEFAULT_PAGE_SIZE, DISABLE_SSL_VERIFICATION
from .utils import get_headers


STATUS_FORCELIST = tuple([429, 500, 502, 503, 504])

def mount_retry(
    session,
    total=10,
    backoff_factor=0.2,
    allowed_methods=None,
    status_forcelist=STATUS_FORCELIST,
):
    """
    Attach retry handlers to HTTP and HTTPS endpoints of a Requests Session
    """

    retries = Retry(
        total=total,
        backoff_factor=backoff_factor,
        allowed_methods=allowed_methods,
        status_forcelist=status_forcelist,
    )

    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

def get_session(
    total=10,
    backoff_factor=0.2,
    allowed_methods=None,
    status_forcelist=STATUS_FORCELIST,
):
    """
    Get a Requests Session with retry handlers for HTTP and HTTPS endpoints
    """

    sess = requests.Session()
    if os.getenv(DISABLE_SSL_VERIFICATION):
        sess.verify = False
    mount_retry(
        sess,
        total=total,
        backoff_factor=backoff_factor,
        allowed_methods=allowed_methods,
        status_forcelist=status_forcelist,
    )

    return sess

def paginate(url, limit=None, offset=0, search=None):
    if limit is None:
        limit = DEFAULT_PAGE_SIZE

    if search is None:
        search = {}

    def _get_results(_url, _limit, _offset=0):
        _response = session.post(_url, json={'limit': _limit, 'offset': _offset, 'search': search}, headers=get_headers())
        _response.raise_for_status()
        return _response

    session = get_session()
    while True:
        response = _get_results(url, limit, offset)
        data = response.json()['data']
        for result in data:
            yield result

        if not data:
            break

        offset += limit
