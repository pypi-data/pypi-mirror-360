import asyncio
from uuid import uuid4
from ascender.common import Injectable, BaseDTO, BaseResponse
from ascender.core import Inject

from typing import Annotated, Any, Mapping, MutableMapping, TypeVar, Unpack, cast

from socketio import AsyncServer

from reactivex import Subject, operators as ops, Observable, of
from reactivex.scheduler.eventloop import AsyncIOScheduler

from alp.interfaces.transmittion import TransmittionData
from alp.utils import validation as alp_validator


T = TypeVar("T")


@Injectable(provided_in=None)
class Transmitter:
    def __init__(self, alp_server: Annotated[AsyncServer, Inject("ALP_SERVER")], namespace: Annotated[str, Inject("SIO_NAMESPACE")]):
        self.alp_server = alp_server
        self.namespace = namespace
        # self.response_subject = Subject[Mapping[str, Any]]()

    async def get_session(self, sid: str, namespace: str | None = None) -> MutableMapping[str, Any]:
        """
        Get session data from ALP communication channel.

        Args:
            sid (str): Session ID to get data from.
            namespace (str): Namespace to get session data from. Defaults to default namespace '/'

        Returns:
            MutableMapping[str, Any]: A mapping containing session data.
        """
        return await self.alp_server.get_session(sid, namespace=namespace or self.namespace)
    
    async def set_session(self, sid: str, data: Mapping[str, Any], namespace: str | None = None) -> None:
        """
        Update session data in ALP communication channel.

        Args:
            sid (str): SocketIO Unique ID of connection to update session data of.
            data (Mapping[str, Any]): Data to update session with. (Typically a modified session dict)
            namespace (str, optional): SocketIO namespace where these actions will be omitted and happened. Defaults to "/".
        """
        await self.alp_server.save_session(sid, data, namespace=namespace or self.namespace)
    
    def get_environ(self, sid: str, namespace: str | None = None) -> MutableMapping[str, Any]:
        return cast(MutableMapping[str, Any], self.alp_server.get_environ(sid, namespace=namespace or self.namespace))

    async def emit(self, event: str, **data: Unpack[TransmittionData]) -> None:
        """
        Emit data to ALP communication channel.

        WARN: Acknowledgement is not supported in this method.
        """
        if isinstance(data.get("data", None), (BaseDTO, BaseResponse)):
            data["data"] = data["data"].model_dump(mode="json") # type: ignore
        
        data["namespace"] = data.get("namespace", self.namespace)
        
        await self.alp_server.emit(event, **data)
    
    async def send(
        self, 
        event: str,
        data: dict | BaseDTO | BaseResponse,
        namespace: str | None = None,
        to: str | None = None,
        expected_response: type[T] | Any = Any,
    ) -> Observable[T | Any | None]:
        """
        Send data to ALP communication channel and acknowledge response.

        Args:
            event (str): Event name to emit.
            data (dict | BaseDTO | BaseResponse): Data to emit. (Validation included)
            namespace (str | None, optional): A SocketIO namespace where to emit . Defaults to None.
            to (str | None, optional): Receiver ID or room name. Defaults to None.
            expected_response (type[T] | Any, optional): Response to which response will be serialized. Defaults to Any.

        Returns:
            Observable[T | Any | None]: An RxPy Observable of callback response.
        """
        scheduler = AsyncIOScheduler(asyncio.get_running_loop())

        if isinstance(data, (BaseDTO, BaseResponse)):
            data = data.model_dump(mode="json")

        response_subject = Subject[T | None]()

        await self.alp_server.emit(
            event, data, 
            to=to, 
            namespace=namespace or self.namespace, 
            callback=lambda res: response_subject.on_next(alp_validator.isvalid(expected_response, res) if res else None) # type: ignore
        )
        return response_subject.pipe(
            ops.subscribe_on(scheduler),
            ops.take(1)
        )
    
    async def broadcast(self, data: dict | BaseDTO | BaseResponse, namespace: str | None = None) -> None:
        """
        Broadcast data to all connected clients.

        WARN: Acknowledgement is not supported in this method.
        """
        await self.emit(event="broadcast", data=data, namespace=namespace or self.namespace)

    async def disconnect(self, sid: str, namespace: str | None = None) -> None:
        """
        Disconnect a client from the ALP communication channel.

        Args:
            sid (str): SocketIO Unique ID of SIO connection to disconnect.
            namespace (str, optional): SocketIO namespace where these actions will be omitted and happened. Defaults to "/".
        """
        await self.alp_server.disconnect(sid, namespace=namespace or self.namespace)
    
    async def enter_room(self, sid: str, room: str, namespace: str | None = None) -> None:
        """
        Join a room in the ALP communication channel.

        Args:
            sid (str): SocketIO Unique ID of SIO connection to join room.
            room (str): Room name to join.
            namespace (str, optional): SocketIO namespace where these actions will be omitted and happened. Defaults to "/".
        """
        await self.alp_server.enter_room(sid, room, namespace=namespace or self.namespace)
    
    async def leave_room(self, sid: str, room: str, namespace: str | None = None) -> None:
        """
        Leave a room in the ALP communication channel.

        Args:
            sid (str): SocketIO Unique ID of SIO connection to leave room.
            room (str): Room name to leave.
            namespace (str, optional): SocketIO namespace where these actions will be omitted and happened. Defaults to "/".
        """
        await self.alp_server.leave_room(sid, room, namespace=namespace or self.namespace)