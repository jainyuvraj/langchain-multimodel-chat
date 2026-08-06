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
        name="Groq Free (Llama 3 / Qwen 3.6 / GPT-OSS)",
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
                id="qwen/qwen3.6-27b",
                name="Qwen 3.6 27B",
                description="Alibaba Cloud's latest state-of-the-art open reasoning & code model.",
            ),
            ModelInfoSchema(
                id="openai/gpt-oss-120b",
                name="GPT-OSS 120B",
                description="High-capacity open-weights model by OpenAI.",
            ),
            ModelInfoSchema(
                id="llama-3.1-8b-instant",
                name="Llama 3.1 8B Instant",
                description="Ultra-fast compact model for instant responses.",
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


class SmartTavilySearchService:
    @staticmethod
    def should_trigger_web_search(query: str, user_preference: Optional[bool] = None) -> bool:
        """Determines if real-time web search is required based on user toggle or smart intent detection."""
        if user_preference is False:
            return False
        if user_preference is True:
            return True
        
        if not query or len(query.strip()) < 3:
            return False

        realtime_keywords = [
            "today", "latest", "now", "current", "news", "price", "stock",
            "who won", "match", "score", "weather", "release", "2026", "2025",
            "recent", "yesterday", "update", "version", "winner", "result", "trending"
        ]
        q_lower = query.lower()
        return any(kw in q_lower for kw in realtime_keywords)

    @classmethod
    def execute_search(cls, query: str) -> str:
        """Execute search via Tavily API and return formatted prompt context."""
        api_key = settings.TAVILY_API_KEY or os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return ""

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)
            results = client.search(query=query.strip(), max_results=3, search_depth="basic")
            
            if not results or "results" not in results:
                return ""

            snippets = []
            for idx, res in enumerate(results["results"][:3], 1):
                title = res.get("title", "Web Page")
                url = res.get("url", "")
                content = res.get("content", "")
                snippets.append(f"[{idx}] '{title}' ({url}):\n{content}")

            if snippets:
                return (
                    "\n\n🌐 [LIVE REAL-TIME WEB SEARCH RESULTS (via Tavily)]:\n"
                    + "\n\n".join(snippets)
                    + "\n(Use the above up-to-date web search results to answer the user accurately with live real-time information)."
                )
            return ""
        except Exception as e:
            print(f"[Tavily Search Warning]: {str(e)}")
            return ""


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
    def format_langchain_messages(
        cls, request: ChatRequestSchema, user_id: Optional[str] = None, chat_id: Optional[str] = None
    ) -> List[BaseMessage]:
        """
        Assemble hybrid context:
        1. Base System Prompt
        2. Top 5 Semantically Relevant Historical Messages from ChromaDB Vector Memory
        3. Last 5 Recent Short-Term Messages
        """
        lc_messages = []
        system_content = request.system_prompt or "You are a helpful, creative, and precise AI assistant."
        user_query = ""

        if request.messages:
            last_msg = request.messages[-1]
            if last_msg.role == "user":
                user_query = last_msg.content

        # 1. Real-Time Web Search Context (Tavily - Smart Intent Activated)
        web_search_context_str = ""
        if user_query and SmartTavilySearchService.should_trigger_web_search(user_query, request.enable_web_search):
            web_search_context_str = SmartTavilySearchService.execute_search(user_query)

        # 2. Vector Memory Retrieval (Top 5 Semantically Relevant Matches)
        vector_context_str = ""
        if user_id and user_query:
            from backend.vector_service import VectorMemoryService
            top_k_relevant = VectorMemoryService.get_top_k_relevant_context(
                user_id=user_id, 
                chat_id=chat_id, 
                query_text=user_query, 
                top_k=5, 
                enable_inter_chat=request.enable_inter_chat_memory
            )
            if top_k_relevant:
                context_blocks = [
                    f"- [From Thread '{item.get('title', 'Chat Thread')}'] [{item['role'].upper()}]: {item['content']}"
                    for item in top_k_relevant
                ]
                memory_type = "ALL USER THREADS" if request.enable_inter_chat_memory else "CURRENT THREAD ONLY"
                vector_context_str = (
                    f"\n\n📚 [VECTOR SEMANTIC MEMORY ({memory_type}) - Top 5 Relevant Past Turns]:\n"
                    + "\n".join(context_blocks)
                    + "\n(Use this vector context to recall relevant details if applicable)."
                )

        lc_messages.append(SystemMessage(content=system_content + web_search_context_str + vector_context_str))

        # 3. Short-Term Recent Messages (Last 5 Messages)
        # Exclude the very last user query if we append it separately, or include last 5 total
        recent_messages = request.messages[-5:] if len(request.messages) > 5 else request.messages

        for msg in recent_messages:
            role = msg.role.lower()
            content = msg.content
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            elif role == "system" and len(lc_messages) == 1:
                pass  # Avoid duplicate system message

        return lc_messages

    @classmethod
    async def stream_chat_tokens(
        cls, request: ChatRequestSchema, user_id: Optional[str] = None, chat_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Async generator streaming token deltas from LangChain chat models."""
        try:
            model = cls.get_chat_model(request)
            lc_messages = cls.format_langchain_messages(request, user_id=user_id, chat_id=chat_id)

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
