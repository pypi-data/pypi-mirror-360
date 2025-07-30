from __future__ import annotations

import asyncio
import csv
import random
import sys
from abc import ABC, abstractmethod
from asyncio import Queue, StreamReader, StreamWriter
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple, Type, Union

import arrow
from pydantic import ValidationError
from pydantic.dataclasses import dataclass

from kelvin.application.config import ConfigurationError
from kelvin.application.stream import KelvinStreamConfig
from kelvin.config.appyaml import (
    AppBridge,
    AppKelvin,
    AppYaml,
    AssetsEntry,
    Metric,
    ParameterDefinition,
)
from kelvin.config.common import AppTypes
from kelvin.config.exporter import ExporterConfig
from kelvin.config.external import ExternalConfig
from kelvin.config.importer import ImporterConfig
from kelvin.config.parser import AppConfigObj
from kelvin.config.smart_app import IOConfig, SmartAppConfig, SmartAppParams
from kelvin.krn import KRN, KRNAssetDataStream, KRNAssetParameter, KRNWorkloadAppVersion
from kelvin.message import (
    KMessageType,
    KMessageTypeControl,
    KMessageTypeData,
    KMessageTypeDataTag,
    KMessageTypeParameter,
    KMessageTypeRecommendation,
    Message,
)
from kelvin.message.base_messages import (
    ManifestDatastream,
    Resource,
    ResourceDatastream,
    RuntimeManifest,
    RuntimeManifestPayload,
)
from kelvin.message.msg_builders import MessageBuilder
from kelvin.message.msg_type import PrimitiveTypes


def flatten_dict(d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
    items: list = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, Dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parse_assets_csv(csv_file_path: str) -> List[AssetsEntry]:
    non_properties = ["Name ID", "Display Name", "Asset Type Name ID"]
    with open(csv_file_path) as f:
        csv_reader = csv.DictReader(f)
        return [
            AssetsEntry(
                name=row["Name ID"], properties={k.lower(): v for k, v in row.items() if k not in non_properties}
            )
            for row in csv_reader
        ]


def string_to_strict_type(value: Any, data_type: Type) -> Union[bool, float, str, dict]:
    if isinstance(value, data_type):
        return value
    if data_type is bool:
        return str(value).lower() in ["true", "1"]
    if data_type is float:
        return float(value)
    return value


def msg_type_param_dict(msg_type_on_config: str) -> Dict:
    """To parse different arguments of KMessageTypePrimitive if type is a object with icd"""
    if msg_type_on_config in PrimitiveTypes.__members__:
        return {"primitive": msg_type_on_config}
    return {"primitive": "object", "icd": msg_type_on_config}


class KelvinPublisherConfig(KelvinStreamConfig):
    model_config = {"env_prefix": "KELVIN_PUBLISHER_"}

    ip: str = "0.0.0.0"


class PublisherError(Exception):
    pass


class PublishServer:
    CYCLE_TIMEOUT_S = 0.25
    NODE = "test_node"
    WORKLOAD = "test_workload"

    app_config: AppConfigObj
    allowed_assets: Optional[List[AssetsEntry]] = None
    asset_params: Dict[Tuple[str, str], Union[bool, float, str]] = {}

    on_message: Callable[[Message], None]
    write_queue: Queue[Message]

    def __init__(self, conf: AppConfigObj, generator: DataGenerator, replay: bool = False) -> None:
        self.app_config = conf

        if (
            isinstance(self.app_config.config, AppYaml)
            and self.app_config.type == AppTypes.kelvin_app
            and self.app_config.config.app.kelvin is not None
        ):
            assets = self.app_config.config.app.kelvin.assets
            if assets:
                self.allowed_assets = assets
        elif (
            isinstance(self.app_config.config, AppYaml)
            and self.app_config.type == AppTypes.bridge
            and self.app_config.config.app.bridge is not None
        ):
            metrics_map = self.app_config.config.app.bridge.metrics_map
            if metrics_map:
                self.allowed_assets = [AssetsEntry(name=metric.asset_name) for metric in metrics_map]

        self.writer = None
        self.on_message = log_message
        self.write_queue = Queue()
        self.config = KelvinPublisherConfig()
        self.running = False
        self.generator = generator
        # replay re-runs generator if it returns
        self.replay = replay

    def update_param(self, asset: str, param: str, value: Union[bool, float, str]) -> None:
        """Sets an asset parameter.
        Empty asset ("") to change app default

        Args:
            asset (Optional[str]): asset name (empty ("") for fallback)
            param (str): param name
            value (Union[bool, float, str]): param value
        """
        value_lower = str(value).strip().lower()
        if value_lower in ["true", "false"]:
            value = value_lower == "true"
        elif value_lower.isnumeric():
            value = float(value)

        self.asset_params[(asset, param)] = value

    def add_extra_assets(self, assets_extra: List[AssetsEntry]) -> None:
        self.allowed_assets = assets_extra

    def bridge_app_yaml_to_runtime(self, bridge: AppBridge) -> RuntimeManifest:
        asset_metrics_map: Dict[str, Resource] = {}
        metric_datastream_map: Dict[str, ManifestDatastream] = {}
        for metric in bridge.metrics_map:
            resource = asset_metrics_map.setdefault(metric.asset_name, Resource(type="asset", name=metric.asset_name))

            resource.datastreams[metric.name] = ResourceDatastream(
                map_to=metric.name, access=metric.access, owned=True, configuration=metric.configuration
            )

            metric_datastream_map.setdefault(
                metric.name, ManifestDatastream(name=metric.name, primitive_type_name=metric.data_type)
            )

        resources = list(asset_metrics_map.values())
        datastreams = list(metric_datastream_map.values())

        return RuntimeManifest(
            resource=KRNWorkloadAppVersion(
                node=self.NODE,
                workload=self.WORKLOAD,
                app=self.app_config.name,
                version=self.app_config.version,
            ),
            payload=RuntimeManifestPayload(
                resources=resources, configuration=bridge.configuration, datastreams=datastreams
            ),
        )

    def kelvin_app_yaml_to_runtime(
        self, kelvin: AppKelvin, allowed_assets: List[AssetsEntry] | None
    ) -> RuntimeManifest:
        if allowed_assets is None:
            allowed_assets = kelvin.assets

        manif_ds_map: Dict[str, ManifestDatastream] = {}
        resource_ds_map: Dict[str, ResourceDatastream] = {}

        for input in kelvin.inputs:
            ds_name = input.name
            owned = input.control_change
            access = "WO" if owned else "RO"

            resource_ds_map[ds_name] = ResourceDatastream(map_to=ds_name, access=access, owned=owned)
            manif_ds_map[ds_name] = ManifestDatastream(name=ds_name, primitive_type_name=input.data_type)

        for output in kelvin.outputs:
            ds_name = output.name
            owned = not output.control_change
            access = "RO" if owned else "WO"

            resource_ds = resource_ds_map.setdefault(
                ds_name, ResourceDatastream(map_to=ds_name, access=access, owned=owned)
            )
            if resource_ds.access != access:
                resource_ds.access = "RW"

            manif_ds = manif_ds_map.setdefault(
                ds_name, ManifestDatastream(name=ds_name, primitive_type_name=output.data_type)
            )

            if manif_ds.primitive_type_name != output.data_type:
                raise ConfigurationError(f"data type mismatch for output {ds_name}")

        resources: List[Resource] = []
        for asset in allowed_assets:
            asset_params = {}
            for param in kelvin.parameters:
                payload = (
                    self.asset_params.get((asset.name, param.name))  # asset override
                    or self.asset_params.get(("", param.name))  # asset override default ("")
                    or next(  # asset parameter defined in configuration
                        (
                            asset.parameters.get(param.name, {}).get("value")
                            for asset in kelvin.assets
                            if asset.name == asset
                        ),
                        None,
                    )
                    or (param.default.get("value", None) if param.default else None)  # app defaults
                )

                if payload is None:
                    # asset has no parameter and parameter doesn't have default value
                    continue

                try:
                    if param.data_type == "number":
                        payload = float(payload)
                    elif param.data_type == "string":
                        payload = str(payload)
                    elif param.data_type == "boolean":
                        payload = str(payload).lower() in ["true", "1"]
                except ValueError:
                    continue

                asset_params[param.name] = payload

            resources.append(
                Resource(
                    type="asset",
                    name=asset.name,
                    parameters=asset_params,
                    properties=asset.properties,
                    datastreams=resource_ds_map,
                )
            )

        return RuntimeManifest(
            resource=KRNWorkloadAppVersion(
                node=self.NODE,
                workload=self.WORKLOAD,
                app=self.app_config.name,
                version=self.app_config.version,
            ),
            payload=RuntimeManifestPayload(
                resources=resources, configuration=kelvin.configuration, datastreams=list(manif_ds_map.values())
            ),
        )

    def smart_app_yaml_to_runtime(
        self, smart_app: SmartAppConfig, allowed_assets: List[AssetsEntry] | None
    ) -> RuntimeManifest:
        if allowed_assets is None:
            raise ConfigurationError("allowed_assets must be set for smart apps")

        manif_ds_map: Dict[str, ManifestDatastream] = {}
        resource_ds_map: Dict[str, ResourceDatastream] = {}
        resources: List[Resource] = []

        # control changes

        for input in smart_app.control_changes.inputs:
            ds_name = input.name
            owned = True
            access = "WO"
            resource_ds_map[ds_name] = ResourceDatastream(map_to=ds_name, access=access, owned=owned)
            manif_ds_map[ds_name] = ManifestDatastream(name=ds_name, primitive_type_name=input.data_type)

        for output in smart_app.control_changes.outputs:
            ds_name = output.name
            owned = False
            access = "WO"

            resource_ds = resource_ds_map.setdefault(
                ds_name, ResourceDatastream(map_to=ds_name, access=access, owned=owned)
            )
            if resource_ds.access != access:
                resource_ds.access = "RW"

            manif_ds = manif_ds_map.setdefault(
                ds_name, ManifestDatastream(name=ds_name, primitive_type_name=output.data_type)
            )

            if manif_ds.primitive_type_name != output.data_type:
                raise ConfigurationError(f"data type mismatch for control change {ds_name}")

        # data streams

        for input in smart_app.data_streams.inputs:
            ds_name = input.name
            owned = False
            access = "RO"

            resource_ds = resource_ds_map.setdefault(
                ds_name, ResourceDatastream(map_to=ds_name, access=access, owned=owned)
            )
            if resource_ds.access != access:
                resource_ds.access = "RW"

            manif_ds = manif_ds_map.setdefault(
                ds_name, ManifestDatastream(name=ds_name, primitive_type_name=input.data_type)
            )

            if manif_ds.primitive_type_name != input.data_type:
                raise ConfigurationError(f"data type mismatch for datastream {ds_name}")

        for output in smart_app.data_streams.outputs:
            ds_name = output.name
            owned = True
            access = "RO"

            resource_ds = resource_ds_map.setdefault(
                ds_name, ResourceDatastream(map_to=ds_name, access=access, owned=owned)
            )
            if resource_ds.access != access:
                resource_ds.access = "RW"

            manif_ds = manif_ds_map.setdefault(
                ds_name, ManifestDatastream(name=ds_name, primitive_type_name=output.data_type)
            )

            if manif_ds.primitive_type_name != output.data_type:
                raise ConfigurationError(f"data type mismatch for datastream {ds_name}")

        # assets

        for asset in allowed_assets:
            asset_params = {}
            for param in smart_app.parameters:
                payload = (
                    self.asset_params.get((asset.name, param.name))  # asset override
                    or self.asset_params.get(("", param.name))  # asset override default ("")
                    or smart_app.defaults.parameters.get(param.name, None)
                )
                if payload is None:
                    continue
                asset_params[param.name] = payload

            resources.append(
                Resource(
                    type="asset",
                    name=asset.name,
                    properties=asset.properties,
                    parameters=asset_params,
                    datastreams=resource_ds_map,
                )
            )

        return RuntimeManifest(
            resource=KRNWorkloadAppVersion(
                node=self.NODE,
                workload=self.WORKLOAD,
                app=self.app_config.name,
                version=self.app_config.version,
            ),
            payload=RuntimeManifestPayload(
                resources=resources,
                configuration=smart_app.defaults.configuration,
                datastreams=list(manif_ds_map.values()),
            ),
        )

    def build_config_message(self) -> RuntimeManifest:
        if (
            isinstance(self.app_config.config, AppYaml)
            and self.app_config.type == AppTypes.bridge
            and self.app_config.config.app.bridge is not None
        ):
            return self.bridge_app_yaml_to_runtime(self.app_config.config.app.bridge)
        elif (
            isinstance(self.app_config.config, AppYaml)
            and self.app_config.type == AppTypes.kelvin_app
            and self.app_config.config.app.kelvin is not None
        ):
            return self.kelvin_app_yaml_to_runtime(self.app_config.config.app.kelvin, self.allowed_assets)
        elif isinstance(self.app_config.config, SmartAppConfig):
            return self.smart_app_yaml_to_runtime(self.app_config.config, self.allowed_assets)
        else:
            raise ConfigurationError(f"invalid app type: {self.app_config.type}")

    async def start_server(self) -> None:
        server = await asyncio.start_server(self.new_client, self.config.ip, self.config.port, limit=self.config.limit)
        print(f"Publisher started. Listening on {self.config.ip}:{self.config.port}")

        async with server:
            await server.serve_forever()

    async def new_client(self, reader: StreamReader, writer: StreamWriter) -> None:
        if self.running is True:
            writer.close()
            return

        print("Connected")
        self.running = True

        connection_tasks = {
            asyncio.create_task(self.handle_read(reader)),
            asyncio.create_task(self.handle_write(writer, self.write_queue)),
        }

        gen_task = asyncio.create_task(self.handle_generator(self.generator))
        try:
            config_msg = self.build_config_message()
            writer.write(config_msg.encode() + b"\n")
        except ConfigurationError as e:
            print("Configuration error:", e)
            writer.close()
            self.running = False

        try:
            await writer.drain()
        except ConnectionResetError:
            pass

        _, pending = await asyncio.wait(connection_tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()

        if not gen_task.done():
            gen_task.cancel()

        self.running = False
        print("Disconnected")

    async def handle_read(self, reader: StreamReader) -> None:
        while self.running:
            data = await reader.readline()
            if not len(data):
                break
            try:
                msg = Message.model_validate_json(data)
                self.on_message(msg)
            except Exception as e:
                print("error parsing message", e)

    async def handle_write(self, writer: StreamWriter, queue: Queue[Message]) -> None:
        while self.running and not writer.is_closing():
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=self.CYCLE_TIMEOUT_S)
            except asyncio.TimeoutError:
                continue

            writer.write(msg.encode() + b"\n")

            try:
                await writer.drain()
            except ConnectionResetError:
                pass

    async def handle_generator(self, generator: DataGenerator) -> None:
        first_run = True
        while first_run or self.replay:
            first_run = False
            async for data in generator.run():
                if isinstance(data, MessageData):
                    await self.publish_data(data)
                elif isinstance(data, Message):
                    await self.publish_unsafe(data)
                elif isinstance(data, MessageBuilder):
                    await self.publish_unsafe(data.to_message())

    async def publish_unsafe(self, msg: Message) -> None:
        """Publish the message as is, do not validate it against the app configuration

        Args:
            msg (Message): message to publish
        """
        await self.write_queue.put(msg)

    async def publish_data(self, data: MessageData) -> bool:
        allowed_asset_names = []
        if self.allowed_assets is not None:
            allowed_asset_names = [asset.name for asset in self.allowed_assets]
            if data.resource.asset and data.resource.asset not in allowed_asset_names:
                print(f"error publishing: asset not allowed to app. asset={data.resource.asset}")
                return False

        # if data.asset is empty publish to all allowed_assets (if set)
        assets = [data.resource.asset] if data.resource.asset else allowed_asset_names
        if assets is None:
            print("error publishing to empty asset: no allowed assets set")
            return False

        msg_type: KMessageType
        app_resource: Union[Metric, ParameterDefinition, IOConfig, SmartAppParams, None] = None
        msg_resource_builder: Optional[type[KRN]] = None
        if (
            isinstance(self.app_config.config, AppYaml)
            and self.app_config.type == AppTypes.kelvin_app
            and self.app_config.config.app.kelvin is not None
        ):
            try:
                # check is app input
                app_resource = next(
                    i for i in self.app_config.config.app.kelvin.inputs if i.name == data.resource.data_stream
                )
                msg_type = KMessageTypeData(**msg_type_param_dict(app_resource.data_type))
                msg_resource_builder = KRNAssetDataStream
            except StopIteration:
                try:
                    # check is app param
                    app_resource = next(
                        p for p in self.app_config.config.app.kelvin.parameters if p.name == data.resource.data_stream
                    )
                    msg_type = KMessageTypeParameter(**msg_type_param_dict(app_resource.data_type))
                    msg_resource_builder = KRNAssetParameter
                except StopIteration:
                    app_resource = None
        elif (
            isinstance(self.app_config.config, AppYaml)
            and self.app_config.type == AppTypes.bridge
            and self.app_config.config.app.bridge is not None
        ):
            try:
                app_resource = next(
                    Metric(name=m.name, data_type=m.data_type)
                    for m in self.app_config.config.app.bridge.metrics_map
                    if m.name == data.resource.data_stream
                )
                msg_type = KMessageTypeData(**msg_type_param_dict(app_resource.data_type))
                msg_resource_builder = KRNAssetDataStream
            except StopIteration:
                app_resource = None
        elif isinstance(self.app_config.config, SmartAppConfig):
            try:
                app_resource = next(
                    i for i in self.app_config.config.data_streams.inputs if i.name == data.resource.data_stream
                )
                msg_type = KMessageTypeData(**msg_type_param_dict(app_resource.data_type))
                msg_resource_builder = KRNAssetDataStream
            except StopIteration:
                try:
                    app_resource = next(
                        i for i in self.app_config.config.control_changes.inputs if i.name == data.resource.data_stream
                    )
                    msg_type = KMessageTypeData(**msg_type_param_dict(app_resource.data_type))
                    msg_resource_builder = KRNAssetDataStream
                except StopIteration:
                    try:
                        app_resource = next(
                            i for i in self.app_config.config.parameters if i.name == data.resource.data_stream
                        )
                        msg_type = KMessageTypeParameter(**msg_type_param_dict(app_resource.data_type))
                        msg_resource_builder = KRNAssetParameter
                    except StopIteration:
                        app_resource = None

        if app_resource is None or msg_resource_builder is None:
            # invalid resource for this app
            print(f"error publishing: invalid resource to app. resource={data.resource!s}")
            return False

        for asset in assets:
            try:
                msg = Message(
                    type=msg_type,
                    timestamp=data.timestamp or datetime.now().astimezone(),
                    resource=msg_resource_builder(asset, data.resource.data_stream),
                )
                msg.payload = string_to_strict_type(data.value, type(msg.payload))

                await self.write_queue.put(msg)
            except (ValidationError, ValueError) as e:
                print(
                    (
                        "error publishing value: invalid value for resource."
                        f" resource={data.resource!s}, value={data.value}"
                    ),
                    e,
                )
        return True


def log_message(msg: Message) -> None:
    msg_log = ""
    if isinstance(msg.type, KMessageTypeData):
        msg_log = "Data "
    elif isinstance(msg.type, KMessageTypeControl):
        msg_log = "Control Change "
    elif isinstance(msg.type, KMessageTypeRecommendation):
        msg_log = "Recommendation "
    elif isinstance(msg.type, KMessageTypeDataTag):
        msg_log = "Data Tag "

    print(f"\nReceived {msg_log}Message:\n", repr(msg))


@dataclass
class MessageData:
    resource: KRNAssetDataStream
    timestamp: Optional[datetime]
    value: Any


@dataclass
class AppIO:
    name: str
    data_type: str
    asset: str


class DataGenerator(ABC):
    @abstractmethod
    async def run(self) -> AsyncGenerator[Union[MessageData, Message, MessageBuilder], None]:
        if False:
            yield  # trick for mypy


class CSVPublisher(DataGenerator):
    CSV_ASSET_KEY = "asset_name"

    def __init__(
        self,
        csv_file_path: str,
        publish_interval: Optional[float] = None,
        playback: bool = False,
        ignore_timestamps: bool = False,
        now_offset: bool = False,
    ):
        csv.field_size_limit(sys.maxsize)
        self.csv_file_path = csv_file_path
        self.publish_rate = publish_interval
        self.playback = playback
        self.ignore_timestamps = ignore_timestamps
        self.now_offset = now_offset

        csv_file = open(self.csv_file_path)
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)

        self.csv_has_timestamp = "timestamp" in headers
        self.use_csv_timestamps = self.csv_has_timestamp and not self.ignore_timestamps

        if self.playback and not self.use_csv_timestamps:
            raise PublisherError("csv must have timestamp column to use csv timestamps")

    def parse_timestamp(self, ts_str: str, offset: timedelta = timedelta(0)) -> Optional[datetime]:
        try:
            timestamp = float(ts_str)
            return arrow.get(timestamp).datetime + offset
        except ValueError:
            pass

        try:
            return arrow.get(ts_str).datetime + offset
        except Exception as e:
            print(f"csv: error parsing timestamp. timestamp={ts_str}", e)
            return None

    async def run(self) -> AsyncGenerator[MessageData, None]:
        csv_file = open(self.csv_file_path)
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        last_timestamp = datetime.max

        ts_offset = timedelta(0)
        row = next(csv_reader)
        row_dict = dict(zip(headers, row))
        timestamp = datetime.now()
        row_ts_str = row_dict.pop("timestamp", "")

        if self.use_csv_timestamps:
            row_ts = self.parse_timestamp(row_ts_str)
            if row_ts is None:
                raise PublisherError(f"csv: invalid timestamp in first row. timestamp={row_ts_str}")

            if self.now_offset:
                ts_offset = timestamp.astimezone() - row_ts.astimezone()

            timestamp = row_ts + ts_offset

        asset = row_dict.pop(self.CSV_ASSET_KEY, "")
        for r, v in row_dict.items():
            if not v:
                continue
            yield MessageData(resource=KRNAssetDataStream(asset, r), value=v, timestamp=timestamp)
        last_timestamp = timestamp
        if self.publish_rate:
            await asyncio.sleep(self.publish_rate)

        for row in csv_reader:
            row_dict = dict(zip(headers, row))
            asset = row_dict.pop(self.CSV_ASSET_KEY, "")

            row_ts_str = row_dict.pop("timestamp", "")
            parsed_ts = self.parse_timestamp(row_ts_str, ts_offset) if self.use_csv_timestamps else datetime.now()
            if parsed_ts is None:
                print("csv: skipping row", row_dict)
                continue
            timestamp = parsed_ts

            if self.playback:
                # wait time between rows
                wait_time = max((timestamp.astimezone() - last_timestamp.astimezone()).total_seconds(), 0)
                last_timestamp = timestamp
                await asyncio.sleep(wait_time)

            for r, v in row_dict.items():
                if not v:
                    continue
                yield MessageData(resource=KRNAssetDataStream(asset, r), value=v, timestamp=timestamp)

            if self.publish_rate:
                await asyncio.sleep(self.publish_rate)

        if self.playback and wait_time > 0:
            # wait same time as last row, before replay
            await asyncio.sleep(wait_time)

        print("\nCSV ingestion is complete")


class Simulator(DataGenerator):
    app_yaml: str
    app_config: ExporterConfig | ImporterConfig | SmartAppConfig | ExternalConfig | AppYaml
    rand_min: float
    rand_max: float
    random: bool
    current_value: float
    assets: List[AssetsEntry]
    params_override: Dict[str, Union[bool, float, str]]

    def __init__(
        self,
        app_config: ExporterConfig | ImporterConfig | SmartAppConfig | ExternalConfig | AppYaml,
        period: float,
        rand_min: float = 0,
        rand_max: float = 100,
        random: bool = True,
        assets_extra: List[AssetsEntry] = [],
        parameters_override: List[str] = [],
    ):
        self.app_config = app_config
        self.period = period
        self.rand_min = rand_min
        self.rand_max = rand_max
        self.random = random
        self.current_value = self.rand_min - 1
        self.params_override: Dict[str, Union[bool, float, str]] = {}

        for override in parameters_override:
            param, value = override.split("=", 1)
            self.params_override[param] = value

        if len(assets_extra) > 0:
            self.assets = assets_extra

    def generate_random_value(self, data_type: str) -> Union[bool, float, str, dict]:
        if data_type == "boolean":
            return random.choice([True, False])

        if self.random:
            number = round(random.random() * (self.rand_max - self.rand_min) + self.rand_min, 2)
        else:
            if self.current_value >= self.rand_max:
                self.current_value = self.rand_min
            else:
                self.current_value += 1
            number = self.current_value

        if data_type == "number":
            return number

        if data_type == "string":
            return f"str_{number}"

        # object or other icd
        return {"key": number}

    async def run(self) -> AsyncGenerator[MessageData, None]:
        app_inputs: List[AppIO] = []
        if (
            isinstance(self.app_config, AppYaml)
            and self.app_config.app.type == AppTypes.kelvin_app
            and self.app_config.app.kelvin is not None
        ):
            for asset in self.assets:
                for app_input in self.app_config.app.kelvin.inputs:
                    app_inputs.append(AppIO(name=app_input.name, data_type=app_input.data_type, asset=asset.name))

        elif (
            isinstance(self.app_config, AppYaml)
            and self.app_config.app.type == AppTypes.bridge
            and self.app_config.app.bridge is not None
        ):
            app_inputs = [
                AppIO(name=metric.name, data_type=metric.data_type, asset=metric.asset_name)
                for metric in self.app_config.app.bridge.metrics_map
                if metric.access == "RW"
            ]

        elif isinstance(self.app_config, SmartAppConfig):
            for asset in self.assets:
                for inpt in self.app_config.data_streams.inputs:
                    app_inputs.append(AppIO(name=inpt.name, data_type=inpt.data_type, asset=asset.name))

                for cc in self.app_config.control_changes.inputs:
                    app_inputs.append(AppIO(name=cc.name, data_type=cc.data_type, asset=asset.name))

        else:
            raise ConfigurationError("invalid app type")

        while True:
            for i in app_inputs:
                yield MessageData(
                    resource=KRNAssetDataStream(i.asset, i.name),
                    value=self.generate_random_value(i.data_type),
                    timestamp=None,
                )

            await asyncio.sleep(self.period)
