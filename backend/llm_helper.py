import os
from typing import AsyncGenerator, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from backend.config import settings
from backend.schemas import ChatRequestSchema, ProviderModelsSchema, ModelInfoSchema

# Import LangChain provider integrations safely
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None


AVAILABLE_PROVIDERS: List[ProviderModelsSchema] = [
    ProviderModelsSchema(
        id="google",
        name="Google Gemini",
        icon="Sparkles",
        requires_key=True,
        models=[
            ModelInfoSchema(
                id="gemini-flash-latest",
                name="Gemini Flash (Latest)",
                description="Fastest, ultra-responsive model optimized for real-time chat.",
                recommended=True,
            ),
            ModelInfoSchema(
                id="gemini-2.5-flash",
                name="Gemini 2.5 Flash",
                description="High-performance next-gen flash model.",
            ),
            ModelInfoSchema(
                id="gemini-3.6-flash",
                name="Gemini 3.6 Flash",
                description="State-of-the-art fast reasoning model.",
            ),
            ModelInfoSchema(
                id="gemini-pro-latest",
                name="Gemini Pro (Latest)",
                description="Advanced flagship model for complex tasks and analysis.",
            ),
        ],
    ),
    ProviderModelsSchema(
        id="groq",
        name="Groq Free (Llama 3 / DeepSeek / Qwen / Mixtral)",
        icon="Zap",
        requires_key=True,
        models=[
            ModelInfoSchema(
                id="llama-3.3-70b-versatile",
                name="Llama 3.3 70B",
                description="Meta's flagship 70B open-weights model with ultra-fast inference.",
                recommended=True,
            ),
            ModelInfoSchema(
                id="deepseek-r1-distill-llama-70b",
                name="DeepSeek R1 (70B)",
                description="State-of-the-art reasoning & logic model distilled by DeepSeek.",
            ),
            ModelInfoSchema(
                id="qwen-2.5-32b",
                name="Qwen 2.5 32B",
                description="Alibaba Cloud's highly capable coding & math open model.",
            ),
            ModelInfoSchema(
                id="mixtral-8x7b-32768",
                name="Mixtral 8x7B",
                description="Mistral AI's high-efficiency Mixture-of-Experts architecture.",
            ),
        ],
    ),
    ProviderModelsSchema(
        id="openai",
        name="OpenAI",
        icon="Bot",
        requires_key=True,
        models=[
            ModelInfoSchema(
                id="gpt-4o",
                name="GPT-4o",
                description="Flagship high-intelligence model for multi-step reasoning.",
                recommended=True,
            ),
            ModelInfoSchema(
                id="gpt-4o-mini",
                name="GPT-4o Mini",
                description="Affordable, fast small model for lightweight tasks.",
            ),
            ModelInfoSchema(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="Legacy fast model for standard chat completions.",
            ),
        ],
    ),
    ProviderModelsSchema(
        id="anthropic",
        name="Anthropic Claude",
        icon="Brain",
        requires_key=True,
        models=[
            ModelInfoSchema(
                id="claude-3-5-sonnet-20240620",
                name="Claude 3.5 Sonnet",
                description="State-of-the-art intelligence for code, writing, and analysis.",
                recommended=True,
            ),
            ModelInfoSchema(
                id="claude-3-haiku-20240307",
                name="Claude 3 Haiku",
                description="Fastest, most compact model for instant responses.",
            ),
        ],
    ),
]


class LLMService:
    """Modular LLM Manager encapsulating LangChain provider integrations."""

    @staticmethod
    def resolve_api_key(provider: str, req_keys: Optional[Any] = None) -> str:
        """Resolve system API key from backend environment configuration (.env)."""
        key = None
        
        # Check server environment variables & config
        if provider == "google":
            key = settings.GOOGLE_API_KEY or os.environ.get("GOOGLE_API_KEY")
        elif provider == "openai":
            key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
        elif provider == "anthropic":
            key = settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY")
        elif provider == "groq":
            key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")

        # Fallback check client payload if provided
        if not key and req_keys:
            if provider == "google":
                key = getattr(req_keys, "google", None)
            elif provider == "openai":
                key = getattr(req_keys, "openai", None)
            elif provider == "anthropic":
                key = getattr(req_keys, "anthropic", None)
            elif provider == "groq":
                key = getattr(req_keys, "groq", None)

        if not key or not key.strip() or key.startswith("your_"):
            raise ValueError(
                f"Server configuration error: Missing API Key for '{provider}'. "
                f"Please set {provider.upper()}_API_KEY in the server's .env file."
            )
        return key.strip()

    @classmethod
    def get_chat_model(cls, request: ChatRequestSchema):
        """Instantiate the appropriate LangChain Chat Model."""
        provider = request.provider.lower()
        model_name = request.model
        temp = request.temperature
        max_tokens = request.max_tokens or 2048
        api_key = cls.resolve_api_key(provider, request.api_keys)

        if provider == "google":
            if ChatGoogleGenerativeAI is None:
                raise RuntimeError("langchain-google-genai package is not installed.")
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temp,
                max_output_tokens=max_tokens,
            )

        elif provider == "groq":
            if ChatGroq is None:
                raise RuntimeError("langchain-groq package is not installed.")
            return ChatGroq(
                model_name=model_name,
                groq_api_key=api_key,
                temperature=temp,
                max_tokens=max_tokens,
            )

        elif provider == "openai":
            if ChatOpenAI is None:
                raise RuntimeError("langchain-openai package is not installed.")
            return ChatOpenAI(
                model=model_name,
                api_key=api_key,
                temperature=temp,
                max_tokens=max_tokens,
                streaming=True,
            )

        elif provider == "anthropic":
            if ChatAnthropic is None:
                raise RuntimeError("langchain-anthropic package is not installed.")
            return ChatAnthropic(
                model_name=model_name,
                api_key=api_key,
                temperature=temp,
                max_tokens=max_tokens,
                streaming=True,
            )

        else:
            raise ValueError(f"Unsupported LLM provider: '{provider}'")

    @classmethod
    def format_langchain_messages(cls, request: ChatRequestSchema) -> List[BaseMessage]:
        """Convert payload messages into LangChain message primitives."""
        lc_messages: List[BaseMessage] = []

        if request.system_prompt and request.system_prompt.strip():
            lc_messages.append(SystemMessage(content=request.system_prompt.strip()))

        for msg in request.messages:
            role = msg.role.lower()
            content = msg.content
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            elif role == "system" and not lc_messages:
                lc_messages.append(SystemMessage(content=content))

        return lc_messages

    @classmethod
    async def stream_chat_tokens(cls, request: ChatRequestSchema) -> AsyncGenerator[str, None]:
        """Async generator streaming token deltas from LangChain chat models."""
        try:
            model = cls.get_chat_model(request)
            lc_messages = cls.format_langchain_messages(request)

            async for chunk in model.astream(lc_messages):
                content = getattr(chunk, "content", "")
                
                # Safely extract text string from chunk content
                text = ""
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    parts = []
                    for item in content:
                        if isinstance(item, str):
                            parts.append(item)
                        elif isinstance(item, dict):
                            if "text" in item:
                                parts.append(str(item["text"]))
                            elif "content" in item:
                                parts.append(str(item["content"]))
                        else:
                            parts.append(str(item))
                    text = "".join(parts)
                elif isinstance(content, dict):
                    text = str(content.get("text", ""))
                elif content is not None:
                    text = str(content)

                if text:
                    yield text

        except Exception as e:
            # Clean readable error output streamed back to UI
            error_msg = f"[ERROR]: {str(e)}"
            yield error_msg
