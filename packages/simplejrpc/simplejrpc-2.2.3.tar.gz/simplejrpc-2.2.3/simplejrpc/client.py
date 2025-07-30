# -*- encoding: utf-8 -*-
import asyncio
import json
import socket
from typing import Any, Dict, Optional, Tuple, Union, overload

from jsonrpcclient import request
from jsonrpcclient.sentinels import NOID

from simplejrpc.config import DEFAULT_GA_SOCKET
from simplejrpc.interfaces import ClientTransport
from simplejrpc.response import Response


# ------------------------------
# Implementer: Transport Adapter
# ------------------------------
class UnixSocketTransport(ClientTransport):
    """Async UNIX Socket Adapter"""

    def __init__(self, socket_path: str):
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._socket_path = socket_path

    async def connect(self) -> None:
        self.reader, self.writer = await asyncio.open_unix_connection(
            path=self._socket_path
        )

    async def send_message(self, message: Union[str, dict]) -> Response:
        """Unified Message Sending Interface"""
        if isinstance(message, dict):
            message = json.dumps(message)

        payload = f"Content-Length: {len(message)}\r\n\r\n{message}"
        self.writer.write(payload.encode("utf-8"))
        await self.writer.drain()

        return await self._read_response()

    async def _read_response(self) -> Response:
        """ """
        header = await self.reader.readuntil(b"\r\n\r\n")
        content_length = int(header.split(b":")[1].strip())
        response_body = await self.reader.readexactly(content_length)
        return Response(json.loads(response_body))

    def close(self) -> None:
        if self.writer:
            self.writer.close()


class SyncUnixSocketTransport(ClientTransport):
    """Synchronous UNIX Socket Adapter"""

    def __init__(self, socket_path: str):
        self._socket_path = socket_path
        self._sock: Optional[socket.socket] = None

    def connect(self) -> None:
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.connect(self._socket_path)

    def send_message(self, message: Union[str, dict]) -> Response:
        if isinstance(message, dict):
            message = json.dumps(message)

        payload = f"Content-Length: {len(message)}\r\n\r\n{message}"
        self._sock.sendall(payload.encode("utf-8"))
        return self._read_response()

    def _extract_header_length(self, header) -> int:
        """ """
        try:
            return int((header.split(b":")[-1]).decode().strip())
        except Exception as _:
            return 0

    def _read_response(self) -> Response:
        header = b""
        while b"\r\n\r\n" not in header:
            header += self._sock.recv(1024)

        header_content, body_content = header.split(b"\r\n\r\n")
        content_length = self._extract_header_length(header_content)
        response_body = body_content
        while len(response_body) < content_length:
            response_body += self._sock.recv(content_length - len(response_body))

        return Response(json.loads(response_body))

    def close(self) -> None:
        if self._sock:
            self._sock.close()


# ------------------------------
# Abstraction layer: RPC client
# ------------------------------
class RpcClient:
    """Abstract RPC Client (Bridge Mode Abstraction Layer)"""

    def __init__(self, transport: Optional[ClientTransport] = None):
        self._transport = transport

    async def _create_transport(self) -> ClientTransport:
        """The transmission creation logic (factory method) that subclasses need to implement"""
        raise NotImplementedError

    async def _get_transport(self) -> ClientTransport:
        """Get the transmission instance (prioritize using the incoming adapter)"""
        if self._transport:
            return self._transport
        # Delay creation of built-in transmission (subclass implementation)
        return await self._create_transport()

    @overload
    async def send_request(
        self, method: str, params: Optional[Dict[str, Any]] = None, id: Any = NOID
    ) -> Response: ...

    @overload
    async def send_request(
        self, method: str, params: Optional[Tuple[Any, ...]] = None, id: Any = NOID
    ) -> Response: ...

    @overload
    async def send_request(
        self, method: str, params: Optional[Any] = None, id: Any = NOID
    ) -> Response: ...

    async def send_request(
        self,
        method: str,
        params: Optional[Union[Dict[str, Any], Tuple[Any, ...], None]] = None,
        id: Any = NOID,
    ) -> Response:
        """Unified request sending interface"""
        transport = await self._get_transport()
        try:
            await transport.connect()
            request_body = request(method, params, id=id)
            return await transport.send_message(request_body)
        finally:
            transport.close()

    def _get_transport_sync(self) -> ClientTransport:
        """Get transport instance synchronously"""
        if self._transport:
            return self._transport
        return self._create_transport_sync()

    def _create_transport_sync(self) -> ClientTransport:
        """Synchronous transport factory method"""
        raise NotImplementedError


# ------------------------------
# Specific Implementation Class: Default RPC Client
# ------------------------------
class DefaultRpcClient(RpcClient):
    """Default request client exposed to the outside world (bridge mode concrete abstraction)"""

    def __init__(
        self,
        socket_path: str,
        transport: Optional[ClientTransport] = None,
    ):
        self._socket_path = socket_path
        super().__init__(transport)

    async def _create_transport(self) -> ClientTransport:
        """Default use of UNIX Socket transmission (can be modified to other default implementations)"""
        return UnixSocketTransport(socket_path=self._socket_path)


# ------------------------------
# Specific scenario client: GM requests client
# ------------------------------
class GmRpcClient(RpcClient):
    """GM tool specific request client (inherited from abstract class)"""

    def __init__(
        self,
        socket_path: str = DEFAULT_GA_SOCKET,
        transport: Optional[ClientTransport] = None,
    ):
        super().__init__(transport)
        self._socket_path = socket_path

    async def _create_transport(self) -> ClientTransport:
        """The GM scenario defaults to using the specified UNIX Socket"""
        return UnixSocketTransport(socket_path=self._socket_path)


# ------------------------------
# External calling interface object
# ------------------------------
class Request:
    """Unified request interface with sync/async support"""

    def __init__(
        self,
        socket_path: Optional[str] = None,
        adapter: Optional[RpcClient] = None,
        sync: bool = False,
    ):
        if sync:
            if not socket_path:
                socket_path = DEFAULT_GA_SOCKET
            self._adapter = SyncRpcClient(socket_path)
        else:
            # Default to async transport
            if socket_path:
                self._adapter = DefaultRpcClient(socket_path)
            else:
                self._adapter = adapter or GmRpcClient()

    def send_request(
        self,
        method: str,
        params: Optional[Union[Dict, Tuple, None]] = None,
        id: Any = NOID,
    ) -> Response:
        """Send request with automatic sync/async handling"""
        return self._adapter.send_request(method, params, id=id)


class SyncRpcClient(RpcClient):
    """Synchronous RPC Client"""

    def __init__(
        self,
        socket_path: str,
        transport: Optional[ClientTransport] = None,
    ):
        self._socket_path = socket_path
        super().__init__(transport)
        self._transport_instance: Optional[ClientTransport] = None

    def _create_transport(self) -> ClientTransport:
        return SyncUnixSocketTransport(socket_path=self._socket_path)

    def _get_transport(self) -> ClientTransport:
        """Get transport instance synchronously"""
        if self._transport:
            return self._transport
        if not self._transport_instance:
            self._transport_instance = self._create_transport()
        return self._transport_instance

    def send_request(
        self,
        method: str,
        params: Optional[Union[Dict[str, Any], Tuple[Any, ...], None]] = None,
        id: Any = NOID,
    ) -> Response:
        transport = self._get_transport()
        try:
            transport.connect()
            request_body = request(method, params, id=id)
            return transport.send_message(request_body)
        finally:
            transport.close()


class GmSyncRpcClient(SyncRpcClient):
    """Synchronous GM RPC Client"""

    def __init__(
        self,
        socket_path: str = DEFAULT_GA_SOCKET,
        transport: Optional[ClientTransport] = None,
    ):
        super().__init__(socket_path, transport)
