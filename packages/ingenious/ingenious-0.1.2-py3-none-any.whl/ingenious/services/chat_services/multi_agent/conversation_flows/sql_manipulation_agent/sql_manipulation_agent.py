from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

import ingenious.config.config as config
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.tool_functions_standard import (
    SQL_ToolFunctions,
)
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

        # Create SQL tool functions
        if (
            not _config.azure_sql_services
            or _config.azure_sql_services.database_name == "skip"
        ):
            table_name, column_names = SQL_ToolFunctions.get_db_attr(_config)

            # Create SQL tool as function
            async def execute_sql_tool(query: str) -> str:
                """Execute SQL query on local database"""
                return SQL_ToolFunctions.execute_sql_local(query)

            sql_tool = FunctionTool(
                execute_sql_tool,
                description=f"Execute SQL query on local database with table '{table_name}' and columns: {', '.join(column_names)}",
            )

            system_message = f"""You are a SQL expert that helps write and execute SQL queries.

Tasks:
- Write SQL queries to answer user questions about data
- Use the 'execute_sql_tool' to run queries
- Format your response based on the number of rows:
  - Single Row: Use the format {{column_name: value, column_name: value}}
  - Multiple Rows: Use a list format with each row as a dictionary

The target table contains the following columns: {", ".join(column_names)}.
Use "SELECT ... FROM {table_name}" format for your queries.
DO NOT change schema or table names.
When composing summary statistics, use functions like AVG(), COUNT(), etc.
When the user asks what columns are available, just list them without running a query.
"""
        else:
            database_name, table_name, column_names = (
                SQL_ToolFunctions.get_azure_db_attr(_config)
            )

            # Create SQL tool as function
            async def execute_sql_tool(query: str) -> str:
                """Execute SQL query on Azure database"""
                return SQL_ToolFunctions.execute_sql_azure(query)

            sql_tool = FunctionTool(
                execute_sql_tool,
                description=f"Execute SQL query on Azure database with table '{database_name}.{table_name}' and columns: {', '.join(column_names)}",
            )

            system_message = f"""You are a SQL expert that helps write and execute SQL queries.

Tasks:
- Write SQL queries to answer user questions about data
- Use the 'execute_sql_tool' to run queries
- Format your response based on the number of rows:
  - Single Row: Use the format {{column_name: value, column_name: value}}
  - Multiple Rows: Use a list format with each row as a dictionary

The target table contains the following columns: {", ".join(column_names)}.
Use "SELECT ... FROM {database_name}.{table_name}" format for your queries.
DO NOT change schema or table names.
When composing summary statistics, use functions like AVG(), COUNT(), etc.
When the user asks what columns are available, just list them without running a query.
"""

        # Set up the agent team with the SQL assistant and a user proxy
        sql_assistant = AssistantAgent(
            name="sql_assistant",
            system_message=system_message,
            model_client=model_client,
            tools=[sql_tool],
            reflect_on_tool_use=True,
        )

        # Create cancellation token
        cancellation_token = CancellationToken()

        # Prepare user message with context
        user_msg = (
            f"Context: {context}\n\nUser question: {message}" if context else message
        )

        # Use the SQL assistant directly with on_messages for a simpler interaction
        from autogen_agentchat.messages import TextMessage

        # Send the message directly to the SQL assistant
        response = await sql_assistant.on_messages(
            messages=[TextMessage(content=user_msg, source="user")],
            cancellation_token=cancellation_token,
        )

        # Extract the response content
        final_message = (
            response.chat_message.content
            if response.chat_message
            else "No response generated"
        )

        # Update context for future conversations
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
        )
