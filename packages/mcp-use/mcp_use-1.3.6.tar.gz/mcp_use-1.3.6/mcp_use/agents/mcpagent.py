"""
MCP: Main integration module with customizable system prompt.

This module provides the main MCPAgent class that integrates all components
to provide a simple interface for using MCP tools with different LLMs.
"""

import logging
import time
from collections.abc import AsyncGenerator, AsyncIterator

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.agents.output_parsers.tools import ToolAgentAction
from langchain.globals import set_debug
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain.schema.language_model import BaseLanguageModel
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException
from langchain_core.runnables.schema import StreamEvent
from langchain_core.tools import BaseTool
from langchain_core.utils.input import get_color_mapping

from mcp_use.client import MCPClient
from mcp_use.connectors.base import BaseConnector
from mcp_use.telemetry.telemetry import Telemetry
from mcp_use.telemetry.utils import extract_model_info

from ..adapters.langchain_adapter import LangChainAdapter
from ..logging import logger
from ..managers.server_manager import ServerManager
from .prompts.system_prompt_builder import create_system_message
from .prompts.templates import DEFAULT_SYSTEM_PROMPT_TEMPLATE, SERVER_MANAGER_SYSTEM_PROMPT_TEMPLATE

set_debug(logger.level == logging.DEBUG)


class MCPAgent:
    """Main class for using MCP tools with various LLM providers.

    This class provides a unified interface for using MCP tools with different LLM providers
    through LangChain's agent framework, with customizable system prompts and conversation memory.
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        client: MCPClient | None = None,
        connectors: list[BaseConnector] | None = None,
        max_steps: int = 5,
        auto_initialize: bool = False,
        memory_enabled: bool = True,
        system_prompt: str | None = None,
        system_prompt_template: str | None = None,  # User can still override the template
        additional_instructions: str | None = None,
        disallowed_tools: list[str] | None = None,
        use_server_manager: bool = False,
        verbose: bool = False,
    ):
        """Initialize a new MCPAgent instance.

        Args:
            llm: The LangChain LLM to use.
            client: The MCPClient to use. If provided, connector is ignored.
            connectors: A list of MCP connectors to use if client is not provided.
            max_steps: The maximum number of steps to take.
            auto_initialize: Whether to automatically initialize the agent when run is called.
            memory_enabled: Whether to maintain conversation history for context.
            system_prompt: Complete system prompt to use (overrides template if provided).
            system_prompt_template: Template for system prompt with {tool_descriptions} placeholder.
            additional_instructions: Extra instructions to append to the system prompt.
            disallowed_tools: List of tool names that should not be available to the agent.
            use_server_manager: Whether to use server manager mode instead of exposing all tools.
        """
        self.llm = llm
        self.client = client
        self.connectors = connectors or []
        self.max_steps = max_steps
        self.auto_initialize = auto_initialize
        self.memory_enabled = memory_enabled
        self._initialized = False
        self._conversation_history: list[BaseMessage] = []
        self.disallowed_tools = disallowed_tools or []
        self.use_server_manager = use_server_manager
        self.verbose = verbose
        # System prompt configuration
        self.system_prompt = system_prompt  # User-provided full prompt override
        # User can provide a template override, otherwise use the imported default
        self.system_prompt_template_override = system_prompt_template
        self.additional_instructions = additional_instructions

        # Either client or connector must be provided
        if not client and len(self.connectors) == 0:
            raise ValueError("Either client or connector must be provided")

        # Create the adapter for tool conversion
        self.adapter = LangChainAdapter(disallowed_tools=self.disallowed_tools)

        # Initialize telemetry
        self.telemetry = Telemetry()

        # Initialize server manager if requested
        self.server_manager = None
        if self.use_server_manager:
            if not self.client:
                raise ValueError("Client must be provided when using server manager")
            self.server_manager = ServerManager(self.client, self.adapter)

        # State tracking - initialize _tools as empty list
        self._agent_executor: AgentExecutor | None = None
        self._system_message: SystemMessage | None = None
        self._tools: list[BaseTool] = []

        # Track model info for telemetry
        self._model_provider, self._model_name = extract_model_info(self.llm)

    async def initialize(self) -> None:
        """Initialize the MCP client and agent."""
        logger.info("🚀 Initializing MCP agent and connecting to services...")
        # If using server manager, initialize it
        if self.use_server_manager and self.server_manager:
            await self.server_manager.initialize()
            # Get server management tools
            management_tools = self.server_manager.tools
            self._tools = management_tools
            logger.info(f"🔧 Server manager mode active with {len(management_tools)} management tools")

            # Create the system message based on available tools
            await self._create_system_message_from_tools(self._tools)
        else:
            # Standard initialization - if using client, get or create sessions
            if self.client:
                # First try to get existing sessions
                self._sessions = self.client.get_all_active_sessions()
                logger.info(f"🔌 Found {len(self._sessions)} existing sessions")

                # If no active sessions exist, create new ones
                if not self._sessions:
                    logger.info("🔄 No active sessions found, creating new ones...")
                    self._sessions = await self.client.create_all_sessions()
                    self.connectors = [session.connector for session in self._sessions.values()]
                    logger.info(f"✅ Created {len(self._sessions)} new sessions")

                # Create LangChain tools directly from the client using the adapter
                self._tools = await self.adapter.create_tools(self.client)
                logger.info(f"🛠️ Created {len(self._tools)} LangChain tools from client")
            else:
                # Using direct connector - only establish connection
                # LangChainAdapter will handle initialization
                connectors_to_use = self.connectors
                logger.info(f"🔗 Connecting to {len(connectors_to_use)} direct connectors...")
                for connector in connectors_to_use:
                    if not hasattr(connector, "client_session") or connector.client_session is None:
                        await connector.connect()

                # Create LangChain tools using the adapter with connectors
                self._tools = await self.adapter._create_tools_from_connectors(connectors_to_use)
                logger.info(f"🛠️ Created {len(self._tools)} LangChain tools from connectors")

            # Get all tools for system message generation
            all_tools = self._tools
            logger.info(f"🧰 Found {len(all_tools)} tools across all connectors")

            # Create the system message based on available tools
            await self._create_system_message_from_tools(all_tools)

        # Create the agent
        self._agent_executor = self._create_agent()
        self._initialized = True
        logger.info("✨ Agent initialization complete")

    async def _create_system_message_from_tools(self, tools: list[BaseTool]) -> None:
        """Create the system message based on provided tools using the builder."""
        # Use the override if provided, otherwise use the imported default
        default_template = self.system_prompt_template_override or DEFAULT_SYSTEM_PROMPT_TEMPLATE
        # Server manager template is now also imported
        server_template = SERVER_MANAGER_SYSTEM_PROMPT_TEMPLATE

        # Delegate creation to the imported function
        self._system_message = create_system_message(
            tools=tools,
            system_prompt_template=default_template,
            server_manager_template=server_template,  # Pass the imported template
            use_server_manager=self.use_server_manager,
            disallowed_tools=self.disallowed_tools,
            user_provided_prompt=self.system_prompt,
            additional_instructions=self.additional_instructions,
        )

        # Update conversation history if memory is enabled
        if self.memory_enabled:
            history_without_system = [msg for msg in self._conversation_history if not isinstance(msg, SystemMessage)]
            self._conversation_history = [self._system_message] + history_without_system

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with the configured system message.

        Returns:
            An initialized AgentExecutor.
        """
        logger.debug(f"Creating new agent with {len(self._tools)} tools")

        system_content = "You are a helpful assistant"
        if self._system_message:
            system_content = self._system_message.content

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_content),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        tool_names = [tool.name for tool in self._tools]
        logger.info(f"🧠 Agent ready with tools: {', '.join(tool_names)}")

        # Use the standard create_tool_calling_agent
        agent = create_tool_calling_agent(llm=self.llm, tools=self._tools, prompt=prompt)

        # Use the standard AgentExecutor
        executor = AgentExecutor(agent=agent, tools=self._tools, max_iterations=self.max_steps, verbose=self.verbose)
        logger.debug(f"Created agent executor with max_iterations={self.max_steps}")
        return executor

    def get_conversation_history(self) -> list[BaseMessage]:
        """Get the current conversation history.

        Returns:
            The list of conversation messages.
        """
        return self._conversation_history

    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self._conversation_history = []

        # Re-add the system message if it exists
        if self._system_message and self.memory_enabled:
            self._conversation_history = [self._system_message]

    def add_to_history(self, message: BaseMessage) -> None:
        """Add a message to the conversation history.

        Args:
            message: The message to add.
        """
        if self.memory_enabled:
            self._conversation_history.append(message)

    def get_system_message(self) -> SystemMessage | None:
        """Get the current system message.

        Returns:
            The current system message, or None if not set.
        """
        return self._system_message

    def set_system_message(self, message: str) -> None:
        """Set a new system message.

        Args:
            message: The new system message content.
        """
        self._system_message = SystemMessage(content=message)

        # Update conversation history if memory is enabled
        if self.memory_enabled:
            # Remove old system message if it exists
            history_without_system = [msg for msg in self._conversation_history if not isinstance(msg, SystemMessage)]
            self._conversation_history = history_without_system

            # Add new system message
            self._conversation_history.insert(0, self._system_message)

        # Recreate the agent with the new system message if initialized
        if self._initialized and self._tools:
            self._agent_executor = self._create_agent()
            logger.debug("Agent recreated with new system message")

    def set_disallowed_tools(self, disallowed_tools: list[str]) -> None:
        """Set the list of tools that should not be available to the agent.

        This will take effect the next time the agent is initialized.

        Args:
            disallowed_tools: List of tool names that should not be available.
        """
        self.disallowed_tools = disallowed_tools
        self.adapter.disallowed_tools = disallowed_tools

        # If the agent is already initialized, we need to reinitialize it
        # to apply the changes to the available tools
        if self._initialized:
            logger.debug("Agent already initialized. Changes will take effect on next initialization.")
            # We don't automatically reinitialize here as it could be disruptive
            # to ongoing operations. The user can call initialize() explicitly if needed.

    def get_disallowed_tools(self) -> list[str]:
        """Get the list of tools that are not available to the agent.

        Returns:
            List of tool names that are not available.
        """
        return self.disallowed_tools

    async def _consume_and_return(
        self,
        generator: AsyncGenerator[tuple[AgentAction, str], str],
    ) -> str:
        """Consume the generator and return the final result.

        This method manually iterates through the generator to consume the steps.
        In Python, async generators cannot return values directly, so we expect
        the final result to be yielded as a special marker.

        Args:
            generator: The async generator that yields steps and a final result.

        Returns:
            The final result from the generator.
        """
        final_result = ""
        steps_taken = 0
        tools_used_names = []
        async for item in generator:
            # If it's a string, it's the final result
            if isinstance(item, str):
                final_result = item
                break
            # Otherwise it's a step tuple, just consume it
            steps_taken += 1
            tools_used_names.append(item[0].tool)
        return final_result, steps_taken, tools_used_names

    async def stream(
        self,
        query: str,
        max_steps: int | None = None,
        manage_connector: bool = True,
        external_history: list[BaseMessage] | None = None,
        track_execution: bool = True,
    ) -> AsyncGenerator[tuple[AgentAction, str] | str, None]:
        """Run the agent and yield intermediate steps as an async generator.

        Args:
            query: The query to run.
            max_steps: Optional maximum number of steps to take.
            manage_connector: Whether to handle the connector lifecycle internally.
            external_history: Optional external history to use instead of the
                internal conversation history.

        Yields:
            Intermediate steps as (AgentAction, str) tuples, followed by the final result as a string.
        """
        result = ""
        initialized_here = False
        start_time = time.time()
        tools_used_names = []
        steps_taken = 0
        success = False

        try:
            # Initialize if needed
            if manage_connector and not self._initialized:
                await self.initialize()
                initialized_here = True
            elif not self._initialized and self.auto_initialize:
                await self.initialize()
                initialized_here = True

            # Check if initialization succeeded
            if not self._agent_executor:
                raise RuntimeError("MCP agent failed to initialize")

            steps = max_steps or self.max_steps
            if self._agent_executor:
                self._agent_executor.max_iterations = steps

            display_query = query[:50].replace("\n", " ") + "..." if len(query) > 50 else query.replace("\n", " ")
            logger.info(f"💬 Received query: '{display_query}'")

            # Add the user query to conversation history if memory is enabled
            if self.memory_enabled:
                self.add_to_history(HumanMessage(content=query))

            # Use the provided history or the internal history
            history_to_use = external_history if external_history is not None else self._conversation_history

            # Convert messages to format expected by LangChain agent input
            # Exclude the main system message as it's part of the agent's prompt
            langchain_history = []
            for msg in history_to_use:
                if isinstance(msg, HumanMessage):
                    langchain_history.append(msg)
                elif isinstance(msg, AIMessage):
                    langchain_history.append(msg)

            intermediate_steps: list[tuple[AgentAction, str]] = []
            inputs = {"input": query, "chat_history": langchain_history}

            # Construct a mapping of tool name to tool for easy lookup
            name_to_tool_map = {tool.name: tool for tool in self._tools}
            color_mapping = get_color_mapping([tool.name for tool in self._tools], excluded_colors=["green", "red"])

            logger.info(f"🏁 Starting agent execution with max_steps={steps}")

            for step_num in range(steps):
                steps_taken = step_num + 1
                # --- Check for tool updates if using server manager ---
                if self.use_server_manager and self.server_manager:
                    current_tools = self.server_manager.tools
                    current_tool_names = {tool.name for tool in current_tools}
                    existing_tool_names = {tool.name for tool in self._tools}

                    if current_tool_names != existing_tool_names:
                        logger.info(
                            f"🔄 Tools changed before step {step_num + 1}, updating agent."
                            f"New tools: {', '.join(current_tool_names)}"
                        )
                        self._tools = current_tools
                        # Regenerate system message with ALL current tools
                        await self._create_system_message_from_tools(self._tools)
                        # Recreate the agent executor with the new tools and system message
                        self._agent_executor = self._create_agent()
                        self._agent_executor.max_iterations = steps
                        # Update maps for this iteration
                        name_to_tool_map = {tool.name: tool for tool in self._tools}
                        color_mapping = get_color_mapping(
                            [tool.name for tool in self._tools], excluded_colors=["green", "red"]
                        )

                logger.info(f"👣 Step {step_num + 1}/{steps}")

                # --- Plan and execute the next step ---
                try:
                    # Use the internal _atake_next_step which handles planning and execution
                    # This requires providing the necessary context like maps and intermediate steps
                    next_step_output = await self._agent_executor._atake_next_step(
                        name_to_tool_map=name_to_tool_map,
                        color_mapping=color_mapping,
                        inputs=inputs,
                        intermediate_steps=intermediate_steps,
                        run_manager=None,
                    )

                    # Process the output
                    if isinstance(next_step_output, AgentFinish):
                        logger.info(f"✅ Agent finished at step {step_num + 1}")
                        result = next_step_output.return_values.get("output", "No output generated")
                        break

                    # If it's actions/steps, add to intermediate steps and yield them
                    intermediate_steps.extend(next_step_output)

                    # Yield each step and track tool usage
                    for agent_step in next_step_output:
                        yield agent_step
                        action, observation = agent_step
                        tool_name = action.tool
                        tools_used_names.append(tool_name)
                        tool_input_str = str(action.tool_input)
                        # Truncate long inputs for readability
                        if len(tool_input_str) > 100:
                            tool_input_str = tool_input_str[:97] + "..."
                        logger.info(f"🔧 Tool call: {tool_name} with input: {tool_input_str}")
                        # Truncate long outputs for readability
                        observation_str = str(observation)
                        if len(observation_str) > 100:
                            observation_str = observation_str[:97] + "..."
                        observation_str = observation_str.replace("\n", " ")
                        logger.info(f"📄 Tool result: {observation_str}")

                    # Check for return_direct on the last action taken
                    if len(next_step_output) > 0:
                        last_step: tuple[AgentAction, str] = next_step_output[-1]
                        tool_return = self._agent_executor._get_tool_return(last_step)
                        if tool_return is not None:
                            logger.info(f"🏆 Tool returned directly at step {step_num + 1}")
                            result = tool_return.return_values.get("output", "No output generated")
                            break

                except OutputParserException as e:
                    logger.error(f"❌ Output parsing error during step {step_num + 1}: {e}")
                    result = f"Agent stopped due to a parsing error: {str(e)}"
                    break
                except Exception as e:
                    logger.error(f"❌ Error during agent execution step {step_num + 1}: {e}")
                    import traceback

                    traceback.print_exc()
                    result = f"Agent stopped due to an error: {str(e)}"
                    break

            # --- Loop finished ---
            if not result:
                logger.warning(f"⚠️ Agent stopped after reaching max iterations ({steps})")
                result = f"Agent stopped after reaching the maximum number of steps ({steps})."

            # Add the final response to conversation history if memory is enabled
            if self.memory_enabled:
                self.add_to_history(AIMessage(content=result))

            logger.info(f"🎉 Agent execution complete in {time.time() - start_time} seconds")
            success = True

            # Yield the final result as a string
            yield result

        except Exception as e:
            logger.error(f"❌ Error running query: {e}")
            if initialized_here and manage_connector:
                logger.info("🧹 Cleaning up resources after initialization error in stream")
                await self.close()
            raise

        finally:
            # Track comprehensive execution data
            execution_time_ms = int((time.time() - start_time) * 1000)

            server_count = 0
            if self.client:
                server_count = len(self.client.get_all_active_sessions())
            elif self.connectors:
                server_count = len(self.connectors)

            conversation_history_length = len(self._conversation_history) if self.memory_enabled else 0

            # Safely access _tools in case initialization failed
            tools_available = getattr(self, "_tools", [])

            if track_execution:
                self.telemetry.track_agent_execution(
                    execution_method="stream",
                    query=query,
                    success=success,
                    model_provider=self._model_provider,
                    model_name=self._model_name,
                    server_count=server_count,
                    server_identifiers=[connector.public_identifier for connector in self.connectors],
                    total_tools_available=len(tools_available),
                    tools_available_names=[tool.name for tool in tools_available],
                    max_steps_configured=self.max_steps,
                    memory_enabled=self.memory_enabled,
                    use_server_manager=self.use_server_manager,
                    max_steps_used=max_steps,
                    manage_connector=manage_connector,
                    external_history_used=external_history is not None,
                    steps_taken=steps_taken,
                    tools_used_count=len(tools_used_names),
                    tools_used_names=tools_used_names,
                    response=result,
                    execution_time_ms=execution_time_ms,
                    error_type=None if success else "execution_error",
                    conversation_history_length=conversation_history_length,
                )

            # Clean up if necessary (e.g., if not using client-managed sessions)
            if manage_connector and not self.client and initialized_here:
                logger.info("🧹 Closing agent after stream completion")
                await self.close()

    async def run(
        self,
        query: str,
        max_steps: int | None = None,
        manage_connector: bool = True,
        external_history: list[BaseMessage] | None = None,
    ) -> str:
        """Run a query using the MCP tools and return the final result.

        This method uses the streaming implementation internally and returns
        the final result after consuming all intermediate steps.

        Args:
            query: The query to run.
            max_steps: Optional maximum number of steps to take.
            manage_connector: Whether to handle the connector lifecycle internally.
                If True, this method will connect, initialize, and disconnect from
                the connector automatically. If False, the caller is responsible
                for managing the connector lifecycle.
            external_history: Optional external history to use instead of the
                internal conversation history.

        Returns:
            The result of running the query.
        """
        success = True
        start_time = time.time()
        generator = self.stream(query, max_steps, manage_connector, external_history, track_execution=False)
        error = None
        steps_taken = 0
        tools_used_names = []
        result = None
        try:
            result, steps_taken, tools_used_names = await self._consume_and_return(generator)
        except Exception as e:
            success = False
            error = str(e)
            logger.error(f"❌ Error during agent execution: {e}")
            raise
        finally:
            self.telemetry.track_agent_execution(
                execution_method="run",
                query=query,
                success=success,
                model_provider=self._model_provider,
                model_name=self._model_name,
                server_count=len(self.client.get_all_active_sessions()) if self.client else len(self.connectors),
                server_identifiers=[connector.public_identifier for connector in self.connectors],
                total_tools_available=len(self._tools) if self._tools else 0,
                tools_available_names=[tool.name for tool in self._tools],
                max_steps_configured=self.max_steps,
                memory_enabled=self.memory_enabled,
                use_server_manager=self.use_server_manager,
                max_steps_used=max_steps,
                manage_connector=manage_connector,
                external_history_used=external_history is not None,
                steps_taken=steps_taken,
                tools_used_count=len(tools_used_names),
                tools_used_names=tools_used_names,
                response=result,
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_type=error,
                conversation_history_length=len(self._conversation_history),
            )
        return result

    async def _generate_response_chunks_async(
        self,
        query: str,
        max_steps: int | None = None,
        manage_connector: bool = True,
        external_history: list[BaseMessage] | None = None,
    ) -> AsyncIterator[StreamEvent]:
        """Internal async generator yielding response chunks.

        The implementation purposefully keeps the logic compact:
        1. Ensure the agent is initialised (optionally handling connector
           lifecycle).
        2. Forward the *same* inputs we use for ``run`` to LangChain's
           ``AgentExecutor.astream``.
        3. Diff the growing ``output`` field coming from LangChain and yield
           only the new part so the caller receives *incremental* chunks.
        4. Persist conversation history when memory is enabled.
        """

        # 1. Initialise on-demand ------------------------------------------------
        initialised_here = False
        if (manage_connector and not self._initialized) or (not self._initialized and self.auto_initialize):
            await self.initialize()
            initialised_here = True

        if not self._agent_executor:
            raise RuntimeError("MCP agent failed to initialise – call initialise() first?")

        # 2. Build inputs --------------------------------------------------------
        effective_max_steps = max_steps or self.max_steps
        self._agent_executor.max_iterations = effective_max_steps

        if self.memory_enabled:
            self.add_to_history(HumanMessage(content=query))

        history_to_use = external_history if external_history is not None else self._conversation_history
        inputs = {"input": query, "chat_history": history_to_use}

        # 3. Stream & diff -------------------------------------------------------
        async for event in self._agent_executor.astream_events(inputs):
            if event.get("event") == "on_chain_end":
                output = event["data"]["output"]
                if isinstance(output, list):
                    for message in output:
                        if not isinstance(message, ToolAgentAction):
                            self.add_to_history(message)
            yield event
        # 5. House-keeping -------------------------------------------------------
        # Restrict agent cleanup in _generate_response_chunks_async to only occur
        #  when the agent was initialized in this generator and is not client-managed
        #  and the user does want us to manage the connection.
        if not self.client and initialised_here and manage_connector:
            logger.info("🧹 Closing agent after generator completion")
            await self.close()

    async def stream_events(
        self,
        query: str,
        max_steps: int | None = None,
        manage_connector: bool = True,
        external_history: list[BaseMessage] | None = None,
    ) -> AsyncIterator[str]:
        """Asynchronous streaming interface.

        Example::

            async for chunk in agent.astream("hello"):
                print(chunk, end="|", flush=True)
        """
        start_time = time.time()
        success = False
        chunk_count = 0
        total_response_length = 0

        try:
            async for chunk in self._generate_response_chunks_async(
                query=query,
                max_steps=max_steps,
                manage_connector=manage_connector,
                external_history=external_history,
            ):
                chunk_count += 1
                if isinstance(chunk, str):
                    total_response_length += len(chunk)
                yield chunk
            success = True
        finally:
            # Track comprehensive execution data for streaming
            execution_time_ms = int((time.time() - start_time) * 1000)

            server_count = 0
            if self.client:
                server_count = len(self.client.get_all_active_sessions())
            elif self.connectors:
                server_count = len(self.connectors)

            conversation_history_length = len(self._conversation_history) if self.memory_enabled else 0

            self.telemetry.track_agent_execution(
                execution_method="stream_events",
                query=query,
                success=success,
                model_provider=self._model_provider,
                model_name=self._model_name,
                server_count=server_count,
                server_identifiers=[connector.public_identifier for connector in self.connectors],
                total_tools_available=len(self._tools) if self._tools else 0,
                tools_available_names=[tool.name for tool in self._tools],
                max_steps_configured=self.max_steps,
                memory_enabled=self.memory_enabled,
                use_server_manager=self.use_server_manager,
                max_steps_used=max_steps,
                manage_connector=manage_connector,
                external_history_used=external_history is not None,
                response=f"[STREAMED RESPONSE - {total_response_length} chars]",
                execution_time_ms=execution_time_ms,
                error_type=None if success else "streaming_error",
                conversation_history_length=conversation_history_length,
            )

    async def close(self) -> None:
        """Close the MCP connection with improved error handling."""
        logger.info("🔌 Closing agent and cleaning up resources...")
        try:
            # Clean up the agent first
            self._agent_executor = None
            self._tools = []

            # If using client with session, close the session through client
            if self.client:
                logger.info("🔄 Closing sessions through client")
                await self.client.close_all_sessions()
                if hasattr(self, "_sessions"):
                    self._sessions = {}
            # If using direct connector, disconnect
            elif self.connectors:
                for connector in self.connectors:
                    logger.info("🔄 Disconnecting connector")
                    await connector.disconnect()

            # Clear adapter tool cache
            if hasattr(self.adapter, "_connector_tool_map"):
                self.adapter._connector_tool_map = {}

            self._initialized = False
            logger.info("👋 Agent closed successfully")

        except Exception as e:
            logger.error(f"❌ Error during agent closure: {e}")
            # Still try to clean up references even if there was an error
            self._agent_executor = None
            if hasattr(self, "_tools"):
                self._tools = []
            if hasattr(self, "_sessions"):
                self._sessions = {}
            self._initialized = False
