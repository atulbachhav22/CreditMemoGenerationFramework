"""
McpCaller - Utility for calling MCP (Model Context Protocol) tools to fetch context data.

Supports two transports:
  - SSE  : HTTP/HTTPS-based MCP servers  (server starts with http:// or https://)
  - Stdio : subprocess-based MCP servers  (server is a shell command, e.g. "npx -y @mcp/server-fs /data")

Transport auto-detection uses the server field prefix.

All async MCP operations are bridged to synchronous callers via asyncio.run(),
keeping the rest of the skill execution engine synchronous.
"""

import asyncio
import json
import shlex
from typing import Any, Optional

from loguru import logger

from skill_engine.models.skill import McpContextDefinition, McpTransport


class McpCallError(Exception):
    """Raised when an MCP tool call fails."""

    def __init__(self, message: str, alias: str = ""):
        super().__init__(message)
        self.alias = alias


class McpCaller:
    """
    Executes MCP tool calls defined in McpContextDefinition objects.

    Usage:
        caller = McpCaller()
        result = caller.call_tool(mcp_def)
    """

    def call_tool(self, mcp_def: McpContextDefinition) -> Any:
        """
        Execute an MCP tool call and return the result.

        Args:
            mcp_def: The MCP context definition to execute

        Returns:
            Tool result (string, dict, or list depending on tool output)

        Raises:
            McpCallError: If the call fails
        """
        transport = self._resolve_transport(mcp_def)
        logger.info(
            f"Calling MCP tool [{transport.value}] server={mcp_def.server!r} "
            f"tool={mcp_def.tool!r} alias={mcp_def.alias!r}"
        )

        try:
            if transport == McpTransport.SSE:
                return asyncio.run(self._call_sse(mcp_def))
            else:
                return asyncio.run(self._call_stdio(mcp_def))
        except McpCallError:
            raise
        except Exception as e:
            raise McpCallError(
                f"MCP call failed for '{mcp_def.alias}': {e}",
                alias=mcp_def.alias,
            ) from e

    # ------------------------------------------------------------------
    # Transport resolution
    # ------------------------------------------------------------------

    def _resolve_transport(self, mcp_def: McpContextDefinition) -> McpTransport:
        if mcp_def.transport != McpTransport.AUTO:
            return mcp_def.transport
        if mcp_def.server.startswith(("http://", "https://")):
            return McpTransport.SSE
        return McpTransport.STDIO

    # ------------------------------------------------------------------
    # SSE transport (HTTP-based MCP servers)
    # ------------------------------------------------------------------

    async def _call_sse(self, mcp_def: McpContextDefinition) -> Any:
        try:
            from mcp.client.sse import sse_client
            from mcp import ClientSession
        except ImportError as exc:
            raise McpCallError(
                "The 'mcp' package is required for MCP calls. "
                "Install it with: pip install mcp",
                alias=mcp_def.alias,
            ) from exc

        async with sse_client(mcp_def.server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    mcp_def.tool,
                    arguments=mcp_def.arguments or {},
                )
                return self._extract_content(result, mcp_def.alias)

    # ------------------------------------------------------------------
    # Stdio transport (subprocess-based MCP servers)
    # ------------------------------------------------------------------

    async def _call_stdio(self, mcp_def: McpContextDefinition) -> Any:
        try:
            from mcp.client.stdio import stdio_client
            from mcp import ClientSession, StdioServerParameters
        except ImportError as exc:
            raise McpCallError(
                "The 'mcp' package is required for MCP calls. "
                "Install it with: pip install mcp",
                alias=mcp_def.alias,
            ) from exc

        command, *args = shlex.split(mcp_def.server)
        server_params = StdioServerParameters(command=command, args=args)

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    mcp_def.tool,
                    arguments=mcp_def.arguments or {},
                )
                return self._extract_content(result, mcp_def.alias)

    # ------------------------------------------------------------------
    # Result extraction
    # ------------------------------------------------------------------

    def _extract_content(self, result: Any, alias: str) -> Any:
        """
        Extract usable content from an MCP CallToolResult.

        MCP tool results contain a list of content items (text, image, etc.).
        We join text items and return the combined string, or the raw list
        if non-text content is present.
        """
        if not hasattr(result, "content"):
            return result

        text_parts = []
        other_parts = []

        for item in result.content:
            item_type = getattr(item, "type", None)
            if item_type == "text":
                text_parts.append(item.text)
            else:
                other_parts.append(item)

        if other_parts:
            # Return a structured dict when there is non-text content
            return {
                "text": "\n".join(text_parts) if text_parts else None,
                "other": [vars(p) if hasattr(p, "__dict__") else str(p) for p in other_parts],
            }

        combined = "\n".join(text_parts)

        # Try to parse as JSON so downstream LLM context is richer
        try:
            return json.loads(combined)
        except (json.JSONDecodeError, ValueError):
            return combined
