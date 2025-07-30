import os
from langchain_core.documents import Document
from abc import ABC, abstractmethod
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.pipeline.pipeline import Pipeline, PartitionerConfig, FiltererConfig
from typing import Union
from ws_bom_robot_app.llm.utils.secrets import Secrets

class IntegrationStrategy(ABC):
  @classmethod
  def _parse_data(cls, data: dict[str, Union[str, int, list]]) -> dict[str, Union[str, int, list]]:
    for key, fn in (
      ("__from_env", Secrets.from_env),
      ("__from_file", Secrets.from_file),
    ):
      if key in data:
        if secret := fn(data[key]):
          return secret
    return data
  def __init__(self, knowledgebase_path: str, data: dict[str, Union[str,int,list]]):
    self.knowledgebase_path = knowledgebase_path
    self.data = self._parse_data(data)
    self.working_directory = os.path.join(self.knowledgebase_path,self.working_subdirectory())
    os.makedirs(self.working_directory, exist_ok=True)
  @property
  @abstractmethod
  def working_subdirectory(self) -> str:
    pass
  @abstractmethod
  #@timer
  def load(self) -> list[Document]:
    pass

class UnstructuredIngest():
  def __init__(self, working_directory: str):
    self.working_directory = working_directory
  def pipeline(self,indexer,downloader,connection,extension: list[str] = None) -> Pipeline:
    return Pipeline.from_configs(
      context=ProcessorConfig(
        reprocess=False,
        verbose=False,
        tqdm=False,
        num_processes=2,
        preserve_downloads=True,
        download_only=True,
        raise_on_error=False
      ),
      indexer_config=indexer,
      downloader_config=downloader,
      source_connection_config=connection,
      partitioner_config=PartitionerConfig(),
      filterer_config=FiltererConfig(file_glob=[f"**/*{ext}" for ext in extension] if extension else None)
    )

