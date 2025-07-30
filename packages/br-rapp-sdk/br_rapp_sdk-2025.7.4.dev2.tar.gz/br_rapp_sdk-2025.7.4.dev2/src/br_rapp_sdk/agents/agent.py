import httpx
import logging
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import Event, EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, InMemoryPushNotifier, TaskUpdater
from a2a.types import (
    AgentCard,
    InternalError,
    InvalidParamsError,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from abc import ABC, abstractmethod
from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamMode
from pydantic import BaseModel
from starlette.applications import Starlette
from typing import AsyncIterable, Literal
from typing_extensions import override

AgentTaskStatus = Literal["working", "input_required", "completed", "error"]
"""AgentTaskStatus is a type alias for the status of an agent task.

The possible values are:
- `working`: The agent is currently processing the task.
- `input_required`: The agent requires additional input from the user to proceed.
- `completed`: The agent has successfully completed the task.
- `error`: An error occurred during the task execution.
"""

class AgentTaskResult(BaseModel):
    """Result of an agent invocation.

    Attributes:
        task_status (AgentTaskStatus): The status of the agent task.
        content (str): The content of the agent's response or message.
    
    Attributes meaning:
    | `task_status`  | `content`                                                            |
    |----------------|----------------------------------------------------------------------|
    | working        | Ongoing task description or progress update.                         |
    | input_required | Description of the required user input or context.                   |
    | completed      | Final response or result of the agent's processing.                  |
    | error          | Error message indicating what went wrong during the task execution.  |
    """

    task_status: AgentTaskStatus
    content: str

class AgentGraph(ABC):
    """Abstract base class for agent graphs.
    
    Extend this class to implement the specific behavior of an agent.

    Example:
    ```python
    from br_rapp_sdk.agents import AgentGraph, AgentTaskResult
    from langgraph.runnables import RunnableConfig
    from langgraph.graph import StateGraph
    from pydantic import BaseModel
    from typing import AsyncIterable
    from typing_extensions import override

    class MyGraphState(BaseModel):
        property1: str
        property2: int

        def to_task_result(self) -> AgentTaskResult:
            return AgentTaskResult(
                task_status="completed",
                content=f"Processed {self.property1} with value {self.property2}"
            )

    class MyAgentGraph(AgentGraph):
        def __init__(self):
            # Define the agent graph using langgraph
            graph_builder = StateGraph(MyGraphState)
            # Add nodes and edges to the graph as needed ...

            self.graph = graph_builder.compile()

        @override
        async def astream(
            self,
            query: str,
            config: RunnableConfig
        ) -> AsyncIterable[AgentTaskResult]:
            state = ... # Create or retrieve the initial state for the agent graph
            graph_stream = self.graph.astream(
                state,
                config,
                stream_mode="values"
            )
            async for item in graph_stream:
                state_item: MyGraphState = MyGraphState.model_validate(item)
                yield state_item.to_task_result()
            return
    """

    @abstractmethod
    async def astream(
        self,
        query: str,
        config: RunnableConfig,
    ) -> AsyncIterable[AgentTaskResult]:
        """Stream results from the agent graph based on the query and configuration.
        
        Args:
            query (str): The query to process.
            config (RunnableConfig): Configuration for the runnable.
        Returns:
            AsyncIterable[AgentTaskResult]: An asynchronous iterable of agent task results.
        """
        pass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalAgentExecutor(AgentExecutor):
    """Minimal Agent Executor.
    
    Minimal implementation of the AgentExecutor interface used by the `AgentApplication` class to execute agent tasks.
    """

    def __init__(
        self,
        agent_graph: AgentGraph
    ):
        self.agent_graph = agent_graph

    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        if not self._request_ok(context):
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.contextId)
        try:
            config = {"configurable": {"thread_id": task.contextId}}
            async for item in self.agent_graph.astream(query, config):
                match item.task_status:
                    case "working":
                        await updater.update_status(
                            TaskState.working,
                            new_agent_text_message(
                                item.content,
                                task.contextId,
                                task.id,
                            ),
                        )
                    case "input_required":
                        await updater.update_status(
                            TaskState.input_required,
                            new_agent_text_message(
                                item.content,
                                task.contextId,
                                task.id,
                            ),
                            final=True,
                        )
                        break
                    case "completed":
                        await updater.add_artifact(
                            [Part(root=TextPart(text=item.content))],
                        )
                        await updater.complete()
                        break
                    case "error":
                        raise ServerError(error=InternalError(message=item.content))
                    case _:
                        logger.warning(f"Unknown task status: {item.task_status}")
        except Exception as e:
            logger.error(f'An error occurred while streaming the response: {e}')
            raise ServerError(error=InternalError()) from e

    def _request_ok(self, context: RequestContext) -> bool:
        return True

    @override
    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())

class AgentApplication:
    """Agent Application based on `Starlette`.

    Attributes:
        agent_card (AgentCard): The agent card containing metadata about the agent.
        agent_graph (AgentGraph): The agent graph that defines the agent's behavior and capabilities.
    
    Example:
    ```python
        import httpx
        import json
        import uvicorn
        from a2a.types import AgentCard
        from br_rapp_sdk.agents import AgentApplication

        with open('./agent.json', 'r') as file:
            agent_data = json.load(file)
            agent_card = AgentCard.model_validate(agent_data)
            logger.info(f'Agent Card loaded: {agent_card}')
        
        url = httpx.URL(agent_card.url)
        graph = MyAgentGraph()
        agent = AgentApplication(
            agent_card=agent_card,
            agent_graph=graph,
        )

        uvicorn.run(agent.build(), host=url.host, port=url.port)
    ```
    """

    def __init__(
        self,
        agent_card: AgentCard,
        agent_graph: AgentGraph
    ):
        """
        Initialize the AgentApplication with an agent card and agent graph.
        Args:
            agent_card (AgentCard): The agent card.
            agent_graph (AgentGraph): The agent graph implementing the agent's logic.
        """
        self._agent_executor = MinimalAgentExecutor(agent_graph)
        self.agent_card = agent_card

        self._httpx_client = httpx.AsyncClient()
        self._request_handler = DefaultRequestHandler(
            agent_executor=self._agent_executor,
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(self._httpx_client),
        )
        self._server = A2AStarletteApplication(
            agent_card=self.agent_card,
            http_handler=self._request_handler
        )

    @property
    def agent_graph(self) -> AgentGraph:
        """Get the agent graph."""
        return self._agent_executor.agent_graph
    
    def build(self) -> Starlette:
        """Build the A2A Starlette application.
        
        Returns:
            Starlette: The built Starlette application.
        """
        return self._server.build()