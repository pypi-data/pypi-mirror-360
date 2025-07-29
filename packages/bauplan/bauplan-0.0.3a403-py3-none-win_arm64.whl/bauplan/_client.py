from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Literal, Optional, Tuple, Union

import grpc._channel
import pyarrow as pa
import pydantic
import requests

from bauplan._jobs import _Jobs

from . import exceptions
from ._common import BAUPLAN_VERSION, Constants
from ._common_operation import _JobLifeCycleHandler, _lifecycle, _OperationContainer
from ._info import InfoState, _Info
from ._profile import Profile
from ._query import _Query
from ._run import ReRunState, RunState, _Run
from ._table_create_plan import TableCreatePlanApplyState, TableCreatePlanState, _TableCreate
from ._table_data_import import TableDataImportState, _TableImport
from ._validators import _Validate
from .schema import (
    APIResponse,
    APIResponseWithData,
    APIResponseWithError,
    Branch,
    Commit,
    GetBranchesResponse,
    GetCommitsResponse,
    GetNamespacesResponse,
    GetTablesResponse,
    GetTagsResponse,
    Job,
    JobLog,
    Namespace,
    Ref,
    Table,
    TableWithMetadata,
    Tag,
)


class Client(_OperationContainer):
    """
    A consistent interface to access Bauplan operations.

    **Using the client**

    .. code-block:: python

        import bauplan
        client = bauplan.Client()

        # query the table and return result set as an arrow Table
        my_table = client.query('SELECT sum(trips) trips FROM travel_table', branch_name='main')

        # efficiently cast the table to a pandas DataFrame
        df = my_table.to_pandas()

    **Notes on authentication**

    .. code-block:: python

        # by default, authenticate from BAUPLAN_API_KEY >> BAUPLAN_PROFILE >> ~/.bauplan/config.yml
        client = bauplan.Client()
        # client used ~/.bauplan/config.yml profile 'default'

        os.environ['BAUPLAN_PROFILE'] = "someprofile"
        client = bauplan.Client()
        # >> client now uses profile 'someprofile'

        os.environ['BAUPLAN_API_KEY'] = "mykey"
        client = bauplan.Client()
        # >> client now authenticates with api_key value "mykey", because api key > profile

        # specify authentication directly - this supercedes BAUPLAN_API_KEY in the environment
        client = bauplan.Client(api_key='MY_KEY')

        # specify a profile from ~/.bauplan/config.yml - this supercedes BAUPLAN_PROFILE in the environment
        client = bauplan.Client(profile='default')

    **Handling Exceptions**

    Catalog operations (branch/table methods) raise a subclass of ``bauplan.exceptions.BauplanError`` that mirror HTTP status codes.

        * 400: InvalidDataError
        * 401: UnauthorizedError
        * 403: AccessDeniedError
        * 404: ResourceNotFoundError e.g .ID doesn't match any records
        * 404: ApiRouteError e.g. the given route doesn't exist
        * 405: ApiMethodError e.g. POST on a route with only GET defined
        * 409: UpdateConflictError e.g. creating a record with a name that already exists
        * 429: TooManyRequestsError

    Run/Query/Scan/Import operations raise a subclass of ``bauplan.exceptions.BauplanError`` that represents, and also return a ``RunState`` object containing details and logs:

        * ``JobError`` e.g. something went wrong in a run/query/import/scan; includes error details

    Run/import operations also return a state object that includes a ``job_status`` and other details.
    There are two ways to check status for run/import operations:
        1. try/except the JobError exception
        2. check the ``state.job_status`` attribute

    Examples:

    .. code-block:: python

        try:
            state = client.run(...)
            state = client.query(...)
            state = client.scan(...)
            state = client.plan_table_creation(...)
        except bauplan.exceptions.JobError as e:
            ...

        state = client.run(...)
        if state.job_status != "success":
            ...


    :param profile: (optional) The Bauplan config profile name to use to determine api_key.
    :param api_key: (optional) Your unique Bauplan API key; mutually exclusive with ``profile``. If not provided, fetch precedence is 1) environment BAUPLAN_API_KEY 2) .bauplan/config.yml
    :param branch: (optional) The default branch to use for queries and runs. If not provided active_branch from the profile is used.
    :param namespace: (optional) The default namespace to use for queries and runs.
    :param cache: (optional) Whether to enable or disable caching for all the requests.
    :param debug: (optional) Whether to enable or disable debug mode for all the requests.
    :param verbose: (optional) Whether to enable or disable verbose mode for all the requests.
    :param args: (optional) Additional arguments to pass to all the requests.
    :param api_endpoint: (optional) The Bauplan API endpoint to use. If not provided, fetch precedence is 1) environment BAUPLAN_API_ENDPOINT 2) .bauplan/config.yml
    :param catalog_endpoint: (optional) The Bauplan catalog endpoint to use. If not provided, fetch precedence is 1) environment BAUPLAN_CATALOG_ENDPOINT 2) .bauplan/config.yml
    :param catalog_max_records: (optional) The maximum number of records to fetch, per page, from the catalog.
    :param client_timeout: (optional) The client timeout in seconds for all the requests.
    :param env: (optional) The environment to use for all the requests. Default: 'prod'.
    :param config_file_path: (optional) The path to the Bauplan config file to use. If not provided, fetch precedence is 1) environment BAUPLAN_CONFIG_PATH 2) ~/.bauplan/config.yml
    :param user_session_token: (optional) Your unique Bauplan user session token.
    """

    def __init__(
        self,
        profile: Optional[str] = None,
        api_key: Optional[str] = None,
        branch: Optional[str] = None,
        namespace: Optional[str] = None,
        cache: Optional[Literal['on', 'off']] = None,
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        api_endpoint: Optional[str] = None,
        catalog_endpoint: Optional[str] = None,
        catalog_max_records: Optional[int] = None,
        client_timeout: Optional[int] = None,
        env: Optional[str] = None,
        config_file_path: Optional[Union[str, Path]] = None,
        user_session_token: Optional[str] = None,
        feature_flags: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            profile=Profile.load_profile(
                profile=profile,
                api_key=api_key,
                user_session_token=user_session_token,
                branch=branch,
                namespace=namespace,
                cache=cache,
                debug=debug,
                verbose=verbose,
                args=args,
                api_endpoint=api_endpoint,
                catalog_endpoint=catalog_endpoint,
                client_timeout=client_timeout,
                catalog_max_records=catalog_max_records,
                env=env,
                config_file_path=config_file_path,
                feature_flags=feature_flags,
            ),
        )

        # instantiate interfaces to authenticated modules
        self._query = _Query(self.profile)
        self._run = _Run(self.profile)
        self._table_create = _TableCreate(self.profile)
        self._table_import = _TableImport(self.profile)
        self._info = _Info(self.profile)
        self._jobs = _Jobs(self.profile)

    # Run

    def run(
        self,
        project_dir: Optional[str] = None,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        parameters: Optional[Dict[str, Optional[Union[str, int, float, bool]]]] = None,
        cache: Optional[Literal['on', 'off']] = None,
        transaction: Optional[Literal['on', 'off']] = None,
        dry_run: Optional[bool] = None,
        strict: Optional[Literal['on', 'off']] = None,
        preview: Optional[Union[Literal['on', 'off', 'head', 'tail'], str]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        detach: Optional[bool] = None,
    ) -> RunState:
        """
        Run a Bauplan project and return the state of the run. This is the equivalent of
        running through the CLI the ``bauplan run`` command.

        :param project_dir: The directory of the project (where the ``bauplan_project.yml`` file is located).
        :param ref: The ref, branch name or tag name from which to run the project.
        :param namespace: The Namespace to run the job in. If not set, the job will be run in the default namespace.
        :param parameters: Parameters for templating into SQL or Python models.
        :param cache: Whether to enable or disable caching for the run.
        :param transaction: Whether to enable or disable transaction mode for the run.
        :param dry_run: Whether to enable or disable dry-run mode for the run; models are not materialized.
        :param strict: Whether to enable or disable strict schema validation.
        :param preview: Whether to enable or disable preview mode for the run.
        :param debug: Whether to enable or disable debug mode for the run.
        :param args: Additional arguments (optional).
        :param verbose: Whether to enable or disable verbose mode for the run.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.
        :param detach: Whether to detach the run and return immediately instead of blocking on log streaming.

        :return: The state of the run.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._run.run(
                project_dir=project_dir,
                ref=ref_value,
                namespace=namespace_name,
                parameters=parameters,
                cache=cache,
                transaction=transaction,
                dry_run=dry_run,
                strict=strict,
                preview=preview,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
                detach=detach,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def rerun(
        self,
        job_id: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        cache: Optional[Literal['on', 'off']] = None,
        transaction: Optional[Literal['on', 'off']] = None,
        dry_run: Optional[bool] = None,
        strict: Optional[Literal['on', 'off']] = None,
        preview: Optional[Union[Literal['on', 'off', 'head', 'tail'], str]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> ReRunState:
        """
        Re run a Bauplan project by its ID and return the state of the run. This is the equivalent of
        running through the CLI the ``bauplan rerun`` command.

        :param job_id: The Job ID of the previous run. This can be used to re-run a previous run, e.g., on a different branch.
        :param ref: The ref, branch name or tag name from which to rerun the project.
        :param namespace: The Namespace to run the job in. If not set, the job will be run in the default namespace.
        :param cache: Whether to enable or disable caching for the run.
        :param transaction: Whether to enable or disable transaction mode for the run.
        :param dry_run: Whether to enable or disable dry-run mode for the run; models are not materialized.
        :param strict: Whether to enable or disable strict schema validation.
        :param preview: Whether to enable or disable preview mode for the run.
        :param debug: Whether to enable or disable debug mode for the run.
        :param args: Additional arguments (optional).
        :param verbose: Whether to enable or disable verbose mode for the run.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The state of the run.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._run.rerun(
                job_id=job_id,
                ref=ref_value,
                namespace=namespace_name,
                cache=cache,
                transaction=transaction,
                dry_run=dry_run,
                strict=strict,
                preview=preview,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Query

    def query(
        self,
        query: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> pa.Table:
        """
        Execute a SQL query and return the results as a pyarrow.Table.
        Note that this function uses Arrow also internally, resulting
        in a fast data transfer.

        If you prefer to return the results as a pandas DataFrame, use
        the ``to_pandas`` function of pyarrow.Table.

        .. code-block:: python

            import bauplan

            client = bauplan.Client()

            # query the table and return result set as an arrow Table
            my_table = client.query(
                query='SELECT c1 FROM my_table',
                ref='my_ref_or_branch_name',
            )

            # efficiently cast the table to a pandas DataFrame
            df = my_table.to_pandas()

        :param query: The Bauplan query to execute.
        :param ref: The ref, branch name or tag name to query from.
        :param max_rows: The maximum number of rows to return; default: ``None`` (no limit).
        :param cache: Whether to enable or disable caching for the query.
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
        :param debug: Whether to enable or disable debug mode for the query.
        :param args: Additional arguments to pass to the query (default: None).
        :param verbose: Whether to enable or disable verbose mode for the query.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The query results as a ``pyarrow.Table``.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query(
                query=query,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_generator(
        self,
        query: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        as_json: Optional[bool] = False,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a SQL query and return the results as a generator, where each row is
        a Python dictionary.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # query the table and iterate through the results one row at a time
            res = client.query_to_generator(
                query='SELECT c1 FROM my_table',
                ref='my_ref_or_branch_name',
            )
            for row in res:
                # do logic

        :param query: The Bauplan query to execute.
        :param ref: The ref, branch name or tag name to query from.
        :param max_rows: The maximum number of rows to return; default: ``None`` (no limit).
        :param cache: Whether to enable or disable caching for the query.
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
        :param debug: Whether to enable or disable debug mode for the query.
        :param as_json: Whether to return the results as a JSON-compatible string (default: ``False``).
        :param args: Additional arguments to pass to the query (default: ``None``).
        :param verbose: Whether to enable or disable verbose mode for the query.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :yield: A dictionary representing a row of query results.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query_to_generator(
                query=query,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                as_json=as_json,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_parquet_file(
        self,
        path: Union[str, Path],
        query: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> Path:
        """
        Export the results of a SQL query to a file in Parquet format.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # query the table and iterate through the results one row at a time
            client.query_to_parquet_file(
                path='./my.parquet',
                query='SELECT c1 FROM my_table',
                ref='my_ref_or_branch_name',
            ):

        :param path: The name or path of the file parquet to write the results to.
        :param query: The Bauplan query to execute.
        :param ref: The ref, branch name or tag name to query from.
        :param max_rows: The maximum number of rows to return; default: ``None`` (no limit).
        :param cache: Whether to enable or disable caching for the query.
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
        :param debug: Whether to enable or disable debug mode for the query.
        :param args: Additional arguments to pass to the query (default: None).
        :param verbose: Whether to enable or disable verbose mode for the query.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The path of the file written.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query_to_parquet_file(
                path=path,
                query=query,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
                **kwargs,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_csv_file(
        self,
        path: Union[str, Path],
        query: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> Path:
        """
        Export the results of a SQL query to a file in CSV format.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # query the table and iterate through the results one row at a time
            client.query_to_csv_file(
                path='./my.csv',
                query='SELECT c1 FROM my_table',
                ref='my_ref_or_branch_name',
            ):

        :param path: The name or path of the file csv to write the results to.
        :param query: The Bauplan query to execute.
        :param ref: The ref, branch name or tag name to query from.
        :param max_rows: The maximum number of rows to return; default: ``None`` (no limit).
        :param cache: Whether to enable or disable caching for the query.
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
        :param debug: Whether to enable or disable debug mode for the query.
        :param args: Additional arguments to pass to the query (default: None).
        :param verbose: Whether to enable or disable verbose mode for the query.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The path of the file written.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query_to_csv_file(
                path=path,
                query=query,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
                **kwargs,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_json_file(
        self,
        path: Union[str, Path],
        query: str,
        file_format: Optional[Literal['json', 'jsonl']] = 'json',
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Path:
        """
        Export the results of a SQL query to a file in JSON format.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # query the table and iterate through the results one row at a time
            client.query_to_json_file(
                path='./my.json',
                query='SELECT c1 FROM my_table',
                ref='my_ref_or_branch_name',
            ):

        :param path: The name or path of the file json to write the results to.
        :param query: The Bauplan query to execute.
        :param file_format: The format to write the results in; default: ``json``. Allowed values are 'json' and 'jsonl'.
        :param ref: The ref, branch name or tag name to query from.
        :param max_rows: The maximum number of rows to return; default: ``None`` (no limit).
        :param cache: Whether to enable or disable caching for the query.
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
        :param debug: Whether to enable or disable debug mode for the query.
        :param args: Additional arguments to pass to the query (default: None).
        :param verbose: Whether to enable or disable verbose mode for the query.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The path of the file written.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query_to_json_file(
                path=path,
                query=query,
                file_format=file_format,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def create_table(
        self,
        table: Union[str, Table],
        search_uri: str,
        branch: Optional[Union[str, Branch]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        partitioned_by: Optional[str] = None,
        replace: Optional[bool] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Table:
        """
        Create a table from an S3 location.

        This operation will attempt to create a table based of schemas of N
        parquet files found by a given search uri. This is a two step operation using
        ``plan_table_creation `` and  ``apply_table_creation_plan``.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            table = client.create_table(
                table='my_table_name',
                search_uri='s3://path/to/my/files/*.parquet',
                ref='my_ref_or_branch_name',
            )

        :param table: The table which will be created.
        :param search_uri: The location of the files to scan for schema.
        :param branch: The branch name in which to create the table in.
        :param namespace: Optional argument specifying the namespace. If not.
            specified, it will be inferred based on table location or the default.
            namespace.
        :param partitioned_by: Optional argument specifying the table partitioning.
        :param replace: Replace the table if it already exists.
        :param debug: Whether to enable or disable debug mode for the query.
        :param args: dict of arbitrary args to pass to the backend.
        :param verbose: Whether to enable or disable verbose mode.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :raises TableCreatePlanStatusError: if the table creation plan fails.
        :raises TableCreatePlanApplyStatusError: if the table creation plan apply fails.

        :return: Table
        """
        table_create_plan = self.plan_table_creation(
            table=table,
            search_uri=search_uri,
            branch=branch,
            namespace=namespace,
            partitioned_by=partitioned_by,
            replace=replace,
            debug=debug,
            args=args,
            verbose=verbose,
            client_timeout=client_timeout,
        )
        _ = self.apply_table_creation_plan(
            plan=table_create_plan,
            debug=debug,
            args=args,
            verbose=verbose,
            client_timeout=client_timeout,
        )

        # The namespace has been resolved by the commander
        parts = table_create_plan.ctx.table_name.split('.')
        if len(parts) > 1:
            return Table(
                name=parts[-1],
                namespace='.'.join(parts[:-1]),
            )

        return Table(
            name=table_create_plan.ctx.table_name,
            namespace=table_create_plan.ctx.namespace,
        )

    def plan_table_creation(
        self,
        table: Union[str, Table],
        search_uri: str,
        branch: Optional[Union[str, Branch]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        partitioned_by: Optional[str] = None,
        replace: Optional[bool] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> TableCreatePlanState:
        """
        Create a table import plan from an S3 location.

        This operation will attempt to create a table based of schemas of N
        parquet files found by a given search uri. A YAML file containing the
        schema and plan is returns and if there are no conflicts, it is
        automatically applied.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            plan_state = client.plan_table_creation(
                table='my_table_name',
                search_uri='s3://path/to/my/files/*.parquet',
                ref='my_ref_or_branch_name',
            )
            if plan_state.error:
                plan_error_action(...)
            success_action(plan_state.plan)

        :param table: The table which will be created.
        :param search_uri: The location of the files to scan for schema.
        :param branch: The branch name in which to create the table in.
        :param namespace: Optional argument specifying the namespace. If not.
            specified, it will be inferred based on table location or the default.
            namespace.
        :param partitioned_by: Optional argument specifying the table partitioning.
        :param replace: Replace the table if it already exists.
        :param debug: Whether to enable or disable debug mode.
        :param args: dict of arbitrary args to pass to the backend.
        :param verbose: Whether to enable or disable verbose mode.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :raises TableCreatePlanStatusError: if the table creation plan fails.

        :return: The plan state.
        """
        branch_name = _Validate.optional_branch_name('branch', branch)
        table_name = _Validate.table_name('table', table)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._table_create.plan(
                table_name=table_name,
                search_uri=search_uri,
                branch_name=branch_name,
                namespace=namespace_name,
                partitioned_by=partitioned_by,
                replace=replace,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def apply_table_creation_plan(
        self,
        plan: Union[Dict, TableCreatePlanState],
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> TableCreatePlanApplyState:
        """
        Apply a plan for creating a table. It is done automaticaly during th
        table plan creation if no schema conflicts exist. Otherwise, if schema
        conflicts exist, then this function is used to apply them after the
        schema conflicts are resolved. Most common schema conflict is a two
        parquet files with the same column name but different datatype

        :param plan: The plan to apply.
        :param debug: Whether to enable or disable debug mode for the query.
        :param args: dict of arbitrary args to pass to the backend.
        :param verbose: Whether to enable or disable verbose mode.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :raises TableCreatePlanApplyStatusError: if the table creation plan apply fails.

        :return The plan state.
        """
        try:
            return self._table_create.apply(
                plan=plan,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def import_data(
        self,
        table: Union[str, Table],
        search_uri: str,
        branch: Optional[Union[str, Branch]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        continue_on_error: bool = False,
        import_duplicate_files: bool = False,
        best_effort: bool = False,
        # transformation_query: Optional[str] = None,
        preview: Optional[Union[Literal['on', 'off', 'head', 'tail'], str]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> TableDataImportState:
        """
        Imports data into an already existing table.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            plan_state = client.import_data(
                table='my_table_name',
                search_uri='s3://path/to/my/files/*.parquet',
                branch='my_branch_name',
            )
            if plan_state.error:
                plan_error_action(...)
            success_action(plan_state.plan)

        :param table: Previously created table in into which data will be imported.
        :param search_uri: Uri which to scan for files to import.
        :param branch: Branch in which to import the table.
        :param namespace: Namespace of the table. If not specified, namespace will be infered from table name or default settings.
        :param continue_on_error: Do not fail the import even if 1 data import fails.
        :param import_duplicate_files: Ignore prevention of importing s3 files that were already imported.
        :param best_effort: Don't fail if schema of table does not match.
        :param transformation_query: Optional duckdb compliant query applied on each parquet file. Use `original_table` as the table in the query.
        :param preview: Whether to enable or disable preview mode for the import.
        :param debug: Whether to enable or disable debug mode for the import.
        :param args: dict of arbitrary args to pass to the backend.
        :param verbose: Whether to enable or disable verbose mode.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The plan state.
        """
        table_name = _Validate.table_name('table', table)
        branch_name = _Validate.optional_branch_name('branch', branch)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._table_import.data_import(
                table_name=table_name,
                search_uri=search_uri,
                branch_name=branch_name,
                namespace=namespace_name,
                continue_on_error=continue_on_error,
                import_duplicate_files=import_duplicate_files,
                best_effort=best_effort,
                transformation_query=None,
                preview=preview,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Scan

    def scan(
        self,
        table: Union[str, Table],
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        columns: Optional[List[str]] = None,
        filters: Optional[str] = None,
        limit: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> pa.Table:
        """
        Execute a table scan (with optional filters) and return the results as an arrow Table.

        Note that this function uses SQLGlot to compose a safe SQL query,
        and then internally defer to the query_to_arrow function for the actual
        scan.

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # run a table scan over the data lake
            # filters are passed as a string
            my_table = client.scan(
                table='my_table_name',
                ref='my_ref_or_branch_name',
                columns=['c1'],
                filters='c2 > 10',
            )

        :param table: The table to scan.
        :param ref: The ref, branch name or tag name to scan from.
        :param columns: The columns to return (default: ``None``).
        :param filters: The filters to apply (default: ``None``).
        :param limit: The maximum number of rows to return (default: ``None``).
        :param cache: Whether to enable or disable caching for the query.
        :param connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
        :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
        :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
        :param namespace: The Namespace to run the scan in. If not set, the scan will be run in the default namespace for your account.
        :param debug: Whether to enable or disable debug mode for the query.
        :param args: dict of arbitrary args to pass to the backend.
        :param client_timeout: seconds to timeout; this also cancels the remote job execution.

        :return: The scan results as a ``pyarrow.Table``.
        """
        table_name = _Validate.table_name('table', table)
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.scan(
                table_name=table_name,
                ref=ref_value,
                columns=columns,
                filters=filters,
                limit=limit,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                client_timeout=client_timeout,
                **kwargs,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Catalog

    def get_branches(
        self,
        name: Optional[str] = None,
        user: Optional[str] = None,
        limit: Optional[int] = None,
        itersize: Optional[int] = None,
    ) -> GetBranchesResponse:
        """
        Get the available data branches in the Bauplan catalog.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            for branch in client.get_branches():
                print(branch.name, branch.hash)

        :param name: Filter the branches by name.
        :param user: Filter the branches by user.
        :param limit: Optional, max number of branches to get.
        :param itersize: Optional, overwrites `profile.catalog_max_records`, the max number of objects per HTTP request.

        :return: A GetBranchesResponse object.
        """
        params = {
            'filter_by_name': _Validate.optional_string('name', name),
            'filter_by_user': _Validate.optional_string('user', user),
        }
        limit = _Validate.optional_positive_int('limit', limit)
        itersize = _Validate.optional_positive_int('itersize', itersize) or self.profile.catalog_max_records

        return GetBranchesResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                'get',
                path=['v0', 'branches'],
                params=params,
            ),
            data_mapper=Branch.model_validate,
            limit=limit,
            itersize=itersize,
        )

    def get_branch(
        self,
        branch: Union[str, Branch],
    ) -> Branch:
        """
        Get the branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # retrieve only the tables as tuples of (name, kind)
            branch = client.get_branch('my_branch_name')
            print(branch.hash)

        :param branch: The name of the branch to retrieve.

        :raises BranchNotFoundError: if the branch does not exist.
        :raises NotABranchRefError: if the object is not a branch.
        :raises ForbiddenError: if the user does not have access to the branch.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A Branch object.
        """
        branch_name = _Validate.branch_name('branch', branch)
        out = self._make_catalog_api_call(
            'get',
            path=['v0', 'branch', branch_name],
        )
        return Branch.model_validate(out.data)

    def has_branch(
        self,
        branch: Union[str, Branch],
    ) -> bool:
        """
        Check if a branch exists.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.has_branch('my_branch_name')

        :param branch: The name of the branch to check.

        :raises NotABranchRefError: if the object is not a branch.
        :raises ForbiddenError: if the user does not have access to the branch.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A boolean for if the branch exists.
        """
        try:
            self.get_branch(branch=branch)
            return True
        except exceptions.BranchNotFoundError:
            return False

    def create_branch(
        self,
        branch: Union[str, Branch],
        from_ref: Union[str, Branch, Tag],
    ) -> Branch:
        """
        Create a new branch at a given ref.
        The branch name should follow the convention of "username.branch_name",
        otherwise non-admin users won't be able to complete the operation.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.create_branch(
                branch='username.my_branch_name',
                from_ref='my_ref_or_branch_name',
            )

        :param branch: The name of the new branch.
        :param from_ref: The name of the base branch; either a branch like "main" or ref like "main@[sha]".

        :raises CreateBranchForbiddenError: if the user does not have access to create the branch.
        :raises BranchExistsError: if the branch already exists.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: The created branch object.
        """
        out = self._make_catalog_api_call(
            'post',
            path=['v0', 'branches'],
            body={
                'branch_name': _Validate.branch_name('branch', branch),
                'from_ref': _Validate.ref('from_ref', from_ref),
            },
        )
        return Branch.model_validate(out.data)

    def merge_branch(
        self,
        source_ref: Union[str, Branch, Tag],
        into_branch: Union[str, Branch],
        commit_message: Optional[str] = None,
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
        # TODO: TO DEPRECATE
        message: Optional[str] = None,
        # TODO: TO DEPRECATE
        properties: Optional[Dict[str, str]] = None,
    ) -> Branch:
        """
        Merge one branch into another.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert merge_branch(
                source_ref='my_ref_or_branch_name',
                into_branch='main',
            )

        :param source_ref: The name of the merge source; either a branch like "main" or ref like "main@[sha]".
        :param into_branch: The name of the merge target.
        :param commit_message: Optional, the commit message.
        :param commit_body: Optional, the commit body.
        :param commit_properties: Optional, a list of properties to attach to the merge.

        :raises MergeForbiddenError: if the user does not have access to merge the branch.
        :raises BranchNotFoundError: if the destination branch does not exist.
        :raises NotAWriteBranchError: if the destination branch is not a writable ref.
        :raises MergeConflictError: if the merge operation results in a conflict.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: the Branch where the merge was made.
        """
        into_branch_name = _Validate.branch_name('into_branch', into_branch)
        source_ref_value = _Validate.ref('source_ref', source_ref)
        out = self._make_catalog_api_call(
            'post',
            path=['v0', 'refs', source_ref_value, 'merge', into_branch_name],
            body={
                'commit_message': _Validate.optional_string('commit_message', commit_message or message),
                'commit_body': _Validate.optional_string('commit_body', commit_body),
                'commit_properties': _Validate.optional_properties(
                    'commit_properties', commit_properties or properties
                ),
            },
        )
        assert out.ref is not None
        return Branch(**out.ref.model_dump())

    def delete_branch(
        self,
        branch: Union[str, Branch],
    ) -> bool:
        """
        Delete a branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.delete_branch('my_branch_name')

        :param branch: The name of the branch to delete.

        :raises DeleteBranchForbiddenError: if the user does not have access to delete the branch.
        :raises BranchNotFoundError: if the branch does not exist.
        :raises BranchHeadChangedError: if the branch head hash has changed.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A boolean for if the branch was deleted.
        """
        branch_name = _Validate.branch_name('branch', branch)
        self._make_catalog_api_call(
            'delete',
            path=['v0', 'branches', branch_name],
        )
        return True

    def get_namespaces(
        self,
        ref: Union[str, Branch, Tag, Ref],
        *,  # From here only keyword arguments are allowed
        filter_by_name: Optional[str] = None,
        limit: Optional[int] = None,
        itersize: Optional[int] = None,
    ) -> GetNamespacesResponse:
        """
        Get the available data namespaces in the Bauplan catalog branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            for namespace in client.get_namespaces('my_namespace_name'):
                print(namespace.name)

        :param ref: The ref, branch name or tag name to retrieve the namespaces from.
        :param filter_by_name: Optional, filter the namespaces by name.
        :param limit: Optional, max number of namespaces to get.
        :param itersize: Optional, overwrites `profile.catalog_max_records`, the max number of objects per HTTP request.

        :raises RefNotFoundError: if the ref does not exist.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :yield: A Namespace object.
        """
        ref_value = _Validate.ref('ref', ref)
        params = {
            'filter_by_name': _Validate.optional_string('filter_by_name', filter_by_name),
        }
        limit = _Validate.optional_positive_int('limit', limit)
        itersize = _Validate.optional_positive_int('itersize', itersize) or self.profile.catalog_max_records

        return GetNamespacesResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                'get',
                path=['v0', 'refs', ref_value, 'namespaces'],
                params=params,
            ),
            data_mapper=Namespace.model_validate,
            limit=limit,
            itersize=itersize,
        )

    def get_namespace(
        self,
        namespace: Union[str, Namespace],
        ref: Union[str, Branch, Tag, Ref],
    ) -> Namespace:
        """
        Get a namespace.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            namespace =  client.get_namespace(
                namespace='my_namespace_name',
                ref='my_ref_or_branch_name',
            )

        :param namespace: The name of the namespace to get.
        :param ref: The ref, branch name or tag name to check the namespace on.

        :raises NamespaceNotFoundError: if the namespace does not exist.
        :raises RefNotFoundError: if the ref does not exist.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A Namespace object.
        """
        namespace_name = _Validate.namespace_name('namespace', namespace)
        ref_value = _Validate.ref('ref', ref)
        out = self._make_catalog_api_call(
            method='get',
            path=['v0', 'refs', ref_value, 'namespaces', namespace_name],
        )
        return Namespace.model_validate({**out.data, 'ref': out.ref})

    def create_namespace(
        self,
        namespace: Union[str, Namespace],
        branch: Union[str, Branch],
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
        # TODO: TO DEPRECATE
        properties: Optional[Dict[str, str]] = None,
    ) -> Namespace:
        """
        Create a new namespace at a given branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.create_namespace(
                namespace='my_namespace_name'
                branch='my_branch_name',
            )

        :param namespace: The name of the namespace.
        :param branch: The name of the branch to create the namespace on.
        :param commit_body: Optional, the commit body to attach to the operation.
        :param commit_properties: Optional, a list of properties to attach to the commit.

        :raises CreateNamespaceForbiddenError: if the user does not have access to create the namespace.
        :raises BranchNotFoundError: if the branch does not exist.
        :raises NotAWriteBranchError: if the destination branch is not a writable ref.
        :raises BranchHeadChangedError: if the branch head hash has changed.
        :raises NamespaceExistsError: if the namespace already exists.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: The created namespace.
        """
        namespace_name = _Validate.namespace_name('namespace', namespace)
        branch_name = _Validate.branch_name('branch', branch)
        out = self._make_catalog_api_call(
            method='post',
            path=['v0', 'branches', branch_name, 'namespaces'],
            body={
                'namespace_name': namespace_name,
                'commit_body': _Validate.optional_string('commit_body', commit_body),
                'commit_properties': _Validate.optional_properties(
                    'commit_properties', commit_properties or properties
                ),
            },
        )
        return Namespace.model_validate({**out.data, 'ref': out.ref})

    def delete_namespace(
        self,
        namespace: Union[str, Namespace],
        branch: Union[str, Branch],
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
        # TODO: TO DEPRECATE
        properties: Optional[Dict[str, str]] = None,
    ) -> Branch:
        """
        Delete a namespace.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.delete_namespace(
                namespace='my_namespace_name',
                branch='my_branch_name',
            )

        :param namespace: The name of the namespace to delete.
        :param form_branch: The name of the branch to delete the namespace from.
        :param commit_body: Optional, the commit body to attach to the operation.
        :param commit_properties: Optional, a list of properties to attach to the commit.

        :raises DeleteBranchForbiddenError: if the user does not have access to delete the branch.
        :raises BranchNotFoundError: if the branch does not exist.
        :raises NotAWriteBranchError: if the destination branch is not a writable ref.
        :raises BranchHeadChangedError: if the branch head hash has changed.
        :raises NamespaceNotFoundError: if the namespace does not exist.
        :raises NamespaceIsNotEmptyError: if the namespace is not empty.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A Branch object pointing to head.
        """
        namespace_name = _Validate.namespace_name('namespace', namespace)
        branch_name = _Validate.branch_name('branch', branch)
        out = self._make_catalog_api_call(
            'delete',
            path=['v0', 'branches', branch_name, 'namespaces', namespace_name],
            body={
                'commit_properties': _Validate.optional_properties(
                    'properties', commit_properties or properties
                ),
                'commit_body': _Validate.optional_string('commit_body', commit_body),
            },
        )
        assert out.ref is not None
        return Branch(**out.ref.model_dump())

    def has_namespace(
        self,
        namespace: Union[str, Namespace],
        ref: Union[str, Branch, Tag, Ref],
    ) -> bool:
        """
        Check if a namespace exists.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.has_namespace(
                namespace='my_namespace_name',
                ref='my_ref_or_branch_name',
            )

        :param namespace: The name of the namespace to check.
        :param ref: The ref, branch name or tag name to check the namespace on.

        :raises RefNotFoundError: if the ref does not exist.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A boolean for if the namespace exists.
        """
        try:
            self.get_namespace(namespace=namespace, ref=ref)
            return True
        except exceptions.ResourceNotFoundError:
            return False

    def get_job(self, job_id: str) -> Job:
        """
        EXPERIMENTAL: Get a job by ID.
        """
        return self._jobs.get_job(job_id)

    def list_jobs(
        self,
        all_users: Optional[bool] = None,
    ) -> List[Job]:
        """
        EXPERIMENTAL: List all jobs
        """
        return self._jobs.list_jobs(
            all_users=all_users,
        )

    def get_job_logs(self, job_id_prefix: str) -> List[JobLog]:
        """
        EXPERIMENTAL: Get logs for a job by ID prefix.
        """
        return self._jobs.get_logs(job_id_prefix)

    def cancel_job(self, job_id: str) -> Job:
        """
        EXPERIMENTAL: Cancel a job by ID.
        """
        return self._jobs.cancel_job(job_id)

    def get_tables(
        self,
        ref: Union[str, Branch, Tag, Ref],
        *,  # From here only keyword arguments are allowed
        filter_by_name: Optional[str] = None,
        filter_by_namespace: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        include_raw: bool = False,
        limit: Optional[int] = None,
        itersize: Optional[int] = None,
    ) -> GetTablesResponse:
        """
        Get the tables and views in the target branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # retrieve only the tables as tuples of (name, kind)
            for table in client.get_tables('my_ref_or_branch_name'):
                print(table.name, table.kind)

        :param ref: The ref or branch to get the tables from.
        :param filter_by_name: Optional, the table name to filter by.
        :param filter_by_namespace: Optional, the namespace to get filtered tables from.
        :param namespace: DEPRECATED: Optional, the namespace to get filtered tables from.
        :param include_raw: Whether or not to include the raw metadata.json object as a nested dict.
        :param limit: Optional, max number of tables to get.
        :param itersize: Optional, overwrites `profile.catalog_max_records`, the max number of objects per HTTP request.

        :return: A GetTablesResponse object.
        """
        ref_value = _Validate.ref('ref', ref)
        params = {
            'filter_by_name': _Validate.optional_string('filter_by_name', filter_by_name),
            'filter_by_namespace': _Validate.optional_namespace_name(
                'filter_by_namespace', filter_by_namespace
            )
            or _Validate.optional_namespace_name('namespace', namespace),
            'raw': 1 if include_raw else 0,
        }
        limit = _Validate.optional_positive_int('limit', limit)
        itersize = _Validate.optional_positive_int('itersize', itersize) or self.profile.catalog_max_records
        return GetTablesResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                'get',
                path=['v0', 'refs', ref_value, 'tables'],
                params=params,
            ),
            data_mapper=TableWithMetadata.model_validate,
            limit=limit,
            itersize=itersize,
        )

    def get_table(
        self,
        table: Union[str, Table],
        ref: Union[str, Branch, Tag, Ref],
        include_raw: bool = False,
    ) -> TableWithMetadata:
        """
        Get the table data and metadata for a table in the target branch.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # get the fields and metadata for a table
            table = client.get_table(
                table='my_table_name',
                ref='my_ref_or_branch_name',
            )

            # loop through the fields and print their name, required, and type
            for c in table.fields:
                print(c.name, c.required, c.type)

            # show the number of records in the table
            print(table.records)

        :param ref: The ref, branch name or tag name to get the table from.
        :param table: The table to retrieve.
        :param include_raw: Whether or not to include the raw metadata.json object as a nested dict.

        :raises RefNotFoundError: if the ref does not exist.
        :raises NamespaceNotFoundError: if the namespace does not exist.
        :raises TableNotFoundError: if the table does not exist.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: a TableWithMetadata object, optionally including the raw metadata.json object.
        """
        ref_value = _Validate.ref('ref', ref)
        table_name = _Validate.table_name('table', table)
        out = self._make_catalog_api_call(
            'get',
            path=['v0', 'refs', ref_value, 'tables', table_name],
            params={
                'raw': 1 if include_raw else 0,
            },
        )
        return TableWithMetadata.model_validate(out.data)

    def has_table(
        self,
        table: Union[str, Table],
        ref: Union[str, Branch, Tag, Ref],
    ) -> bool:
        """
        Check if a table exists.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.has_table(
                table='my_table_name',
                ref='my_ref_or_branch_name',
            )

        :param ref: The ref, branch name or tag name to get the table from.
        :param table: The table to retrieve.

        :raises RefNotFoundError: if the ref does not exist.
        :raises NamespaceNotFoundError: if the namespace does not exist.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A boolean for if the table exists.
        """
        try:
            self.get_table(table=table, ref=ref)
            return True
        except exceptions.TableNotFoundError:
            return False

    def delete_table(
        self,
        table: Union[str, Table],
        branch: Union[str, Branch],
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
        # TODO: TO DEPRECATE
        properties: Optional[Dict[str, str]] = None,
    ) -> Branch:
        """
        Drop a table.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.delete_table(
                table='my_table_name',
                branch='my_branch_name',
            )

        :param table: The table to delete.
        :param branch: The branch on which the table is stored.
        :param commit_body: Optional, the commit body message to attach to the commit.
        :param commit_properties: Optional, a list of properties to attach to the commit.

        :raises DeleteTableForbiddenError: if the user does not have access to delete the table.
        :raises BranchNotFoundError: if the branch does not exist.
        :raises NotAWriteBranchError: if the destination branch is not a writable ref.
        :raises BranchHeadChangedError: if the branch head hash has changed.
        :raises TableNotFoundError: if the table does not exist.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A boolean for if the table was deleted.
        """
        branch_name = _Validate.branch_name('branch', branch)
        table_name = _Validate.table_name('table', table)
        out = self._make_catalog_api_call(
            'delete',
            path=['v0', 'branches', branch_name, 'tables', table_name],
            body={
                'commit_body': _Validate.optional_string('commit_body', commit_body),
                'commit_properties': _Validate.optional_properties(
                    'commit_properties', commit_properties or properties
                ),
            },
        )
        assert out.ref is not None
        return Branch(**out.ref.model_dump())

    def revert_table(
        self,
        table: Union[str, Table],
        *,  # From here only keyword arguments are allowed
        source_ref: Union[str, Branch, Tag, Ref],
        into_branch: Union[str, Branch],
        replace: Optional[bool] = None,
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
    ) -> Branch:
        """
        Revert a table to a previous state.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert revert_table(
                table='my_table_name',
                source_ref='my_ref_or_branch_name',
                into_branch='main',
            )

        :param table: The table to revert.
        :param source_ref: The name of the source ref; either a branch like "main" or ref like "main@[sha]".
        :param into_branch: The name of the target branch where the table will be reverted.
        :param replace: Optional, whether to replace the table if it already exists.
        :param commit_body: Optional, the commit body message to attach to the operation.
        :param commit_properties: Optional, a list of properties to attach to the operation.

        :raises RevertTableForbiddenError: if the user does not have access to revert the table.
        :raises RefNotFoundError: if the ref does not exist.
        :raises BranchNotFoundError: if the destination branch does not exist.
        :raises NotAWriteBranchError: if the destination branch is not a writable ref.
        :raises BranchHeadChangedError: if the branch head hash has changed.
        :raises MergeConflictError: if the merge operation results in a conflict.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: the Branch where the revert was made.
        """
        table_name = _Validate.table_name('table', table)
        into_branch_name = _Validate.branch_name('into_branch', into_branch)
        source_ref_value = _Validate.ref('source_ref', source_ref)
        out = self._make_catalog_api_call(
            'post',
            path=['v0', 'refs', source_ref_value, 'tables', table_name, 'revert', into_branch_name],
            body={
                'replace': _Validate.optional_boolean('replace', replace),
                'commit_body': _Validate.optional_string('commit_body', commit_body),
                'commit_properties': _Validate.optional_properties('commit_properties', commit_properties),
            },
        )
        assert out.ref is not None
        return Branch(**out.ref.model_dump())

    def get_tags(
        self,
        *,  # From here only keyword arguments are allowed
        filter_by_name: Optional[str] = None,
        limit: Optional[int] = None,
        itersize: Optional[int] = None,
    ) -> GetTagsResponse:
        """
        Get all the tags.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        :param filter_by_name: Optional, filter the commits by message.
        :param filter_by_job_id: Optional, filter for a job_id.
        :param limit: Optional, max number of commits to get.
        :param itersize: Optional, overwrites `profile.catalog_max_records`, the max number of objects per HTTP request.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A GetTagsResponse object.
        """

        params = {
            'filter_by_name': _Validate.optional_string('filter_by_name', filter_by_name),
        }
        limit = _Validate.optional_positive_int('limit', limit)
        itersize = _Validate.optional_positive_int('itersize', itersize) or self.profile.catalog_max_records

        return GetTagsResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                'get',
                path=['v0', 'tags'],
                params=params,
            ),
            data_mapper=Tag.model_validate,
            limit=limit,
            itersize=itersize,
        )

    def get_tag(
        self,
        tag: Union[str, Tag],
    ) -> Tag:
        """
        Get the tag.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            # retrieve only the tables as tuples of (name, kind)
            tag = client.get_tag('my_tag_name')
            print(tag.hash)

        :param tag: The name of the tag to retrieve.

        :raises TagNotFoundError: if the tag does not exist.
        :raises NotATagRefError: if the object is not a tag.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A Tag object.
        """
        # Tag (with hash) is not supported in the catalog API
        tag_name = _Validate.tag_name('tag', tag)
        out = self._make_catalog_api_call(
            'get',
            path=['v0', 'tags', tag_name],
        )
        return Tag.model_validate(out.data)

    def has_tag(
        self,
        tag: Union[str, Tag],
    ) -> bool:
        """
        Check if a tag exists.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.has_tag(
                tag='my_tag_name',
            )

        :param tag: The tag to retrieve.

        :raises NotATagRefError: if the object is not a tag.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A boolean for if the tag exists.
        """
        try:
            self.get_tag(tag=tag)
            return True
        except exceptions.TagNotFoundError:
            return False

    def create_tag(
        self,
        tag: Union[str, Tag],
        from_ref: Union[str, Branch, Ref],
    ) -> Tag:
        """
        Create a new tag at a given ref.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.create_tag(
                tag='my_tag',
                from_ref='my_ref_or_branch_name',
            )

        :param tag: The name of the new tag.
        :param from_ref: The name of the base branch; either a branch like "main" or ref like "main@[sha]".

        :raises CreateTagForbiddenError: if the user does not have access to create the tag.
        :raises RefNotFoundError: if the ref does not exist.
        :raises TagExistsError: if the tag already exists.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: The created tag object.
        """
        tag_name = _Validate.tag_name('tag', tag)
        from_ref_value = _Validate.ref('from_ref', from_ref)
        out = self._make_catalog_api_call(
            'post',
            path=['v0', 'tags'],
            body={
                'tag_name': tag_name,
                'from_ref': from_ref_value,
            },
        )
        return Tag.model_validate(out.data)

    def delete_tag(
        self,
        tag: Union[str, Tag],
    ) -> bool:
        """
        Delete a tag.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        .. code-block:: python

            import bauplan
            client = bauplan.Client()

            assert client.delete_tag('my_tag_name')

        :param tag: The name of the tag to delete.

        :raises DeleteTagForbiddenError: if the user does not have access to delete the tag.
        :raises TagNotFoundError: if the tag does not exist.
        :raises NotATagRefError: if the object is not a tag.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A boolean for if the tag was deleted.
        """
        tag_value = _Validate.tag('tag', tag)
        self._make_catalog_api_call(
            'delete',
            path=['v0', 'tags', str(tag_value)],
        )
        return True

    def _get_tag_by_job_id(self, job_id: str) -> Tag:
        """
        EXPERIMENTAL: Get a tag by job ID.

        :raises TagNotFoundError: if the tag does not exist.
        :raises NotATagRefError: if the object is not a tag.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :meta private:
        """
        job_id = _Validate.string('job_id', job_id)
        return self.get_tag(f'bpln.job_id.{job_id}')

    def _get_commit_by_job_id(self, job_id: str) -> Commit:
        """
        EXPERIMENTAL: Get a commiy by job ID.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :meta private:
        """
        job_id = _Validate.string('job_id', job_id)
        commit = self.get_commits(f'bpln.job_id.{job_id}', limit=1)
        assert len(commit) == 1
        return commit[0]

    def get_commits(
        self,
        ref: Union[str, Branch, Tag, Ref],
        *,  # From here only keyword arguments are allowed
        filter_by_message: Optional[str] = None,
        filter_by_author_username: Optional[str] = None,
        filter_by_author_name: Optional[str] = None,
        filter_by_author_email: Optional[str] = None,
        filter_by_authored_date: Optional[Union[str, datetime]] = None,
        filter_by_authored_date_start_at: Optional[Union[str, datetime]] = None,
        filter_by_authored_date_end_at: Optional[Union[str, datetime]] = None,
        filter_by_parent_hash: Optional[str] = None,
        filter_by_properties: Optional[Dict[str, str]] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
        itersize: Optional[int] = None,
    ) -> GetCommitsResponse:
        """
        Get the commits for the target branch or ref.

        Upon failure, raises ``bauplan.exceptions.BauplanError``

        :param ref: The ref or branch to get the commits from.
        :param filter_by_message: Optional, filter the commits by message (can be a string or a regex like '^abc.*$')
        :param filter_by_author_username: Optional, filter the commits by author username (can be a string or a regex like '^abc.*$')
        :param filter_by_author_name: Optional, filter the commits by author name (can be a string or a regex like '^abc.*$')
        :param filter_by_author_email: Optional, filter the commits by author email (can be a string or a regex like '^abc.*$')
        :param filter_by_authored_date: Optional, filter the commits by the exact authored date.
        :param filter_by_authored_date_start_at: Optional, filter the commits by authored date start at.
        :param filter_by_authored_date_end_at: Optional, filter the commits by authored date end at.
        :param filter_by_parent_hash: Optional, filter the commits by parent hash.
        :param filter_by_properties: Optional, filter the commits by commit properties.
        :param filter: Optional, a CEL filter expression to filter the commits.
        :param limit: Optional, max number of commits to get.
        :param itersize: Optional, overwrites `profile.catalog_max_records`, the max number of objects per HTTP request.

        :raises UnauthorizedError: if the user's credentials are invalid.
        :raises ValueError: if one or more parameters are invalid.

        :return: A GetCommitsResponse object.
        """
        ref_value = _Validate.ref('ref', ref)

        params = {
            'filter_by_message': _Validate.optional_string('filter_by_message', filter_by_message),
            'filter_by_author_username': _Validate.optional_string(
                'filter_by_author_username', filter_by_author_username
            ),
            'filter_by_author_name': _Validate.optional_string(
                'filter_by_author_name', filter_by_author_name
            ),
            'filter_by_author_email': _Validate.optional_string(
                'filter_by_author_email', filter_by_author_email
            ),
            'filter_by_authored_date': _Validate.optional_timestamp(
                'filter_by_authored_date', filter_by_authored_date
            ),
            'filter_by_authored_date_start_at': _Validate.optional_timestamp(
                'filter_by_authored_date_start_at', filter_by_authored_date_start_at
            ),
            'filter_by_authored_date_end_at': _Validate.optional_timestamp(
                'filter_by_authored_date_end_at', filter_by_authored_date_end_at
            ),
            'filter_by_parent_hash': _Validate.optional_string(
                'filter_by_parent_hash', filter_by_parent_hash
            ),
            'filter_by_properties': json.dumps(
                _Validate.optional_properties('filter_by_properties', filter_by_properties)
            ),
            'filter': _Validate.optional_string('filter', filter),
        }
        limit = _Validate.optional_positive_int('limit', limit)
        itersize = _Validate.optional_positive_int('itersize', itersize) or self.profile.catalog_max_records

        # TODO:
        # Recover these filters:
        # filter_by_committer_name: Optional[str] = None,
        # filter_by_committer_email: Optional[str] = None,
        # filter_by_committed_date: Optional[Union[str, datetime]] = None,
        # filter_by_committed_date_start_at: Optional[Union[str, datetime]] = None,
        # filter_by_committed_date_end_at: Optional[Union[str, datetime]] = None,
        # &&
        # 'filter_by_committer_name': _Validate.optional_string(
        #     'filter_by_committer_name', filter_by_committer_name
        # ),
        # 'filter_by_committer_email': _Validate.optional_string(
        #     'filter_by_committer_email', filter_by_committer_email
        # ),
        # 'filter_by_committed_date': _Validate.optional_timestamp(
        #     'filter_by_committed_date', filter_by_committed_date
        # ),
        # 'filter_by_committed_date_start_at': _Validate.optional_timestamp(
        #     'filter_by_committed_date_start_at', filter_by_committed_date_start_at
        # ),
        # 'filter_by_committed_date_end_at': _Validate.optional_timestamp(
        #     'filter_by_committed_date_end_at', filter_by_committed_date_end_at
        # ),

        return GetCommitsResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                'get',
                path=['v0', 'refs', ref_value, 'commits'],
                params=params,
            ),
            data_mapper=Commit.model_validate,
            limit=limit,
            itersize=itersize,
        )

    def info(
        self,
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> InfoState:
        """
        Fetch organization & account information.
        """
        return self._info.info(
            debug=debug,
            verbose=verbose,
            client_timeout=client_timeout,
            **kwargs,
        )

    # Helpers

    @_lifecycle
    def _make_catalog_api_call(
        self,
        method: str,
        path: Union[str, List[str], Tuple[str]],
        params: Optional[Dict] = None,
        body: Optional[Dict] = None,
        pagination_token: Optional[str] = None,
        # shared
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> APIResponseWithData:
        """
        Helper to make a request to the API.

        :meta private:
        """
        if isinstance(path, list) or isinstance(path, tuple):
            path = _Validate.quoted_url(*path)
        url = self.profile.catalog_endpoint + path
        headers = {Constants.METADATA_PYPI_VERSION_KEY: BAUPLAN_VERSION}
        if self.profile.user_session_token:
            headers = {Constants.METADATA_USER_SESSION_TOKEN: self.profile.user_session_token}
        elif self.profile.api_key:
            headers = {Constants.METADATA_API_KEY: self.profile.api_key}
        if self.profile.feature_flags:
            headers[Constants.METADATA_FEATURE_FLAGS] = json.dumps(self.profile.feature_flags)
        params = params or {}
        if pagination_token and pagination_token.strip():
            params['pagination_token'] = pagination_token.strip()

        if body is not None and not isinstance(body, dict):
            raise exceptions.BauplanError(
                f'SDK INTERNAL ERROR: API request body must be dict, not {type(body)}'
            )
        res = requests.request(
            method,
            url,
            headers=headers,
            timeout=Constants.DEFAULT_API_CALL_TIMEOUT_SECONDS,
            params=params or {},
            json=body,
        )

        try:
            res_data = res.json()
            if res.status_code == 200:
                return APIResponseWithData.model_validate(res_data)

            if not isinstance(res_data, dict) or not res_data.get('metadata'):
                # We can't parse the response, raise a generic error
                raise exceptions.BauplanError(f'API response error: {res.status_code} - {res_data}')

            # This is a bauplan error
            if not res_data.get('error'):
                # This is the old response error, catalog is not updated yet
                res_data['error'] = {
                    'code': res.status_code,
                    'type': 'APIError',
                    'message': res_data.get('metadata', {})['error'],
                    'context': {},
                }
            raise exceptions.BauplanHTTPError.new_from_response(
                out=APIResponseWithError.model_validate(res_data),
            )
        except exceptions.BauplanHTTPError as e:
            raise e
        except pydantic.ValidationError as e:
            raise exceptions.BauplanError(f'API response parsing error: {e}') from e

    def _new_paginate_api_data_fetcher(
        self, method: str, path: Union[str, List[str]], params: dict[str, Any]
    ) -> Callable[[int, Optional[str]], APIResponse]:
        """
        Helper to create a new data fetcher.

        :meta private:
        """

        def _fetcher(max_records: int, pagination_token: Optional[str]) -> APIResponse:
            return self._make_catalog_api_call(
                method=method,
                path=path,
                params={**params, 'max_records': max_records},
                pagination_token=pagination_token,
            )

        return _fetcher
