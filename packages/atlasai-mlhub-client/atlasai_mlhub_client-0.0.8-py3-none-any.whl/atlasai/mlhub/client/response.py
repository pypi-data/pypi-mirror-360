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

import inspect
import pandas as pd

from .output import render_block, render_table
from .requests import get_session
from .utils import flatten_nested_json_df

class SingleResponse:
    def get_properties(self):
        return [name for name, member in inspect.getmembers(self.__class__, lambda x: isinstance(x, property))]

    def as_df(self):
        return flatten_nested_json_df(pd.json_normalize(self.as_dict()))

    def as_dict(self):
        return {prop: getattr(self, '_' + prop) for prop in self.get_properties() if hasattr(self, '_' + prop)}


class JobResponse(SingleResponse):

    def __init__(self, model, version, job_id, tabular=True):
        self._model = model
        self._version = version
        self._job_id = job_id
        self._tabular = tabular

    @property
    def model(self):
        return self._model

    @property
    def version(self):
        return self._version

    @property
    def job_id(self):
        return self._job_id

    def __repr__(self):
        return f'JobResponse(job_id={self.job_id})'


class JobResultResponse(SingleResponse):
    def __init__(self,
        status, info, predictions=None, url=None, tabular=True
    ):
        self._status = status
        self._info = info
        self._tabular = tabular
        self._predictions = predictions
        self._url = url
        if url:
            self._predictions = self.get_data_from_path(url)


    @property
    def status(self):
        return self._status

    @property
    def info(self):
        return self._info

    @property
    def predictions(self):
        if self._tabular is False or not isinstance(self._predictions, list):
            return self._predictions
        return pd.DataFrame(self._predictions, columns=['Predictions'])


    def get_data_from_path(self, url):
        session = get_session()
        response = session.get(url)
        response.raise_for_status()
        return response.json()

    def __str__(self):
        return f'Status: {self.status}'

    def __repr__(self):
        return f'JobResultResponse(status={self.status})'

class JobInfoResponse(SingleResponse):
    def __init__(self, id, job_id, user_id, deployment_type, data, tabular=True):
        self._id = id
        self._job_id = job_id
        self._user_id = user_id
        self._deployment_type = deployment_type
        self._data = data
        self._tabular = tabular

    @property
    def id(self):
        return self._id

    @property
    def job_id(self):
        return self._job_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def deployment_type(self):
        return self._deployment_type

    @property
    def data(self):
        if self._tabular is False:
            return self._data
        return flatten_nested_json_df(pd.json_normalize(self._data or []))

    def __repr__(self):
        return f'JobInfoResponse(job_id={self.job_id})'


class ModelResponse(SingleResponse):

    def __init__(self,
        id, name, version, tags, aliases, signature, input_example,
        metrics, retired, retired_date, create_date, source, config,
        deployments=None, tabular=True
    ):
        self._id = id
        self._name = name
        self._version = version
        self._source = source
        self._retired = retired
        self._retired_date = retired_date
        self._create_date = create_date
        self._tabular = tabular
        self._tags = tags
        self._aliases = aliases
        self._inputs = signature.get('inputs', [])
        self._outputs = signature.get('outputs', [])
        self._params = signature.get('params', [])
        self._input_example = input_example
        self._metrics = metrics
        self._config = config
        self._deployments = deployments or []

        if isinstance(self._tags, str):
            self._tags = {self._tags: 'True'}

    def __str__(self):
        return f'Version {self.version} of {self.name}'

    def __repr__(self):
        return f'ModelResponse(name={self.name}, version={self.version})'

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def deployments(self):
        return self._deployments

    @property
    def retired(self):
        return self._retired

    @property
    def retired_date(self):
        return self._retired_date

    @property
    def create_date(self):
        return self._create_date

    @property
    def metrics(self):
        if self._tabular is False:
            return self._metrics
        return pd.DataFrame(self._metrics, index=[0])

    @property
    def tags(self):
        if self._tabular is False:
            return self._tags
        return pd.DataFrame(self._tags or {}, index=[0])

    @property
    def aliases(self):
        if self._tabular is False:
            return self._aliases
        return pd.DataFrame(self._aliases or [])

    @property
    def inputs(self):
        if self._tabular is False:
            return self._inputs
        return pd.json_normalize(self._inputs or [])

    @property
    def outputs(self):
        if self._tabular is False:
            return self._outputs
        return pd.json_normalize(self._outputs or [])

    @property
    def params(self):
        if self._tabular is False:
            return self._params
        return pd.json_normalize(self._params or [])

    @property
    def input_example(self):
        if self._tabular is False:
            return self._input_example
        return pd.json_normalize(self._input_example or [])

    @property
    def signature(self):
        if self._tabular is False:
            return {'inputs': self.inputs, 'outputs': self.outputs, 'params': self.params}
        inputs, outputs, params = self.inputs, self.outputs, self.params
        inputs['_type'], outputs['_type'], params['_type'] = 'input', 'output', 'param'

        return pd.concat([inputs, outputs, params], ignore_index=True)

    def describe(self):
        render_block(f'Model: {self.name}', f'Version: {self.version}')
        render_block('Created at', self.create_date)
        render_block('Deployments', ' | '.join(self._deployments) or 'No available deployments')
        render_table('Tags', self._tags)
        render_table('Aliases', self._aliases)
        render_table('Model Inputs', self._inputs)
        render_table('Model Outputs', self._outputs)
        render_table('Parameters', self._params)
