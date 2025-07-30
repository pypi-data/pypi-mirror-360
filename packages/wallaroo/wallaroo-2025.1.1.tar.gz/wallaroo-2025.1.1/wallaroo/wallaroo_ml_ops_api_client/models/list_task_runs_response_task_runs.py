import datetime
from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)
from dateutil.parser import isoparse

from ..models.task_status import TaskStatus

T = TypeVar("T", bound="ListTaskRunsResponseTaskRuns")


@_attrs_define
class ListTaskRunsResponseTaskRuns:
    """
    Attributes:
        created_at (datetime.datetime): Time this run was created.
        run_id (str): The ID of the Pod for this individual run. This is identical to `pod_id` in the database.
        status (TaskStatus): Possible states that a task can be in
        task (str): Task ID associated with this rnu.
        updated_at (datetime.datetime): Time this run's status was last updated.
    """

    created_at: datetime.datetime
    run_id: str
    status: TaskStatus
    task: str
    updated_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()

        run_id = self.run_id

        status = self.status.value

        task = self.task

        updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "run_id": run_id,
                "status": status,
                "task": task,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        run_id = d.pop("run_id")

        status = TaskStatus(d.pop("status"))

        task = d.pop("task")

        updated_at = isoparse(d.pop("updated_at"))

        list_task_runs_response_task_runs = cls(
            created_at=created_at,
            run_id=run_id,
            status=status,
            task=task,
            updated_at=updated_at,
        )

        list_task_runs_response_task_runs.additional_properties = d
        return list_task_runs_response_task_runs

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
