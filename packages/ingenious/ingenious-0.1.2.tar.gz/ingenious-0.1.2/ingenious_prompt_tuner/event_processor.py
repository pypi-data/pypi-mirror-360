import json
from typing import List

import jsonpickle

import ingenious.dependencies as ingen_deps
from ingenious.files.files_repository import FileStorage
from ingenious.models.agent import Agent
from ingenious.models.chat import ChatRequest
from ingenious.models.config import Config
from ingenious.services.chat_service import ChatService
from ingenious_prompt_tuner.utilities import utils_class


class functional_tests:
    def __init__(
        self,
        config: Config,
        revision_prompt_folder: str,
        revision_id: str,
        make_llm_calls: bool,
    ):
        self.config = config
        self.fs = FileStorage(self.config, Category="revisions")
        self.fs_data = FileStorage(self.config, Category="data")
        self.revision_prompt_folder = revision_prompt_folder
        self.revision_id = revision_id
        self.make_llm_calls = make_llm_calls
        self.utils = utils_class(self.config)

    async def pre_process_file(self, file_name, file_path, revision_id):
        # copy files from
        pass

    async def run_event_from_pre_processed_file(
        self,
        event_type,
        identifier,
        identifier_group,
        file_name,
        agents: List[Agent],
        conversation_flow: str,
    ):
        # Note sample data is loaded from the revision folder
        print("sub folders:", self.config.file_storage.data.add_sub_folders)
        if self.config.file_storage.data.add_sub_folders:
            file_path = f"functional_test_outputs/{self.revision_id}"
        else:
            file_path = "./"

        # Get payload file from the file system
        file_contents = await self.fs_data.read_file(
            file_name=file_name, file_path=file_path
        )
        json_object = json.loads(file_contents)

        # Need to put flow into the test data object
        self.chat_service = ChatService(
            chat_service_type="multi_agent",
            chat_history_repository=ingen_deps.get_chat_history_repository(),
            conversation_flow=conversation_flow,
            config=self.config,
        )

        # Make sure that the prompt template folder exists
        await self.utils.get_prompt_template_folder()

        print(f"Processing {file_name}")

        # thread_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        json_object["identifier"] = identifier
        json_object["revision_id"] = self.revision_id
        if self.make_llm_calls:
            chat_request = ChatRequest(
                user_id=identifier_group,
                thread_id=identifier,
                user_prompt=jsonpickle.dumps(json_object, unpicklable=False),
                conversation_flow=conversation_flow,
                event_type=event_type,
            )

            await self.chat_service.get_chat_response(chat_request)

            # print(response)
