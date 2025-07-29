from typing import Any, Type

from .schema import APIResponseWithError
from .state import TableCreatePlanApplyState, TableCreatePlanState


class BauplanError(Exception): ...


class BauplanHTTPError(BauplanError):
    response: APIResponseWithError

    def __init__(self, response: APIResponseWithError, *args, **kwds) -> None:
        super().__init__(response.error.message, *args, **kwds)
        self.response = response

    @property
    def code(self) -> int:
        return self.response.error.code

    @property
    def type(self) -> str:
        return self.response.error.type

    @property
    def message(self) -> str:
        return self.response.error.message

    @property
    def context(self) -> dict[str, Any]:
        return self.response.error.context

    @staticmethod
    def new_from_response(out: APIResponseWithError) -> 'BauplanHTTPError':
        # Map the error by error type
        if out.error.type in _map_type_to_exception:
            return _map_type_to_exception[out.error.type](out)
        # Fallback to status_code
        if out.error.code in _map_code_to_exception:
            return _map_code_to_exception[out.error.code](out)
        # Fall back to generic error
        raise BauplanHTTPError(out)


# More specific exceptions raised during API calls


# region 400 Bad Request


class BadRequestError(BauplanHTTPError): ...


class InvalidDataError(BadRequestError): ...


class InvalidRefError(BadRequestError): ...


class NonBranchRefWriteError(InvalidRefError): ...


class NotATagRefError(InvalidRefError): ...


class NotABranchRefError(InvalidRefError): ...


class NotAWriteBranchRefError(NotABranchRefError): ...


class SameRefError(InvalidRefError): ...


# endregion
# region 401 Unauthorized


class UnauthorizedError(BauplanHTTPError): ...


# endregion
# region 403 Forbidden


# TODO: deprecated
class AccessDeniedError(BauplanHTTPError): ...


class ForbiddenError(BauplanHTTPError): ...


class CreateBranchForbiddenError(ForbiddenError): ...


class CreateNamespaceForbiddenError(ForbiddenError): ...


class CreateTagForbiddenError(ForbiddenError): ...


class DeleteBranchForbiddenError(ForbiddenError): ...


class DeleteNamespaceForbiddenError(ForbiddenError): ...


class DeleteTableForbiddenError(ForbiddenError): ...


class DeleteTagForbiddenError(ForbiddenError): ...


class MergeForbiddenError(ForbiddenError): ...


class RevertTableForbiddenError(ForbiddenError): ...


# endregion
# region 404 Not Found


class NotFoundError(BauplanHTTPError): ...


class ResourceNotFoundError(NotFoundError): ...


class BranchNotFoundError(ResourceNotFoundError): ...


class NamespaceNotFoundError(ResourceNotFoundError): ...


class RefNotFoundError(ResourceNotFoundError): ...


class TableNotFoundError(ResourceNotFoundError): ...


class TagNotFoundError(ResourceNotFoundError): ...


class ApiMethodError(ResourceNotFoundError): ...


# endregion
# region 405 Method Not Allowed


class MethodNotAllowedError(BauplanHTTPError): ...


class ApiRouteError(MethodNotAllowedError): ...


# endregion
# region 409 Conflict


class ConflictError(BauplanHTTPError): ...


class UpdateConflictError(ConflictError): ...


class BranchExistsError(UpdateConflictError): ...


class BranchHeadChangedError(UpdateConflictError): ...


class MergeConflictError(UpdateConflictError): ...


class NamespaceExistsError(UpdateConflictError): ...


class NamespaceIsNotEmptyError(UpdateConflictError): ...


class RevertDestinationTableExistsError(UpdateConflictError): ...


class RevertIdenticalTableError(UpdateConflictError): ...


class TagExistsError(UpdateConflictError): ...


# endregion
# region 429 Too Many Requests


class TooManyRequestsError(BauplanHTTPError): ...


# endregion
# region 500 Internal Server Error


class InternalError(BauplanHTTPError): ...


# endregion
# region 502 Bad Gateway


class BadGatewayError(BauplanHTTPError): ...


# endregion
# region 503 Service Unavailable


class ServiceUnavailableError(BauplanHTTPError): ...


# endregion
# region 504 Gateway Timeout


class GatewayTimeoutError(BauplanHTTPError): ...


# endregion


# Exceptions raised during loading of object
class UserObjectKeyNotExistsError(BauplanError): ...


class MismatchedPythonVersionsError(BauplanError): ...


# Exceptions raised during saving object
class UserObjectWithKeyExistsError(BauplanError): ...


class ObjectTooBigError(BauplanError): ...


class ObjectCannotBeSerializedError(BauplanError): ...


class UnhandledRuntimeError(BauplanError): ...


# Exceptions during a run


class NoResultsFoundError(BauplanError): ...


class JobError(BauplanError): ...


class BauplanQueryError(JobError): ...


# Exceptions during an import


class InvalidPlanError(BauplanError): ...


class MissingPandasError(BauplanError):
    def __init__(self) -> None:
        super().__init__('Pandas is not installed. Please do `pip3 install pandas` to resolve this error.')


class MissingMagicCellError(BauplanError):
    def __init__(self) -> None:
        super().__init__(
            '`from IPython.core.magic import register_cell_magic` failed: are you in a Python notebook context? You can do `pip3 install jupyterlab` to resolve this error.'
        )


# Exceptions during table creation


class TableCreatePlanError(BauplanError): ...


class TableCreatePlanStatusError(TableCreatePlanError):
    def __init__(self, message: str, state: TableCreatePlanState, *args) -> None:
        super().__init__(*args)
        self.message = message
        self.state = state


class TableCreatePlanApplyStatusError(BauplanError):
    def __init__(self, message: str, state: TableCreatePlanApplyState, *args) -> None:
        super().__init__(*args)
        self.message = message
        self.state = state


_map_type_to_exception: dict[str, Type[BauplanHTTPError]] = {
    'BRANCH_EXISTS': BranchExistsError,
    'BRANCH_HEAD_CHANGED': BranchHeadChangedError,
    'BRANCH_NOT_FOUND': BranchNotFoundError,
    'CREATE_BRANCH_FORBIDDEN': CreateBranchForbiddenError,
    'CREATE_NAMESPACE_FORBIDDEN': CreateNamespaceForbiddenError,
    'CREATE_TAG_FORBIDDEN': CreateTagForbiddenError,
    'DELETE_BRANCH_FORBIDDEN': DeleteBranchForbiddenError,
    'DELETE_NAMESPACE_FORBIDDEN': DeleteNamespaceForbiddenError,
    'DELETE_TABLE_FORBIDDEN': DeleteTableForbiddenError,
    'DELETE_TAG_FORBIDDEN': DeleteTagForbiddenError,
    'INVALID_REF': InvalidRefError,
    'MERGE_CONFLICT': MergeConflictError,
    'MERGE_FORBIDDEN': MergeForbiddenError,
    'NAMESPACE_EXISTS': NamespaceExistsError,
    'NAMESPACE_IS_NOT_EMPTY': NamespaceIsNotEmptyError,
    'NAMESPACE_NOT_FOUND': NamespaceNotFoundError,
    'NOT_A_BRANCH_REF': NotABranchRefError,
    'NOT_A_TAG_REF': NotATagRefError,
    'NOT_A_WRITE_BRANCH_REF': NotAWriteBranchRefError,
    'REF_NOT_FOUND': RefNotFoundError,
    'REVERT_DESTINATION_TABLE_EXISTS': RevertDestinationTableExistsError,
    'REVERT_IDENTICAL_TABLE': RevertIdenticalTableError,
    'REVERT_TABLE_FORBIDDEN': RevertTableForbiddenError,
    'SAME_REF': SameRefError,
    'TABLE_NOT_FOUND': TableNotFoundError,
    'TAG_EXISTS': TagExistsError,
    'TAG_NOT_FOUND': TagNotFoundError,
}
_map_code_to_exception: dict[int, Type[BauplanHTTPError]] = {
    400: InvalidDataError,
    401: UnauthorizedError,
    403: AccessDeniedError,
    404: ResourceNotFoundError,
    405: ApiRouteError,
    409: UpdateConflictError,
    429: TooManyRequestsError,
    500: InternalError,
    502: BadGatewayError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}
