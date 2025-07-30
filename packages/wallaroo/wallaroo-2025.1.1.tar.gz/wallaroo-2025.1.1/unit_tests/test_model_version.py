import datetime
import time
from io import StringIO
from unittest.mock import patch

import pytest
import responses
import respx

import wallaroo
from wallaroo.continuous_batching_config import ContinuousBatchingConfig
from wallaroo.deployment import WaitForDeployError, WaitForError
from wallaroo.dynamic_batching_config import DynamicBatchingConfig
from wallaroo.engine_config import Acceleration
from wallaroo.model_version import ModelVersion
from wallaroo.object import InvalidNameError
from wallaroo.openai_config import OpenaiConfig
from wallaroo.pipeline import Pipeline
from wallaroo.tag import Tag

from . import status_samples, testutil
from .reusable_responders import (
    add_create_pipeline_responder,
    add_deploy_responder,
    add_get_model_config_response,
    add_insert_model_config_response,
    add_undeploy_responder,
)


class TestModelVersion:
    def setup_method(self):
        self.now = datetime.datetime.now()
        self.gql_client = testutil.new_gql_client(endpoint="http://api-lb/v1/graphql")
        self.test_client = wallaroo.Client(
            gql_client=self.gql_client,
            request_timeout=2,
            interactive=False,
            auth_type="test_auth",
            api_endpoint="http://api-lb:8080",
            config={"default_arch": "x86"},
        )

    def add_deploy_onnx_responses(self, respx_mock):
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("WorkspaceById")],
            json={
                "data": {
                    "workspace_by_pk": {
                        "id": 1,
                        "name": "Unused workspace name",
                        "created_at": self.now.isoformat(),
                        "created_by": 44,
                        "pipelines": [],
                        "models": [],
                        "users": [],
                        "archived": False,
                    }
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
                                "id": 2,
                            }
                        ]
                    }
                }
            },
        )

        add_deploy_responder(respx_mock, 3, self.test_client.api_endpoint)

        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("DeploymentById")],
            json={
                "data": {
                    "deployment_by_pk": {
                        "id": 3,
                        "deploy_id": "my-deployment-name",
                        "deployed": False,
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

        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("UserDefaultWorkspace")],
            json={
                "data": {
                    "user_default_workspace": [
                        {
                            "workspace": {
                                "id": 1,
                            }
                        }
                    ]
                }
            },
        )
        responses.add(
            responses.POST,
            f"{self.test_client.api_endpoint}/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher({"name": "my-deployment-name-3"})
            ],
            status=200,
            json=status_samples.RUNNING,
        )

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
                        "tensor_fields": None,
                    },
                },
            },
        )

        # FIXME TODO OPTIMIZE - This one is because we are deploying a model we already have in
        # hand but it's going out to server anyway. This could be short circuited.
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("ModelById")],
            json={
                "data": {
                    "model_by_pk": {
                        "id": 1,
                        "sha": "adfaf",
                        "model_id": "some_model_name",
                        "model_version": "some_model_variant_name",
                        "file_name": "some_model_file.onnx",
                        "updated_at": self.now.isoformat(),
                        "visibility": "private",
                        "arch": None,
                        "accel": Acceleration._None,
                    },
                },
            },
        )

        # FIXME TODO OPTIMIZE - This one is because we are deploying a model we already have in
        # hand but it's going out to server anyway. This could be short circuited.
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.mutation_name_matcher("InsertDeploymentModelConfig")],
            json={"data": {}},  # Return data currently unused
        )

        # FIXME TODO OPTIMIZE - This one is because we are deploying a model we already have in
        # hand but it's going out to server anyway. This could be short circuited.
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.mutation_name_matcher("InsertDeploymentPipelineVersion")],
            json={"data": {}},  # Return data currently unused
        )

        # TODO same ...
        add_create_pipeline_responder(
            respx_mock, api_endpoint=self.test_client.api_endpoint
        )

        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("PipelineVariantById")],
            json={
                "data": {
                    "pipeline_version_by_pk": {
                        "id": 2,
                        "created_at": self.now.isoformat(),
                        "updated_at": self.now.isoformat(),
                        "version": "v1",
                        "pipeline": {"id": 1},
                        "deployment_pipeline_versions": [],
                    }
                }
            },
        )

        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("PipelineById")],
            json={
                "data": {
                    "pipeline_by_pk": {
                        "id": 1,
                        "pipeline_id": "foo-278333879",
                        "created_at": "2022-02-01T18:42:27.592326+00:00",
                        "updated_at": "2022-02-01T18:42:34.055532+00:00",
                        "visibility": "private",
                        "pipeline_versions": [{"id": 2}, {"id": 1}],
                    }
                }
            },
        )

        responses.add(
            responses.POST,
            f"{self.test_client.api_endpoint}/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher({"name": "my-deployment-name-3"})
            ],
            status=200,
            json=status_samples.RUNNING,
        )

        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("QueryLimitStatus")],
            json={"data": {"deployment": []}},
        )

        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.mutation_name_matcher("Undeploy")],
            json={"data": {}},  # Return data currently unused
        )

    def create_onnx_model(self, client):
        return ModelVersion(
            client=client,
            data={
                "id": 1,
                "model_id": "some_model_name",
                "model_version": "some_model_variant_name",
                "file_name": "some_model_file.onnx",
                "updated_at": self.now.isoformat(),
                "visibility": "private",
            },
        )

    @responses.activate
    def test_init_full_dict(self):
        variant = ModelVersion(
            client=self.test_client,
            data={
                "id": 1,
                "model_id": "some_model_name",
                "model_version": "some_model_variant_name",
                "file_name": "some_model_file.onnx",
                "updated_at": self.now.isoformat(),
                "visibility": "private",
            },
        )

        assert 1 == variant.id()
        assert "some_model_variant_name" == variant.version()
        assert "some_model_name" == variant.name()
        assert "some_model_file.onnx" == variant.file_name()
        assert self.now == variant.last_update_time()

    @pytest.mark.parametrize(
        "method_name, want_value",
        [
            ("name", "some_model_name"),
            ("version", "some_model_variant_name"),
            ("status", "ready"),
            ("file_name", "some_model_file.onnx"),
            ("last_update_time", datetime.datetime(2024, 1, 1, 0, 0, 0)),
        ],
    )
    @responses.activate
    def test_rehydrate(self, method_name, want_value):
        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("ModelById")],
            json={
                "data": {
                    "model_by_pk": {
                        "id": 1,
                        "sha": "adsfadsf",
                        "model_id": "some_model_name",
                        "model_version": "some_model_variant_name",
                        "status": "ready",
                        "file_name": "some_model_file.onnx",
                        "updated_at": datetime.datetime(
                            2024, 1, 1, 0, 0, 0
                        ).isoformat(),
                        "visibility": "private",
                        "model": {
                            "workspace": {"id": 1, "name": "test-workspace"},
                        },
                    },
                },
            },
        )

        variant = ModelVersion(client=self.test_client, data={"id": 1})

        assert want_value == getattr(variant, method_name)()
        if method_name == "status":
            assert 2 == len(responses.calls)
        else:
            assert 1 == len(responses.calls)
        responses.reset()

    @responses.activate
    def test_configure(self):
        add_insert_model_config_response(self.test_client.api_endpoint)
        model = ModelVersion(
            client=self.test_client,
            data={
                "id": 1,
                "model_id": "some_model_name",
                "model_version": "some_model_variant_name",
                "file_name": "some_model_file.onnx",
                "updated_at": self.now.isoformat(),
                "visibility": "private",
            },
        )
        config = model.configure(runtime="onnx")

        assert isinstance(config, ModelVersion)
        assert 1 == len(responses.calls)

    def test_configure_with_batch_config_single_fails_with_dynamic_batching_config_set(
        self,
    ):
        model = ModelVersion(
            client=self.test_client,
            data={
                "id": 1,
                "model_id": "some_model_name",
                "model_version": "some_model_variant_name",
                "file_name": "some_model_file.onnx",
                "updated_at": self.now.isoformat(),
                "visibility": "private",
            },
        )
        dynamic_batching_config = DynamicBatchingConfig(
            max_batch_delay_ms=10, batch_size_target=4, batch_size_limit=10
        )
        with pytest.raises(ValueError):
            model.configure(
                runtime="onnx",
                batch_config="single",
                dynamic_batching_config=dynamic_batching_config,
            )

    def test_configure_with_batch_config_fails_with_continuous_batching_config_set(
        self,
    ):
        model = ModelVersion(
            client=self.test_client,
            data={
                "id": 1,
                "model_id": "some_model_name",
                "model_version": "some_model_variant_name",
                "file_name": "some_model_file.onnx",
                "updated_at": self.now.isoformat(),
                "visibility": "private",
            },
        )
        continuous_batching_config = ContinuousBatchingConfig(
            max_concurrent_batch_size=1
        )

        with pytest.raises(ValueError):
            model.configure(
                batch_config="single",
                continuous_batching_config=continuous_batching_config,
            )

    @responses.activate
    def test_model_version_configure_with_openai_config(self):
        """Test that ModelVersion.configure() works correctly with OpenaiConfig"""

        # Mock the API response
        responses.add(
            responses.POST,
            f"{self.test_client.api_endpoint}/v1/api/models/insert_model_config",
            status=200,
            json={
                "model_config": {
                    "id": 1,
                    "tensor_fields": None,
                    "filter_threshold": None,
                    "openai": {
                        "enabled": True,
                        "completion_config": {"model": "gpt-3.5-turbo"},
                        "chat_completion_config": {"model": "gpt-4"},
                    },
                }
            },
        )

        # Create a model version
        model = ModelVersion(
            client=self.test_client,
            data={
                "id": 1,
                "model_id": "test-model",
                "model_version": "1.0",
                "file_name": "model.onnx",
                "updated_at": "2024-01-01T00:00:00Z",
                "visibility": "private",
            },
        )

        # Create OpenAI config
        openai_config = OpenaiConfig(
            enabled=True,
            completion_config={"model": "gpt-3.5-turbo"},
            chat_completion_config={"model": "gpt-4"},
        )

        # Configure the model with OpenAI config
        configured_model = model.configure(openai_config=openai_config)

        # Verify the configuration
        assert isinstance(configured_model, ModelVersion)
        assert len(responses.calls) == 1
        assert configured_model._config._openai_config is not None
        assert configured_model._config._openai_config.enabled is True

    @responses.activate
    @respx.mock(assert_all_mocked=True)
    def test_deploy_onnx_noninteractive(self, respx_mock):
        self.add_deploy_onnx_responses(respx_mock)
        variant = self.create_onnx_model(self.test_client)
        add_get_model_config_response(self.test_client.api_endpoint)
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            with patch("sys.stderr", new_callable=StringIO) as stderr:
                deployment = variant.deploy("my-deployment-name")
                assert stdout.getvalue() == ""
                assert stderr.getvalue() == ""

        assert isinstance(deployment, Pipeline)

        # tack on a failure case
        responses.replace(
            responses.POST,
            f"{self.test_client.api_endpoint}/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher({"name": "my-deployment-name-3"})
            ],
            status=200,
            json=status_samples.ERROR,
        )

        beg = time.time()
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            with patch("sys.stderr", new_callable=StringIO) as stderr:
                with pytest.raises(WaitForDeployError):
                    deployment = variant.deploy("my-deployment-name")
                assert stdout.getvalue() == ""
                assert stderr.getvalue() == ""

        end = time.time()
        assert end - beg > 2

    @responses.activate
    @respx.mock(assert_all_mocked=True)
    def test_deploy_onnx_interactive(self, respx_mock):
        test_client = wallaroo.Client(
            gql_client=self.gql_client,
            request_timeout=2,
            interactive=True,
            auth_type="test_auth",
            api_endpoint="http://api-lb:8080",
            config={"default_arch": "x86"},
        )

        self.add_deploy_onnx_responses(respx_mock)
        variant = self.create_onnx_model(test_client)
        add_get_model_config_response(test_client.api_endpoint)

        with patch("sys.stdout", new_callable=StringIO) as stdout:
            with patch("sys.stderr", new_callable=StringIO) as stderr:
                # validate that 'deploy' requires DNS-compliant names
                try:
                    variant.deploy("not-quite-right-")
                except InvalidNameError as _:
                    pass
                else:
                    assert False
                deployment = variant.deploy("my-deployment-name")
                assert stdout.getvalue() == " ok\n"
                assert stderr.getvalue() == ""

        assert isinstance(deployment, Pipeline)

        # tack on a failure case
        responses.replace(
            responses.POST,
            f"{self.test_client.api_endpoint}/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher({"name": "my-deployment-name-3"})
            ],
            status=200,
            json=status_samples.ERROR,
        )

        beg = time.time()
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            with patch("sys.stderr", new_callable=StringIO) as stderr:
                with pytest.raises(WaitForDeployError):
                    deployment = variant.deploy("my-deployment-name")
                assert stdout.getvalue().startswith("Waiting for deployment")
                assert stderr.getvalue() == ""

        end = time.time()
        assert end - beg > 2

    @responses.activate
    @respx.mock(assert_all_mocked=True)
    def test_undeploy_onnx_interactive(self, respx_mock):
        test_client = wallaroo.Client(
            gql_client=self.gql_client,
            request_timeout=2,
            interactive=True,
            auth_type="test_auth",
            api_endpoint="http://api-lb:8080",
            config={"default_arch": "x86"},
        )

        self.add_deploy_onnx_responses(respx_mock)
        add_undeploy_responder(respx_mock, self.test_client.api_endpoint)
        variant = self.create_onnx_model(test_client)
        add_get_model_config_response(test_client.api_endpoint)

        # get a normal deployment
        success_deployment = variant.deploy("my-deployment-name")
        assert isinstance(success_deployment, Pipeline)

        # failure case
        beg = time.time()
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            with patch("sys.stderr", new_callable=StringIO) as stderr:
                with pytest.raises(WaitForError):
                    deployment = success_deployment.undeploy()
                assert stdout.getvalue().startswith("Waiting for undeployment")
                assert stderr.getvalue() == ""

        end = time.time()
        assert end - beg > 2

        # success case
        responses.replace(
            responses.POST,
            f"{self.test_client.api_endpoint}/v1/api/status/get_deployment",
            match=[
                responses.matchers.json_params_matcher({"name": "my-deployment-name-3"})
            ],
            status=404,
        )
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            with patch("sys.stderr", new_callable=StringIO) as stderr:
                success_deployment.undeploy()
                outvalue = stdout.getvalue()
                assert stdout.getvalue() == " ok\n"
                assert stderr.getvalue() == ""

    @responses.activate
    def test_pipeline_tags(self):
        tag_1 = Tag(client=self.test_client, data={"id": 1, "tag": "bartag314"})
        tag_2 = Tag(client=self.test_client, data={"id": 2, "tag": "footag123"})

        responses.add(
            responses.POST,
            "http://api-lb/v1/graphql",
            status=200,
            match=[testutil.query_name_matcher("ModelById")],
            json={
                "data": {
                    "model_by_pk": {
                        "id": 1,
                        "sha": "adsfadsf",
                        "model_id": "some_model_name",
                        "model_version": "some_model_variant_name",
                        "file_name": "some_model_file.onnx",
                        "updated_at": self.now.isoformat(),
                        "visibility": "private",
                        "model_tags": [
                            {"tag": {"id": 1, "tag": "bartag314"}},
                            {"tag": {"id": 2, "tag": "footag123"}},
                        ],
                    },
                },
            },
        )

        variant = ModelVersion(client=self.test_client, data={"id": 1})
        assert list(map(vars, [tag_1, tag_2])) == list(map(vars, variant.tags()))
