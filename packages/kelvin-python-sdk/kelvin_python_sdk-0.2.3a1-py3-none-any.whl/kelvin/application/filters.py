from __future__ import annotations

from typing import Callable, List, Union

from typing_extensions import TypeAlias

from kelvin.krn import KRN, KRNAssetDataStream
from kelvin.message import ControlChangeStatus, KMessageTypeData, Message
from kelvin.message.base_messages import CustomActionMsg

KelvinFilterType: TypeAlias = Callable[[Message], bool]


def is_asset_data_message(msg: Message) -> bool:
    return isinstance(msg.resource, KRNAssetDataStream) and isinstance(msg.type, KMessageTypeData)


def is_data_message(msg: Message) -> bool:
    return isinstance(msg.type, KMessageTypeData)


def is_control_status_message(msg: Message) -> bool:
    return isinstance(msg, ControlChangeStatus)


def resource_equals(resource: Union[KRN, List[KRN]]) -> KelvinFilterType:
    def _check(msg: Message) -> bool:

        if not isinstance(msg.resource, KRN):
            return False

        if isinstance(resource, list):
            return msg.resource in resource

        return msg.resource == resource

    return _check


def input_equals(data: Union[str, List[str]]) -> KelvinFilterType:
    def _check(msg: Message) -> bool:

        if not isinstance(msg.resource, KRNAssetDataStream):
            return False

        if isinstance(data, list):
            return msg.resource.data_stream in data

        return msg.resource.data_stream == data

    return _check


def asset_equals(asset: Union[str, List[str]]) -> KelvinFilterType:
    def _check(msg: Message) -> bool:

        if not isinstance(msg.resource, KRNAssetDataStream):
            return False

        if isinstance(asset, list):
            return msg.resource.asset in asset

        return msg.resource.asset == asset

    return _check


def is_custom_action(msg: Message) -> bool:
    return isinstance(msg, CustomActionMsg)
