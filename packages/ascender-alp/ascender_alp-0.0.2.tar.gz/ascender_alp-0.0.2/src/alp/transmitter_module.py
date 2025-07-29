from alp.transmitter_service import Transmitter
from ascender.core import AscModule


@AscModule(
    imports=[
    ],
    declarations=[
    ],
    providers=[
        {
            "provide": "SIO_NAMESPACE",
            "value": "/"
        },
        Transmitter,
    ],
    exports=[
        Transmitter
    ]
)
class TransmitterModule:
    @classmethod
    def with_namespace(cls, namespace: str):
        return AscModule(
            imports=[],
            declarations=[],
            providers=[
                {
                    "provide": "SIO_NAMESPACE",
                    "value": namespace
                },
                Transmitter,
            ],
            exports=[
                Transmitter
            ],
        )(cls)