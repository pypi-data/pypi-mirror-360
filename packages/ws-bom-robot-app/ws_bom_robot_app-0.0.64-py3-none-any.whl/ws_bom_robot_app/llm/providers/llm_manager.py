import json
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, ConfigDict, Field
import os

class LlmConfig(BaseModel):
    api_url: Optional[str] = None
    api_key: str
    embedding_api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0)

# abstract LLM interface with default implementations
class LlmInterface:
    def __init__(self, config: LlmConfig):
        self.config = config

    def get_llm(self) -> BaseChatModel:
        raise NotImplementedError

    def get_embeddings(self) -> Embeddings:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            api_key=self.config.embedding_api_key or os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small")

    def get_models(self) -> list:
        raise NotImplementedError

    def get_formatter(self,intermadiate_steps):
        from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
        return format_to_openai_tool_messages(intermediate_steps=intermadiate_steps)

    def get_parser(self):
        from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
        return OpenAIToolsAgentOutputParser()

class Anthropic(LlmInterface):
    def get_llm(self):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            api_key=self.config.api_key or os.getenv("ANTHROPIC_API_KEY"),
            model=self.config.model,
            temperature=self.config.temperature,
            streaming=True,
            stream_usage=True
        )

    """
    def get_embeddings(self):
        from langchain_voyageai import VoyageAIEmbeddings
        return VoyageAIEmbeddings(
            api_key=self.config.embedding_api_key, #voyage api key
            model="voyage-3")
    """

    def get_models(self):
        import anthropic
        client = anthropic.Client(api_key=self.config.api_key or os.getenv("ANTHROPIC_API_KEY"))
        response = client.models.list()
        return response.data

class OpenAI(LlmInterface):
    def __init__(self, config: LlmConfig):
        super().__init__(config)
        self.config.embedding_api_key = self.config.api_key

    def get_llm(self):
        from langchain_openai import ChatOpenAI
        chat = ChatOpenAI(
            api_key=self.config.api_key or os.getenv("OPENAI_API_KEY"),
            model=self.config.model,
            stream_usage=True)
        if not (any(self.config.model.startswith(prefix) for prefix in ["o1", "o3"]) or "search" in self.config.model):
            chat.temperature = self.config.temperature
            chat.streaming = True
        return chat

    def get_models(self):
        import openai
        openai.api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        response = openai.models.list()
        return response.data

class DeepSeek(LlmInterface):
    def get_llm(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.config.api_key or os.getenv("DEEPSEEK_API_KEY"),
            model=self.config.model,
            base_url="https://api.deepseek.com",
            max_tokens=8192,
            temperature=self.config.temperature,
            streaming=True,
            stream_usage=True,
        )

    def get_models(self):
        import openai
        openai.api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY")
        openai.base_url = "https://api.deepseek.com"
        response = openai.models.list()
        return response.data

class Google(LlmInterface):
  def get_llm(self):
    from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
      name="chat",
      api_key=self.config.api_key or os.getenv("GOOGLE_API_KEY"),
      model=self.config.model,
      temperature=self.config.temperature,
      disable_streaming=False,
    )

  def get_embeddings(self):
    from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
      google_api_key=self.config.api_key,
      model="models/text-embedding-005")

  def get_models(self):
    import google.generativeai as genai
    genai.configure(api_key=self.config.api_key or os.getenv("GOOGLE_API_KEY"))
    response = genai.list_models()
    return [{
      "id": model.name,
      "name": model.display_name,
      "description": model.description,
      "input_token_limit": model.input_token_limit,
      "output_token_limit": model.output_token_limit
    } for model in response if "gemini" in model.name.lower()]

class Gvertex(LlmInterface):
    def get_llm(self):
        from langchain_google_vertexai  import ChatVertexAI
        return ChatVertexAI(
            model=self.config.model,
            temperature=self.config.temperature
        )
    def get_embeddings(self):
        from langchain_google_vertexai import VertexAIEmbeddings
        return VertexAIEmbeddings(model_name="text-embedding-005")
    def get_models(self):
        #from google.cloud import aiplatform
        #aiplatform.init()
        #models = aiplatform.Model.list()
        # removed due issue: https://github.com/langchain-ai/langchain-google/issues/733
        # Message type "google.cloud.aiplatform.v1beta1.GenerateContentResponse" has no field named "createTime" at "GenerateContentResponse".  Available Fields(except extensions): "['candidates', 'modelVersion', 'promptFeedback', 'usageMetadata']"

        #see https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations#united-states for available models
        return [
              {"id":"gemini-2.5-pro-preview-05-06"},
              {"id":"gemini-2.0-flash"},
              {"id":"gemini-2.0-flash-lite"},
              {"id":"gemini-1.5-pro-002"}
            ]

class Groq(LlmInterface):
    def get_llm(self):
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=self.config.api_key or os.getenv("GROQ_API_KEY"),
            model=self.config.model,
            #max_tokens=8192,
            temperature=self.config.temperature,
            streaming=True,
        )

    def get_models(self):
        import requests
        url = "https://api.groq.com/openai/v1/models"
        headers = {
            "Authorization": f"Bearer {self.config.api_key or os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.json().get("data", [])

class IBM(LlmInterface):
    def __init__(self, config: LlmConfig):
        super().__init__(config)
        self.__apy_key = self.config.api_key or os.getenv("WATSONX_APIKEY")
        self.__base_url = self.config.api_url or "https://us-south.ml.cloud.ibm.com"
    def get_llm(self):
        from langchain_ibm import ChatWatsonx
        return ChatWatsonx(
            model_id=self.config.model,
            url=self.__base_url,
            apikey=self.__apy_key
        )
    def get_models(self):
        import requests
        from datetime import date
        try:
          # https://cloud.ibm.com/apidocs/watsonx-ai#list-foundation-model-specs
          today = date.today().strftime("%Y-%m-%d")
          url = f"{self.__base_url}/ml/v1/foundation_model_specs?version={today}&filters=task_generation,task_summarization:and"
          headers = {
              "Authorization": f"Bearer {self.__apy_key}",
              "Content-Type": "application/json"
          }
          response = requests.get(url, headers=headers)
          models = response.json().get("resources", [])
          return [{
                "id": model['model_id'],
                "provider": model['provider'],
                "tasks": model['task_ids'],
                "limits": model.get('model_limits', {}),
              } for model in models if model['provider'].lower() in ['ibm','meta','mistral ai']]
        except Exception as e:
          print(f"Error fetching models from IBM WatsonX: {e}")
          # https://www.ibm.com/products/watsonx-ai/foundation-models
          return [
            {"id":"granite-3-3-8b-instruct"},
            {"id":"granite-vision-3-2-2b"},
            {"id":"granite-13b-instruct"},
            {"id":"llama-4-scout-17b-16e-instruct"},
            {"id":"llama-3-3-70b-instruct"},
            {"id":"mistral-medium-2505"},
            {"id":"mistral-small-3-1-24b-instruct-2503"},
            {"id":"mistral-large-2"}
          ]

    def get_embeddings(self):
        from langchain_ibm import WatsonxEmbeddings
        return WatsonxEmbeddings(
            model_id="ibm/granite-embedding-107m-multilingual", #https://www.ibm.com/products/watsonx-ai/foundation-models
            url=self.__base_url,
            apikey=self.__apy_key
        )

class Ollama(LlmInterface):
    def __init__(self, config: LlmConfig):
        super().__init__(config)
        self.__base_url = self.config.api_url or os.getenv("OLLAMA_API_URL") or "http://localhost:11434"
    def get_llm(self):
        from langchain_ollama.chat_models import ChatOllama
        return ChatOllama(
            model=self.config.model,
            base_url=self.__base_url,
            temperature=self.config.temperature,
            streaming=True,
        )
    def get_embeddings(self):
        from langchain_ollama.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(
            base_url=self.__base_url,
            model="nomic-embed-text" #mxbai-embed-large
        )
    def get_models(self):
        import requests
        url = f"{self.__base_url}/api/tags"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        models = response.json().get("models", [])
        return [{
              "id": model['model'],
              "modified_at": model['modified_at'],
              "size": model['size'],
              "details": model['details']
            } for model in models]

class LlmManager:

    #class variables (static)
    _list: dict[str,LlmInterface] = {
        "anthropic": Anthropic,
        "deepseek": DeepSeek,
        "google": Google,
        "gvertex": Gvertex,
        "groq": Groq,
        "ibm": IBM,
        "openai": OpenAI,
        "ollama": Ollama
    }
