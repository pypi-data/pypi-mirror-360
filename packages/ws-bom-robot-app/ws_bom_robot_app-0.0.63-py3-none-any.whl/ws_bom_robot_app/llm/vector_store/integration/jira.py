import asyncio, os
from ws_bom_robot_app.llm.vector_store.integration.base import IntegrationStrategy
from langchain_core.documents import Document
from ws_bom_robot_app.llm.vector_store.loader.base import Loader
from pydantic import BaseModel, Field, AliasChoices
from typing import Any, Optional, Union
from unstructured_ingest.interfaces import  ProcessorConfig, ReadConfig
from unstructured_ingest.connector.jira import SimpleJiraConfig, JiraAccessConfig, JiraSourceConnector, JiraIngestDoc, nested_object_to_field_getter, _get_id_fields_for_issue, _get_project_fields_for_issue
from unstructured_ingest.runner import JiraRunner


class JiraParams(BaseModel):
  """
  JiraParams is a Pydantic model that represents the parameters required to interact with a Jira instance.

  Attributes:
    url (str): The URL of the Jira instance, e.g., 'https://example.atlassian.net'.
    access_token (str): The access token for authenticating with the Jira API.
    user_email (str): The email address of the Jira user.
    projects (list[str]): A list of project keys or IDs to interact with, e.g., ['SCRUM', 'PROJ1'].
    boards (Optional[list[str]]): An optional list of board IDs to interact with. Defaults to None, e.g., ['1', '2'].
    issues (Optional[list[str]]): An optional list of issue keys or IDs to interact with. Defaults to None, e.g., ['SCRUM-1', 'PROJ1-1'].
  """
  url: str = Field(..., pattern=r'^https?:\/\/.+')
  access_token: str = Field(..., validation_alias=AliasChoices("accessToken","access_token"), min_length=1)
  user_email: str = Field(validation_alias=AliasChoices("userEmail","user_email"), min_length=1)
  projects: list[str]
  boards: Optional[list[str]] | None = None
  issues: Optional[list[str]] | None = None

class Jira(IntegrationStrategy):
  def __init__(self, knowledgebase_path: str, data: dict[str, Union[str,int,list]]):
    super().__init__(knowledgebase_path, data)
    self.__data = JiraParams.model_validate(self.data)
  def working_subdirectory(self) -> str:
    return 'jira'
  def run(self) -> None:
    access_config = JiraAccessConfig(
      api_token=self.__data.access_token
    )
    config = SimpleJiraConfig(
      user_email=self.__data.user_email,
      url = self.__data.url,
      access_config=access_config,
      projects=self.__data.projects,
      boards=self.__data.boards,
      issues=self.__data.issues
    )
    # runner override: waiting for v2 migration https://github.com/Unstructured-IO/unstructured-ingest/issues/106
    runner = _JiraRunner(
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


# region override
class _JiraIngestDoc(JiraIngestDoc):
  def _get_dropdown_custom_fields_for_issue(issue: dict, c_sep=" " * 5, r_sep="\n") -> str:
      def _parse_value(value: Any) -> Any:
          if isinstance(value, dict):
            _candidate = ["displayName", "name", "value"]
            for item in _candidate:
                if item in value:
                    return value[item]
          return value
      def _remap_custom_fields(fields: dict):
        remapped_fields = {}
        for field_key, field_value in fields.items():
          new_key = next((map_item["name"] for map_item in _JiraSourceConnector.CUSTOM_FIELDS if field_key == map_item["id"]), field_key)
          if new_key != field_value:
            remapped_fields[new_key] = field_value
        return remapped_fields
      filtered_fields = {key: _parse_value(value) for key, value in issue.items() if value is not None and type(value) not in [list]}
      custom_fields =_remap_custom_fields(filtered_fields)
      return (r_sep + c_sep ).join([f"{key}: {value}{r_sep}" for key, value in custom_fields.items()])
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    _issue = self.issue
    _nested: dict = nested_object_to_field_getter(_issue["fields"])
    document = "\n\n\n".join(
              [
                  _get_id_fields_for_issue(_issue),
                  _get_project_fields_for_issue(_nested),
                  _JiraIngestDoc._get_dropdown_custom_fields_for_issue(_nested)
              ],
          )
    _full_filename = str(self.filename)
    _file_extension  = _full_filename.split(".")[-1]
    _file_without_extension = _full_filename.replace(f".{_file_extension}","")
    os.makedirs(os.path.dirname(_file_without_extension), exist_ok=True)
    with open(f"{_file_without_extension}_extra.{_file_extension}", "w", encoding="utf8") as f:
      f.write(document)

class _JiraSourceConnector(JiraSourceConnector):
  CUSTOM_FIELDS: list | None = None
  def __set_custom_fields(self) -> None:
    _custom_fields = self.jira.get_all_custom_fields()
    _JiraSourceConnector.CUSTOM_FIELDS = [{"id":item["id"],"name":item["name"]} for item in _custom_fields]
    self._jira = None # fix serialization
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not _JiraSourceConnector.CUSTOM_FIELDS:
      self.__set_custom_fields()
  def get_ingest_docs(self) -> list[_JiraIngestDoc]:
     return [_JiraIngestDoc(**item.__dict__) for item in super().get_ingest_docs()]

class _JiraRunner(JiraRunner):
  def get_source_connector_cls(self):
    return _JiraSourceConnector
# endregion
