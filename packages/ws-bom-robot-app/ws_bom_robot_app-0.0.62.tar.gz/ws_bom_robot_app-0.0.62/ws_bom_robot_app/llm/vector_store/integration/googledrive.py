import asyncio
from ws_bom_robot_app.llm.vector_store.integration.base import IntegrationStrategy, UnstructuredIngest
from unstructured_ingest.v2.processes.connectors.google_drive import GoogleDriveConnectionConfig, GoogleDriveDownloaderConfig, GoogleDriveIndexerConfig, GoogleDriveAccessConfig
from langchain_core.documents import Document
from ws_bom_robot_app.llm.vector_store.loader.base import Loader
from typing import Union
from pydantic import BaseModel, Field, AliasChoices
class GoogleDriveParams(BaseModel):
  """
  GoogleDriveParams is a model that holds parameters for Google Drive integration.

  Attributes:
    service_account_key (dict): The service account key for Google Drive API authentication \n
      - detail: https://developers.google.com/workspace/guides/create-credentials#service-accountc \n
      - create a service account key, download the JSON file, and pass the content of the JSON file as a dictionary \n
      - e.g., {
        "type": "service_account",
        "project_id": "demo-project-123456",
        "private_key_id": "**********",
        "private_key": "-----BEGIN PRIVATE KEY-----...----END PRIVATE KEY-----",
        "client_email": "demo-client@demo-project-123456.iam.gserviceaccount.com",
        "client_id": "123456",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/demo-client%40demo-project-123456.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
      }
      - enable Google Drive API: https://console.cloud.google.com/marketplace/product/google/drive.googleapis.com
      - copy email address of the service account and share the Google Drive with the email address: https://www.youtube.com/watch?v=ykJQzEe_2dM&t=2s

    drive_id (str): The {folder_id} of the Google Drive to interact with, e.g., https://drive.google.com/drive/folders/{folder_id}
    extensions (list[str]): A list of file extensions to filter the files in the Google Drive, e.g., ['.pdf', '.docx'].
    recursive (bool): A flag indicating whether to search files recursively in the Google Drive.
  """
  service_account_key: dict = Field(validation_alias=AliasChoices("serviceAccountKey","service_account_key"))
  drive_id: str = Field(validation_alias=AliasChoices("driveId","drive_id"))
  extensions: list[str] = []
  recursive: bool = False
class GoogleDrive(IntegrationStrategy):
  def __init__(self, knowledgebase_path: str, data: dict[str, Union[str,int,list]]):
    super().__init__(knowledgebase_path, data)
    self.__data = GoogleDriveParams.model_validate(self.data)
    self.__unstructured_ingest = UnstructuredIngest(self.working_directory)
  def working_subdirectory(self) -> str:
    return 'googledrive'
  def run(self) -> None:
    indexer_config = GoogleDriveIndexerConfig(
      extensions=self.__data.extensions,
      recursive=self.__data.recursive
    )
    downloader_config = GoogleDriveDownloaderConfig(
      download_dir=self.working_directory
    )
    connection_config = GoogleDriveConnectionConfig(
      access_config=GoogleDriveAccessConfig(
        service_account_key=self.__data.service_account_key
        ),
      drive_id=self.__data.drive_id
    )
    self.__unstructured_ingest.pipeline(
      indexer_config,
      downloader_config,
      connection_config).run()
  async def load(self) -> list[Document]:
      await asyncio.to_thread(self.run)
      await asyncio.sleep(1)
      return await Loader(self.working_directory).load()

