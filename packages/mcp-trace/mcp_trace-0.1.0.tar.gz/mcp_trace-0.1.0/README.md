# mcp-trace

Tracing middleware for FastMCP with pluggable adapters (local file, PostgreSQL, custom).

## Usage

```python
from mcp_trace.middleware import TraceMiddleware
from mcp_trace.adapters.local import LocalTraceAdapter

trace_adapter = LocalTraceAdapter("trace.log")
trace_middleware = TraceMiddleware(adapter=trace_adapter)
mcp.add_middleware(trace_middleware)
```
