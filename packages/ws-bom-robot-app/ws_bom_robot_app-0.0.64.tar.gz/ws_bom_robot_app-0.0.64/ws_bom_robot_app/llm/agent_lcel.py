from typing import Any, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import render_text_description
import chevron
from ws_bom_robot_app.llm.agent_context import AgentContext
from ws_bom_robot_app.llm.providers.llm_manager import LlmInterface
from ws_bom_robot_app.llm.models.api import LlmMessage, LlmRules
from ws_bom_robot_app.llm.utils.agent import get_rules
from ws_bom_robot_app.llm.defaut_prompt import default_prompt, tool_prompt

class AgentLcel:

    def __init__(self, llm: LlmInterface, sys_message: str, sys_context: AgentContext, tools: list, rules: LlmRules = None):
        self.sys_message = chevron.render(template=sys_message,data=sys_context)
        self.__llm = llm
        self.__tools = tools
        self.rules = rules
        self.embeddings = llm.get_embeddings()
        self.memory_key: str = "chat_history"
        self.__llm_with_tools = llm.get_llm().bind_tools(self.__tools) if len(self.__tools) > 0 else llm.get_llm()
        self.executor = self.__create_agent()

    async def __create_prompt(self, input: dict) -> ChatPromptTemplate:
        message : LlmMessage = input[self.memory_key][-1]
        rules_prompt = await get_rules(self.embeddings, self.rules, message.content) if self.rules else ""
        system = default_prompt + (tool_prompt(render_text_description(self.__tools)) if len(self.__tools)>0 else "") + self.sys_message + rules_prompt
        return ChatPromptTemplate([
                ("system", system),
                MessagesPlaceholder(variable_name=self.memory_key),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

    def __create_agent(self) -> AgentExecutor:
      agent: Any = (
          {
            "agent_scratchpad": lambda x: self.__llm.get_formatter(x["intermediate_steps"]),
             str(self.memory_key): lambda x: x[self.memory_key],
          }
          | RunnableLambda(self.__create_prompt)
          | self.__llm_with_tools
          | self.__llm.get_parser()
      )
      return AgentExecutor(agent=agent,tools=self.__tools,verbose=False)
