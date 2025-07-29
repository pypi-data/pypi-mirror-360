from typing import Any, Optional
import time
from datetime import datetime, timezone
from fastmcp.server.middleware import MiddlewareContext, CallNext
from fastmcp.server.context import Context

# Try importing TextContent for specific handling of tool responses
try:
    from mcp.types import TextContent
except ImportError:
    TextContent = None


class TraceMiddleware:
    """
    Middleware to trace incoming MCP requests and responses.

    It logs metadata such as request type, method, session ID, duration, tool inputs,
    and outputs to a provided adapter (e.g., file logger, OpenTelemetry exporter, etc.).
    """

    def __init__(self, adapter):
        """
        Initialize the middleware with a custom adapter to export trace data.
        
        Args:
            adapter: A logging/export adapter implementing an `export(dict)` method.
        """
        self.adapter = adapter

    async def __call__(self, context: MiddlewareContext, call_next: CallNext):
        """
        Middleware entrypoint. Measures the request duration and builds the trace data.
        
        Args:
            context: The current middleware context including request metadata.
            call_next: A function to pass control to the next handler.
        
        Returns:
            The response returned from downstream handlers.
        """
        start_time = time.time()
        response = await call_next(context)
        duration = time.time() - start_time

        trace_data = self._extract_base_trace_data(context, duration)

        if self._is_tool_call(context):
            # If this is a tool call, augment trace data with tool request/response info
            trace_data.update(self._extract_tool_call_trace(context, response))

        # Export collected trace data to the adapter
        self.adapter.export(trace_data)
        return response

    def _extract_base_trace_data(self, context: MiddlewareContext, duration: float) -> dict[str, Any]:
        """
        Extracts common trace metadata for all request types.

        Args:
            context: MiddlewareContext object with request metadata.
            duration: Request duration in seconds.

        Returns:
            A dictionary of base trace metadata.
        """
        fastmcp_ctx: Optional[Context] = getattr(context, 'fastmcp_context', None)
        timestamp = getattr(context, 'timestamp', datetime.now(timezone.utc))

        return {
            'type': getattr(context, 'type', None),
            'method': getattr(context, 'method', None),
            'timestamp': timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
            'session_id': getattr(fastmcp_ctx, 'session_id', None),
            'request_id': getattr(fastmcp_ctx, 'request_id', None),
            'client_id': getattr(fastmcp_ctx, 'client_id', None),
            'duration': duration,
        }

    def _is_tool_call(self, context: MiddlewareContext) -> bool:
        """
        Checks whether the current request is a tool invocation.

        Args:
            context: MiddlewareContext with the request type/method.

        Returns:
            True if the request is a tool call; otherwise, False.
        """
        return getattr(context, 'type', None) == 'request' and getattr(context, 'method', None) == 'tools/call'

    def _extract_tool_call_trace(self, context: MiddlewareContext, response: Any) -> dict[str, Any]:
        """
        Extracts tool request and response data if this is a tool call.

        Args:
            context: MiddlewareContext with the tool call.
            response: The response returned by the downstream handler.

        Returns:
            A dictionary of tool-specific trace metadata.
        """
        trace = {}

        # Extract the tool name and arguments
        request_msg = getattr(context, 'message', None)
        if request_msg:
            if hasattr(request_msg, 'name'):
                trace['tool_name'] = getattr(request_msg, 'name', None)
            if hasattr(request_msg, 'arguments'):
                trace['tool_arguments'] = getattr(request_msg, 'arguments', None)

        # Extract response text and structured content if available
        tool_response = self._extract_text_response(response)
        structured = self._extract_structured_response(response)

        if tool_response:
            trace['tool_response'] = tool_response
        if structured:
            trace['tool_response_structured'] = structured

        return trace

    def _extract_text_response(self, response: Any) -> Optional[str]:
        """
        Extracts plain-text content from the tool response.

        Args:
            response: The response object, possibly with `.content`.

        Returns:
            A string of concatenated text blocks, if available.
        """
        content_blocks = getattr(response, 'content', [])
        if not content_blocks:
            return None

        # Use `TextContent` type if available
        if TextContent:
            texts = [
                block.text for block in content_blocks
                if isinstance(block, TextContent)
            ]
        else:
            texts = [str(block) for block in content_blocks]

        return '\n'.join(texts) if texts else None

    def _extract_structured_response(self, response: Any) -> Optional[Any]:
        """
        Extracts structured content from the response.

        Args:
            response: The response object.

        Returns:
            The structured content, if found.
        """
        return (
            getattr(response, 'structured_content', None)
            or getattr(response, 'structuredContent', None)
        )
