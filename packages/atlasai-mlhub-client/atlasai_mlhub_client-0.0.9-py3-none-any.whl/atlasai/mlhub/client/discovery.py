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

import hmac
import logging
import os
from urllib.parse import urlparse
import warnings

import arrow


logger = logging.getLogger(__name__)


def get_url():
    url = os.getenv('DISCOVERY_GRAPHQL_URL')
    if not url:
        raise RuntimeError(f'Missing Discovery GraphQL URL. Provide the Environment variable: DISCOVERY_GRAPHQL_URL')
    return url


def get_secret_data(secret_id):
    try:
        from google.api_core.retry import Retry
        from google.cloud import secretmanager
    except ImportError:
        logger.warning('Client library not found: google-cloud-secret-manager')
        return None

    try:
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(
            request={
                'name': secret_id,
            },
            retry=Retry(),
        )
    except Exception as e:
        logger.error(f'Error getting data from Secret Manager: {secret_id} {e}')
        raise
    else:
        return response.payload.data.decode('utf-8')

def load_credentials(access_key=None, secret_key=None):
    access_key = access_key or os.getenv('DISCOVERY_ACCESS_KEY')
    secret_key = secret_key or os.getenv('DISCOVERY_SECRET_KEY')
    api_secret = os.getenv('DISCOVERY_API_SECRET')

    if not secret_key and api_secret:
        secret_key = get_secret_data(api_secret)
        if secret_key is not None:
            os.environ['DISCOVERY_SECRET_KEY'] = secret_key

    return access_key, secret_key


def include_authorization(url, headers, bearer_token=None, access_key=None, secret_key=None):
    bearer_token = bearer_token or os.getenv('DISCOVERY_BEARER_TOKEN')
    access_key, secret_key = load_credentials(
        access_key=access_key,
        secret_key=secret_key,
    )

    if bearer_token:
        headers['Authorization'] = f'Bearer {bearer_token}'
        return

    if not access_key and not secret_key:
        warnings.warn('No API Keys provided to access Discovery GraphQL. Provide the following: DISCOVERY_BEARER_TOKEN or the pair DISCOVERY_ACCESS_KEY and DISCOVERY_SECRET_KEY')
        return
    elif any([
        access_key is None,
        secret_key is None,
    ]):
        raise ValueError('DISCOVERY_ACCESS_KEY and DISCOVERY_SECRET_KEY must be provided together')

    product, version = 'discovery', '1'
    headers.update({
        'Host': urlparse(url).netloc,
        'X-Discovery-Date': arrow.utcnow().isoformat(),
        'X-Discovery-Credential': '/'.join([product, version, access_key]),
        'X-Discovery-SignedHeaders': 'x-discovery-date;x-discovery-credential;host',
    })

    sign_request(headers, secret_key)


def sign_request(headers, secret_key):
    product, version, access_key = headers['X-Discovery-Credential'].split('/')
    key = f'{product}{version}{secret_key}'.encode('utf-8')
    for msg in (
        headers['X-Discovery-Date'],
        f'{product}_{version}_request',
    ):
        obj = hmac.new(key, msg.encode('utf-8'), 'sha256')
        key = obj.digest()

    msg = '\n'.join([
        headers['X-Discovery-Date'],
        headers['X-Discovery-Credential'],
        headers['Host']
    ])
    headers['X-Discovery-Signature'] = hmac.new(key, msg.encode('utf-8'), 'sha256').hexdigest()
