import logging
import contextvars
from opentelemetry import trace

# --- Контекст для request_id ---
request_id_ctx = contextvars.ContextVar("request_id", default="-")

def _hex_trace_id():
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.trace_id:
        return f"{ctx.trace_id:032x}"
    return "-"

def _hex_span_id():
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.span_id:
        return f"{ctx.span_id:016x}"
    return "-"

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        record.trace_id = _hex_trace_id()
        record.span_id = _hex_span_id()
        return True

LOG_FORMAT = ('%(asctime)s - %(name)s - %(levelname)s - '
              'trace_id=%(trace_id)s span_id=%(span_id)s '
              'req_id=%(request_id)s - %(message)s')
LOG_DEFAULT_HANDLERS = ['console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': RequestIdFilter,  # 👈 добавили фильтр
        },
    },
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT
        },
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(message)s',
            'use_colors': None,
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['request_id'],  # 👈 навешиваем фильтр
        },
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'filters': ['request_id'],
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': LOG_DEFAULT_HANDLERS,
            'level': 'INFO',
        },
        'uvicorn.error': {
            'level': 'INFO',
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'level': 'INFO',
        'formatter': 'verbose',
        'handlers': LOG_DEFAULT_HANDLERS,
    },
}
