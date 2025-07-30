import importlib
from abc import ABC, abstractmethod
from pathlib import Path

from ingenious.models.config import Config, FileStorageContainer


class IFileStorage(ABC):
    def __init__(self, config: Config, fs_config: FileStorageContainer):
        self.config: Config = config
        self.fs_config: FileStorageContainer = fs_config

    @abstractmethod
    async def write_file(self, contents: str, file_name: str, file_path: str) -> str:
        """writes a file to the file storage"""
        pass

    @abstractmethod
    async def read_file(self, file_name: str, file_path: str) -> str:
        """reads a file to the file storage"""
        pass

    @abstractmethod
    async def delete_file(self, file_name: str, file_path: str) -> str:
        """deletes a file to the file storage"""
        pass

    @abstractmethod
    async def list_files(self, file_path: str) -> str:
        """lists files in the file storage"""
        pass

    @abstractmethod
    async def check_if_file_exists(self, file_path: str, file_name: str) -> bool:
        """checks if a file exists in the file storage"""
        pass

    @abstractmethod
    async def get_base_path(self) -> str:
        """returns the base path of the file storage"""
        pass


class FileStorage:
    def __init__(self, config: Config, Category: str = "revisions"):
        self.config = config
        self.add_sub_folders = getattr(
            self.config.file_storage, Category
        ).add_sub_folders
        module_name = (
            f"ingenious.files.{self.config.file_storage.revisions.storage_type.lower()}"
        )

        # Dynamically import the module based on the storage type

        class_name0 = f"{Category}"
        class_name1 = getattr(self.config.file_storage, class_name0)
        class_name2 = getattr(class_name1, "storage_type")
        fs_config = class_name1

        class_name = f"{class_name2}_FileStorageRepository"

        try:
            module = importlib.import_module(module_name)
            repository_class: IFileStorage = getattr(module, class_name)
            self.repository: IFileStorage = repository_class(
                config=self.config, fs_config=fs_config
            )

        except (ImportError, AttributeError) as e:
            raise ValueError(
                f"Unsupported File Storage client type: {module_name}.{class_name}"
            ) from e

    async def write_file(self, contents: str, file_name: str, file_path: str):
        return await self.repository.write_file(
            contents=contents, file_name=file_name, file_path=file_path
        )

    async def get_base_path(self):
        return await self.repository.get_base_path()

    async def read_file(self, file_name: str, file_path: str):
        return await self.repository.read_file(file_name, file_path)

    async def delete_file(self, file_name: str, file_path: str):
        return await self.repository.delete_file(file_name, file_path)

    async def list_files(self, file_path: str):
        return await self.repository.list_files(file_path)

    async def check_if_file_exists(self, file_path: str, file_name: str):
        return await self.repository.check_if_file_exists(file_path, file_name)

    async def get_prompt_template_path(self, revision_id: str = None):
        if revision_id:
            template_path = str(Path("templates") / Path("prompts") / Path(revision_id))
        else:
            template_path = str(Path("templates") / Path("prompts"))
        return template_path

    async def get_data_path(self, revision_id: str = None):
        if self.add_sub_folders:
            if revision_id:
                template_path = str(Path("functional_test_outputs") / Path(revision_id))
            else:
                template_path = str(Path("functional_test_outputs"))
        else:
            template_path = ""
        return template_path

    async def get_output_path(self, revision_id: str = None):
        if revision_id:
            template_path = str(Path("functional_test_outputs") / Path(revision_id))
        else:
            template_path = str(Path("functional_test_outputs"))
        return template_path

    async def get_events_path(self, revision_id: str = None):
        if revision_id:
            template_path = str(Path("functional_test_outputs") / Path(revision_id))
        else:
            template_path = str(Path("functional_test_outputs"))
        return template_path
