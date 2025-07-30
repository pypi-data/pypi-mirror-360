import logging
import uuid as uuid_module
from abc import ABC, abstractmethod
from typing import List, Optional

from jinja2 import Environment
from openai.types.chat import ChatCompletionMessageParam

import ingenious.config.config as ig_config
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.dependencies import get_openai_service
from ingenious.errors.content_filter_error import ContentFilterError
from ingenious.files.files_repository import FileStorage
from ingenious.models.chat import IChatRequest, IChatResponse
from ingenious.utils.namespace_utils import (
    import_class_with_fallback,
    normalize_workflow_name,
)

logger = logging.getLogger(__name__)


class multi_agent_chat_service:
    config: ig_config.Config
    chat_history_repository: ChatHistoryRepository
    conversation_flow: str
    openai_service: Optional[ChatCompletionMessageParam]

    def __init__(
        self,
        config: ig_config.Config,
        chat_history_repository: ChatHistoryRepository,
        conversation_flow: str,
    ):
        self.config = config
        self.chat_history_repository = chat_history_repository
        self.conversation_flow = conversation_flow
        self.openai_service = get_openai_service()

    async def get_chat_response(self, chat_request: IChatRequest) -> IChatResponse:
        if not chat_request.conversation_flow:
            raise ValueError(f"conversation_flow not set {chat_request}")

        if isinstance(chat_request.topic, str):
            chat_request.topic = [
                topic.strip() for topic in chat_request.topic.split(",")
            ]

        # Initialize additional response fields - to be populated later
        chat_request.thread_chat_history = [{"role": "user", "content": ""}]
        # thread_memory = ""

        # Check if thread exists
        if not chat_request.thread_id:
            chat_request.thread_id = str(uuid_module.uuid4())

        # Get thread messages & add to messages list
        thread_messages = await self.chat_history_repository.get_thread_messages(
            chat_request.thread_id
        )
        chat_request.thread_memory = "no existing context."

        msg = f"current_memory: {chat_request.thread_memory}"
        logger.log(level=logging.INFO, msg=msg)
        # print(msg)

        for thread_message in thread_messages:
            # Validate user_id
            # if thread_message.user_id != chat_request.user_id:
            #     raise ValueError("User ID does not match thread messages.")

            # Validate content_filter_results not present
            if thread_message.content_filter_results:
                raise ContentFilterError(
                    content_filter_results=thread_message.content_filter_results
                )

            chat_request.thread_chat_history.append(
                {"role": thread_message.role, "content": thread_message.content}
            )

        try:
            # call specific agent flow here and get final response
            print(
                f"DEBUG: Starting conversation flow execution for: {self.conversation_flow}"
            )
            if not self.conversation_flow:
                self.conversation_flow = chat_request.conversation_flow
            if not self.conversation_flow:
                raise ValueError(f"conversation_flow4 not set {chat_request}")

            # Normalize workflow name to support both hyphenated and underscored formats
            normalized_flow = normalize_workflow_name(self.conversation_flow)
            module_name = f"services.chat_services.multi_agent.conversation_flows.{normalized_flow}.{normalized_flow}"
            class_name = "ConversationFlow"
            print(f"DEBUG: Loading module: {module_name}, class: {class_name}")
            print(
                f"DEBUG: Original workflow name: {self.conversation_flow}, normalized: {normalized_flow}"
            )

            conversation_flow_service_class = import_class_with_fallback(
                module_name, class_name
            )
            print(
                f"DEBUG: Successfully loaded conversation flow class: {conversation_flow_service_class}"
            )

            # Try to instantiate with new pattern first (IConversationFlow)
            try:
                # Check if it's the new pattern by trying to instantiate with parent service
                conversation_flow_service_class_instance = (
                    conversation_flow_service_class(
                        parent_multi_agent_chat_service=self
                    )
                )

                response_task = (
                    conversation_flow_service_class_instance.get_conversation_response(
                        chat_request=chat_request
                    )
                )

                agent_response = await response_task

            except TypeError as te:
                # Fall back to old pattern (static methods)
                print(
                    f"DEBUG: Using static method pattern for conversation flow: {self.conversation_flow}"
                )
                print(f"DEBUG: TypeError: {te}")

                # Try different static method signatures
                import inspect

                sig = inspect.signature(
                    conversation_flow_service_class.get_conversation_response
                )
                params = list(sig.parameters.keys())
                print(f"DEBUG: Method signature parameters: {params}")

                if len(params) == 1 and params[0] not in ["self", "cls"]:
                    # Single parameter - likely ChatRequest
                    print("DEBUG: Using single ChatRequest parameter")
                    response_task = (
                        conversation_flow_service_class.get_conversation_response(
                            chat_request
                        )
                    )
                else:
                    # Multiple parameters - individual arguments
                    print("DEBUG: Using individual parameters")
                    response_task = (
                        conversation_flow_service_class.get_conversation_response(
                            message=chat_request.user_prompt,
                            topics=chat_request.topic
                            if isinstance(chat_request.topic, list)
                            and chat_request.topic
                            else [chat_request.topic]
                            if chat_request.topic
                            else [],
                            thread_memory=getattr(chat_request, "thread_memory", ""),
                            memory_record_switch=getattr(
                                chat_request, "memory_record", True
                            ),
                            thread_chat_history=getattr(
                                chat_request, "thread_chat_history", []
                            ),
                        )
                    )

                print("DEBUG: About to await response_task")
                agent_response_tuple = await response_task
                print(f"DEBUG: Got agent_response_tuple: {type(agent_response_tuple)}")

                # Convert old response format to new format
                from ingenious.models.chat import ChatResponse

                print(
                    f"DEBUG: About to create ChatResponse, uuid_module available: {uuid_module}"
                )

                # Handle different response types
                if isinstance(agent_response_tuple, ChatResponse):
                    # Already a ChatResponse object
                    print("DEBUG: Response is already ChatResponse")
                    agent_response = agent_response_tuple
                elif (
                    isinstance(agent_response_tuple, tuple)
                    and len(agent_response_tuple) == 2
                ):
                    # Tuple response (response_text, memory_summary)
                    print("DEBUG: Converting tuple response to ChatResponse")
                    response_text, memory_summary = agent_response_tuple
                    agent_response = ChatResponse(
                        thread_id=chat_request.thread_id,
                        message_id=str(uuid_module.uuid4()),
                        agent_response=response_text,
                        token_count=0,
                        max_token_count=0,
                        memory_summary=memory_summary,
                    )
                else:
                    # Handle single response case
                    print("DEBUG: Converting single response to ChatResponse")
                    agent_response = ChatResponse(
                        thread_id=chat_request.thread_id,
                        message_id=str(uuid_module.uuid4()),
                        agent_response=str(agent_response_tuple),
                        token_count=0,
                        max_token_count=0,
                        memory_summary="",
                    )

        except Exception as e:
            logger.error(f"Error occurred while processing conversation flow: {e}")
            raise e

        # Save chat history if memory_record is enabled
        if getattr(chat_request, "memory_record", True):
            try:
                # Save user message
                if chat_request.user_id and chat_request.thread_id:
                    from ingenious.models.message import Message

                    user_message_id = await self.chat_history_repository.add_message(
                        Message(
                            user_id=chat_request.user_id,
                            thread_id=chat_request.thread_id,
                            role="user",
                            content=chat_request.user_prompt,
                        )
                    )
                    logger.info(f"Saved user message: {user_message_id}")

                    # Save agent response
                    agent_message_id = await self.chat_history_repository.add_message(
                        Message(
                            user_id=chat_request.user_id,
                            thread_id=chat_request.thread_id,
                            role="assistant",
                            content=agent_response.agent_response,
                        )
                    )
                    logger.info(f"Saved agent message: {agent_message_id}")

                    # Save memory summary if available
                    if (
                        hasattr(agent_response, "memory_summary")
                        and agent_response.memory_summary
                    ):
                        memory_id = await self.chat_history_repository.add_memory(
                            Message(
                                user_id=chat_request.user_id,
                                thread_id=chat_request.thread_id,
                                role="memory_assistant",
                                content=agent_response.memory_summary,
                            )
                        )
                        logger.info(f"Saved memory: {memory_id}")

            except Exception as e:
                logger.warning(f"Failed to save chat history: {e}")

        return agent_response


class IConversationPattern(ABC):
    _config: ig_config.Config
    _memory_path: str
    _memory_file_path: str
    _memory_manager: any

    def __init__(self):
        super().__init__()
        self._config = ig_config.get_config()
        self._memory_path = self.GetConfig().chat_history.memory_path
        self._memory_file_path = f"{self._memory_path}/context.md"

        # Initialize memory manager for cloud storage support
        from ingenious.services.memory_manager import get_memory_manager

        self._memory_manager = get_memory_manager(self._config, self._memory_path)

    def GetConfig(self):
        return self._config

    def Get_Models(self):
        return self._config.models.__dict__

    def Get_Memory_Path(self):
        return self._memory_path

    def Get_Memory_File(self):
        return self._memory_file_path

    def Maintain_Memory(self, new_content, max_words=150):
        """
        Maintain memory using the MemoryManager for cloud storage support.
        """
        from ingenious.services.memory_manager import run_async_memory_operation

        return run_async_memory_operation(
            self._memory_manager.maintain_memory(new_content, max_words)
        )

    async def write_llm_responses_to_file(
        self, response_array: List[dict], event_type: str, output_path: str
    ):
        fs = FileStorage(self.config)
        for res in response_array:
            make_llm_calls = True
            if make_llm_calls:
                this_response = res["chat_response"]
            else:
                this_response = "Insight not yet generated"

            await fs.write_file(
                this_response,
                f"agent_response_{event_type}_{res['chat_title']}.md",
                output_path,
            )

    @abstractmethod
    async def get_conversation_response(
        self, message: str, thread_memory: str
    ) -> IChatResponse:
        pass


class IConversationFlow(ABC):
    _config: ig_config.Config
    _memory_path: str
    _memory_file_path: str
    _logger: logging.Logger
    _chat_service: multi_agent_chat_service
    _memory_manager: any

    def __init__(self, parent_multi_agent_chat_service: multi_agent_chat_service):
        super().__init__()
        self._config = ig_config.get_config()
        self._memory_path = self.GetConfig().chat_history.memory_path
        self._memory_file_path = f"{self._memory_path}/context.md"
        self._logger = logging.getLogger(__name__)
        self._chat_service = parent_multi_agent_chat_service

        # Initialize memory manager for cloud storage support
        from ingenious.services.memory_manager import get_memory_manager

        self._memory_manager = get_memory_manager(self._config, self._memory_path)

    def GetConfig(self):
        return self._config

    async def Get_Template(
        self, revision_id: str = None, file_name: str = "user_prompt.md"
    ):
        fs = FileStorage(self._config)
        template_path = await fs.get_prompt_template_path(revision_id)
        content = await fs.read_file(file_name=file_name, file_path=template_path)
        if content is None:
            print(f"Prompt file {file_name} not found in {template_path}")
            return ""
        env = Environment()
        template = env.from_string(content)
        return template.render()

    def Get_Models(self):
        return self._config.models

    def Get_Memory_Path(self):
        return self._memory_path

    def Get_Memory_File(self):
        return self._memory_file_path

    def Maintain_Memory(self, new_content, max_words=150):
        """
        Maintain memory using the MemoryManager for cloud storage support.
        """
        from ingenious.services.memory_manager import run_async_memory_operation

        return run_async_memory_operation(
            self._memory_manager.maintain_memory(new_content, max_words)
        )

    @abstractmethod
    async def get_conversation_response(
        self, chat_request: IChatRequest
    ) -> IChatResponse:
        pass


# Save agent response
# agent_message_id = await self.chat_history_repository.add_message(
#     Message(
#         user_id=chat_request.user_id,
#         thread_id=chat_request.thread_id,
#         role="assistant",
#         content=agent_response[0])
# )

# # print("the response:", agent_response)
# _ = await self.chat_history_repository.add_memory(
#     Message(
#         user_id=chat_request.user_id,
#         thread_id=chat_request.thread_id,
#         role="memory_assistant",
#         content=agent_response[1]),
# )
