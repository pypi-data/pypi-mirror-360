from ascender.core.applications.application import Application
from ascender.core import Provider

from socketio import AsyncServer, Manager, ASGIApp

from alp.receiver_service import ReceiverService


def provideALP(
    path: str = "/alp",
    client_manager: Manager | None = None, 
) -> list[Provider]:
    def client_factory(application: Application):
        server = AsyncServer(client_manager=client_manager, async_mode="asgi", cors_allowed_origins="*")
        asgi = ASGIApp(server, socketio_path=None)
        application.app.mount(path, asgi, name="ALP")
        return server
    
    return [{
        "provide": "ALP_SERVER",
        "use_factory": client_factory,
        "deps": [Application]
    }, ReceiverService]