from ascender.core import ControllerDecoratorHook, inject
from ascender.core.di.none_injector import NoneInjectorException

from alp.receiver_service import ReceiverService


class ALPReceiver(ControllerDecoratorHook):
    def __init__(self, event: str, namespace: str = "/"):
        super().__init__()
        self.event = event
        self.namespace = namespace

    def on_load(self, callable):
        try:
            receiver_service = inject(ReceiverService)
        except NoneInjectorException:
            raise RuntimeError("ALP module is not provided in application!")

        receiver_service.add_event_handler(self.event, callable, self.namespace)
