from contextvars import ContextVar
from intelliw.utils.intelliwapi.request import Request

_data_pool_context_storage: ContextVar = ContextVar(
    "data-pool", default=None
)

_request_header_context_storage: ContextVar = ContextVar(
    "request-header", default={}
)

_request_pool_context_storage: ContextVar = ContextVar(
    "req-pool", default=Request()
)
