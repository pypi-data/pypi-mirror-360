import datetime
import json
import time

import httpx
import numpy
import pandas as pd
import pyarrow as pa
import pytest
import responses
import respx

import wallaroo
from wallaroo.deployment import (
    Deployment,
    WaitForDeployError,
    _hack_pandas_dataframe_order,
)
from wallaroo.exceptions import InferenceError, InferenceTimeoutError
from wallaroo.model_config import ModelConfig
from wallaroo.model_version import ModelVersion
from wallaroo.object import CommunicationError, EntityNotFoundError
from wallaroo.pipeline_version import PipelineVersion

from . import status_samples, testutil
from .reusable_responders import add_insert_model_config_response

SAMPLE_ARROW_FILE = "unit_tests/outputs/dev_smoke_test.arrow"
SAMPLE_PANDAS_RECORDS_FILE = "unit_tests/outputs/dev_smoke_test.pandas.json"
SAMPLE_PANDAS_RECORDS_INFERENCE_RESPONSE = json.load(
    open("unit_tests/outputs/sample_inference_result.pandas.json", "rb")
)
SAMPLE_PANDAS_RECORDS_INFERENCE_LIMITED_RESPONSE = json.load(
    open("unit_tests/outputs/sample_inference_limited_result.pandas.json", "rb")
)

sink = pa.BufferOutputStream()
with pa.ipc.open_file("unit_tests/outputs/sample_inference_result.arrow") as reader:
    infer_result_table = reader.read_all()
    with pa.ipc.new_file(sink, infer_result_table.schema) as arrow_ipc:
        arrow_ipc.write(infer_result_table)
        arrow_ipc.close()
SAMPLE_ARROW_INFERENCE_RESULT_TABLE = infer_result_table
SAMPLE_ARROW_INFERENCE_RESPONSE = sink.getvalue()
with open("unit_tests/outputs/dev_smoke_test.pandas.json", "r") as fp:
    SAMPLE_PANDAS_RECORDS_JSON = pd.read_json(fp)


class TestDeployment:
    def setup_method(self):
        self.now = datetime.datetime.now()
        self.gql_client = testutil.new_gql_client(endpoint="http://api-lb/v1/graphql")
        self.test_client = wallaroo.Client(
            api_endpoint="http://api-lb:1234",
            gql_client=self.gql_client,
            auth_type="test_auth",
            config={"default_arch": "x86"},
            request_timeout=2,  # this field used only by deployment.wait_for_running() tests
        )

        self.gql_client = testutil.new_gql_client(endpoint="http://foo.org/v1/graphql")
        self.remote_test_client = wallaroo.Client(
            api_endpoint="http://foo.api.org:1234",
            auth_type="test_auth",
            gql_client=self.gql_client,
            config={"default_arch": "x86"},
            request_timeout=2,  # this field used only by deployment.wait_for_running() tests
        )

    def assert_wait_for_running(self, deployment, exception_type):
        """Expects a timeout and exception type"""
        begtime = time.time()
        with pytest.raises(exception_type):
            res = deployment.wait_for_running()
        endtime = time.time()
        elapsed = endtime - begtime
        assert 1.0 <= elapsed <= self.test_client.timeout + 3

    @responses.activate
    def test_init_full_dict(self):
        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some_deployment_name",
                "deployed": False,
                "deployment_model_configs": [
                    {
                        "model_config": {
                            "id": 2,
                        },
                    },
                ],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 3,
                        }
                    }
                ],
            },
        )

        assert 1 == deployment.id()
        assert "some_deployment_name" == deployment.name()
        assert False is deployment.deployed()
        assert isinstance(deployment.model_configs()[0], ModelConfig)
        assert isinstance(deployment.pipeline_versions()[0], PipelineVersion)

    @pytest.mark.parametrize(
        "method_name, want_value",
        [
            ("name", "some_deployment_name"),
            ("deployed", False),
            ("model_configs", None),
            ("pipeline_versions", None),
        ],
    )
    @responses.activate
    def test_rehydrate(self, method_name, want_value):
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("DeploymentById")],
            json={
                "data": {
                    "deployment_by_pk": {
                        "id": 1,
                        "deploy_id": "some_deployment_name",
                        "deployed": False,
                        "deployment_model_configs": [
                            {
                                "model_config": {
                                    "id": 2,
                                },
                            },
                        ],
                        "deployment_pipeline_versions": [
                            {
                                "pipeline_version": {
                                    "id": 3,
                                }
                            }
                        ],
                    },
                },
            },
        )

        deployment = Deployment(client=self.test_client, data={"id": 1})
        got_value = getattr(deployment, method_name)()

        if want_value is not None:
            assert want_value == got_value
        assert 1 == len(responses.calls)
        # Another call to the same accessor shouldn't trigger any
        # additional GraphQL queries.
        got_value = getattr(deployment, method_name)()
        if want_value is not None:
            assert want_value == got_value
        assert 1 == len(responses.calls)
        responses.reset()

    @responses.activate
    def test_infer_from_file_with_arrow(self):
        responses.add(
            responses.POST,
            url="http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
            body=SAMPLE_ARROW_INFERENCE_RESPONSE,
        )
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.json_body_printer()],
        )
        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
                "pipeline": {
                    "pipeline_id": "some-pipeline",
                },
            },
        )

        output = deployment.infer_from_file(SAMPLE_ARROW_FILE)

        assert isinstance(output, pa.Table)
        output.equals(infer_result_table)

    def test_pandas_order_hack(self):
        # hacky fake aloha-like data
        columns = [
            "out.banjori",
            "out.cryptolocker",
            "out.main",
            "out.dircrypt",
            "out._model_split",
            "out.ramdo",
            "time",
            "out.suppobox",
            "out.ramnit",
            "out.corebot",
            "out.pykspa",
            "out.gozi",
            "out.matsnu",
            "in.text_input",
            "out.qakbot",
            "out.locky",
            "out.simda",
            "out.kraken",
        ]
        df = pd.DataFrame(data=[list(range(len(columns)))] * 10, columns=columns)

        fixed = _hack_pandas_dataframe_order(df)

        assert list(fixed.columns)[:4] == [
            "time",
            "in.text_input",
            "out._model_split",
            "out.banjori",
        ]

    @responses.activate
    def test_infer_from_file_with_pandas_records(self):
        result_df = pd.DataFrame.from_records(SAMPLE_PANDAS_RECORDS_INFERENCE_RESPONSE)

        responses.add(
            responses.POST,
            url="http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
            json=SAMPLE_PANDAS_RECORDS_INFERENCE_RESPONSE,
        )
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.json_body_printer()],
        )
        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
                "pipeline": {
                    "pipeline_id": "some-pipeline",
                },
            },
        )

        output_df = deployment.infer_from_file(SAMPLE_PANDAS_RECORDS_FILE)
        assert isinstance(output_df, pd.DataFrame)
        assert type(output_df["time"][0]) == pd.Timestamp
        assert type(output_df["check_failures"][0]) == numpy.int64

    @responses.activate
    def test_infer_from_file_with_invalid_file_type(self):
        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
            },
        )
        with pytest.raises(TypeError):
            output = deployment.infer_from_file("unit_tests/outputs/dev_smoke_test.txt")

    @responses.activate
    def test_infer_with_arrow(self):
        with pa.ipc.open_file("unit_tests/outputs/dev_smoke_test.arrow") as source:
            table = source.read_all()

        responses.add(
            responses.POST,
            url="http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
            body=SAMPLE_ARROW_INFERENCE_RESPONSE,
        )

        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
                "pipeline": {
                    "pipeline_id": "some-pipeline",
                },
            },
        )

        output = deployment.infer(table)
        assert isinstance(output, pa.Table)
        assert output["time"].type == pa.timestamp(unit="ms")
        assert output["check_failures"].type == pa.int8()

        # Infer should check its tensor type
        with pytest.raises(TypeError):
            deployment.infer(123)

        with pytest.raises(TypeError):
            deployment.infer("foo")

    @responses.activate
    def test_infer_with_pandas_returns_503(self):
        responses.add(
            responses.POST,
            url="http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
            json={},
            status=503,
        )

        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
                "pipeline": {
                    "pipeline_id": "some-pipeline",
                },
            },
        )

        with pytest.raises(InferenceError):
            deployment.infer(SAMPLE_PANDAS_RECORDS_JSON)

        # first call plus 10 retries
        assert len(responses.calls) == 11

    @responses.activate
    def test_infer_raises_connection_timeout(self, mocker):
        mocker.patch(
            "wallaroo.deployment.requests.post",
            side_effect=ConnectionError,
        )

        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
                "pipeline": {
                    "pipeline_id": "some-pipeline",
                },
            },
        )

        with pytest.raises(InferenceTimeoutError):
            deployment.infer(SAMPLE_PANDAS_RECORDS_JSON)

    @responses.activate
    def test_infer_with_pandas_records(self):
        data_df = pd.DataFrame.from_records(SAMPLE_PANDAS_RECORDS_INFERENCE_RESPONSE)

        responses.add(
            responses.POST,
            url="http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
            json=SAMPLE_PANDAS_RECORDS_INFERENCE_RESPONSE,
        )

        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
                "pipeline": {
                    "pipeline_id": "some-pipeline",
                },
            },
        )

        output_df = deployment.infer(SAMPLE_PANDAS_RECORDS_JSON)
        assert isinstance(output_df, pd.DataFrame)
        assert type(output_df["time"][0]) == pd.Timestamp
        assert type(output_df["check_failures"][0]) == numpy.int64

        # Infer should check its tensor type
        with pytest.raises(TypeError):
            deployment.infer(123)

        with pytest.raises(TypeError):
            deployment.infer("foo")

    @responses.activate
    def test_infer_with_pandas_with_some_fields_excluded(self):
        responses.add(
            responses.POST,
            url="http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
            json=SAMPLE_PANDAS_RECORDS_INFERENCE_LIMITED_RESPONSE,
        )

        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
                "pipeline": {
                    "pipeline_id": "some-pipeline",
                },
            },
        )

        output_df = deployment.infer(SAMPLE_PANDAS_RECORDS_JSON, dataset=["in", "out"])
        assert isinstance(output_df, pd.DataFrame)
        assert "time" not in output_df.columns
        assert "check_failures" not in output_df.columns

    @responses.activate
    def test_replace_configured_model(self):
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.mutation_name_matcher("ReplaceModel")],
            json={
                "data": {
                    "insert_deployment_model_configs": {
                        "id": 1,
                        "deployment_id": 2,
                        "model_config_id": 3,
                    },
                },
            },
        )
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("DeploymentById")],
            json={
                "data": {
                    "deployment_by_pk": {
                        "id": 2,
                        "deploy_id": "some_deployment_name",
                        "deployed": True,
                        "deployment_model_configs": [
                            {
                                "model_config": {
                                    "id": 3,
                                },
                            },
                        ],
                    },
                },
            },
        )
        mc = ModelConfig(client=self.test_client, data={"id": 3})
        d = Deployment(client=self.test_client, data={"id": 2})

        d = d.replace_configured_model(mc)

        assert 2 == d.id()
        assert 3 == d.model_configs()[0].id()

    @responses.activate
    def test_replace_model(self):
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("ModelById")],
            json={
                "data": {
                    "model_by_pk": {
                        "id": 3,
                        "sha": "adfasdfaf",
                        "model_id": "some_model_name",
                        "model_version": "some_model_variant_name",
                        "file_name": "some_model_file.onnx",
                        "updated_at": self.now.isoformat(),
                    },
                },
            },
        )
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.mutation_name_matcher("ConfigureModel")],
            json={
                "data": {
                    "insert_model_config": {
                        "returning": [
                            {
                                "id": 4,
                            }
                        ]
                    }
                }
            },
        )
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.mutation_name_matcher("ReplaceModel")],
            json={
                "data": {
                    "insert_deployment_model_configs": {
                        "id": 1,
                        "deployment_id": 2,
                        "model_config_id": 4,
                    },
                },
            },
        )
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("DeploymentById")],
            json={
                "data": {
                    "deployment_by_pk": {
                        "id": 2,
                        "deploy_id": "some_deployment_name",
                        "deployed": True,
                        "deployment_model_configs": [
                            {
                                "model_config": {
                                    "id": 4,
                                },
                            },
                        ],
                    },
                },
            },
        )
        add_insert_model_config_response(self.test_client.api_endpoint)
        mv = ModelVersion(client=self.test_client, data={"id": 3})
        d = Deployment(client=self.test_client, data={"id": 2})

        d = d.replace_model(mv)

        assert 2 == d.id()
        assert 4 == d.model_configs()[0].id()

    @responses.activate
    def test_status_model(self):
        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some_deployment_name",
                "deployed": False,
                "deployment_model_configs": [
                    {
                        "model_config": {
                            "id": 2,
                            "model": {
                                "id": 3,
                                "model_id": "foo-model",
                                "model_version": "v1",
                            },
                        },
                    },
                ],
                "deployment_pipeline_versions": [],
            },
        )
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("QueryLimitStatus")],
            json={"data": {"deployment": []}},
        )

        # missing server case
        with pytest.raises(CommunicationError):
            res = deployment.status()

        self.assert_wait_for_running(deployment, CommunicationError)

        # no such model
        responses.add(
            responses.POST,
            "http://api-lb:1234/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher(
                    {"name": "some_deployment_name-1"}
                )
            ],
            status=404,
        )
        with pytest.raises(EntityNotFoundError):
            res = deployment.status()
        self.assert_wait_for_running(deployment, WaitForDeployError)

        responses.replace(
            responses.POST,
            "http://api-lb:1234/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher(
                    {"name": "some_deployment_name-1"}
                )
            ],
            status=200,
            json=status_samples.ERROR,
        )
        res = deployment.status()
        assert res["status"] == "Error"
        self.assert_wait_for_running(deployment, WaitForDeployError)

        responses.replace(
            responses.POST,
            "http://api-lb:1234/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher(
                    {"name": "some_deployment_name-1"}
                )
            ],
            status=200,
            json=status_samples.RUNNING,
        )
        res = deployment.status()
        assert res["status"] == "Running"
        begtime = time.time()
        dep = deployment.wait_for_running()
        endtime = time.time()
        elapsed = endtime - begtime
        assert elapsed <= 1
        assert dep is not None
        assert isinstance(dep, Deployment)

    @responses.activate
    def test_status_pipeline(self):
        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some_deployment_name",
                "deployed": False,
                "deployment_model_configs": [
                    {
                        "model_config": {
                            "id": 2,
                        },
                    },
                ],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 3,
                        }
                    }
                ],
            },
        )

        # missing server case
        with pytest.raises(CommunicationError):
            res = deployment.status()

        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("QueryLimitStatus")],
            json={"data": {"deployment": []}},
        )

        self.assert_wait_for_running(deployment, CommunicationError)

        # no such model
        responses.add(
            responses.POST,
            "http://api-lb:1234/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher(
                    {"name": "some_deployment_name-1"}
                )
            ],
            status=404,
        )
        with pytest.raises(EntityNotFoundError):
            res = deployment.status()
        self.assert_wait_for_running(deployment, WaitForDeployError)

        responses.replace(
            responses.POST,
            "http://api-lb:1234/v1/api/status/get_deployment",
            status=200,
            json=status_samples.ERROR,
        )
        res = deployment.status()
        assert res["status"] == "Error"
        self.assert_wait_for_running(deployment, WaitForDeployError)

        responses.replace(
            responses.POST,
            "http://api-lb:1234/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher(
                    {"name": "some_deployment_name-1"}
                )
            ],
            status=200,
            json=status_samples.RUNNING,
        )
        res = deployment.status()
        assert res["status"] == "Running"

        begtime = time.time()
        dep = deployment.wait_for_running()
        endtime = time.time()
        elapsed = endtime - begtime
        assert elapsed <= 1
        assert dep is not None
        assert isinstance(dep, Deployment)

    def test_url(self):
        deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some_deployment_name",
                "deployed": False,
                "deployment_model_configs": [
                    {
                        "model_config": {
                            "id": 2,
                        },
                    },
                ],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 3,
                        }
                    }
                ],
                "pipeline": {
                    "pipeline_id": "some_deployment_name",
                },
            },
        )
        assert (
            deployment.url()
            == "http://engine-lb.some_deployment_name-1:29502/pipelines/some_deployment_name"
        )

    def test_external_url(self):
        deployment = Deployment(
            client=self.remote_test_client,
            data={
                "id": 1,
                "deploy_id": "some_deployment_name",
                "deployed": False,
                "deployment_model_configs": [
                    {
                        "model_config": {
                            "id": 2,
                        },
                    },
                ],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 3,
                        }
                    }
                ],
                "pipeline": {
                    "pipeline_id": "some_pipeline_name",
                },
            },
        )
        print(deployment.url())
        assert (
            deployment.url()
            == "http://foo.api.org:1234/v1/api/pipelines/infer/some_deployment_name-1/some_pipeline_name"
        )

    @pytest.mark.parametrize(
        "json_data, expected",
        [
            # Valid pandas records format
            ([{"a": 1, "b": 2}, {"a": 3, "b": 4}], True),
            # Data that is not a list
            ({"a": 1, "b": 2}, False),
            # Empty list
            ([], False),
            # Inconsistent keys
            ([{"a": 1, "b": 2}, {"a": 3}], False),
            # Non-dictionary elements in the list
            ([{"a": 1, "b": 2}, "not a dict"], False),
        ],
    )
    def test_validate_pandas_records_format(self, json_data, expected):
        deployment = Deployment(client=self.test_client, data={"id": 2})
        assert deployment._validate_pandas_records_format(json_data) == expected


class TestDeploymentAsync:
    def setup_method(self) -> None:
        self.now = datetime.datetime.now()
        self.gql_client = testutil.new_gql_client(endpoint="http://api-lb/v1/graphql")
        self.test_client = wallaroo.Client(
            api_endpoint="http://api-lb:1234",
            gql_client=self.gql_client,
            auth_type="test_auth",
            config={"default_arch": "x86"},
            request_timeout=2,  # this field used only by deployment.wait_for_running() tests
        )
        self.deployment = Deployment(
            client=self.test_client,
            data={
                "id": 1,
                "deploy_id": "some-pipeline",
                "deployed": False,
                "deployment_model_configs": [],
                "deployment_pipeline_versions": [
                    {
                        "pipeline_version": {
                            "id": 2,
                            "version": "v1",
                            "pipeline": {
                                "id": 3,
                                "pipeline_id": "some-pipeline",
                            },
                        }
                    },
                ],
                "pipeline": {
                    "pipeline_id": "some-pipeline",
                },
            },
        )

    @respx.mock
    @pytest.mark.asyncio(loop_scope="function")
    async def test_async_infer(self):
        async with httpx.AsyncClient() as client:
            respx.post(
                "http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
            ).mock(
                return_value=httpx.Response(
                    200, json=SAMPLE_PANDAS_RECORDS_INFERENCE_RESPONSE
                )
            )
            output_df = await self.deployment.async_infer(
                tensor=SAMPLE_PANDAS_RECORDS_JSON, async_client=client
            )
            assert isinstance(output_df, pd.DataFrame)
            assert isinstance(output_df["time"][0], pd.Timestamp)
            assert isinstance(output_df["check_failures"][0], numpy.int64)

    @pytest.mark.asyncio
    async def test_async_infer_timeout(self):
        """Test that async_infer() handles timeouts correctly"""
        async with httpx.AsyncClient() as client:
            respx.post(
                "http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
            ).mock(
                return_value=httpx.Response(
                    503, json=SAMPLE_PANDAS_RECORDS_INFERENCE_RESPONSE
                )
            )
            with pytest.raises(httpx.TimeoutException) as exc_info:
                await self.deployment.async_infer(
                    tensor={"data": [1, 2, 3]},
                    async_client=client,
                    timeout=0.001,  # Very short timeout to trigger error
                )

            assert "did not return within" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_infer_raises_http_error(self):
        """Test that async_infer() handles HTTP errors correctly"""
        # Configure respx to intercept all requests
        respx.start()
        try:
            async with httpx.AsyncClient() as client:
                mock = respx.post(
                    "http://engine-lb.some-pipeline-1:29502/pipelines/some-pipeline",
                ).mock(
                    return_value=httpx.Response(
                        500,
                        json={
                            "code": 500,
                            "status": "error",
                            "source": "model",
                            "error": "Failed to run inference on record batch. `PythonStep` call failed. 'UtilityAlertDailyId'",
                        },
                    )
                )
                with pytest.raises(InferenceError) as exc_info:
                    await self.deployment.async_infer(
                        tensor={"data": [1, 2, 3]},
                        async_client=client,
                    )

                assert "Failed to run inference" in str(exc_info.value)
                assert len(respx.calls) == 1  # Verify the mock was called exactly once
                assert mock.called  # Verify this specific mock was called
                assert mock.call_count == 1  # Verify it was called exactly once
        finally:
            respx.stop()
