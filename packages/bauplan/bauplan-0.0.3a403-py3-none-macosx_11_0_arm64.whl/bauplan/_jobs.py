import time
from typing import List, Optional

from bauplan._bpln_proto.commander.service.v2.runner_events_pb2 import RuntimeLogEvent

from ._bpln_proto.commander.service.v2 import (
    CancelJobRequest,
    GetJobsRequest,
    GetLogsRequest,
    JobId,
)
from ._common_operation import (
    _OperationContainer,
)
from .errors import (
    JobAmbiguousError,
    JobCancelError,
    JobGetError,
    JobLogsError,
    JobNotFoundError,
    JobsListError,
)
from .schema import (
    Job,
    JobLog,
    JobLogStream,
    JobState,
)


class _Jobs(_OperationContainer):
    """
    Implements operations for retrieving jobs and logs.
    """

    def get_job(self, job_id: str) -> Job:
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)
        req = GetJobsRequest(job_ids=[job_id])

        try:
            resp = client_v2.GetJobs(req, metadata=metadata)
        except Exception as e:
            raise JobGetError(f'Failed to get job {job_id}: {e}') from e

        if len(resp.jobs) < 1:
            raise JobNotFoundError(f'No job found for ID {job_id}')

        return Job.from_proto(resp.jobs[0])

    def list_jobs(
        self,
        all_users: Optional[bool] = None,
    ) -> List[Job]:
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)
        req = GetJobsRequest()

        if all_users is not None:
            req.all_users = all_users

        try:
            resp = client_v2.GetJobs(req, metadata=metadata)
        except Exception as e:
            raise JobsListError(f'Failed to list jobs: {e}') from e

        return [Job.from_proto(j) for j in resp.jobs]

    def get_logs(self, job_id_prefix: str) -> List[JobLog]:
        """
        Retrieve *only user logs* for one job by matching a prefix of its ID.

        Steps:
        1) Find exactly 1 matching job (prefix).
        2) Call GetLogs on that job's ID.
        3) For each RunnerEvent, skip system logs and gather user logs,
            splitting them into STDOUT or STDERR.
        """
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)

        req = GetJobsRequest(job_ids=[job_id_prefix])
        try:
            resp = client_v2.GetJobs(req, metadata=metadata)
        except Exception as e:
            raise JobLogsError(f'Failed to get job with prefix {job_id_prefix}: {e}') from e

        if len(resp.jobs) == 0:
            raise JobNotFoundError(f'No jobs found matching prefix: {job_id_prefix}')
        if len(resp.jobs) > 1:
            raise JobAmbiguousError(
                f'Multiple jobs found matching prefix: {job_id_prefix}. Please use a more specific prefix.'
            )

        full_job_id = resp.jobs[0].id

        logs_req = GetLogsRequest(job_id=full_job_id)
        try:
            logs_resp = client_v2.GetLogs(logs_req, metadata=metadata)
        except Exception as e:
            raise JobLogsError(f'Failed to get logs for job {full_job_id}: {e}') from e

        returned_logs: List[JobLog] = []

        for evt in logs_resp.events:
            if not evt.HasField('runtime_user_log'):
                continue

            user_log = evt.runtime_user_log

            # Skip system logs
            if user_log.type != RuntimeLogEvent.LOG_TYPE_USER:
                continue

            if user_log.output_stream == RuntimeLogEvent.OUTPUT_STREAM_STDERR:
                stream = JobLogStream.STDERR
            else:
                stream = JobLogStream.STDOUT

            returned_logs.append(JobLog(message=user_log.msg, stream=stream))

        return returned_logs

    def cancel_job(self, id: str) -> None:
        """
        Cancels a running job and polls its status to verify it has been
        cancelled.
        """
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)
        req = CancelJobRequest(job_id=JobId(id=id))

        try:
            client_v2.CancelJob(req, metadata=metadata)
        except Exception as e:
            raise JobCancelError(f'Failed to cancel job {id}: {e}') from e

        retry_count = 0
        encountered_states = []

        while retry_count < 10:
            job = self.get_job(id)
            encountered_states.append(job.status)

            if job.status == JobState.ABORT:
                return

            retry_count += 1
            time.sleep(1)

        raise JobCancelError(
            id, f'Could not verify job was cancelled. Encountered states: {encountered_states}'
        )
