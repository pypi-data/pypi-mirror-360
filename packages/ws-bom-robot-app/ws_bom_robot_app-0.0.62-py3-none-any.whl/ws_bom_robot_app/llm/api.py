from typing import Annotated, Any, Mapping
from fastapi import APIRouter, HTTPException, Request, Header, Body
from fastapi.responses import StreamingResponse
from ws_bom_robot_app.llm.agent_description import AgentDescriptor
from ws_bom_robot_app.llm.models.api import InvokeRequest, StreamRequest, RulesRequest, KbRequest, VectorDbResponse
from ws_bom_robot_app.llm.main import invoke, stream
from ws_bom_robot_app.llm.models.base import IdentifiableEntity
from ws_bom_robot_app.llm.vector_store.generator import kb, rules, kb_stream_file
from ws_bom_robot_app.llm.tools.tool_manager import ToolManager
from ws_bom_robot_app.llm.vector_store.integration.manager import IntegrationManager
from ws_bom_robot_app.task_manager import task_manager, TaskHeader
from ws_bom_robot_app.llm.feedbacks.feedback_manager import FeedbackConfig, FeedbackManager, FeedbackInterface
from uuid import uuid4
router = APIRouter(prefix="/api/llm", tags=["llm"])

@router.get("/")
async def root():
    return {}

@router.post("/invoke")
async def _invoke(rq: InvokeRequest):
    return await invoke(rq)

def _stream_headers(rq: StreamRequest) -> Mapping[str, str]:
    return {
        "X-thread-id": rq.msg_id or str(uuid4()),
        "X-msg-id": rq.msg_id or str(uuid4()),
        }

@router.get("/cms/app", tags=["cms"])
async def cms_apps():
    from ws_bom_robot_app.llm.utils.cms import get_apps
    return await get_apps()

@router.get("/cms/app/{id}", tags=["cms"])
async def cms_app_by_id(id: str):
    from ws_bom_robot_app.llm.utils.cms import get_app_by_id
    return await get_app_by_id(id)


@router.post("/stream")
async def _stream(rq: StreamRequest, ctx: Request) -> StreamingResponse:
    return StreamingResponse(stream(rq, ctx), media_type="application/json", headers=_stream_headers(rq))

@router.post("/stream/raw")
async def _stream_raw(rq: StreamRequest, ctx: Request) -> StreamingResponse:
    return StreamingResponse(stream(rq, ctx, formatted=False), media_type="application/json", headers=_stream_headers(rq))

@router.post("/kb")
async def _kb(rq: KbRequest) -> VectorDbResponse:
    return await kb(rq)

@router.post("/kb/task")
async def _kb_task(rq: KbRequest, headers: Annotated[TaskHeader, Header()]) -> IdentifiableEntity:
    return task_manager.create_task(kb(rq),headers)

@router.post("/rules")
async def _rules(rq: RulesRequest) -> VectorDbResponse:
    return await rules(rq)

@router.post("/rules/task")
async def _rules_task(rq: RulesRequest, headers: Annotated[TaskHeader, Header()]) -> IdentifiableEntity:
    return task_manager.create_task(rules(rq),headers)

@router.get("/kb/file/{filename}")
async def _kb_get_file(filename: str) -> StreamingResponse:
    return await kb_stream_file(filename)

@router.get("/extension/dbs", tags=["extension"])
def _extension_dbs():
    from ws_bom_robot_app.llm.vector_store.db.manager import VectorDbManager
    return [{"id": key, "value": key} for key in VectorDbManager._list.keys()]
@router.get("/extension/providers", tags=["extension"])
def _extension_providers():
    from ws_bom_robot_app.llm.providers.llm_manager import LlmManager
    return [{"id": key, "value": key} for key in LlmManager._list.keys()]
@router.get("/extension/tools", tags=["extension"])
def _extension_tools():
    return [{"id": key, "value": key} for key in ToolManager._list.keys()]
@router.get("/extension/agents", tags=["extension"])
def _extension_agents():
    return [{"id": key, "value": key} for key in AgentDescriptor._list.keys()]
@router.get("/extension/integrations", tags=["extension"])
def _extension_integrations():
    return [{"id": key, "value": key} for key in IntegrationManager._list.keys()]

@router.post("/{provider}/models")
def _llm_models(provider: str, secrets: dict[str, Any]):
  """_summary_
  Args:
      provider: str, e.x. openai, google, anthropic
      secrets: dict[str, str] with apiKey key
  Returns:
      list: id,[other specific provider fields]
  """
  from ws_bom_robot_app.llm.providers.llm_manager import LlmInterface,LlmConfig, LlmManager
  #if not any(key in secrets for key in ["apiKey"]):
  #    raise HTTPException(status_code=401, detail="apiKey not found in secrets")
  _llm: LlmInterface = LlmManager._list[provider](LlmConfig(api_key=secrets.get("apiKey","")))
  try:
    return _llm.get_models()
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

@router.post("/feedback", tags=["feedback"])
async def _send_feedback(feedback: FeedbackConfig):
    """
    Invia un feedback usando lo strategy FeedbackManager.
    """
    provider = feedback.provider
    strategy_cls = FeedbackManager._list.get(provider)
    if not strategy_cls:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Provider '{provider}' non supportato")
    strategy: FeedbackInterface = strategy_cls(feedback)
    result = strategy.send_feedback()
    return {"result": result}
