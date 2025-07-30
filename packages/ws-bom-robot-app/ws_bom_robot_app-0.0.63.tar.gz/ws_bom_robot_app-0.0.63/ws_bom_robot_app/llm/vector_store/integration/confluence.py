import asyncio
from ws_bom_robot_app.llm.vector_store.integration.base import IntegrationStrategy, UnstructuredIngest
from unstructured_ingest.v2.processes.connectors.confluence import ConfluenceIndexerConfig, ConfluenceDownloaderConfig, ConfluenceConnectionConfig, ConfluenceAccessConfig
from langchain_core.documents import Document
from ws_bom_robot_app.llm.vector_store.loader.base import Loader
from typing import Optional, Union
from pydantic import BaseModel, Field, AliasChoices

class ConfluenceParams(BaseModel):
  """
  ConfluenceParams is a data model for storing Confluence integration parameters.

  Attributes:
    url (str): The URL of the Confluence instance, e.g., 'https://example.atlassian.net'.
    username (str): The email address or username of the Confluence user
    password: Confluence password or Cloud API token, if filled, set the access_token to None and vice versa.
    access_token (str): The personal access token for authenticating with Confluence, e.g., 'AT....'
    spaces (list[str]): A list of Confluence spaces to interact with, e.g., ['SPACE1', 'SPACE2'].
    extension (list[str], optional): A list of file extensions to filter by. Defaults to None, e.g., ['.pdf', '.docx'].
  """
  url: str
  username: str = Field(validation_alias=AliasChoices("userName","userEmail","username"))
  password: Optional[str] = None
  access_token: Optional[str] = Field(None, validation_alias=AliasChoices("accessToken","access_token"))
  spaces: list[str] = []
  extension: list[str] = Field(default=None)
class Confluence(IntegrationStrategy):
  def __init__(self, knowledgebase_path: str, data: dict[str, Union[str,int,list]]):
    super().__init__(knowledgebase_path, data)
    self.__data = ConfluenceParams.model_validate(self.data)
    self.__unstructured_ingest = UnstructuredIngest(self.working_directory)
  def working_subdirectory(self) -> str:
    return 'confluence'
  def run(self) -> None:
    indexer_config = ConfluenceIndexerConfig(
      spaces=self.__data.spaces
    )
    downloader_config = ConfluenceDownloaderConfig(
      download_dir=self.working_directory
    )
    connection_config = ConfluenceConnectionConfig(
      access_config=ConfluenceAccessConfig(password=self.__data.password, token=self.__data.access_token),
      url=self.__data.url,
      username=self.__data.username
    )
    self.__unstructured_ingest.pipeline(
      indexer_config,
      downloader_config,
      connection_config,
      extension=self.__data.extension).run()
  async def load(self) -> list[Document]:
      await asyncio.to_thread(self.run)
      await asyncio.sleep(1)
      return await Loader(self.working_directory).load()

