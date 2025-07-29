# tracemorph/core/error_hook.py

import sys
import traceback
from ..store.trace_log import TraceStore

def global_exception_hook(exc_type, exc_value, exc_traceback):
    tb_list = traceback.extract_tb(exc_traceback)
    last_frame = tb_list[-1] if tb_list else None

    trace_id = TraceStore.next_id()
    recent_trace = TraceStore.get_last(1)
    parent_id = recent_trace[0]["id"] if recent_trace else None

    filename = last_frame.filename if last_frame else "<unknown>"
    lineno = last_frame.lineno if last_frame else -1

    exception_str = str(exc_value)
    exception_name = exc_type.__name__

    # Klasifikasikan level dan status_code berdasarkan tipe exception
    status_code = _map_status_code(exception_name)
    level = _map_level(status_code)

    # Penentuan kategori berdasarkan nama exception
    category = _map_category(exception_name)

    TraceStore.log_call(
        id=trace_id,
        name="uncaught_exception",
        file=filename,
        line=lineno,
        args=[],
        kwargs={},
        result=None,
        duration=0,
        parent=parent_id,
        success=False,
        exception_message=exception_str,
        category=category,
        level=level,
        status_code=status_code,
    )

    # Handler lain akan jalan via TraceStore.register_handler()

def setup_error_hook():
    sys.excepthook = global_exception_hook

# ===============================================
# Helpers untuk mapping exception → category, dll
# ===============================================

def _map_status_code(exception_name: str) -> int:
    """
    Menerjemahkan nama exception menjadi status_code semantik.
    """
    if "Permission" in exception_name or "Auth" in exception_name:
        return 403
    elif "NotFound" in exception_name:
        return 404
    elif "Validation" in exception_name or "ValueError" in exception_name:
        return 422
    elif "KeyboardInterrupt" in exception_name:
        return 499
    elif "ZeroDivisionError" in exception_name or "TypeError" in exception_name:
        return 400
    else:
        return 500

def _map_level(status_code: int) -> str:
    if status_code >= 500:
        return "critical"
    elif status_code >= 400:
        return "error"
    elif status_code >= 300:
        return "warning"
    else:
        return "info"

def _map_category(exception_name: str) -> str:
    exception_name = exception_name.lower()
    if "auth" in exception_name:
        return "auth"
    elif "permission" in exception_name:
        return "permission"
    elif "validate" in exception_name or "value" in exception_name:
        return "validation"
    elif "type" in exception_name:
        return "type"
    elif "key" in exception_name:
        return "key"
    elif "notfound" in exception_name:
        return "missing"
    elif "interrupt" in exception_name:
        return "signal"
    else:
        return "uncaught"
