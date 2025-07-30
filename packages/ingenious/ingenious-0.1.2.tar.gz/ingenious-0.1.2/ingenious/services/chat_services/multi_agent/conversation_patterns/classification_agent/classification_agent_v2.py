import logging
from typing import Tuple

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from ingenious.models import config as _config

logger = logging.getLogger(__name__)


class ConversationPattern:
    def __init__(
        self,
        default_llm_config: dict,
        topics: list,
        memory_record_switch: bool,
        memory_path: str,
        thread_memory: str,
    ):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory
        self.context = ""

        # Create Azure OpenAI model client from config
        self.model_client = AzureOpenAIChatCompletionClient(
            model=default_llm_config.get(
                "azure_deployment", default_llm_config.get("model", "gpt-4.1-nano")
            ),
            api_key=default_llm_config.get("api_key", "mock-openai-key"),
            azure_endpoint=default_llm_config.get(
                "azure_endpoint", "http://127.0.0.1:3001"
            ),
            api_version=default_llm_config.get("api_version", "2024-08-01-preview"),
        )

        # Initialize memory manager for cloud storage support
        from ingenious.services.memory_manager import (
            get_memory_manager,
            run_async_memory_operation,
        )

        self.memory_manager = get_memory_manager(_config.get_config(), memory_path)

        # Initialize context file
        if not self.thread_memory:
            run_async_memory_operation(
                self.memory_manager.write_memory(
                    "New conversation. Continue based on user question."
                )
            )

        if self.memory_record_switch and self.thread_memory:
            logger.log(
                level=logging.DEBUG,
                msg="Memory recording enabled. Requires `ChatHistorySummariser` for optional dependency.",
            )
            run_async_memory_operation(
                self.memory_manager.write_memory(self.thread_memory)
            )

        # Read current context
        self.context = run_async_memory_operation(
            self.memory_manager.read_memory(default_content="")
        )

        # Simplified: Just one classifier agent that does both classification and response
        self.classifier = AssistantAgent(
            name="classifier",
            model_client=self.model_client,
            system_message=(
                "You are a classification and response agent. Classify user messages into these categories:\n"
                "1. payload_type_1: General product inquiries, features, specifications\n"
                "2. payload_type_2: Purchase-related questions, pricing, availability\n"
                "3. payload_type_3: Support issues, problems, complaints\n"
                "4. undefined: Messages that don't fit the above categories\n\n"
                "Respond with a JSON object containing:\n"
                "- 'category': the classification category\n"
                "- 'explanation': brief reason for classification\n"
                "- 'response': helpful response to the user\n"
                "Then say TERMINATE to end the conversation."
            ),
        )

        # Simple user proxy to start the conversation
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
        )

    def add_topic_agent(self, agent_name: str, system_message: str):
        """Add a topic agent - simplified to do nothing since we use single classifier"""
        pass

    async def get_conversation_response(self, input_message: str) -> Tuple[str, str]:
        """
        Simplified conversation with just classifier + user proxy in round-robin (max 2 turns)
        """
        try:
            # Create a simple round-robin team with just 2 agents
            team = RoundRobinGroupChat(participants=[self.user_proxy, self.classifier])

            # Run with a much simpler task and max 2 turns
            result = await team.run(
                task=f"Classify and respond to this message: {input_message}",
                max_turns=2,  # Much faster - just user proxy -> classifier -> done
            )

            # Get the final message content
            final_message = (
                result.messages[-1].content if result.messages else "No response"
            )

            # Update context using MemoryManager
            from ingenious.services.memory_manager import run_async_memory_operation

            run_async_memory_operation(self.memory_manager.write_memory(final_message))
            self.context = final_message

            return final_message, self.context

        except Exception as e:
            logger.error(f"Error in conversation response: {e}")
            error_response = {
                "category": "payload_type_1",
                "explanation": "Error occurred during classification",
                "response": "I apologize, but I encountered an issue. How can I help you today?",
            }
            return str(error_response), str(e)

    async def close(self):
        """Close the model client connection"""
        await self.model_client.close()
