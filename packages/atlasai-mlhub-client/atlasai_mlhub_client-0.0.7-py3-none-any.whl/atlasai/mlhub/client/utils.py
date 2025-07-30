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

import os
import pandas as pd

def validate_request_headers(headers):
    if not headers.get('Authorization'):
        raise Exception('No Authorization token found. Authenticate first')


def get_headers():
    headers = {"Content-Type": "application/json"}

    if os.getenv('ATLASAI_TOKEN'):
        headers['Authorization'] = f'Bearer {os.getenv("ATLASAI_TOKEN")}'

    validate_request_headers(headers)
    return headers

def get_model_url(model, version):
    return f"{get_base_url()}/model/{model}/version/{version}"

def get_deployment_url(model, version, deployment_type):
    return f"{get_model_url(model, version)}/deployment/{deployment_type}"

def get_base_url():
    return f"{os.environ['MLHUB_URL']}"


def flatten_nested_json_df(df, flatten_depth=-1, flatten_columns=None, should_drop=True):
    if flatten_depth == 0:
        return df

    flatten_counter = 0
    if flatten_columns is None:
        flatten_columns = df.keys()
    elif isinstance(flatten_columns, str):
        flatten_columns = [flatten_columns]

    def should_flatten():
        return flatten_depth == -1 or flatten_counter < flatten_depth

    def is_flattenable(col):
        return col.split('.')[0] in flatten_columns

    def get_all_columns_of_type(_type, current_index=None):
        s = ((df if current_index is None else df[current_index]).map(type) == _type).any()
        res = s[s].index.tolist()
        if _type == dict:
            res = [column for column in res if is_flattenable(column)]
        return res

    list_columns = get_all_columns_of_type(list)
    dict_columns = get_all_columns_of_type(dict)
    columns_to_drop = []
    while should_flatten() and (len(list_columns) > 0 or len(dict_columns) > 0):
        new_columns = []
        to_expand = []

        for col in dict_columns:
            horiz_exploded = pd.json_normalize(df[col]).add_prefix(f'{col}.')
            horiz_exploded.index = df.index
            to_expand.append(horiz_exploded)
            new_columns.extend(horiz_exploded.columns)

        if dict_columns:
            columns_to_drop.extend(dict_columns)

        for col in list_columns:
            horiz_exploded = pd.json_normalize(df[col]).add_prefix(f'{col}.')
            to_expand.append(horiz_exploded)
            new_columns.extend(horiz_exploded.columns)

        if to_expand:
            df = pd.concat([df, *to_expand], axis=1)

        list_columns = get_all_columns_of_type(list, new_columns)
        dict_columns = get_all_columns_of_type(dict, new_columns)
        flatten_counter += 1

    if columns_to_drop and should_drop:
        df = df.drop(columns=columns_to_drop)
    return df
