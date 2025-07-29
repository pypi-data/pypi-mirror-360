from ascender.common import BaseDTO, BaseResponse

from typing import Any, NotRequired, TypedDict


class TransmittionData(TypedDict):
    data: NotRequired[dict[str, Any] | BaseDTO | BaseResponse]
    """
    The data to send. This can be any JSON serializable data.
    Including Ascender Framework's DTOs and Responses.
    """
    room: NotRequired[str]
    """
    The recipient of the message. This can be set to the
    session ID of a client to address only that client, to any
    any custom room created by the application to address all
    the clients in that room, or to a list of custom room names. 
    If this argument is omitted the event is broadcasted
    to all connected clients.
    """
    skip_sid: NotRequired[str]
    """
    The session ID of a client to skip when broadcasting to a room or to all clients. This can be used to prevent a message from being sent to the sender.
    """
    namespace: NotRequired[str]
    """
    The Socket.IO namespace for the event. If this argument is omitted the event is emitted to the default namespace
    """
    ignore_queue: NotRequired[bool]
    """
    If queue is enabled, this will ignore the queue and send the message immediately
    """