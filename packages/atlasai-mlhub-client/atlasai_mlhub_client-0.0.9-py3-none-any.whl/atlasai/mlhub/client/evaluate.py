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

import concurrent.futures
import io
import json
import logging
import os
import pandas as pd
import time
from typing import Union

from .constants import DEPLOYMENT_TYPES, DEFAULT_POLLING_TIMEOUT, MAX_BODY_SIZE, POLLING_INTERVAL
from .requests import get_session
from .response import JobResultResponse, JobResponse
from .utils import get_base_url, get_headers, get_model_url, get_deployment_url

logger = logging.getLogger(__name__)

def evaluate(
        model: str, version: str, data: Union[dict, str, pd.DataFrame] = None,
        deployment_type: str = DEPLOYMENT_TYPES.http,
        timeout: int = DEFAULT_POLLING_TIMEOUT,
        wait_for_completion: bool = True,
        tabular: bool = True,
        data_type: str = 'json'
) -> Union[JobResultResponse, JobResponse]:
    """
    Evaluate a specific model with specific data.

    Args:
        model (str): The name of the model you want to evaluate
        version (str): The version of the model you want to evaluate
        deployment_type (str): The type of deployment you want. http or batch.

        data (Union[dict, str, pd.DataFrame]): The data to be sent in the request body.
        timeout (int, optional): Maximum time interval to wait for a response
        wait_for_completion (bool, optional, default: true). Wait for the function to poll for results in case of batch.
            Set to false in case you want to do the polling yourself.
        tabular (bool, default True): How to display the columns if they are list or dict. Tabular format or json
        data_type (str, default: json): The type of the input data. Can be json or csv.

    Returns:
        JobResultResponse: The response object from the evaluation.
        JobResponse: If batch deployment type is true and wait_for_completion is false will return a string with the resource to poll.

    """

    if not os.environ['MLHUB_URL']:
        raise ValueError('MLHUB_URL must be provided.')

    if isinstance(data, pd.DataFrame):
        data = {'dataframe_records': data.to_dict(orient='records')}

    str_data = json.dumps(data) if not isinstance(data, str) else data

    if len(str_data) < MAX_BODY_SIZE:
        body = {'data': data}
    else:
        logger.debug(f'Input data exceeds {MAX_BODY_SIZE} size.')
        if deployment_type != DEPLOYMENT_TYPES.batch:
            raise ValueError(f'Input data size exceeds {MAX_BODY_SIZE} bytes.'
                             f' This is allowed only for batch evaluations.')
        storage_path = upload_data(str_data, data_type)
        body = {'url': storage_path}

    url = f"{get_deployment_url(model, version, deployment_type)}/evaluate"
    session = get_session()
    response = session.post(url, json=body, headers=get_headers(), timeout=timeout)
    response.raise_for_status()

    if response.status_code == 200:
        return JobResultResponse(**response.json(), tabular=tabular)
    elif response.status_code == 202:
        if wait_for_completion:
            return process_polling_response(model, version, response.headers['Location'], timeout=timeout)
        else:
            return JobResponse(model=model, version=version, job_id=response.headers['Location'], tabular=tabular)



def upload_data(data, file_type):
    logger.debug('Requesting signed url.')
    session = get_session()
    url = f"{get_base_url()}/create-signed-url"
    response = session.post(url, json={'file_type': file_type}, headers=get_headers())
    response.raise_for_status()

    response_data = response.json()
    logger.debug('Uploading data to storage.')
    response = session.put(response_data['signed_url'], data=io.StringIO(data), headers=response_data['headers'])
    response.raise_for_status()
    return response_data['storage_path']


def get_job_result(job: JobResponse, timeout: int = DEFAULT_POLLING_TIMEOUT, tabular: bool = True, wait: bool = False):
    """
    Get results for a specific job

    Args:
        job: JobResponse. Object that contains the model, version and resource to poll

        timeout (int, optional): Maximum time interval to wait for a response

        tabular (bool, default True): How to display the columns if they are list or dict. Tabular format or json

        wait (bool, default False): Wait for the job to finish

    Returns:
        JobResultResponse: The response object from the evaluation.

    """
    if not os.environ['MLHUB_URL']:
        raise ValueError('MLHUB_URL must be provided.')

    session = get_session()

    headers = get_headers()
    url = f"{get_model_url(job.model, job.version)}/job/{job.job_id}"

    if wait is True:
        return process_polling_response(job.model, job.version, job.job_id, timeout=timeout)

    response = session.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return JobResultResponse(**response.json(), tabular=tabular)


def process_polling_response(model, version, job_id, timeout=DEFAULT_POLLING_TIMEOUT, tabular=True):
    def poll(_url):
        while True:
            headers = get_headers()
            session = get_session()
            _response = session.get(_url, headers=headers)
            _response.raise_for_status()

            data = _response.json()
            status = data.get("status")
            if status != "InProgress":
                return data

            time.sleep(POLLING_INTERVAL)

    def poll_until_finished(_url):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(poll, _url)
            try:
                done, _ = concurrent.futures.wait([future], timeout=timeout)
                for f in done:
                    return f.result()
            except concurrent.futures.TimeoutError:
                future.cancel()
                raise Exception("Polling timeout")
            except Exception as e:
                logger.error(f"Polling failed: {e}")
                raise e

    url = f"{get_model_url(model, version)}/job/{job_id}"

    response = poll_until_finished(url)
    return JobResultResponse(**response, tabular=tabular)
