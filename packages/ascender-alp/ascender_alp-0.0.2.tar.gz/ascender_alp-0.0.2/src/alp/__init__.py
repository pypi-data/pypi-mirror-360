"""
ALP - Stands for Ascender LiveAPI Protocol (built over SocketIO), earlier it was a protocol that is used to communicate with AgentHub's API.
This module is responsible for adapting SocketIO to work with Ascender Framework.
"""

from alp.interfaces.error import ALPError
from alp.interfaces.transmittion import TransmittionData
from alp.receiver import ALPReceiver
from alp.receiver_service import ReceiverService
from alp.transmitter_module import TransmitterModule
from alp.transmitter_service import Transmitter
from .provider import provideALP
from .alp_module import AlpModule

__all__ = [
    "provideALP",
    "AlpModule",
    "ALPReceiver",
    "ALPError",
    "Transmitter",
    "TransmittionData",
    "TransmitterModule",
    "ReceiverService"
]
