from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Callable, Dict, Generic, List, Literal, Optional, TypeVar, Union, cast

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import google.protobuf as protobuf
from pydantic import BaseModel, Field

from ._bpln_proto.commander.service.v2 import JobInfo, JobStateType, RunnerEvent
from ._bpln_proto.commander.service.v2.runner_events_pb2 import RuntimeLogEvent

T = TypeVar('T')
RT = TypeVar('RT')


REF_REGEX = r'^(.*?)(:?@([^@]+))?$'


# Safely convert proto timestamp fields to native Python datetime
def proto_datetime_to_py_datetime(
    ts: protobuf.timestamp_pb2.Timestamp,
) -> Optional[datetime]:
    if not ts.seconds and not ts.nanos:
        return None
    return ts.ToDatetime()


class _BauplanData(BaseModel):
    def __str__(self) -> str:
        return self.__repr__()


class Ref(_BauplanData):
    """
    A branch or a tag
    """

    name: str
    hash: str | None = None
    type: str | None = None

    def __str__(self) -> str:
        if self.hash:
            return f'{self.name}@{self.hash}'
        return self.name

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        return cls(**data)

    @classmethod
    def from_string(cls, ref: str) -> Self:
        matched = re.match(REF_REGEX, ref)
        if not matched:
            raise ValueError(f'invalid ref format: {ref}')
        name = matched.group(1).strip()
        hash = matched.group(3) or None
        if not name:
            raise ValueError(f'invalid ref format: {ref}')
        return cls(name=name, hash=hash)


class Branch(Ref):
    type: Literal['BRANCH'] = 'BRANCH'


class Tag(Ref):
    type: Literal['TAG'] = 'TAG'


class DetachedRef(Ref):
    type: Literal['DETACHED'] = 'DETACHED'


APIRef = Annotated[
    Union[Branch, Tag, DetachedRef],
    Field(discriminator='type'),
]


class APIMetadata(_BauplanData):
    status_code: int
    ref: Optional[APIRef] = None
    username: Optional[str] = None
    error: Optional[str] = None
    pagination_token: Optional[str] = None
    request_id: str
    request_ts: int
    request_ms: int


class APIError(_BauplanData):
    code: int
    type: str
    message: str
    context: dict[str, Any]


class APIResponse(_BauplanData):
    metadata: APIMetadata
    ref: Optional[APIRef] = None


class APIResponseWithData(APIResponse):
    data: Any
    ref: Optional[APIRef] = None
    metadata: APIMetadata


class APIResponseWithError(APIResponse):
    error: APIError
    ref: Optional[APIRef] = None
    metadata: APIMetadata


class Namespace(_BauplanData):
    name: str
    ref: Optional[APIRef] = None


class Entry(_BauplanData):
    name: str
    namespace: str
    kind: str

    @property
    def fqn(self) -> str:
        return f'{self.namespace}.{self.name}'


class TableField(_BauplanData):
    id: int
    name: str
    required: bool
    type: str


class PartitionField(_BauplanData):
    name: str
    transform: str


class Table(Entry):
    kind: str = 'TABLE'


class TableWithMetadata(Table):
    id: str
    records: Optional[int]
    size: Optional[int]
    last_updated_ms: int
    fields: List[TableField]
    snapshots: Optional[int]
    partitions: List[PartitionField]
    metadata_location: str
    current_snapshot_id: Optional[int]
    current_schema_id: Optional[int]
    raw: Optional[Dict]


class Commit(_BauplanData):
    ref: APIRef
    message: Optional[str]
    authors: List[Actor]
    authored_date: datetime
    committer: Actor
    committed_date: datetime
    parent_ref: APIRef
    parent_hashes: List[str]
    properties: Dict[str, str]
    signed_off_by: List[Actor]

    @property
    def author(self) -> Actor:
        return self.authors[0]

    @property
    def subject(self) -> Optional[str]:
        if self.message is None:
            return None
        subject = self.message.strip().split('\n')[0].strip()
        return subject or None

    @property
    def body(self) -> Optional[str]:
        if self.message is None:
            return None
        body = '\n'.join(self.message.strip().split('\n')[1:]).strip()
        return body or None

    @property
    def parent_merge_ref(self) -> Optional[Branch]:
        if len(self.parent_hashes) > 1:
            return Branch(name=self.parent_ref.name, hash=self.parent_hashes[1])
        return None


class Actor(_BauplanData):
    name: str
    email: str | None


@dataclass
class _BauplanIteratorContext:
    page_idx: int = 0
    page_item_idx: int = 0
    idx: int = 0
    finished: bool = False

    def next_page(self) -> None:
        self.page_idx = self.page_idx + 1
        self.page_item_idx = 0

    def next_item(self, limit: int | None) -> None:
        self.page_item_idx = self.page_item_idx + 1
        self.idx = self.idx + 1
        self.finished = True if limit and self.idx >= limit else False


class _BauplanIterableCatalogAPIResponse(Generic[T, RT]):
    responses: List[APIResponse]

    def __init__(
        self,
        data_fetcher: Callable[[int, Optional[str]], APIResponse],
        data_mapper: Callable[[Dict[str, Any]], T],
        itersize: int,
        limit: int | None = None,
    ) -> None:
        self.responses = []

        self._response_ref: RT = None  # type: ignore
        self._limit = limit
        self._itersize = itersize
        self._data_fetcher = data_fetcher
        self._data_mapper = data_mapper
        self._iter = _BauplanIteratorContext()
        self._has_next_page = True
        self._fetch_next_page()

    def values(self) -> List[T]:
        return list(self)

    def __iter__(self) -> _BauplanIterableCatalogAPIResponse[T, RT]:
        # We need to reset the iterator context
        self._iter = _BauplanIteratorContext()
        return self

    def __getitem__(self, idx: int) -> T:
        if idx < 0:
            raise ValueError('Negative indexing is not supported')
        # TODO: this is not efficient
        pos = 0
        for res in self:
            if pos == idx:
                return res
            pos += 1
        raise IndexError('Index out of range')

    def __next__(self) -> T:
        if self._iter.finished:
            raise StopIteration
        # Get the current page
        page = self.responses[self._iter.page_idx]
        if self._iter.page_item_idx >= len(page.data):
            # We've reached the end of the current page
            self._fetch_next_page()
            self._iter.next_page()
            self._iter.finished = self._iter.page_idx >= len(self.responses)
            return self.__next__()
        # Get the current item
        item = page.data[self._iter.page_item_idx]
        self._iter.next_item(self._limit)
        return self._data_mapper(item)

    def __len__(self) -> int:
        while self._has_next_page:
            self._fetch_next_page()
        return self._response_data_len()

    def __str__(self) -> str:
        ref = '' if not hasattr(self, 'ref') else f'ref={str(self.ref)!r}, '
        return f'{self.__class__.__name__}({ref}iterator={self.responses[0].metadata.request_id!r})'

    def _response_data_len(self) -> int:
        # Actual number of items fetched over all pages
        return sum(len(page.data) for page in self.responses)

    @property
    def _next_pagination_token(self) -> Optional[str]:
        if not self._has_next_page:
            return None
        if self.responses:
            return self.responses[-1].metadata.pagination_token
        return None

    def _fetch_next_page(self) -> None:
        if not self._has_next_page:
            return
        if self._limit:
            # We should fetch only the remaining items, without exceeding the setted itersize
            missing_items = min(self._itersize, self._limit - self._response_data_len())
        else:
            # Without an explicit limit, we should fetch the itersize
            missing_items = self._itersize
        page = self._data_fetcher(missing_items, self._next_pagination_token)
        self.responses.append(page)
        if page.ref and not self._response_ref:
            self._response_ref = cast(RT, page.ref)
        # We need to use the private __len method to prevent an infinite loop
        tot_items = self._response_data_len()
        if self._limit and tot_items >= self._limit:
            # We should stop fetching pages when we have enough items
            self._has_next_page = False
            # and remove the extra items from the last page
            if tot_items > self._limit:
                page.data = page.data[: self._limit - tot_items]
        else:
            # We should stop fetching pages when there are no more pages
            self._has_next_page = self._next_pagination_token is not None


class _BauplanIterableCatalogAPIResponseWithRef(_BauplanIterableCatalogAPIResponse[T, RT]):
    @property
    def ref(self) -> RT:
        return self._response_ref


class GetCommitsResponse(_BauplanIterableCatalogAPIResponseWithRef[Commit, Union[Branch, Tag]]): ...


class GetTablesResponse(_BauplanIterableCatalogAPIResponseWithRef[TableWithMetadata, Union[Branch, Tag]]): ...


class GetNamespacesResponse(_BauplanIterableCatalogAPIResponseWithRef[Namespace, Union[Branch, Tag]]): ...


class GetBranchesResponse(_BauplanIterableCatalogAPIResponse[Branch, None]): ...


class GetTagsResponse(_BauplanIterableCatalogAPIResponse[Tag, None]): ...


class JobState(Enum):
    UNSPECIFIED = JobStateType.JOB_STATE_TYPE_UNSPECIFIED
    NOT_STARTED = JobStateType.JOB_STATE_TYPE_NOT_STARTED
    RUNNING = JobStateType.JOB_STATE_TYPE_RUNNING
    COMPLETE = JobStateType.JOB_STATE_TYPE_COMPLETE
    ABORT = JobStateType.JOB_STATE_TYPE_ABORT
    FAIL = JobStateType.JOB_STATE_TYPE_FAIL
    OTHER = JobStateType.JOB_STATE_TYPE_OTHER

    def __str__(self) -> str:
        return {
            JobState.UNSPECIFIED: 'Unspecified',
            JobState.NOT_STARTED: 'Not Started',
            JobState.RUNNING: 'Running',
            JobState.COMPLETE: 'Complete',
            JobState.ABORT: 'Abort',
            JobState.FAIL: 'Fail',
            JobState.OTHER: 'Other',
        }[self]


class Job(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    Job is a model for a job in the Bauplan system. It is tracked as a result
    of a code snapshot run.
    """

    id: str
    kind: str
    user: str
    human_readable_status: str
    created_at: Optional[datetime]
    finished_at: Optional[datetime]
    status: JobState

    @classmethod
    def from_proto(cls, job_pb: JobInfo) -> 'Job':
        return cls(
            id=job_pb.id,
            kind=job_pb.kind,
            user=job_pb.user,
            human_readable_status=job_pb.human_readable_status,
            created_at=proto_datetime_to_py_datetime(job_pb.created_at),
            finished_at=proto_datetime_to_py_datetime(job_pb.finished_at),
            status=JobState(job_pb.status),
        )


class JobLogStream(Enum):
    STDOUT = 0
    STDERR = 1


class JobLog(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    JobLog is a model for a log message from a job.

    When you output logs within a Python model, they are persisted as JobLogs.
    """

    message: str
    stream: JobLogStream

    @classmethod
    def from_proto(cls, log_pb: RunnerEvent) -> JobLog:
        if not log_pb.HasField('runtime_user_log'):
            raise ValueError('RunnerEvent is not a RuntimeUserLog')

        user_log = log_pb.runtime_user_log

        if user_log.output_stream == RuntimeLogEvent.OUTPUT_STREAM_STDERR:
            stream = JobLogStream.STDERR
        else:
            stream = JobLogStream.STDOUT

        return cls(message=user_log.msg, stream=stream)
