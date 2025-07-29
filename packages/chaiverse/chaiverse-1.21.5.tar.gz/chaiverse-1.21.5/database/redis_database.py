from typing import Optional

from flatten_dict import flatten
import json
from redis import Redis, exceptions
from redis.commands.json.path import Path
from redis.commands.search.field import TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search import Search
from redis.exceptions import ResponseError

from chaiverse.database.inferno_database_adapter import _InfernoDatabaseAdapter


class _RedisDatabase(_InfernoDatabaseAdapter):
    def __init__(self, url: str, port: int, password: str):
        self.url = url
        self.port = port
        self.password = password
        self.client = Redis(
            url, port=port, username="default", password=password, decode_responses=True
        )
        self.json_client = self.client.json()

    def set(self, path: str, value: dict):
        self._set_json(path, value)

    def get(self, path: str, shallow: bool = False):
        record = self._get_json(path)
        record = record[0] if record else None
        return record

    def update(self, path: str, record: dict):
        self._merge_json(path, record)

    def multi_update(self, path: str, record: dict):
        record = flatten(record, reducer="path", max_flatten_depth=2)
        pipeline = self.json_client.pipeline()
        for key, value in record.items():
            key = f"{path}/{key}"
            self._merge_json(key, value, pipeline=pipeline)
        pipeline.execute()

    def remove(self, path: str):
        key, path = self._get_key_and_path(path)
        self.json_client.delete(key, path)

    def where(self, path: str, **kwargs):
        assert len(kwargs) == 1, "Searching by only one field value is currently supported!"
        field = list(kwargs.keys())[0]
        value = list(kwargs.values())[0]
        results = self._get_filtered_json(path, field, value)
        return results

    def _check_health(self):
        return self.client.ping()

    def _get_json(self, path):
        key, path = self._get_key_and_path(path)
        record = self.json_client.get(key, path)
        return record

    def _get_filtered_json(self, path, field, value):
        key, _ = self._get_key_and_path(path)
        query = f"$..[?(@.{field} == '{value}')]"
        results = self.json_client.get(key, query)
        return results

    def _set_json(self, path, record, pipeline=None):
        pipeline = pipeline if pipeline else self.json_client
        key, path = self._get_key_and_path(path)
        record = _ignore_null_values(record)
        try:
            pipeline.set(key, path, record)
        except exceptions.ResponseError:
            pipeline.set(key, "$", {})
            pipeline.set(key, path, record)

    def _merge_json(self, path, record, pipeline=None):
        pipeline = pipeline if pipeline else self.json_client
        key, path = self._get_key_and_path(path)
        record = _ignore_null_values(record)
        try:
            self.json_client.merge(key, path, record)
        except exceptions.ResponseError:
            pipeline.set(key, "$", {})
            pipeline.merge(key, path, record)

    def _get_key_and_path(self, path):
        path = path.lstrip("/")
        split_path = path.split("/", 1)
        key = split_path[0]
        key = _clean_key(key)
        if len(split_path) > 1:
            path = split_path[1].replace("/", ".")
            path = f"$.{path}"
        else:
            path = "$"
        return key, path


def _clean_key(key):
    key = key.replace("//", "/")
    key = key.lstrip("/")
    return key


def _ignore_null_values(d):
    return {k: v for k,v in d.items() if v is not None}
