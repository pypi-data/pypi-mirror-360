import inspect
import traceback
from typing import Annotated, Any, Awaitable, Callable
from ascender.common import Injectable
from ascender.core import Service, Inject
from pydantic import ValidationError, BaseModel
from socketio import AsyncServer

from alp.interfaces.error import ALPError

from .utils import parser as alp_parser


@Injectable(provided_in="any")
class ReceiverService(Service):
    def __init__(self, alp_server: Annotated[AsyncServer, Inject("ALP_SERVER")]):
        self.alp_server = alp_server
    
    def add_event_handler(self, event: str, handler: Callable[..., Awaitable[Any]], namespace: str = "/"):
        """
        Made for `@Receiver` decorator to add event handlers to the ALP server.
        Though can be manually called by injecting this service and calling this method.
        """
        self.alp_server.on(event, self.event_callback(event, handler), namespace)
    
    def event_callback(
        self, event: str, callback: Callable[..., Awaitable[Any]] | None = None
    ) -> Callable[..., Awaitable[Any]]:
        """
        Wraps the given callback in a try/except block.
        It parses the data based on the callback’s signature and, if an error occurs,
        returns an ALPError to the client.
        """
        async def wrapper(sio: str, *args, **kwargs) -> Any:
            try:
                sig = inspect.signature(callback) # type: ignore
                params = list(sig.parameters.values())

                if len(params) == 1:
                    # Only the sio parameter is expected.
                    result = await callback(sio) if inspect.iscoroutinefunction(callback) else callback(sio) # type: ignore
                elif len(params) == 2:
                    # The second parameter commonly `data` is expected.
                    if not args:
                        raise ValueError("Missing data argument for event '{}'".format(event))
                    data_type = params[1].annotation
                    # Assume alp_parser is available in the scope.
                    data = alp_parser.parse(data_type, args[0])
                    result = (
                        await callback(sio, data)
                        if inspect.iscoroutinefunction(callback)
                        else callback(sio, data) # type: ignore
                    )
                else:
                    raise ValueError("Callback for event '{}' must accept 1 or 2 parameters.".format(event))
                
                if isinstance(result, BaseModel):
                    return result.model_dump(mode="json")
                
                return result
            except ValidationError as e:
                traceback.print_exc()
                return ALPError(code=422, details=str(e)).model_dump(mode="json")
            
            except Exception as e:
                if event in ["connect", "disconnect"]:
                    raise e
                
                traceback.print_exc()
                return ALPError(code=500, details=str(e)).model_dump(mode="json")

        return wrapper