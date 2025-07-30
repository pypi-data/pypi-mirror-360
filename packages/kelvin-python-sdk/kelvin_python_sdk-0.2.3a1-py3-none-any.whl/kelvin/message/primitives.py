from __future__ import annotations

from typing import Union

from pydantic import StrictBool, StrictFloat, StrictInt, StrictStr

from kelvin.krn import KRNAssetDataStream
from kelvin.message.message import Message
from kelvin.message.msg_type import KMessageTypeData, KMessageTypeParameter


class AssetDataMessage(Message):
    resource: KRNAssetDataStream


class Number(AssetDataMessage):
    TYPE_ = KMessageTypeData("number")

    payload: Union[StrictFloat, StrictInt] = 0.0


class String(AssetDataMessage):
    TYPE_ = KMessageTypeData("string")

    payload: StrictStr = ""


class Boolean(AssetDataMessage):
    TYPE_ = KMessageTypeData("boolean")

    payload: StrictBool = False


class NumberParameter(Message):
    TYPE_ = KMessageTypeParameter("number")

    payload: Union[StrictFloat, StrictInt] = 0.0


class StringParameter(Message):
    TYPE_ = KMessageTypeParameter("string")

    payload: StrictStr = ""


class BooleanParameter(Message):
    TYPE_ = KMessageTypeParameter("boolean")

    payload: StrictBool = False
