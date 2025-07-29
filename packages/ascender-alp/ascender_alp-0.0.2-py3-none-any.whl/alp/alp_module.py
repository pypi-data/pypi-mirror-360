from alp.provider import provideALP
from alp.receiver_service import ReceiverService
from ascender.core import AscModule


class AlpModule:
    @classmethod
    def forRoot(cls, path: str = "/alp"):
        return AscModule(
            imports=[],
            declarations=[],
            providers=[
                provideALP(path),
            ],
            exports=[
                ReceiverService,
                "ALP_SERVER",
            ]
        )(cls)