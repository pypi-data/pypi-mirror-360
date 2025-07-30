"""Service for handling LLM interactions."""

import asyncio
import importlib
import json
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import Any, Dict, List, Optional

import importlib_resources
import openai
import structlog
from jinja2 import Template

from rasa.builder import config
from rasa.builder.exceptions import LLMGenerationError
from rasa.builder.llm_context import tracker_as_llm_context
from rasa.builder.models import LLMBuilderContext
from rasa.constants import PACKAGE_NAME
from rasa.shared.constants import DOMAIN_SCHEMA_FILE, RESPONSES_SCHEMA_FILE
from rasa.shared.core.flows.yaml_flows_io import FLOWS_SCHEMA_FILE
from rasa.shared.utils.io import read_json_file
from rasa.shared.utils.yaml import read_schema_file

structlogger = structlog.get_logger()


class LLMService:
    """Handles OpenAI LLM interactions with caching for efficiency."""

    def __init__(self):
        self._client: Optional[openai.AsyncOpenAI] = None
        self._domain_schema: Optional[Dict[str, Any]] = None
        self._flows_schema: Optional[Dict[str, Any]] = None
        self._helper_schema: Optional[Dict[str, Any]] = None

    @asynccontextmanager
    async def _get_client(self):
        """Get or create OpenAI client with proper resource management."""
        if self._client is None:
            self._client = openai.AsyncOpenAI(timeout=config.OPENAI_TIMEOUT)

        try:
            yield self._client
        except Exception as e:
            structlogger.error("llm.client_error", error=str(e))
            raise

    def _prepare_schemas(self):
        """Prepare and cache schemas for LLM generation."""
        if self._domain_schema is None:
            self._domain_schema = _prepare_domain_schema()

        if self._flows_schema is None:
            self._flows_schema = _prepare_flows_schema()

        if self._helper_schema is None:
            self._helper_schema = _load_helper_schema()

    async def generate_rasa_project(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate Rasa project data using OpenAI."""
        self._prepare_schemas()

        try:
            async with self._get_client() as client:
                response = await client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    temperature=config.OPENAI_TEMPERATURE,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "rasa_project",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "domain": self._domain_schema,
                                    "flows": self._flows_schema,
                                },
                                "required": ["domain", "flows"],
                            },
                        },
                    },
                )

                content = response.choices[0].message.content
                if not content:
                    raise LLMGenerationError("Empty response from LLM")

                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    raise LLMGenerationError(f"Invalid JSON from LLM: {e}")

        except openai.OpenAIError as e:
            raise LLMGenerationError(f"OpenAI API error: {e}")
        except asyncio.TimeoutError:
            raise LLMGenerationError("LLM request timed out")

    async def create_helper_messages(
        self, llm_builder_context: LLMBuilderContext
    ) -> List[Dict[str, Any]]:
        """Create helper messages for LLM builder."""
        # Format chat history for documentation search
        chat_dump = self._format_chat_dump(llm_builder_context.chat_history)

        # Search documentation
        documentation_results = await self.search_documentation(chat_dump)
        formatted_docs = self._format_documentation_results(documentation_results)

        current_conversation = tracker_as_llm_context(llm_builder_context.tracker)

        # Prepare LLM messages
        system_messages = get_helper_messages(
            current_conversation,
            llm_builder_context.bot_logs,
            llm_builder_context.chat_bot_files,
            formatted_docs,
        )

        # Add user messages
        messages = system_messages.copy()
        for msg in llm_builder_context.chat_history:
            messages.append(
                {
                    "role": "user" if msg.type == "user" else "assistant",
                    "content": json.dumps(msg.content)
                    if isinstance(msg.content, list)
                    else msg.content,
                }
            )
        return messages

    async def generate_helper_response(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate helper response using OpenAI."""
        self._prepare_schemas()

        try:
            async with self._get_client() as client:
                response = await client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "llm_helper",
                            "schema": self._helper_schema,
                        },
                    },
                )

                content = response.choices[0].message.content
                if not content:
                    raise LLMGenerationError("Empty response from LLM helper")

                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    raise LLMGenerationError(f"Invalid JSON from LLM helper: {e}")

        except openai.OpenAIError as e:
            raise LLMGenerationError(f"OpenAI API error in helper: {e}")
        except asyncio.TimeoutError:
            raise LLMGenerationError("LLM helper request timed out")

    async def search_documentation(
        self, query: str, max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search documentation using OpenAI vector store."""
        if max_results is None:
            max_results = config.OPENAI_MAX_VECTOR_RESULTS

        try:
            async with self._get_client() as client:
                results = await client.vector_stores.search(
                    vector_store_id=config.OPENAI_VECTOR_STORE_ID,
                    query=query,
                    max_num_results=max_results,
                    rewrite_query=True,
                )

                return results.data

        except openai.OpenAIError as e:
            structlogger.warning(
                "llm.documentation_search_failed", error=str(e), query=query
            )
            return []

    @staticmethod
    def _format_chat_dump(messages) -> str:
        """Format chat messages for documentation search."""
        result = ""
        for message in messages:
            if message.type == "user":
                content = (
                    message.content
                    if isinstance(message.content, str)
                    else str(message.content)
                )
                result += f"User: {content}\n"
            else:
                if isinstance(message.content, list):
                    for part in message.content:
                        if part.get("type") == "text":
                            result += f"Assistant: {part.get('text')}\n"
                else:
                    result += f"Assistant: {message.content}\n"
        return result

    @staticmethod
    def _format_documentation_results(results) -> str:
        """Format documentation search results."""
        if not results:
            return "<sources>No relevant documentation found.</sources>"

        formatted_results = ""
        for result in results:
            formatted_result = f"<result url='{result.attributes.get('url', '')}'>"
            for part in result.content:
                formatted_result += f"<content>{part.text}</content>"
            formatted_results += formatted_result + "</result>"

        return f"<sources>{formatted_results}</sources>"


# Schema preparation functions (stateless)
def _prepare_domain_schema() -> Dict[str, Any]:
    """Prepare domain schema by removing unnecessary parts."""
    domain_schema = deepcopy(read_schema_file(DOMAIN_SCHEMA_FILE, PACKAGE_NAME, False))

    # Remove parts not needed for CALM bots
    unnecessary_keys = ["intents", "entities", "forms", "config", "session_config"]

    for key in unnecessary_keys:
        domain_schema["mapping"].pop(key, None)

    # Remove problematic slot mappings
    slot_mapping = domain_schema["mapping"]["slots"]["mapping"]["regex;([A-Za-z]+)"][
        "mapping"
    ]
    slot_mapping.pop("mappings", None)
    slot_mapping.pop("validation", None)

    # Add responses schema
    domain_schema["mapping"]["responses"] = read_schema_file(
        RESPONSES_SCHEMA_FILE, PACKAGE_NAME, False
    )["schema;responses"]

    return domain_schema


def _prepare_flows_schema() -> Dict[str, Any]:
    """Prepare flows schema by removing nlu_trigger."""
    schema_file = str(
        importlib_resources.files(PACKAGE_NAME).joinpath(FLOWS_SCHEMA_FILE)
    )
    flows_schema = deepcopy(read_json_file(schema_file))
    flows_schema["$defs"]["flow"]["properties"].pop("nlu_trigger", None)
    return flows_schema


def _load_helper_schema() -> Dict[str, Any]:
    """Load helper schema."""
    return read_json_file(
        importlib_resources.files(PACKAGE_NAME).joinpath(
            "builder/llm-helper-schema.json"
        )
    )


# Template functions (stateless with caching)
_skill_template: Optional[Template] = None
_helper_template: Optional[Template] = None


def get_skill_generation_messages(
    skill_description: str, project_data: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Get messages for skill generation."""
    global _skill_template

    if _skill_template is None:
        template_content = importlib.resources.read_text(
            "rasa.builder",
            "skill_to_bot_prompt.jinja2",
        )
        _skill_template = Template(template_content)

    system_prompt = _skill_template.render(
        skill_description=skill_description,
        project_data=project_data,
    )
    return [{"role": "system", "content": system_prompt}]


def get_helper_messages(
    current_conversation: str,
    bot_logs: str,
    chat_bot_files: Dict[str, str],
    documentation_results: str,
) -> List[Dict[str, Any]]:
    """Get messages for helper response."""
    global _helper_template

    if _helper_template is None:
        template_content = importlib.resources.read_text(
            "rasa.builder",
            "llm_helper_prompt.jinja2",
        )
        _helper_template = Template(template_content)

    system_prompt = _helper_template.render(
        current_conversation=current_conversation,
        bot_logs=bot_logs,
        chat_bot_files=chat_bot_files,
        documentation_results=documentation_results,
    )
    return [{"role": "system", "content": system_prompt}]


# Global service instance
llm_service = LLMService()
