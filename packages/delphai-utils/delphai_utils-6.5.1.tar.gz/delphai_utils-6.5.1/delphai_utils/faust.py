import asyncio
import functools
import logging

from abc import abstractmethod, abstractproperty
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Pattern, Type, TypeVar, Union

import faust

from betterproto import Message
from confluent_kafka.admin import AdminClient, NewTopic
from dacite import from_dict
from dataclasses_avroschema import AvroModel
from faust.models import Model
from faust.serializers import Codec
from faust.streams import Stream
from faust.types.serializers import CodecArg, SchemaT
from faust.types.models import ModelT, ModelArg
from faust.types.topics import Seconds, TopicT
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers.faust import FaustSerializer

from delphai_utils.config import get_config
from delphai_utils.patches import aiokafka_patch, mode_traceback_patch

logger = logging.getLogger(__name__)

mode_traceback_patch()
aiokafka_patch()


@dataclass
class Step:
    name: str
    partitions: int
    output: Optional[str]
    tables: Optional[List[str]] = field(default_factory=lambda: [])


T = TypeVar("T")


class FaustProtobufSerializer(Codec):
    def __init__(self, type_class: T, **kwargs):
        self.type_class = type_class
        super(FaustProtobufSerializer, self).__init__(type_class=type_class, **kwargs)

    def _loads(self, s: bytes) -> T:
        return self.type_class().from_json(s.decode("utf-8"))

    def _dumps(self, s: Message) -> bytes:
        return s.to_json().encode("utf-8")


class FaustAgent:
    step: str
    step_config: Step
    agent_id: str
    input_topic: faust.TopicT
    output_topic: faust.TopicT
    input_value_type: Type[ModelT]
    output_value_type: Type[ModelT]
    input_value_serializer: CodecArg
    output_value_serializer: CodecArg
    agent: faust.Agent

    @abstractproperty
    def step(self) -> str:
        pass

    @abstractproperty
    def input_value_type(self) -> Type[ModelT]:
        pass

    @abstractproperty
    def output_value_type(self) -> Type[ModelT]:
        pass

    @abstractproperty
    def input_value_serializer(self) -> CodecArg:
        pass

    @abstractproperty
    def output_value_serializer(self) -> CodecArg:
        pass

    @abstractmethod
    async def process(self, requests: Stream[Type[ModelT]]):
        pass

    async def on_start(self):
        logger.info(f"started agent {self.agent_id}")

    async def after_attach(self):
        pass


class FaustApp:
    app: faust.App
    worker: faust.Worker
    faust_config: Dict
    pipeline_name: str

    async def on_startup_finished(self):
        logger.info(f"started app {self.app._conf.id}")

    async def on_start(self):
        logger.info(f"starting app {self.app._conf.id}")

    async def on_shutdown(self):
        logger.info(f"shutting down {self.app._conf.id}")

    def __init__(
        self,
        pipeline_name: str,
        broker: str,
        step: Optional[str] = None,
        schema_registry_url: Optional[str] = None,
    ) -> None:
        self.pipeline_name = pipeline_name
        app_id = self.pipeline_name if step is None else f"{self.pipeline_name}.{step}"
        try:
            faust_config = get_config("faust")
            if faust_config is None:
                self.faust_config = {}
            else:
                self.faust_config = faust_config.get("default", {})
                if step:
                    self.faust_config.update(faust_config.get(step, {}))
        except Exception:
            pass
        self.app = _FaustApp(
            id=app_id,
            broker=broker,
            web_enabled=False,
            **self.faust_config,
            schema_registry_url=schema_registry_url,
        )
        loop = asyncio.get_event_loop()

        self.worker = faust.Worker(
            self.app,
            loop=loop,
            override_logging=False,
        )
        self.worker.on_startup_finished = self.on_startup_finished
        self.worker.on_start = self.on_start
        self.worker.on_shutdown = self.on_shutdown

    def start(self, agents: List[FaustAgent], enable_concurrency=False):
        try:
            broker = str(self.app._conf.broker[0])
            steps = list(map(lambda s: s["name"], get_config("steps")))
            for step in steps:
                self.create_topic(broker, step)
            tasks = []
            for agent in agents:
                tasks.append(self.attach(agent, enable_concurrency=enable_concurrency))
            self.worker.loop.run_until_complete(asyncio.gather(*tasks))
            self.worker.execute_from_commandline()
        except KeyboardInterrupt:
            logger.info("keyboard interrupt received")

    def get_step_config(self, step: str) -> Step:
        step_config = next((s for s in get_config("steps") if s["name"] == step), None)
        return from_dict(data_class=Step, data=step_config)

    def create_topic(self, broker: str, step: str):
        step_config = self.get_step_config(step)
        client = AdminClient({"bootstrap.servers": broker.replace("kafka://", "")})
        topics = client.list_topics().topics
        topic_names = [f"{self.pipeline_name}.{step_config.name}"]
        for table in step_config.tables:
            table_topic_name = f"{self.pipeline_name}-{table}-changelog"
            topic_names.append(table_topic_name)
        for topic_name in topic_names:
            if topic_name not in topics:
                logger.info(
                    f"creating topic {topic_name} with {step_config.partitions} partitions"
                )
                resp = client.create_topics(
                    [NewTopic(topic_name, step_config.partitions, replication_factor=1)]
                )
                resp[topic_name].result()
            else:
                logger.info(f"topic {topic_name} already exists")

    async def attach(self, agent: FaustAgent, enable_concurrency=False):
        agent.step_config = self.get_step_config(agent.step)
        agent.agent_id = f"{self.pipeline_name}.{agent.step}"
        agent.input_topic = self.app.topic(
            agent.agent_id,
            value_type=agent.input_value_type,
            value_serializer=agent.input_value_serializer,
        )
        output_topic_name = f"{self.pipeline_name}.{agent.step_config.output}"
        agent.output_topic = self.app.topic(
            output_topic_name,
            value_serializer=agent.output_value_serializer,
        )

        concurrency = agent.step_config.partitions if enable_concurrency else 1
        new_agent = self.app.agent(agent.input_topic, concurrency=concurrency)(
            agent.process
        )
        agent.agent = new_agent
        await agent.after_attach()
        await new_agent.start()


def get_avro_schema(cls):
    @functools.wraps(cls, updated=[])
    class WithAvroModel(dataclass(cls), AvroModel):
        pass

    return WithAvroModel.avro_schema()


class _FaustApp(faust.App):
    def __init__(self, *args, schema_registry_url=None, **kwargs):
        self._delphai_schema_registry_client = (
            SchemaRegistryClient(schema_registry_url) if schema_registry_url else None
        )
        super().__init__(*args, **kwargs)

    def topic(
        self,
        *topics: str,
        pattern: Union[str, Pattern] = None,
        schema: SchemaT = None,
        key_type: ModelArg = None,
        value_type: ModelArg = None,
        key_serializer: CodecArg = None,
        value_serializer: CodecArg = None,
        partitions: int = None,
        retention: Seconds = None,
        compacting: bool = None,
        deleting: bool = None,
        replicas: int = None,
        acks: bool = True,
        internal: bool = False,
        config: Mapping[str, Any] = None,
        maxsize: int = None,
        allow_empty: bool = False,
        has_prefix: bool = False,
        loop: asyncio.AbstractEventLoop = None,
    ) -> TopicT:
        if self._delphai_schema_registry_client and (schema is None) and topics:
            if (key_serializer is None) and key_type and issubclass(key_type, Model):
                key_serializer = FaustSerializer(
                    self._delphai_schema_registry_client,
                    f"{topics[0]}-key",
                    get_avro_schema(key_type),
                )

            if (
                (value_serializer is None)
                and value_type
                and issubclass(value_type, Model)
            ):
                value_serializer = FaustSerializer(
                    self._delphai_schema_registry_client,
                    f"{topics[0]}-value",
                    get_avro_schema(value_type),
                )

        return super().topic(
            *topics,
            pattern=pattern,
            schema=schema,
            key_type=key_type,
            value_type=value_type,
            key_serializer=key_serializer,
            value_serializer=value_serializer,
            partitions=partitions,
            retention=retention,
            compacting=compacting,
            deleting=deleting,
            replicas=replicas,
            acks=acks,
            internal=internal,
            config=config,
            maxsize=maxsize,
            allow_empty=allow_empty,
            has_prefix=has_prefix,
            loop=loop,
        )
