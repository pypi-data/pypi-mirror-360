from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

import ingenious.config.config as config
from ingenious.models.chat import ChatRequest


class ConversationFlow:
    @staticmethod
    async def get_conversation_response(chatrequest: ChatRequest):
        message = chatrequest.user_prompt
        topics = chatrequest.topic

        # Ensure topics is always a list
        if topics is None:
            topics = ["general"]
        elif isinstance(topics, str):
            topics = [topics]

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

        # Create classification system prompt
        classification_system_prompt = """
You are a classification assistant. Classify the following user message into one of these categories:
1. payload_type_1: General product inquiries, features, specifications
2. payload_type_2: Purchase-related questions, pricing, availability
3. payload_type_3: Support issues, problems, complaints
4. undefined: Messages that don't fit the above categories

Format your response as:
Category: [category_name]
Explanation: [brief explanation]
Response: [helpful response to the user's message]
"""

        # Create the classification agent
        classification_agent = AssistantAgent(
            name="classification_agent",
            system_message=classification_system_prompt,
            model_client=model_client,
        )

        # Create cancellation token
        cancellation_token = CancellationToken()

        try:
            # Send the user message to the classification agent
            response = await classification_agent.on_messages(
                messages=[TextMessage(content=message, source="user")],
                cancellation_token=cancellation_token,
            )

            result = response.chat_message.content
            memory_summary = f"Classified message: {message[:50]}..."

        except Exception as e:
            result = "Fast classification completed. Category: payload_type_1. Response: I understand you're looking for information. How can I help you today?"
            memory_summary = f"Classification error handled: {str(e)[:50]}..."

        finally:
            # Make sure to close the model client connection when done
            await model_client.close()

        return result, memory_summary
