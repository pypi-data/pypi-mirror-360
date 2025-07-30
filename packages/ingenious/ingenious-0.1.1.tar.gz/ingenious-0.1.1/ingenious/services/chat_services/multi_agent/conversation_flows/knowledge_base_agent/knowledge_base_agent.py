from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

import ingenious.config.config as config
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.tool_factory import ToolFunctions
from ingenious.services.memory_manager import (
    get_memory_manager,
    run_async_memory_operation,
)


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(
        message: str,
        topics: list = [],
        thread_memory: str = "",
        memory_record_switch=True,
        thread_chat_history: list[str, str] = [],
    ) -> ChatResponse:
        # Get configuration for the LLM
        _config = config.get_config()
        model_config = _config.models[0]

        # Configure Azure OpenAI client for v0.4
        azure_config = {
            "model": model_config.model,
            "api_key": model_config.api_key,
            "azure_endpoint": model_config.base_url,
            "azure_deployment": model_config.deployment or model_config.model,
            "api_version": model_config.api_version,
        }

        # Create the model client
        model_client = AzureOpenAIChatCompletionClient(**azure_config)
        memory_path = _config.chat_history.memory_path

        # Initialize memory manager for cloud storage support
        memory_manager = get_memory_manager(_config, memory_path)

        # Set up context handling
        if not thread_memory:
            run_async_memory_operation(
                memory_manager.write_memory(
                    "New conversation. Continue based on user question."
                )
            )
        else:
            run_async_memory_operation(memory_manager.write_memory(thread_memory))

        # Read current context
        context = run_async_memory_operation(
            memory_manager.read_memory(
                default_content="New conversation. Continue based on user question."
            )
        )

        # Create search tool function
        async def search_tool(
            search_query: str, index_name: str = "index-document-set-1"
        ) -> str:
            """Search for information in Azure Cognitive Search index"""
            try:
                return ToolFunctions.aisearch(
                    search_query=search_query, index_name=index_name
                )
            except Exception as e:
                return f"Search error: {str(e)}"

        search_function_tool = FunctionTool(
            search_tool,
            description="Search for information in Azure Cognitive Search. Use index-document-set-1 for health topics and index-document-set-2 for safety topics.",
        )

        # Create the search assistant agent
        search_system_message = f"""You are a knowledge base search assistant.

Tasks:
- Help users find information by searching knowledge bases
- Use the search_tool to look up information in Azure Cognitive Search indexes
- Always base your responses on search results, not general knowledge
- If no information is found, clearly state that

Guidelines for search queries:
- For health-related questions, use index-document-set-1
- For safety-related questions, use index-document-set-2
- For other topics, try searching both indexes
- Use precise, focused search terms

The available topics are: {", ".join(topics) if topics else "general topics"}

Format your responses clearly with proper citations to sources when available.
TERMINATE your response when the task is complete.
"""

        # Set up the agent team with the search assistant and a user proxy
        search_assistant = AssistantAgent(
            name="search_assistant",
            system_message=search_system_message,
            model_client=model_client,
            tools=[search_function_tool],
            reflect_on_tool_use=True,
        )

        user_proxy = UserProxyAgent("user_proxy")

        # Set up termination conditions
        termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

        # Create the group chat with round-robin configuration
        group_chat = RoundRobinGroupChat(
            agents=[search_assistant, user_proxy],
            termination_condition=termination,
            max_turns=10,
        )

        # Create cancellation token
        cancellation_token = CancellationToken()

        # Prepare user message with context
        user_msg = (
            f"Context: {context}\n\nUser question: {message}" if context else message
        )

        # Run the conversation
        result = await group_chat.run(
            task=user_msg, cancellation_token=cancellation_token
        )

        # Extract the response
        final_message = (
            result.messages[-1].content if result.messages else "No response generated"
        )

        # Update context for future conversations if memory recording is enabled
        if memory_record_switch:
            run_async_memory_operation(memory_manager.write_memory(final_message))

        # Make sure to close the model client connection when done
        await model_client.close()

        # Return the response
        return ChatResponse(
            thread_id="",
            message_id="",
            agent_response=final_message,
            token_count=0,
            max_token_count=0,
            memory_summary=final_message,
        ), final_message
