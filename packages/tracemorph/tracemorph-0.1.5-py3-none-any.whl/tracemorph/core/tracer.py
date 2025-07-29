import sys
import time
import inspect
import functools
import threading
import traceback
from flask import Response
from ..store.trace_log import TraceStore


# Thread-local untuk menyimpan call stack per thread
call_context = threading.local()


def trace(_func=None, *, category=None, level=None):
    """
    Decorator untuk melacak pemanggilan fungsi dan menyimpan metadata-nya ke TraceStore.
    
    Bisa digunakan sebagai:
        @trace
        def foo(): ...
    
    atau dengan opsi:
        @trace(category="db", level="info")
        def bar(): ...
    """

    def decorator_trace(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__

            try:
                func_file = inspect.getfile(func)
            except Exception:
                func_file = "<unknown>"

            try:
                func_line = inspect.getsourcelines(func)[1]
            except Exception:
                func_line = -1

            # Ambil parent ID dari stack thread-local
            stack = getattr(call_context, 'stack', [])
            parent = stack[-1] if stack else None

            current_id = TraceStore.next_id()
            stack.append(current_id)
            call_context.stack = stack

            start = time.time()
            result = None
            success = False
            status_code = None
            exception_message = None
            error_line = func_line

            try:
                result = func(*args, **kwargs)
                success = True

                # Deteksi jika response adalah Flask Response atau (data, status_code)
                if isinstance(result, Response):
                    status_code = result.status_code
                elif isinstance(result, tuple) and len(result) >= 2:
                    status_code = result[1]

                return result

            except Exception as e:
                exception_message = str(e)
                result = f"Exception: {e}"

                tb = traceback.extract_tb(sys.exc_info()[2])
                if tb:
                    error_line = tb[-1].lineno

                raise  # Tetap lempar exception agar tidak ditelan

            finally:
                end = time.time()
                duration = round(end - start, 6)

                final_level = level
                if final_level is None:
                    if not success:
                        final_level = "error" if exception_message else "warning"
                    elif status_code is not None:
                        if status_code >= 500:
                            final_level = "error"
                        elif status_code >= 400:
                            final_level = "warning"
                        else:
                            final_level = "info"
                    else:
                        final_level = "info"

                TraceStore.log_call(
                    id=current_id,
                    name=func_name,
                    file=func_file,
                    line=error_line,
                    args=args,
                    kwargs=kwargs,
                    result=result,
                    duration=duration,
                    parent=parent,
                    success=success,
                    exception_message=exception_message,
                    category=category,
                    level=final_level,
                    status_code=status_code
                )

                # Pop current ID dari stack
                stack.pop()
                call_context.stack = stack

        return wrapper

    # Jika dekorator dipanggil tanpa argumen
    if callable(_func):
        return decorator_trace(_func)

    # Jika dekorator dipanggil dengan argumen
    return decorator_trace
