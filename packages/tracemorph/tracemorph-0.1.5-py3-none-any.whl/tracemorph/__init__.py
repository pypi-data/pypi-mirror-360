# tracemorph/__init__.py

from .core.tracer import trace
from .core.error_hook import setup_error_hook
from .store.trace_log import TraceStore
from .output.json_exporter import JSONExporter
from .core.builder import TraceBuilder

# Default exporter: JSON file
json_exporter = JSONExporter("results.json")
TraceStore.register_handler("json", json_exporter)

# Pasang global exception hook agar semua unhandled error ditrace
setup_error_hook()

# Shortcut: import tracemorph → dapat @trace langsung
__all__ = ["trace", "TraceStore", "json_exporter", "TraceBuilder"]
