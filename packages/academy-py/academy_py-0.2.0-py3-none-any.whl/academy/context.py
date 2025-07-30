from __future__ import annotations

import asyncio
import dataclasses
from typing import Any
from typing import Generic
from typing import TYPE_CHECKING
from typing import TypeVar

from academy.exchange import AgentExchangeClient
from academy.handle import Handle
from academy.identifier import AgentId
from academy.identifier import EntityId
from academy.identifier import UserId

if TYPE_CHECKING:
    from academy.agent import AgentT
else:
    AgentT = TypeVar('AgentT')


class ActionContext:
    """Action invocation context."""

    def __init__(
        self,
        source_id: EntityId,
        exchange_client: AgentExchangeClient[Any, Any],
    ) -> None:
        self._source_id = source_id
        self._exchange_client = exchange_client
        self._source_handle: Handle[Any] | None = None

    @property
    def source_id(self) -> EntityId:
        """ID of the source that requested the action."""
        return self._source_id

    @property
    def source_handle(self) -> Handle[Any]:
        """Get a handle to the source agent of the request.

        Returns:
            Handle to the agent that made the request.

        Raises:
            TypeError: If the source is a user entity.
        """
        if isinstance(self.source_id, UserId):
            raise TypeError(
                'Cannot create handle to source because it is a user entity.',
            )
        if self._source_handle is None:
            self._source_handle = self._exchange_client.get_handle(
                self.source_id,
            )
        return self._source_handle

    def is_agent_source(self) -> bool:
        """Is the source an agent."""
        return isinstance(self.source_id, AgentId)

    def is_user_source(self) -> bool:
        """Is the source a user."""
        return isinstance(self.source_id, UserId)


@dataclasses.dataclass(frozen=True)
class AgentContext(Generic[AgentT]):
    """Agent runtime context."""

    agent_id: AgentId[AgentT]
    """ID of the exchange as registered with the exchange."""
    exchange_client: AgentExchangeClient[AgentT, Any]
    """Client used by agent to communicate with the exchange."""
    shutdown_event: asyncio.Event
    """Shutdown event used to signal the agent to shutdown."""
