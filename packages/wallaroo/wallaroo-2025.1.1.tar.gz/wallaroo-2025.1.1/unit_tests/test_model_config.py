import datetime

import pytest
import responses

import wallaroo
from wallaroo.dynamic_batching_config import DynamicBatchingConfig
from wallaroo.model_config import ModelConfig

from . import testutil


class TestModelConfig:
    def setup_method(self):
        self.now = datetime.datetime.now()
        self.gql_client = testutil.new_gql_client(endpoint="http://api-lb/v1/graphql")
        self.test_client = wallaroo.Client(
            gql_client=self.gql_client,
            auth_type="test_auth",
            api_endpoint="http://api-lb",
            config={"default_arch": "x86"},
        )

    @responses.activate
    def test_init_full_dict(self):
        model_config = ModelConfig(
            client=self.test_client,
            data={
                "id": 1,
                "filter_threshold": 0.1234,
                "model": {
                    "id": 2,
                },
                "runtime": "onnx",
                "tensor_fields": ["foo", "bar", "baz"],
                "dynamic_batching_config": {
                    "max_batch_delay_ms": 10,
                    "batch_size_target": 4,
                    "batch_size_limit": 10,
                },
            },
        )

        assert 1 == model_config.id()
        assert 0.1234 == model_config.filter_threshold()
        assert 2 == model_config.model_version().id()
        assert "onnx" == model_config.runtime()
        assert ["foo", "bar", "baz"] == model_config.tensor_fields()
        assert isinstance(model_config.dynamic_batching_config(), DynamicBatchingConfig)
        assert 10 == model_config.dynamic_batching_config().max_batch_delay_ms

    @pytest.mark.parametrize(
        "method_name, want_value",
        [
            ("filter_threshold", 0.1234),
            ("runtime", "onnx"),
            ("tensor_fields", ["foo", "bar"]),
            ("dynamic_batching_config", None),
        ],
    )
    @responses.activate
    def test_rehydrate(self, method_name, want_value):
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("ModelConfigById")],
            json={
                "data": {
                    "model_config_by_pk": {
                        "id": 1,
                        "filter_threshold": 0.1234,
                        "model": {
                            "id": 2,
                        },
                        "runtime": "onnx",
                        "tensor_fields": ["foo", "bar"],
                        "dynamic_batching_config": None,
                    },
                },
            },
        )

        model_config = ModelConfig(client=self.test_client, data={"id": 1})

        assert want_value == getattr(model_config, method_name)()
        assert 1 == len(responses.calls)
        # Another call to the same accessor shouldn't trigger any
        # additional GraphQL queries.
        assert want_value == getattr(model_config, method_name)()
        assert 1 == len(responses.calls)
        responses.reset()
