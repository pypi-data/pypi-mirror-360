from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional

from dasl_api import (
    CommonV1ObjectMeta,
    CoreV1ResourceStatus,
    CoreV1StatusEvent,
    CoreV1Schedule,
)

from dasl_client.conn.client_identifier import get_client_identifier


class Metadata(BaseModel):
    """
    General resource metadata.

    Attributes:
        name (Optional[str]):
            The name of the resource.
        workspace (Optional[str]):
            The workspace to which the resource belongs.
        comment (Optional[str]):
            A description or comment associated with the resource.
        annotations (Optional[Dict[str, Optional[str]]]):
            Annotations is an unstructured key value map stored with a
            resource that may be set by external tools to store and retrieve
            arbitrary metadata. They are not queryable and should be preserved
            when modifying objects.
        created_timestamp (Optional[datetime]):
            The time at which this resource was created.
        created_by (Optional[str]):
            The account that created this resource.
        modified_timestamp (Optional[datetime]):
            The last time at which this resource was modified.
        last_successful_run_timestamp (Optional[datetime]):
            The last time at which the job associated with this resource
            successfuly completed.
        modified_by (Optional[str]):
            The account that modified this resource most recently.
        version (Optional[int]):
            The resource's version.
        deleted (Optional[bool]):
            Indicates whether the resource has been deleted.
        resource_status (Optional[str]):
            Internal resource status. Cannot be updated by the user.
        ui_status (Optional[str]):
            Internal resource status. Cannot be updated by the user.
        client_of_origin (Optional[str]):
            The client that last created or modified this resource.
    """

    name: Optional[str] = None
    workspace: Optional[str] = None
    comment: Optional[str] = None
    annotations: Optional[Dict[str, Optional[str]]] = None
    created_timestamp: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_timestamp: Optional[datetime] = None
    last_successful_run_timestamp: Optional[datetime] = None
    modified_by: Optional[str] = None
    version: Optional[int] = None
    deleted: Optional[bool] = None
    resource_status: Optional[str] = None
    ui_status: Optional[str] = None
    client_of_origin: Optional[str] = None

    @staticmethod
    def from_api_obj(obj: Optional[CommonV1ObjectMeta]) -> "Metadata":
        if obj is None:
            return None
        return Metadata(
            name=obj.name,
            workspace=obj.workspace,
            comment=obj.comment,
            annotations=obj.annotations,
            created_timestamp=obj.created_timestamp,
            created_by=obj.created_by,
            modified_timestamp=obj.modified_timestamp,
            last_successful_run_timestamp=obj.last_successful_run_timestamp,
            modified_by=obj.modified_by,
            version=obj.version,
            deleted=obj.deleted,
            resource_status=obj.resource_status,
            ui_status=obj.ui_status,
            client_of_origin=obj.client_of_origin,
        )

    def to_api_obj(self) -> CommonV1ObjectMeta:
        return CommonV1ObjectMeta(
            name=self.name,
            workspace=self.workspace,
            comment=self.comment,
            annotations=self.annotations,
            created_timestamp=self.created_timestamp,
            created_by=self.created_by,
            modified_timestamp=self.modified_timestamp,
            last_successful_run_timestamp=self.last_successful_run_timestamp,
            modified_by=self.modified_by,
            version=self.version,
            deleted=self.deleted,
            resource_status=self.resource_status,
            ui_status=self.ui_status,
            client_of_origin=self.client_of_origin or get_client_identifier(),
        )


class ResourceStatus(BaseModel):
    """
    The status of the resource, along with status update events.

    Attributes:
        job_id (Optional[int]):
            The associated Databricks Job ID.
        job_name (str):
            The associated Databricks Job name.
        enabled (bool):
            Indicates whether the resource is enabled.
        notebook_path (str):
            The path to the Databricks notebook that the Job has been
            scheduled with.
        created_at (datetime):
            The time at which the resources were created in Databricks.
        job_status (str):
            The current reported status of the job.
        events (List[StatusEvent]):
            The most recent 25 events related to this resource.
    """

    class StatusEvent(BaseModel):
        """
        An event related to changes in the status of the resource.

        Attributes:
            action (Optional[str]):
                The action taken as part of the lifecycle of a resource.
            message (Optional[str]):
                A human-readable message describing the event.
            recorded_at (Optional[datetime]):
                The timestamp associated with the event.
        """

        action: Optional[str] = None
        message: Optional[str] = None
        recorded_at: Optional[datetime] = None

        @staticmethod
        def from_api_obj(obj: CoreV1StatusEvent) -> "ResourceStatus.StatusEvent":
            return ResourceStatus.StatusEvent(
                action=obj.action,
                message=obj.message,
                recorded_at=obj.recorded_at,
            )

        def to_api_obj(self) -> CoreV1StatusEvent:
            return CoreV1StatusEvent(
                action=self.action,
                message=self.message,
                recorded_at=self.recorded_at,
            )

    job_id: Optional[int] = None
    job_name: str
    enabled: bool
    notebook_path: str
    created_at: datetime
    job_status: str
    events: List[StatusEvent] = []

    @staticmethod
    def from_api_obj(obj: Optional[CoreV1ResourceStatus]) -> "ResourceStatus":
        if obj is None:
            return None
        return ResourceStatus(
            job_id=obj.job_id,
            job_name=obj.job_name,
            enabled=obj.enabled,
            notebook_path=obj.notebook_path,
            created_at=obj.created_at,
            job_status=obj.job_status,
            events=[
                ResourceStatus.StatusEvent.from_api_obj(event) for event in obj.events
            ],
        )

    def to_api_obj(self) -> CoreV1ResourceStatus:
        return CoreV1ResourceStatus(
            job_id=self.job_id,
            job_name=self.job_name,
            enabled=self.enabled,
            notebook_path=self.notebook_path,
            created_at=self.created_at,
            job_status=self.job_status,
            events=[event.to_api_obj() for event in self.events],
        )


class Schedule(BaseModel):
    """
    A schedule for recurring dispatch of the Job(s) associated with a resource.

    Attributes:
        at_least_every (Optional[str]):
            A duration string defining the schedule. The string may contain
            components for days, hours, minutes and seconds. Examples include
            '5d', '5d3h', '3d2h5m12s', and '12m16s'.
        exactly (Optional[str]):
            A quartz cron expression defining the precise schedule for dispatch.
        continuous (Optional[bool]):
            True if the Job should be continuously dispatched, False/None
            otherwise.
        compute_group (Optional[str]):
            'dedicated', 'automatic' or a custom group name.
        enabled (Optional[bool]):
            Whether the schedule (and hence Job associated with the resource)
            is active.
    """

    at_least_every: Optional[str] = None
    exactly: Optional[str] = None
    continuous: Optional[bool] = None
    compute_group: Optional[str] = None
    enabled: Optional[bool] = None

    @staticmethod
    def from_api_obj(obj: Optional[CoreV1Schedule]) -> "Schedule":
        if obj is None:
            return None
        return Schedule(
            at_least_every=obj.at_least_every,
            exactly=obj.exactly,
            continuous=obj.continuous,
            compute_group=obj.compute_group,
            enabled=obj.enabled,
        )

    def to_api_obj(self) -> CoreV1Schedule:
        return CoreV1Schedule(
            at_least_every=self.at_least_every,
            exactly=self.exactly,
            continuous=self.continuous,
            compute_group=self.compute_group,
            enabled=self.enabled,
        )
