from _typeshed import Incomplete
from a2a.types import AgentCard as AgentCard
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any, AsyncGenerator

logger: Incomplete

class A2AConnector:
    """Handles A2A protocol communication between agents.

    This class provides methods for sending messages to other agents using the A2A protocol,
    supporting both synchronous and asynchronous communication patterns, as well as streaming
    responses.
    """
    @staticmethod
    def send_to_agent(agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Synchronously sends a message to another agent using the A2A protocol.

        This method is a synchronous wrapper around asend_to_agent. It handles the creation
        of an event loop if one doesn't exist, and manages the asynchronous call internally.

        Args:
            agent_card: The AgentCard instance containing the target agent's details including
                URL, authentication requirements, and capabilities.
            message: The message to send to the agent. Can be either a string for simple text
                messages or a dictionary for structured data.
            **kwargs: Additional keyword arguments passed to asend_to_agent.

        Returns:
            A dictionary containing the response details:
                - status (str): 'success' or 'error'
                - content (str): Extracted text content from the response
                - task_id (str, optional): ID of the created/updated task
                - task_state (str, optional): Current state of the task
                - raw_response (str): Complete JSON response from the A2A client
                - error_type (str, optional): Type of error if status is 'error'
                - message (str, optional): Error message if status is 'error'

        Raises:
            RuntimeError: If asend_to_agent encounters an unhandled exception.
        """
    @staticmethod
    async def asend_to_agent(agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Asynchronously sends a message to another agent using the A2A protocol.

        This method handles the core A2A communication logic by using astream_to_agent
        internally but only returning the final response.

        Args:
            agent_card: The AgentCard instance containing the target agent's details including
                URL, authentication requirements, and capabilities.
            message: The message to send to the agent. Can be either a string for simple text
                messages or a dictionary for structured data.
            **kwargs: Additional keyword arguments.

        Returns:
            A dictionary containing the response details:
                - status (str): 'success' or 'error'
                - content (str): Extracted text content from the response
                - task_id (str, optional): ID of the created/updated task
                - task_state (str, optional): Current state of the task
                - final (bool): Always True for the final response
                - artifact_name (str, optional): Name of the artifact if present

        Raises:
            httpx.HTTPError: If there's an HTTP-related error during the request.
            Exception: For any other unexpected errors during message sending or processing.
        """
    @staticmethod
    async def astream_to_agent(agent_card: AgentCard, message: str | dict[str, Any], **kwargs: Any) -> AsyncGenerator[dict[str, Any], None]:
        """Asynchronously sends a streaming message to another agent using the A2A protocol.

        This method supports streaming responses from the target agent, yielding chunks of
        the response as they become available. It handles various types of streaming events
        including task status updates, artifact updates, and message parts.

        Args:
            agent_card: The AgentCard instance containing the target agent's details including
                URL, authentication requirements, and capabilities.
            message: The message to send to the agent. Can be either a string for simple text
                messages or a dictionary for structured data.
            **kwargs: Additional keyword arguments.

        Yields:
            Dictionaries containing streaming response chunks:
                For successful chunks:
                    - status (str): 'success'
                    - content (str): Extracted text content from the chunk
                    - task_id (str): ID of the associated task
                    - task_state (str): Current state of the task
                    - final (bool): Whether this is the final chunk
                    - artifact_name (str, optional): Name of the artifact if chunk is an artifact update
                For error chunks:
                    - status (str): 'error'
                    - error_type (str): Type of error encountered
                    - message (str): Error description

        Raises:
            httpx.HTTPError: If there's an HTTP-related error during the streaming request.
            Exception: For any other unexpected errors during message streaming or processing.
        """
