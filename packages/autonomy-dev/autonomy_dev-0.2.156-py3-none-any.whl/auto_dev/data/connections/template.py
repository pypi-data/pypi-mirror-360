"""Template for the connection for the connection scaffolder."""

# pylint: skip-file
# ruff: noqa: E501

from collections import namedtuple


HEADER = """
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright {year} {author}
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
\"\"\" Module for scaffolded component. \"\"\"
"""

DOCSTRING = """\"\"\"{proper_name} connection and channel.\"\"\""""

IMPORTS = """
from abc import abstractmethod
import asyncio
from asyncio.events import AbstractEventLoop
import logging
from typing import Any, Dict, Callable, Optional, Set, cast

from aea.common import Address
from aea.configurations.base import PublicId
from aea.connections.base import Connection, ConnectionStates
from aea.mail.base import Envelope, Message
from aea.protocols.dialogue.base import Dialogue

from packages.{protocol_author}.protocols.{protocol_name}.dialogues import {protocol_name_camelcase}Dialogue
from packages.{protocol_author}.protocols.{protocol_name}.dialogues import Base{protocol_name_camelcase}Dialogues
from packages.{protocol_author}.protocols.{protocol_name}.message import {protocol_name_camelcase}Message

# TODO: import any library dependencies for the connection
"""

PULBIC_ID = """
CONNECTION_ID = PublicId.from_str("{author}/{name}:0.1.0")
"""

LOGGER = """
_default_logger = logging.getLogger("aea.packages.{author}.connections.{name}")
"""

DIALOGUES = """
class {protocol_name_camelcase}Dialogues(Base{protocol_name_camelcase}Dialogues):
    \"\"\"The dialogues class keeps track of all {name} dialogues.\"\"\"

    def __init__(self, self_address: Address, **kwargs) -> None:
        \"\"\"
        Initialize dialogues.

        :param self_address: self address
        :param kwargs: keyword arguments
        \"\"\"

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message, receiver_address: Address
        ) -> Dialogue.Role:
            \"\"\"Infer the role of the agent from an incoming/outgoing first message

            :param message: an incoming/outgoing first message
            :param receiver_address: the address of the receiving agent
            :return: The role of the agent
            \"\"\"
            assert message, receiver_address
            return {protocol_name_camelcase}Dialogue.Role.{ROLE}  # TODO: check

        Base{protocol_name_camelcase}Dialogues.__init__(
            self,
            self_address=self_address,
            role_from_first_message=role_from_first_message,
        )
"""

BASE_ASYNC_CHANNEL = """
class BaseAsyncChannel:
    \"\"\"BaseAsyncChannel.\"\"\"

    def __init__(
        self,
        agent_address: Address,
        connection_id: PublicId,
        message_type: Message,
    ):
        \"\"\"
        Initialize the BaseAsyncChannel channel.

        :param agent_address: the address of the agent.
        :param connection_id: the id of the connection.
        :param message_type: the associated message type.
        \"\"\"

        self.agent_address = agent_address
        self.connection_id = connection_id
        self.message_type = message_type

        self.is_stopped = True
        self._connection = None
        self._tasks: Set[asyncio.Task] = set()
        self._in_queue: Optional[asyncio.Queue] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.logger = _default_logger

    @property
    @abstractmethod
    def performative_handlers(self) -> Dict[Message.Performative, Callable[[Message, Dialogue], Message]]:
        \"\"\"Performative to message handler mapping.\"\"\"

    @abstractmethod
    async def connect(self, loop: AbstractEventLoop) -> None:
        \"\"\"Connect channel using loop.\"\"\"

    @abstractmethod
    async def disconnect(self) -> None:
        \"\"\"Disconnect channel.\"\"\"

    async def send(self, envelope: Envelope) -> None:
        \"\"\"
        Send an envelope with a protocol message.

        It sends the envelope, waits for and receives the result.
        The result is translated into a response envelope.
        Finally, the response envelope is sent to the in-queue.

        :param query_envelope: The envelope containing a protocol message.
        \"\"\"

        if not (self._loop and self._connection):
            raise ConnectionError("{{self.__class__.__name__}} not connected, call connect first!")

        if not isinstance(envelope.message, self.message_type):
            raise TypeError(f"Message not of type {{self.message_type}}")

        message = envelope.message

        if message.performative not in self.performative_handlers:
            log_msg = "Message with unexpected performative `{{message.performative}}` received."
            self.logger.error(log_msg)
            return

        handler = self.performative_handlers[message.performative]

        dialogue = cast(Dialogue, self._dialogues.update(message))
        if dialogue is None:
            self.logger.warning(f"Could not create dialogue for message={{message}}")
            return

        response_message = handler(message, dialogue)
        self.logger.info(f"returning message: {{response_message}}")

        response_envelope = Envelope(
            to=str(envelope.sender),
            sender=str(self.connection_id),
            message=response_message,
            protocol_specification_id=self.message_type.protocol_specification_id,
        )

        await self._in_queue.put(response_envelope)

    async def get_message(self) -> Optional[Envelope]:
        \"\"\"Check the in-queue for envelopes.\"\"\"

        if self.is_stopped:
            return None
        try:
            envelope = self._in_queue.get_nowait()
            return envelope
        except asyncio.QueueEmpty:
            return None

    async def _cancel_tasks(self) -> None:
        \"\"\"Cancel all requests tasks pending.\"\"\"

        for task in list(self._tasks):
            if task.done():  # pragma: nocover
                continue
            task.cancel()

        for task in list(self._tasks):
            try:
                await task
            except KeyboardInterrupt:  # noqa
                raise
            except BaseException:  # noqa
                pass  # nosec
"""

ASYNC_CHANNEL = """
class {name_camelcase}AsyncChannel(BaseAsyncChannel):  # pylint: disable=too-many-instance-attributes
    \"\"\"A channel handling incomming communication from the {proper_name} connection.\"\"\"

    def __init__(
        self,
        agent_address: Address,
        connection_id: PublicId,
        **kwargs  # TODO: pass the neccesary arguments for your channel explicitly
    ):
        \"\"\"
        Initialize the {proper_name} channel.

        :param agent_address: the address of the agent.
        :param connection_id: the id of the connection.
        \"\"\"

        super().__init__(agent_address, connection_id, message_type={protocol_name_camelcase}Message)

        # TODO: assign attributes from custom connection configuration explicitly
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._dialogues = {protocol_name_camelcase}Dialogues(str({name_camelcase}Connection.connection_id))
        self.logger.debug("Initialised the {proper_name} channel")

    async def connect(self, loop: AbstractEventLoop) -> None:
        \"\"\"
        Connect channel using loop.

        :param loop: asyncio event loop to use
        \"\"\"

        if self.is_stopped:
            self._loop = loop
            self._in_queue = asyncio.Queue()
            self.is_stopped = False
            try:
                raise NotImplementedError("{name_camelcase}AsyncChannel.connect")
                self._connection = ...  # TODO: e.g. self.engine.connect()
                self.logger.info("{proper_name} has connected.")
            except Exception as e:  # noqa
                self.is_stopped = True
                self._in_queue = None
                raise ConnectionError(f"Failed to start {proper_name}: {{e}}")

    async def disconnect(self) -> None:
        \"\"\"Disconnect channel.\"\"\"

        if self.is_stopped:
            return

        await self._cancel_tasks()
        raise NotImplementedError("{name_camelcase}AsyncChannel.disconnect")
        ...  # TODO: e.g. self._connection.close()
        self.is_stopped = True
        self.logger.info("{proper_name} has shutdown.")

    @property
    def performative_handlers(self) -> Dict[{protocol_name_camelcase}Message.Performative, Callable[[{protocol_name_camelcase}Message, {protocol_name_camelcase}Dialogue], {protocol_name_camelcase}Message]]:
        return {handler_mapping}

    {handlers}
"""

CONNECTION = """
class {name_camelcase}Connection(Connection):
    \"\"\"Proxy to the functionality of a {proper_name} connection.\"\"\"

    connection_id = CONNECTION_ID

    def __init__(self, **kwargs: Any) -> None:
        \"\"\"
        Initialize a {proper_name} connection.

        :param kwargs: keyword arguments
        \"\"\"

        keys = []  # TODO: pop your custom kwargs
        config = kwargs["configuration"].config
        custom_kwargs = {{key: config.pop(key) for key in keys}}
        super().__init__(**kwargs)

        self.channel = {name_camelcase}AsyncChannel(
            self.address,
            connection_id=self.connection_id,
            **custom_kwargs,
        )

    async def connect(self) -> None:
        \"\"\"Connect to a {proper_name}.\"\"\"

        if self.is_connected:  # pragma: nocover
            return

        with self._connect_context():
            self.channel.logger = self.logger
            await self.channel.connect(self.loop)

    async def disconnect(self) -> None:
        \"\"\"Disconnect from a {proper_name}.\"\"\"

        if self.is_disconnected:
            return  # pragma: nocover
        self.state = ConnectionStates.disconnecting
        await self.channel.disconnect()
        self.state = ConnectionStates.disconnected

    async def send(self, envelope: Envelope) -> None:
        \"\"\"
        Send an envelope.

        :param envelope: the envelope to send.
        \"\"\"

        self._ensure_connected()
        return await self.channel.send(envelope)

    async def receive(self, *args: Any, **kwargs: Any) -> Optional[Envelope]:
        \"\"\"
        Receive an envelope. Blocking.

        :param args: arguments to receive
        :param kwargs: keyword arguments to receive
        :return: the envelope received, if present.  # noqa: DAR202
        \"\"\"

        self._ensure_connected()
        try:

            result = await self.channel.get_message()
            return result
        except Exception as e:  # noqa
            self.logger.info(f"Exception on receive {{e}}")
            return None
"""

ConnectionTemplate = namedtuple(
    "ConnectionTemplate",
    [
        "HEADER",
        "DOCSTRING",
        "IMPORTS",
        "PULBIC_ID",
        "LOGGER",
        "DIALOGUES",
        "BASE_ASYNC_CHANNEL",
        "ASYNC_CHANNEL",
        "CONNECTION",
    ],
)
CONNECTION_TEMPLATE = ConnectionTemplate(
    HEADER, DOCSTRING, IMPORTS, PULBIC_ID, LOGGER, DIALOGUES, BASE_ASYNC_CHANNEL, ASYNC_CHANNEL, CONNECTION
)
