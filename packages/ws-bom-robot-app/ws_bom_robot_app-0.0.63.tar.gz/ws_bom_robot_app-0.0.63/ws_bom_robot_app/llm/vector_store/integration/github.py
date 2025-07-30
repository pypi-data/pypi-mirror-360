import asyncio
from typing import Optional, Union
from ws_bom_robot_app.llm.vector_store.integration.base import IntegrationStrategy
from unstructured_ingest.interfaces import  ProcessorConfig, ReadConfig
from unstructured_ingest.connector.git import GitAccessConfig
from unstructured_ingest.connector.github import SimpleGitHubConfig
from unstructured_ingest.runner import GithubRunner
from langchain_core.documents import Document
from ws_bom_robot_app.llm.vector_store.loader.base import Loader
from pydantic import BaseModel, Field, AliasChoices

class GithubParams(BaseModel):
  """
  GithubParams is a model for storing parameters required to interact with a GitHub repository.

  Attributes:
    repo (str): The name of the GitHub repository, e.g., 'companyname/reponame'
    access_token (Optional[str]): The access token for authenticating with GitHub, e.g., 'ghp_1234567890'.
    branch (Optional[str]): The branch of the repository to interact with. Defaults to 'main'.
    file_ext (Optional[list[str]]): A list of file extensions to filter by, e.g. ['.md', '.pdf']. Defaults to an empty list.
  """
  repo: str
  access_token: Optional[str] | None = Field(None,validation_alias=AliasChoices("accessToken","access_token"))
  branch: Optional[str] = 'main'
  file_ext: Optional[list[str]] = Field(default_factory=list, validation_alias=AliasChoices("fileExt","file_ext"))
class Github(IntegrationStrategy):
  def __init__(self, knowledgebase_path: str, data: dict[str, Union[str,int,list]]):
    super().__init__(knowledgebase_path, data)
    self.__data = GithubParams.model_validate(self.data)
  def working_subdirectory(self) -> str:
    return 'github'
  def run(self) -> None:
    access_config = GitAccessConfig(
      access_token=self.__data.access_token
    )
    file_ext = self.__data.file_ext or None
    file_glob = [f"**/*{ext}" for ext in file_ext] if file_ext else None
    config = SimpleGitHubConfig(
      url = self.__data.repo,
      access_config=access_config,
      branch=self.__data.branch,
      file_glob=file_glob
    )
    runner = GithubRunner(
      connector_config=config,
      processor_config=ProcessorConfig(reprocess=False,verbose=False,num_processes=2,raise_on_error=False),
      read_config=ReadConfig(download_dir=self.working_directory,re_download=True,preserve_downloads=True,download_only=True),
      partition_config=None,
      retry_strategy_config=None
      )
    runner.run()
  async def load(self) -> list[Document]:
      await asyncio.to_thread(self.run)
      await asyncio.sleep(1)
      return await Loader(self.working_directory).load()
