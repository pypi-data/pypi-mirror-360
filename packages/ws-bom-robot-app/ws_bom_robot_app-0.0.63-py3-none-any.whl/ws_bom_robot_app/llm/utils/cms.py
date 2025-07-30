import logging, aiohttp
from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from ws_bom_robot_app.llm.models.api import LlmAppTool
from ws_bom_robot_app.util import cache_with_ttl

class CmsAppCredential(BaseModel):
  app_key: str = Field(..., description="The app key for the credential", validation_alias=AliasChoices("appKey","app_key"))
  api_key: str = Field(..., description="The api key for the credential", validation_alias=AliasChoices("apiKey","api_key"))
  model_config = ConfigDict(extra='ignore')
class CmsApp(BaseModel):
  id: str = Field(..., description="Unique identifier for the app")
  name: str = Field(..., description="Name of the app")
  credentials: CmsAppCredential = None
  app_tools: Optional[List[LlmAppTool]] = Field([], validation_alias=AliasChoices("appTools","app_tools"))
  model_config = ConfigDict(extra='ignore')

@cache_with_ttl(600)  # Cache for 10 minutes
async def get_apps() -> list[CmsApp]:
  import json, os
  from ws_bom_robot_app.config import config
  class DictObject(object):
      def __init__(self, dict_):
          self.__dict__.update(dict_)
      def __repr__(self):
          return json.dumps(self.__dict__)
      @classmethod
      def from_dict(cls, d):
          return json.loads(json.dumps(d), object_hook=DictObject)
  def __attr(obj, *attrs, default=None):
      for attr in attrs:
          obj = getattr(obj, attr, default)
          if obj is None:
              break
      return obj
  host = config.robot_cms_host
  if host:
    url = f"{host}/api/llmApp?depth=1&pagination=false"
    auth = config.robot_cms_auth
    headers = {"Authorization": auth} if auth else {}
    async with aiohttp.ClientSession() as session:
      async with session.get(url, headers=headers) as response:
        if response.status == 200:
          _apps=[]
          cms_apps = await response.json()
          for cms_app in cms_apps:
             if __attr(cms_app,"isActive",default=True) == True:
                _cms_app_dict = DictObject.from_dict(cms_app)
                _app: CmsApp = CmsApp(
                  id=_cms_app_dict.id,
                  name=_cms_app_dict.name,
                  credentials=CmsAppCredential(app_key=_cms_app_dict.settings.credentials.appKey,api_key=_cms_app_dict.settings.credentials.apiKey),
                  app_tools=[LlmAppTool(**tool) for tool in cms_app.get('settings').get('appTools',[])]
                )
                if _app.app_tools:
                  for tool in _app.app_tools:
                    _knowledgeBase = tool.knowledgeBase
                    tool.vector_db = _knowledgeBase.get('vectorDbFile').get('filename') if _knowledgeBase.get('vectorDbFile') else None
                    tool.vector_type = _knowledgeBase.get('vectorDbType') if _knowledgeBase.get('vectorDbType') else 'faiss'
                    del tool.knowledgeBase
                _apps.append(_app)
          return _apps
        else:
          logging.error(f"Error fetching cms apps: {response.status}")
  else:
    logging.error("robot_cms_host environment variable is not set.")
  return []

async def get_app_by_id(app_id: str) -> CmsApp | None:
    apps = await get_apps()
    app = next((a for a in apps if a.id == app_id), None)
    if app:
        return app
    else:
        logging.error(f"App with id {app_id} not found.")
        return None
