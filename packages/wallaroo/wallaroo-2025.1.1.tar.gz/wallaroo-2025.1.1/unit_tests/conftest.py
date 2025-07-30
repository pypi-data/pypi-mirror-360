from datetime import datetime

import gql
import pytest

from wallaroo.assays_v2.assay_result_v2 import AssayResultV2
from wallaroo.assays_v2.assay_v2 import AssayV2
from wallaroo.assays_v2.assay_v2_builder import AssayV2Builder
from wallaroo.assays_v2.baseline import SummaryBaseline
from wallaroo.assays_v2.summarizer import Summarizer
from wallaroo.assays_v2.targeting import Targeting
from wallaroo.client import Client
from wallaroo.wallaroo_ml_ops_api_client.models import (
    Aggregation,
    ArbexStatus,
    AssayResultV2 as MLOPsAssayResultV2,
    BinModeType1,
    Bins,
    DataOrigin,
    DataPath,
    FieldTaggedSummaries,
    IntervalUnit,
    Metric,
    MinimalSummary,
    PGInterval,
    PreviewResultSummaries,
    RollingWindow,
    RunFrequencyType1 as MLOpsSimpleRunFrequency,
    Scheduling,
    ScoreData,
    Scores,
    SeriesSummary,
    SeriesSummaryStatistics,
    Thresholds,
    UnivariateContinuous,
    WindowWidthDuration,
)


@pytest.fixture(scope="module")
def mlops_assay_result_v2(window_start_end, scores, assay_window_summaries):
    return MLOPsAssayResultV2(
        analyzed_at=datetime.fromisoformat("2023-01-01T01:00:00+00:00"),
        assay_id="some-assay-id",
        created_at=datetime.fromisoformat("2023-01-01T01:00:00+00:00"),
        elapsed_millis=1000,
        id="some-assay-result-id",
        pipeline_id=1,
        status=ArbexStatus.SUCCESS,
        updated_at=datetime.fromisoformat("2023-01-01T01:01:00+00:00"),
        window_end=datetime.fromisoformat(window_start_end[1]),
        window_start=datetime.fromisoformat(window_start_end[0]),
        workspace_id=1,
        workspace_name="some-workspace-name",
        scores=scores,
        summaries=assay_window_summaries,
    )


@pytest.fixture
def assay_result_v2(mlops_assay_result_v2, assay_v2):
    return AssayResultV2(
        parent_assay=assay_v2, mlops_assay_result=mlops_assay_result_v2
    )


@pytest.fixture
def assay_v2(mocker, client, baseline_summaries, targeting):
    class MockAssayV2(AssayV2):
        def __init__(self, *args, **kwargs) -> None:
            pass

    assay_v2 = MockAssayV2()

    assay_v2.baseline = mocker.Mock(spec=SummaryBaseline)
    assay_v2.baseline.summary = baseline_summaries
    assay_v2.name = "some-assay-name"
    assay_v2.id = "some-assay-id"
    assay_v2.targeting = targeting
    assay_v2._get_iopath = mocker.Mock(return_value=targeting._get_iopath())
    assay_v2._client = client
    assay_v2._rehydrate = mocker.Mock()
    assay_v2.summarizer = Summarizer(
        univariate_continuous=UnivariateContinuous(
            bin_mode=BinModeType1(5),
            aggregation=Aggregation.CUMULATIVE,
            metric=Metric.MAXDIFF,
            bin_weights=None,
        ),
    )

    mocker.patch(
        "wallaroo.assays_v2.assay_result_v2.Workspace.name",
        return_value="some-workspace-name",
    )

    return assay_v2


@pytest.fixture(scope="function")
def assay_v2_builder(client, baseline_summaries, targeting, mocker):
    mocker.patch(
        "wallaroo.workspace.Workspace.name",
        return_value="some-workspace-name",
    )
    assay_v2_builder = AssayV2Builder(client, 1, "some-pipeline-name", 1)

    summarizer = Summarizer(
        univariate_continuous=UnivariateContinuous(
            bin_mode=BinModeType1(5),
            aggregation=Aggregation.CUMULATIVE,
            metric=Metric.MAXDIFF,
            bin_weights=None,
        ),
    )
    assay_v2_builder.baseline = SummaryBaseline(summary=baseline_summaries)
    assay_v2_builder.scheduling = Scheduling(
        first_run=datetime.fromisoformat("2023-01-01T00:00:00+00:00"),
        run_frequency=MLOpsSimpleRunFrequency(PGInterval(1, IntervalUnit.MINUTE)),
        end=None,
    )
    assay_v2_builder.summarizer = summarizer
    assay_v2_builder.targeting = targeting
    assay_v2_builder.window = RollingWindow(
        width=WindowWidthDuration(seconds=60),
    )
    return assay_v2_builder


@pytest.fixture
def client(mocker):
    client = mocker.Mock(spec=Client)
    client._gql_client = mocker.Mock(spec=gql.Client)
    mock_workspace = mocker.Mock()
    mock_workspace.name.return_value = "some-workspace-name"
    mock_workspace.id.return_value = 1
    client.get_current_workspace.return_value = mock_workspace
    return client


@pytest.fixture(scope="session")
def baseline_start_end():
    return "2023-01-01T00:00:00+00:00", "2023-01-01T00:01:00+00:00"


@pytest.fixture(scope="session")
def baseline_summaries(baseline_start_end, labels, baseline_stats):
    summaries = FieldTaggedSummaries()
    series_summary = SeriesSummary(
        name="out.variable.0",
        aggregation=Aggregation.CUMULATIVE,
        aggregated_values=[1, 2, 3, 4, 5],
        statistics=baseline_stats,
        bins=Bins(
            labels=labels,
            edges=[0, 1, 2, 3, 4],
            mode=BinModeType1(5),
        ),
        start=datetime.fromisoformat(baseline_start_end[0]),
        end=datetime.fromisoformat(baseline_start_end[1]),
    )
    summaries.additional_properties = {"out.variable.0": series_summary}

    return summaries


@pytest.fixture(scope="session")
def baseline_stats():
    return SeriesSummaryStatistics(
        count=500, min_=1, max_=5, mean=3, median=3, std=1.58
    )


@pytest.fixture(scope="session")
def labels():
    return ["a", "b", "c", "d", "e"]


@pytest.fixture(scope="session")
def scores():
    scores = Scores()
    scores.additional_properties = {
        "out.variable.0": ScoreData(score=0.8, scores=[0.1, 0.2, 0.3, 0.4, 0.5])
    }
    return scores


@pytest.fixture(scope="session")
def targeting():
    return Targeting(
        iopath=[
            DataPath(
                field="out.variable",
                indexes=[0],
                thresholds=Thresholds(alert=0.9, warning=0.8),
            )
        ],
        data_origin=DataOrigin(
            pipeline_id=1,
            workspace_id=1,
            workspace_name="some-workspace-name",
            pipeline_name="some-pipeline-name",
        ),
    )


@pytest.fixture(scope="session")
def window_edges():
    return [1, 2, 3, 4, 5]


@pytest.fixture(scope="session")
def window_start_end():
    return "2023-01-01T00:02:00+00:00", "2023-01-01T00:03:00+00:00"


@pytest.fixture(scope="session")
def window_stats():
    return SeriesSummaryStatistics(
        count=1000, min_=2, max_=6, mean=4, median=4, std=1.58
    )


@pytest.fixture(scope="session")
def assay_window_summaries(
    window_start_end, window_stats, labels, window_edges, window_aggregated_values
):
    summaries = FieldTaggedSummaries()
    series_summary = SeriesSummary(
        name="out.variable.0",
        aggregation=Aggregation.CUMULATIVE,
        aggregated_values=window_aggregated_values,
        statistics=window_stats,
        bins=Bins(
            labels=labels,
            edges=window_edges,
            mode=BinModeType1(5),
        ),
        start=datetime.fromisoformat(window_start_end[0]),
        end=datetime.fromisoformat(window_start_end[1]),
    )
    summaries.additional_properties = {"out.variable.0": series_summary}

    return summaries


@pytest.fixture(scope="session")
def preview_window_summaries(
    window_start_end, window_stats, window_bins, window_aggregated_values
):
    summaries = PreviewResultSummaries()
    series_summary = MinimalSummary(
        aggregated_values=window_aggregated_values,
        statistics=window_stats,
        bins=window_bins,
        start=datetime.fromisoformat(window_start_end[0]),
        end=datetime.fromisoformat(window_start_end[1]),
    )
    summaries.additional_properties = {"out.variable.0": series_summary}

    return summaries


@pytest.fixture(scope="session")
def window_aggregated_values():
    return [2, 3, 4, 5, 6]


@pytest.fixture(scope="session")
def window_bins(labels, window_edges):
    return Bins(
        labels=labels,
        edges=window_edges,
        mode=BinModeType1(5),
    )
