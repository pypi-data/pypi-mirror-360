import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import pyodbc

import ingenious.config.config as Config
from ingenious.db.chat_history_repository import IChatHistoryRepository
from ingenious.models.message import Message


class azuresql_ChatHistoryRepository(IChatHistoryRepository):
    def __init__(self, config: Config.Config):
        self.connection_string = config.chat_history.database_connection_string
        if not self.connection_string:
            raise ValueError(
                "Azure SQL connection string is required for azuresql chat history repository"
            )

        self.connection = pyodbc.connect(self.connection_string)
        self.connection.autocommit = True
        self._create_tables()

    def _create_tables(self):
        cursor = self.connection.cursor()

        # Create chat_history table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='chat_history' AND xtype='U')
            CREATE TABLE chat_history (
                user_id NVARCHAR(255),
                thread_id NVARCHAR(255),
                message_id NVARCHAR(255),
                positive_feedback BIT,
                timestamp DATETIME2,
                role NVARCHAR(50),
                content NVARCHAR(MAX),
                content_filter_results NVARCHAR(MAX),
                tool_calls NVARCHAR(MAX),
                tool_call_id NVARCHAR(255),
                tool_call_function NVARCHAR(255)
            );
        """)

        # Create chat_history_summary table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='chat_history_summary' AND xtype='U')
            CREATE TABLE chat_history_summary (
                user_id NVARCHAR(255),
                thread_id NVARCHAR(255),
                message_id NVARCHAR(255),
                positive_feedback BIT,
                timestamp DATETIME2,
                role NVARCHAR(50),
                content NVARCHAR(MAX),
                content_filter_results NVARCHAR(MAX),
                tool_calls NVARCHAR(MAX),
                tool_call_id NVARCHAR(255),
                tool_call_function NVARCHAR(255)
            );
        """)

        # Create users table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                id UNIQUEIDENTIFIER PRIMARY KEY,
                identifier NVARCHAR(255) NOT NULL UNIQUE,
                metadata NVARCHAR(MAX) NOT NULL,
                createdAt DATETIME2
            );
        """)

        # Create threads table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='threads' AND xtype='U')
            CREATE TABLE threads (
                id UNIQUEIDENTIFIER PRIMARY KEY,
                createdAt DATETIME2,
                name NVARCHAR(255),
                userId UNIQUEIDENTIFIER,
                userIdentifier NVARCHAR(255),
                tags NVARCHAR(MAX),
                metadata NVARCHAR(MAX),
                FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Create steps table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='steps' AND xtype='U')
            CREATE TABLE steps (
                id UNIQUEIDENTIFIER PRIMARY KEY,
                name NVARCHAR(255) NOT NULL,
                type NVARCHAR(50) NOT NULL,
                threadId UNIQUEIDENTIFIER NOT NULL,
                parentId UNIQUEIDENTIFIER,
                disableFeedback BIT NOT NULL,
                streaming BIT NOT NULL,
                waitForAnswer BIT,
                isError BIT,
                metadata NVARCHAR(MAX),
                tags NVARCHAR(MAX),
                input NVARCHAR(MAX),
                output NVARCHAR(MAX),
                createdAt DATETIME2,
                start DATETIME2,
                [end] DATETIME2,
                generation NVARCHAR(MAX),
                showInput NVARCHAR(255),
                language NVARCHAR(50),
                indent INT
            );
        """)

        # Create elements table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='elements' AND xtype='U')
            CREATE TABLE elements (
                id UNIQUEIDENTIFIER PRIMARY KEY,
                threadId UNIQUEIDENTIFIER,
                type NVARCHAR(50),
                url NVARCHAR(MAX),
                chainlitKey NVARCHAR(255),
                name NVARCHAR(255) NOT NULL,
                display NVARCHAR(50),
                objectKey NVARCHAR(255),
                size NVARCHAR(50),
                page INT,
                language NVARCHAR(50),
                forId UNIQUEIDENTIFIER,
                mime NVARCHAR(100)
            );
        """)

        # Create feedbacks table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='feedbacks' AND xtype='U')
            CREATE TABLE feedbacks (
                id UNIQUEIDENTIFIER PRIMARY KEY,
                forId UNIQUEIDENTIFIER NOT NULL,
                threadId UNIQUEIDENTIFIER NOT NULL,
                value INT NOT NULL,
                comment NVARCHAR(MAX)
            );
        """)

        cursor.close()

    def execute_sql(self, sql, params=[], expect_results=True):
        cursor = None
        try:
            cursor = self.connection.cursor()

            if expect_results:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                # Convert to list of dictionaries
                columns = [column[0] for column in cursor.description]
                result = [dict(zip(columns, row)) for row in rows]
                return result
            else:
                cursor.execute(sql, params)
                self.connection.commit()

        except Exception as e:
            print(f"SQL Error: {e}")
            raise e

        finally:
            if cursor:
                cursor.close()

    async def _get_user_by_id(self, user_id: str) -> IChatHistoryRepository.User | None:
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT id, identifier, metadata, createdAt FROM users WHERE id = ?""",
            (user_id,),
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return IChatHistoryRepository.User(
                id=row[0], identifier=row[1], metadata=row[2], createdAt=row[3]
            )
        return None

    async def add_memory(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO chat_history_summary (
                user_id, thread_id, message_id, positive_feedback, timestamp,
                role, content, content_filter_results, tool_calls,
                tool_call_id, tool_call_function)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                message.user_id,
                message.thread_id,
                message.message_id,
                message.positive_feedback,
                message.timestamp,
                message.role,
                message.content,
                message.content_filter_results,
                message.tool_calls,
                message.tool_call_id,
                message.tool_call_function,
            ),
        )
        cursor.close()
        return message.message_id

    async def add_message(self, message: Message) -> str:
        message.message_id = str(uuid.uuid4())
        message.timestamp = datetime.now()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO chat_history (
                user_id, thread_id, message_id, positive_feedback, timestamp,
                role, content, content_filter_results, tool_calls,
                tool_call_id, tool_call_function)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                message.user_id,
                message.thread_id,
                message.message_id,
                message.positive_feedback,
                message.timestamp,
                message.role,
                message.content,
                message.content_filter_results,
                message.tool_calls,
                message.tool_call_id,
                message.tool_call_function,
            ),
        )
        cursor.close()
        return message.message_id

    async def add_user(
        self, identifier, metadata: dict = {}
    ) -> IChatHistoryRepository.User:
        now = self.get_now()
        new_id = str(uuid.uuid4())

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO users (id, identifier, metadata, createdAt)
            VALUES (?, ?, ?, ?)
        """,
            (new_id, identifier, json.dumps(metadata), now),
        )
        cursor.close()

        return IChatHistoryRepository.User(
            id=uuid.UUID(new_id),
            identifier=identifier,
            metadata=metadata,
            createdAt=self.get_now_as_string(),
        )

    async def get_user(self, identifier) -> IChatHistoryRepository.User | None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, identifier, metadata, createdAt
            FROM users
            WHERE identifier = ?
        """,
            (identifier,),
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return IChatHistoryRepository.User(
                id=row[0], identifier=row[1], metadata=row[2], createdAt=row[3]
            )
        else:
            usr = await self.add_user(identifier)
            return usr

    async def get_message(self, message_id: str, thread_id: str) -> Message | None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            FROM chat_history
            WHERE message_id = ? AND thread_id = ?
        """,
            (message_id, thread_id),
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return Message(
                user_id=row[0],
                thread_id=row[1],
                message_id=row[2],
                positive_feedback=row[3],
                timestamp=row[4],
                role=row[5],
                content=row[6],
                content_filter_results=row[7],
                tool_calls=row[8],
                tool_call_id=row[9],
                tool_call_function=row[10],
            )
        return None

    async def get_threads_for_user(
        self, identifier: str, thread_id: Optional[str]
    ) -> Optional[List[IChatHistoryRepository.ThreadDict]]:
        # This is a simplified implementation
        # In a full implementation, you'd join with threads table and return proper thread data
        return []

    async def get_thread_messages(self, thread_id: str) -> list[Message]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT TOP 5 user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            FROM (
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function,
                       ROW_NUMBER() OVER (ORDER BY timestamp DESC) as rn
                FROM chat_history
                WHERE thread_id = ?
            ) AS ranked
            WHERE rn <= 5
            ORDER BY timestamp ASC
        """,
            (thread_id,),
        )
        rows = cursor.fetchall()
        cursor.close()

        return [
            Message(
                user_id=row[0],
                thread_id=row[1],
                message_id=row[2],
                positive_feedback=row[3],
                timestamp=row[4],
                role=row[5],
                content=row[6],
                content_filter_results=row[7],
                tool_calls=row[8],
                tool_call_id=row[9],
                tool_call_function=row[10],
            )
            for row in rows
        ]

    async def get_thread(self, thread_id: str) -> list[IChatHistoryRepository.Thread]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, createdAt, name, userId, userIdentifier, tags, metadata
            FROM threads
            WHERE id = ?
        """,
            (thread_id,),
        )
        rows = cursor.fetchall()
        cursor.close()

        return [
            IChatHistoryRepository.Thread(
                id=row[0],
                createdAt=row[1],
                name=row[2],
                userId=row[3],
                userIdentifier=row[4],
                tags=row[5],
                metadata=row[6],
            )
            for row in rows
        ]

    async def update_message_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE chat_history
            SET positive_feedback = ?
            WHERE message_id = ? AND thread_id = ?
        """,
            (positive_feedback, message_id, thread_id),
        )
        cursor.close()

    async def update_message_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE chat_history
            SET content_filter_results = ?
            WHERE message_id = ? AND thread_id = ?
        """,
            (str(content_filter_results), message_id, thread_id),
        )
        cursor.close()

    async def delete_thread(self, thread_id: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            DELETE FROM chat_history
            WHERE thread_id = ?
        """,
            (thread_id,),
        )
        cursor.close()

    async def add_step(self, step_dict: IChatHistoryRepository.StepDict):
        print("Creating step: ", step_dict)

        # If disableFeedback is not provided, default to False
        step_dict["disableFeedback"] = step_dict.get("disableFeedback", False)

        step_dict["showInput"] = (
            str(step_dict.get("showInput", "")).lower()
            if "showInput" in step_dict
            else None
        )
        parameters = {
            key: value
            for key, value in step_dict.items()
            if value is not None and not (isinstance(value, dict) and not value)
        }
        parameters["metadata"] = json.dumps(step_dict.get("metadata", {}))
        parameters["generation"] = json.dumps(step_dict.get("generation", {}))

        columns = ", ".join(f"[{key}]" for key in parameters.keys())
        values = ", ".join("?" for key in parameters.keys())
        query = f"""
            INSERT INTO steps ({columns})
            VALUES ({values});
        """
        self.execute_sql(
            sql=query, params=tuple(parameters.values()), expect_results=False
        )

    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        print("Updating thread: ", thread_id)
        user_identifier = None
        if user_id:
            print("Getting user identifier for user_id: ", user_id)
            user = await self._get_user_by_id(user_id)
            if user:
                user_identifier = user.identifier

        data = {
            "id": thread_id,
            "createdAt": (self.get_now() if metadata is None else None),
            "name": (
                name
                if name is not None
                else (metadata.get("name") if metadata and "name" in metadata else None)
            ),
            "userId": user_id,
            "userIdentifier": user_identifier,
            "tags": json.dumps(tags) if tags else None,
            "metadata": json.dumps(metadata) if metadata else None,
        }

        parameters = {key: value for key, value in data.items() if value is not None}

        columns = ", ".join(f"[{key}]" for key in parameters.keys())
        values = ", ".join("?" for key in parameters.keys())
        updates = ", ".join(f"[{key}] = ?" for key in parameters.keys() if key != "id")

        # Use MERGE for upsert in SQL Server
        query = f"""
            MERGE threads AS target
            USING (SELECT ? as id) AS source ON target.id = source.id
            WHEN MATCHED THEN
                UPDATE SET {updates}
            WHEN NOT MATCHED THEN
                INSERT ({columns})
                VALUES ({values});
        """

        # Prepare parameters for MERGE statement
        merge_params = (
            [thread_id] + list(parameters.values())[1:] + list(parameters.values())
        )

        self.execute_sql(sql=query, params=merge_params, expect_results=False)

        return ""

    async def update_memory(self) -> None:
        cursor = self.connection.cursor()

        # Create a temporary table for the latest records
        cursor.execute("""
            SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            INTO #latest_chat_history
            FROM (
                SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                       content_filter_results, tool_calls, tool_call_id, tool_call_function,
                       ROW_NUMBER() OVER (PARTITION BY thread_id ORDER BY timestamp DESC) AS row_num
                FROM chat_history_summary
            ) AS LatestRecords
            WHERE row_num = 1
        """)

        # Clear the original table
        cursor.execute("DELETE FROM chat_history_summary")

        # Insert the latest records back into the original table
        cursor.execute("""
            INSERT INTO chat_history_summary (user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                                              content_filter_results, tool_calls, tool_call_id, tool_call_function)
            SELECT user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            FROM #latest_chat_history
        """)

        # Drop the temporary table
        cursor.execute("DROP TABLE #latest_chat_history")
        cursor.close()

    async def get_memory(self, message_id: str, thread_id: str) -> Message | None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT TOP 1 user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            FROM chat_history_summary
            WHERE thread_id = ?
            ORDER BY timestamp DESC
        """,
            (thread_id,),
        )
        row = cursor.fetchone()
        cursor.close()

        if row:
            return Message(
                user_id=row[0],
                thread_id=row[1],
                message_id=row[2],
                positive_feedback=row[3],
                timestamp=row[4],
                role=row[5],
                content=row[6],
                content_filter_results=row[7],
                tool_calls=row[8],
                tool_call_id=row[9],
                tool_call_function=row[10],
            )
        return None

    async def get_thread_memory(self, thread_id: str) -> list[Message]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT TOP 1 user_id, thread_id, message_id, positive_feedback, timestamp, role, content,
                   content_filter_results, tool_calls, tool_call_id, tool_call_function
            FROM chat_history_summary
            WHERE thread_id = ?
            ORDER BY timestamp DESC
        """,
            (thread_id,),
        )
        rows = cursor.fetchall()
        cursor.close()

        return [
            Message(
                user_id=row[0],
                thread_id=row[1],
                message_id=row[2],
                positive_feedback=row[3],
                timestamp=row[4],
                role=row[5],
                content=row[6],
                content_filter_results=row[7],
                tool_calls=row[8],
                tool_call_id=row[9],
                tool_call_function=row[10],
            )
            for row in rows
        ]

    async def update_memory_feedback(
        self, message_id: str, thread_id: str, positive_feedback: bool | None
    ) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE chat_history_summary
            SET positive_feedback = ?
            WHERE message_id = ? AND thread_id = ?
        """,
            (positive_feedback, message_id, thread_id),
        )
        cursor.close()

    async def update_memory_content_filter_results(
        self, message_id: str, thread_id: str, content_filter_results: dict[str, object]
    ) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE chat_history_summary
            SET content_filter_results = ?
            WHERE message_id = ? AND thread_id = ?
        """,
            (str(content_filter_results), message_id, thread_id),
        )
        cursor.close()

    async def delete_thread_memory(self, thread_id: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            DELETE FROM chat_history_summary
            WHERE thread_id = ?
        """,
            (thread_id,),
        )
        cursor.close()

    async def delete_user_memory(self, user_id: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            DELETE FROM chat_history_summary
            WHERE user_id = ?
        """,
            (user_id,),
        )
        cursor.close()
