import dataclasses
import importlib.resources
import json
import re
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Text

import dotenv
import structlog
from jinja2 import Template
from pydantic import ValidationError

import rasa.shared.utils.io
from rasa.core.available_endpoints import AvailableEndpoints
from rasa.core.constants import (
    POLICY_MAX_HISTORY,
    POLICY_PRIORITY,
    SEARCH_POLICY_PRIORITY,
    UTTER_SOURCE_METADATA_KEY,
)
from rasa.core.information_retrieval import (
    InformationRetrieval,
    InformationRetrievalException,
    SearchResult,
    create_from_endpoint_config,
)
from rasa.core.information_retrieval.faiss import FAISS_Store
from rasa.core.policies.policy import Policy, PolicyPrediction
from rasa.dialogue_understanding.generator.constants import (
    LLM_CONFIG_KEY,
)
from rasa.dialogue_understanding.patterns.cannot_handle import (
    CannotHandlePatternFlowStackFrame,
)
from rasa.dialogue_understanding.patterns.internal_error import (
    InternalErrorPatternFlowStackFrame,
)
from rasa.dialogue_understanding.stack.frames import (
    DialogueStackFrame,
    PatternFlowStackFrame,
    SearchStackFrame,
)
from rasa.engine.graph import ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.graph_components.providers.forms_provider import Forms
from rasa.graph_components.providers.responses_provider import Responses
from rasa.shared.constants import (
    EMBEDDINGS_CONFIG_KEY,
    MAX_COMPLETION_TOKENS_CONFIG_KEY,
    MAX_RETRIES_CONFIG_KEY,
    MODEL_CONFIG_KEY,
    MODEL_GROUP_ID_CONFIG_KEY,
    MODEL_NAME_CONFIG_KEY,
    OPENAI_PROVIDER,
    PROMPT_CONFIG_KEY,
    PROMPT_TEMPLATE_CONFIG_KEY,
    PROVIDER_CONFIG_KEY,
    RASA_PATTERN_CANNOT_HANDLE_NO_RELEVANT_ANSWER,
    TEMPERATURE_CONFIG_KEY,
    TIMEOUT_CONFIG_KEY,
)
from rasa.shared.core.constants import (
    ACTION_CANCEL_FLOW,
    ACTION_SEND_TEXT_NAME,
    DEFAULT_SLOT_NAMES,
)
from rasa.shared.core.domain import Domain
from rasa.shared.core.events import BotUttered, Event, UserUttered
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.shared.core.trackers import DialogueStateTracker, EventVerbosity
from rasa.shared.exceptions import FileIOException, RasaException
from rasa.shared.nlu.constants import (
    KEY_COMPONENT_NAME,
    KEY_LLM_RESPONSE_METADATA,
    KEY_PROMPT_NAME,
    KEY_USER_PROMPT,
    PROMPTS,
)
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.providers.embedding._langchain_embedding_client_adapter import (
    _LangchainEmbeddingClientAdapter,
)
from rasa.shared.providers.llm.llm_response import LLMResponse, measure_llm_latency
from rasa.shared.utils.cli import print_error_and_exit
from rasa.shared.utils.constants import (
    LOG_COMPONENT_SOURCE_METHOD_FINGERPRINT_ADDON,
    LOG_COMPONENT_SOURCE_METHOD_INIT,
)
from rasa.shared.utils.health_check.embeddings_health_check_mixin import (
    EmbeddingsHealthCheckMixin,
)
from rasa.shared.utils.health_check.llm_health_check_mixin import LLMHealthCheckMixin
from rasa.shared.utils.io import deep_container_fingerprint
from rasa.shared.utils.llm import (
    DEFAULT_OPENAI_CHAT_MODEL_NAME,
    DEFAULT_OPENAI_EMBEDDING_MODEL_NAME,
    check_prompt_config_keys_and_warn_if_deprecated,
    embedder_factory,
    get_prompt_template,
    llm_factory,
    resolve_model_client_config,
    sanitize_message_for_prompt,
    tracker_as_readable_transcript,
)
from rasa.telemetry import (
    track_enterprise_search_policy_predict,
    track_enterprise_search_policy_train_completed,
    track_enterprise_search_policy_train_started,
)

if TYPE_CHECKING:
    from langchain.schema.embeddings import Embeddings

    from rasa.core.featurizers.tracker_featurizers import TrackerFeaturizer

from rasa.utils.log_utils import log_llm

structlogger = structlog.get_logger()

dotenv.load_dotenv("./.env")

SOURCE_PROPERTY = "source"
VECTOR_STORE_TYPE_PROPERTY = "type"
VECTOR_STORE_PROPERTY = "vector_store"
VECTOR_STORE_THRESHOLD_PROPERTY = "threshold"
TRACE_TOKENS_PROPERTY = "trace_prompt_tokens"
CITATION_ENABLED_PROPERTY = "citation_enabled"
USE_LLM_PROPERTY = "use_generative_llm"
CHECK_RELEVANCY_PROPERTY = "check_relevancy"
MAX_MESSAGES_IN_QUERY_KEY = "max_messages_in_query"

DEFAULT_VECTOR_STORE_TYPE = "faiss"
DEFAULT_VECTOR_STORE_THRESHOLD = 0.0
DEFAULT_VECTOR_STORE = {
    VECTOR_STORE_TYPE_PROPERTY: DEFAULT_VECTOR_STORE_TYPE,
    SOURCE_PROPERTY: "./docs",
    VECTOR_STORE_THRESHOLD_PROPERTY: DEFAULT_VECTOR_STORE_THRESHOLD,
}

DEFAULT_CHECK_RELEVANCY_PROPERTY = False
DEFAULT_USE_LLM_PROPERTY = True
DEFAULT_CITATION_ENABLED_PROPERTY = False

DEFAULT_LLM_CONFIG = {
    PROVIDER_CONFIG_KEY: OPENAI_PROVIDER,
    MODEL_CONFIG_KEY: DEFAULT_OPENAI_CHAT_MODEL_NAME,
    TIMEOUT_CONFIG_KEY: 10,
    TEMPERATURE_CONFIG_KEY: 0.0,
    MAX_COMPLETION_TOKENS_CONFIG_KEY: 256,
    MAX_RETRIES_CONFIG_KEY: 1,
}

DEFAULT_EMBEDDINGS_CONFIG = {
    PROVIDER_CONFIG_KEY: OPENAI_PROVIDER,
    MODEL_CONFIG_KEY: DEFAULT_OPENAI_EMBEDDING_MODEL_NAME,
}

ENTERPRISE_SEARCH_PROMPT_FILE_NAME = "enterprise_search_policy_prompt.jinja2"
ENTERPRISE_SEARCH_CONFIG_FILE_NAME = "config.json"

SEARCH_RESULTS_METADATA_KEY = "search_results"
SEARCH_QUERY_METADATA_KEY = "search_query"

DEFAULT_ENTERPRISE_SEARCH_PROMPT_TEMPLATE = importlib.resources.read_text(
    "rasa.core.policies", "enterprise_search_prompt_template.jinja2"
)

DEFAULT_ENTERPRISE_SEARCH_PROMPT_WITH_CITATION_TEMPLATE = importlib.resources.read_text(
    "rasa.core.policies", "enterprise_search_prompt_with_citation_template.jinja2"
)

DEFAULT_ENTERPRISE_SEARCH_PROMPT_WITH_RELEVANCY_CHECK_AND_CITATION_TEMPLATE = (
    importlib.resources.read_text(
        "rasa.core.policies",
        "enterprise_search_prompt_with_relevancy_check_and_citation_template.jinja2",
    )
)

# TODO: Update this pattern once the experiments are done
_ENTERPRISE_SEARCH_ANSWER_NOT_RELEVANT_PATTERN = re.compile(
    r"\[NO_RELEVANT_ANSWER_FOUND\]"
)


class VectorStoreConnectionError(RasaException):
    """Exception raised for errors in connecting to the vector store."""


class VectorStoreConfigurationError(RasaException):
    """Exception raised for errors in vector store configuration."""


@dataclasses.dataclass
class _RelevancyCheckResponse:
    answer: Optional[str]
    relevant: bool


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.POLICY_WITH_END_TO_END_SUPPORT, is_trainable=True
)
class EnterpriseSearchPolicy(LLMHealthCheckMixin, EmbeddingsHealthCheckMixin, Policy):
    """Policy which uses a vector store and LLMs to respond to user messages.

    The policy uses a vector store and LLMs to respond to user messages. The
    vector store is used to retrieve the most relevant responses to the user
    message. The LLMs are used to rank the responses and select the best
    response. The policy can be used to respond to user messages without
    training data.

    Example Configuration:

        policies:
            # - ...
            - name: EnterpriseSearchPolicy
              vector_store:
                type: "milvus"
                <vector_store_config>
            # - ...
    """

    @staticmethod
    def does_support_stack_frame(frame: DialogueStackFrame) -> bool:
        """Checks if the policy supports the given stack frame."""
        return isinstance(frame, SearchStackFrame)

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Returns the default config of the policy."""
        return {
            POLICY_PRIORITY: SEARCH_POLICY_PRIORITY,
            VECTOR_STORE_PROPERTY: DEFAULT_VECTOR_STORE,
        }

    def __init__(
        self,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        vector_store: Optional[InformationRetrieval] = None,
        featurizer: Optional["TrackerFeaturizer"] = None,
        prompt_template: Optional[Text] = None,
    ) -> None:
        """Constructs a new Policy object."""
        super().__init__(config, model_storage, resource, execution_context, featurizer)

        # Check for deprecated keys and issue a warning if those are used
        check_prompt_config_keys_and_warn_if_deprecated(
            config, "enterprise_search_policy"
        )
        # Check for mutual exclusivity of extractive and generative search
        self._check_and_warn_mutual_exclusivity_of_extractive_and_generative_search()

        # Resolve LLM config
        self.config[LLM_CONFIG_KEY] = resolve_model_client_config(
            self.config.get(LLM_CONFIG_KEY), EnterpriseSearchPolicy.__name__
        )
        # Resolve embeddings config
        self.config[EMBEDDINGS_CONFIG_KEY] = resolve_model_client_config(
            self.config.get(EMBEDDINGS_CONFIG_KEY), EnterpriseSearchPolicy.__name__
        )

        # Vector store object and configuration
        self.vector_store = vector_store
        self.vector_store_config = self.config.get(
            VECTOR_STORE_PROPERTY, DEFAULT_VECTOR_STORE
        )
        self.vector_search_threshold = self.vector_store_config.get(
            VECTOR_STORE_THRESHOLD_PROPERTY, DEFAULT_VECTOR_STORE_THRESHOLD
        )

        # Embeddings configuration for encoding the search query
        self.embeddings_config = (
            self.config[EMBEDDINGS_CONFIG_KEY] or DEFAULT_EMBEDDINGS_CONFIG
        )

        # LLM Configuration for response generation
        self.llm_config = self.config[LLM_CONFIG_KEY] or DEFAULT_LLM_CONFIG

        # Maximum number of turns to include in the prompt
        self.max_history = self.config.get(POLICY_MAX_HISTORY)

        # Maximum number of messages to include in the search query
        self.max_messages_in_query = self.config.get(MAX_MESSAGES_IN_QUERY_KEY, 2)

        # Boolean to enable/disable tracing of prompt tokens
        self.trace_prompt_tokens = self.config.get(TRACE_TOKENS_PROPERTY, False)

        # Boolean to enable/disable the use of LLM for response generation
        self.use_llm = self.config.get(USE_LLM_PROPERTY, DEFAULT_USE_LLM_PROPERTY)

        # Boolean to enable/disable citation generation. This flag enables citation
        # logic, but it only takes effect if `use_llm` is True.
        self.citation_enabled = self.config.get(
            CITATION_ENABLED_PROPERTY, DEFAULT_CITATION_ENABLED_PROPERTY
        )

        # Boolean to enable/disable the use of relevancy check alongside answer
        # generation. This flag enables citation logic, but it only takes effect if
        # `use_llm` is True.
        self.relevancy_check_enabled = self.config.get(
            CHECK_RELEVANCY_PROPERTY, DEFAULT_CHECK_RELEVANCY_PROPERTY
        )

        # Resolve the prompt template. The prompt will only be used if the 'use_llm' is
        # set to True.
        self.prompt_template = prompt_template or self._resolve_prompt_template(
            self.config, LOG_COMPONENT_SOURCE_METHOD_INIT
        )

    def _check_and_warn_mutual_exclusivity_of_extractive_and_generative_search(
        self,
    ) -> None:
        if self.config.get(
            CHECK_RELEVANCY_PROPERTY, DEFAULT_CHECK_RELEVANCY_PROPERTY
        ) and not self.config.get(USE_LLM_PROPERTY, DEFAULT_USE_LLM_PROPERTY):
            structlogger.warning(
                "enterprise_search_policy.init"
                ".relevancy_check_enabled_with_disabled_generative_search",
                event_info=(
                    f"The config parameter '{CHECK_RELEVANCY_PROPERTY}' is set to"
                    f"'True', but the generative search is disabled (config"
                    f"parameter '{USE_LLM_PROPERTY}' is set to 'False'). As a result, "
                    "the relevancy check for the generative search will be disabled. "
                    f"To use this check, set the config parameter '{USE_LLM_PROPERTY}' "
                    f"to `True`."
                ),
            )

    @classmethod
    def _create_plain_embedder(cls, config: Dict[Text, Any]) -> "Embeddings":
        """Creates an embedder based on the given configuration.

        Returns:
        The embedder.
        """
        # Copy the config so original config is not modified
        config = config.copy()
        # Resolve config and instantiate the embedding client
        config[EMBEDDINGS_CONFIG_KEY] = resolve_model_client_config(
            config.get(EMBEDDINGS_CONFIG_KEY), EnterpriseSearchPolicy.__name__
        )
        client = embedder_factory(
            config.get(EMBEDDINGS_CONFIG_KEY), DEFAULT_EMBEDDINGS_CONFIG
        )
        # Wrap the embedding client in the adapter
        return _LangchainEmbeddingClientAdapter(client)

    @classmethod
    def _add_prompt_and_llm_response_to_latest_message(
        cls,
        tracker: DialogueStateTracker,
        prompt_name: str,
        user_prompt: str,
        llm_response: Optional[LLMResponse] = None,
    ) -> None:
        """Stores the prompt and LLMResponse metadata in the tracker.

        Args:
            tracker: The DialogueStateTracker containing the current conversation state.
            prompt_name: A name identifying prompt usage.
            user_prompt: The user prompt that was sent to the LLM.
            llm_response: The response object from the LLM (None if no response).
        """
        from rasa.dialogue_understanding.utils import record_commands_and_prompts

        if not record_commands_and_prompts:
            return

        if not tracker.latest_message:
            return

        parse_data = tracker.latest_message.parse_data
        if PROMPTS not in parse_data:
            parse_data[PROMPTS] = []  # type: ignore[literal-required]

        prompt_data: Dict[Text, Any] = {
            KEY_COMPONENT_NAME: cls.__name__,
            KEY_PROMPT_NAME: prompt_name,
            KEY_USER_PROMPT: user_prompt,
            KEY_LLM_RESPONSE_METADATA: llm_response.to_dict() if llm_response else None,
        }

        parse_data[PROMPTS].append(prompt_data)  # type: ignore[literal-required]

    def train(  # type: ignore[override]
        self,
        training_trackers: List[TrackerWithCachedStates],
        domain: Domain,
        responses: Responses,
        forms: Forms,
        training_data: TrainingData,
        **kwargs: Any,
    ) -> Resource:
        """Trains a policy.

        Args:
            training_trackers: The story and rules trackers from the training data.
            domain: The model's domain.
            responses: The model's responses.
            forms: The model's forms.
            training_data: The model's training data.
            **kwargs: Depending on the specified `needs` section and the resulting
                graph structure the policy can use different input to train itself.

        Returns:
            A policy must return its resource locator so that potential children nodes
            can load the policy from the resource.
        """
        # Perform health checks for both LLM and embeddings client configs
        self._perform_health_checks(self.config, "enterprise_search_policy.train")

        store_type = self.vector_store_config.get(VECTOR_STORE_TYPE_PROPERTY)

        # telemetry call to track training start
        track_enterprise_search_policy_train_started()

        # validate embedding configuration
        try:
            embeddings = self._create_plain_embedder(self.config)
        except (ValidationError, Exception) as e:
            structlogger.error(
                "enterprise_search_policy.train.embedder_instantiation_failed",
                message="Unable to instantiate the embedding client.",
                error=e,
            )
            print_error_and_exit(
                "Unable to create embedder. Please make sure you specified the "
                f"required environment variables. Error: {e}"
            )

        if store_type == DEFAULT_VECTOR_STORE_TYPE:
            structlogger.info("enterprise_search_policy.train.faiss")
            with self._model_storage.write_to(self._resource) as path:
                self.vector_store = FAISS_Store(
                    docs_folder=self.vector_store_config.get(SOURCE_PROPERTY),
                    embeddings=embeddings,
                    index_path=path,
                    create_index=True,
                    parse_as_faq_pairs=not self.use_llm,
                )
        else:
            structlogger.info(
                "enterprise_search_policy.train.custom", store_type=store_type
            )

        # telemetry call to track training completion
        track_enterprise_search_policy_train_completed(
            vector_store_type=store_type,
            embeddings_type=self.embeddings_config.get(PROVIDER_CONFIG_KEY),
            embeddings_model=self.embeddings_config.get(MODEL_CONFIG_KEY)
            or self.embeddings_config.get(MODEL_NAME_CONFIG_KEY),
            embeddings_model_group_id=self.embeddings_config.get(
                MODEL_GROUP_ID_CONFIG_KEY
            ),
            llm_type=self.llm_config.get(PROVIDER_CONFIG_KEY),
            llm_model=self.llm_config.get(MODEL_CONFIG_KEY)
            or self.llm_config.get(MODEL_NAME_CONFIG_KEY),
            llm_model_group_id=self.llm_config.get(MODEL_GROUP_ID_CONFIG_KEY),
            citation_enabled=self.citation_enabled,
            relevancy_check_enabled=self.relevancy_check_enabled,
        )
        self.persist()
        return self._resource

    def persist(self) -> None:
        """Persists the policy to storage."""
        with self._model_storage.write_to(self._resource) as path:
            rasa.shared.utils.io.write_text_file(
                self.prompt_template, path / ENTERPRISE_SEARCH_PROMPT_FILE_NAME
            )
            rasa.shared.utils.io.dump_obj_as_json_to_file(
                path / ENTERPRISE_SEARCH_CONFIG_FILE_NAME, self.config
            )

    def _prepare_slots_for_template(
        self, tracker: DialogueStateTracker
    ) -> List[Dict[str, str]]:
        """Prepares the slots for the template.

        Args:
            tracker: The tracker containing the conversation history up to now.

        Returns:
            The non-empty slots.
        """
        template_slots = []
        for name, slot in tracker.slots.items():
            if name not in DEFAULT_SLOT_NAMES and slot.value is not None:
                template_slots.append(
                    {
                        "name": name,
                        "value": str(slot.value),
                        "type": slot.type_name,
                    }
                )
        return template_slots

    def _connect_vector_store_or_raise(
        self, endpoints: Optional[AvailableEndpoints]
    ) -> None:
        """Connects to the vector store or raises an exception.

        Raise exceptions for the following cases:
        - The configuration is not specified
        - Unable to connect to the vector store

        Args:
            endpoints: Endpoints configuration.
        """
        config = endpoints.vector_store if endpoints else None
        store_type = self.vector_store_config.get(VECTOR_STORE_TYPE_PROPERTY)
        if config is None and store_type != DEFAULT_VECTOR_STORE_TYPE:
            structlogger.error(
                "enterprise_search_policy._connect_vector_store_or_raise.no_config"
            )
            raise VectorStoreConfigurationError(
                """No vector store specified. Please specify a vector
                store in the endpoints configuration"""
            )
        try:
            self.vector_store.connect(config)  # type: ignore
        except Exception as e:
            structlogger.error(
                "enterprise_search_policy._connect_vector_store_or_raise.connect_error",
                error=e,
                config=config,
            )
            raise VectorStoreConnectionError(
                f"Unable to connect to the vector store. Error: {e}"
            )

    def _prepare_search_query(self, tracker: DialogueStateTracker, history: int) -> str:
        """Prepares the search query.
        The search query is the last N messages in the conversation history.

        Args:
            tracker: The tracker containing the conversation history up to now.
            history: The number of messages to include in the search query.

        Returns:
            The search query.
        """
        transcript = []
        for event in tracker.applied_events():
            if isinstance(event, UserUttered) or isinstance(event, BotUttered):
                transcript.append(sanitize_message_for_prompt(event.text))

        search_query = " ".join(transcript[-history:][::-1])
        structlogger.debug("search_query", search_query=search_query)
        return search_query

    async def predict_action_probabilities(  # type: ignore[override]
        self,
        tracker: DialogueStateTracker,
        domain: Domain,
        endpoints: Optional[AvailableEndpoints] = None,
        rule_only_data: Optional[Dict[Text, Any]] = None,
        **kwargs: Any,
    ) -> PolicyPrediction:
        """Predicts the next action the bot should take after seeing the tracker.

        Args:
            tracker: The tracker containing the conversation history up to now.
            domain: The model's domain.
            endpoints: The model's endpoints.
            rule_only_data: Slots and loops which are specific to rules and hence
                should be ignored by this policy.
            **kwargs: Depending on the specified `needs` section and the resulting
                graph structure the policy can use different input to make predictions.

        Returns:
             The prediction.
        """
        logger_key = "enterprise_search_policy.predict_action_probabilities"

        if not self.supports_current_stack_frame(
            tracker, False, False
        ) or self.should_abstain_in_coexistence(tracker, True):
            return self._prediction(self._default_predictions(domain))

        if not self.vector_store:
            structlogger.error(f"{logger_key}.no_vector_store")
            return self._create_prediction_internal_error(domain, tracker)

        try:
            self._connect_vector_store_or_raise(endpoints)
        except (VectorStoreConfigurationError, VectorStoreConnectionError) as e:
            structlogger.error(f"{logger_key}.connection_error", error=e)
            return self._create_prediction_internal_error(domain, tracker)

        search_query = self._prepare_search_query(
            tracker, int(self.max_messages_in_query)
        )
        tracker_state = tracker.current_state(EventVerbosity.AFTER_RESTART)

        try:
            documents = await self.vector_store.search(
                query=search_query,
                tracker_state=tracker_state,
                threshold=self.vector_search_threshold,
            )
        except InformationRetrievalException as e:
            structlogger.error(f"{logger_key}.search_error", error=e)
            return self._create_prediction_internal_error(domain, tracker)

        if not documents.results:
            structlogger.info(f"{logger_key}.no_documents")
            return self._create_prediction_cannot_handle(domain, tracker)

        if self.use_llm:
            prompt = self._render_prompt(tracker, documents.results)
            llm_response = await self._invoke_llm(prompt)

            self._add_prompt_and_llm_response_to_latest_message(
                tracker=tracker,
                prompt_name="enterprise_search_prompt",
                user_prompt=prompt,
                llm_response=llm_response,
            )

            if llm_response is None or not llm_response.choices:
                structlogger.debug(f"{logger_key}.no_llm_response")
                response = None
            else:
                llm_answer = llm_response.choices[0]

                if self.relevancy_check_enabled:
                    relevancy_response = self._parse_llm_relevancy_check_response(
                        llm_answer
                    )
                    if not relevancy_response.relevant:
                        structlogger.debug(f"{logger_key}.answer_not_relevant")
                        return self._create_prediction_cannot_handle(
                            domain,
                            tracker,
                            RASA_PATTERN_CANNOT_HANDLE_NO_RELEVANT_ANSWER,
                        )

                if self.citation_enabled:
                    llm_answer = self.post_process_citations(llm_answer)

                structlogger.debug(
                    f"{logger_key}.llm_answer", prompt=prompt, llm_answer=llm_answer
                )
                response = llm_answer
        else:
            response = documents.results[0].metadata.get("answer", None)
            if not response:
                structlogger.error(
                    f"{logger_key}.answer_key_missing_in_metadata",
                    search_results=documents.results,
                )
            structlogger.debug(
                "enterprise_search_policy.predict_action_probabilities.no_llm",
                search_results=documents,
            )
        if response is None:
            return self._create_prediction_internal_error(domain, tracker)

        action_metadata = {
            "message": {
                "text": response,
                SEARCH_RESULTS_METADATA_KEY: [
                    result.text for result in documents.results
                ],
                UTTER_SOURCE_METADATA_KEY: self.__class__.__name__,
                SEARCH_QUERY_METADATA_KEY: search_query,
            }
        }

        # telemetry call to track policy prediction
        track_enterprise_search_policy_predict(
            vector_store_type=self.vector_store_config.get(VECTOR_STORE_TYPE_PROPERTY),
            embeddings_type=self.embeddings_config.get(PROVIDER_CONFIG_KEY),
            embeddings_model=self.embeddings_config.get(MODEL_CONFIG_KEY)
            or self.embeddings_config.get(MODEL_NAME_CONFIG_KEY),
            embeddings_model_group_id=self.embeddings_config.get(
                MODEL_GROUP_ID_CONFIG_KEY
            ),
            llm_type=self.llm_config.get(PROVIDER_CONFIG_KEY),
            llm_model=self.llm_config.get(MODEL_CONFIG_KEY)
            or self.llm_config.get(MODEL_NAME_CONFIG_KEY),
            llm_model_group_id=self.llm_config.get(MODEL_GROUP_ID_CONFIG_KEY),
            citation_enabled=self.citation_enabled,
            relevancy_check_enabled=self.relevancy_check_enabled,
        )
        return self._create_prediction(
            domain=domain, tracker=tracker, action_metadata=action_metadata
        )

    def _render_prompt(
        self, tracker: DialogueStateTracker, documents: List[SearchResult]
    ) -> Text:
        """Renders the prompt from the template.

        Args:
            tracker: The tracker containing the conversation history up to now.
            documents: The documents retrieved from search

        Returns:
            The rendered prompt.
        """
        inputs = {
            "current_conversation": tracker_as_readable_transcript(
                tracker, max_turns=self.max_history
            ),
            "docs": documents,
            "slots": self._prepare_slots_for_template(tracker),
            "check_relevancy": self.relevancy_check_enabled,
            "citation_enabled": self.citation_enabled,
        }
        prompt = Template(self.prompt_template).render(**inputs)
        log_llm(
            logger=structlogger,
            log_module="EnterpriseSearchPolicy",
            log_event="enterprise_search_policy._render_prompt.prompt_rendered",
            prompt=prompt,
        )
        return prompt

    @measure_llm_latency
    async def _invoke_llm(self, prompt: Text) -> Optional[LLMResponse]:
        """Fetches an LLM completion for the provided prompt.

        Args:
            llm: The LLM client used to get the completion.
            prompt: The prompt text to send to the model.

        Returns:
            An LLMResponse object, or None if the call fails.
        """
        llm = llm_factory(self.config.get(LLM_CONFIG_KEY), DEFAULT_LLM_CONFIG)
        try:
            response = await llm.acompletion(prompt)
            return LLMResponse.ensure_llm_response(response)
        except Exception as e:
            # unfortunately, langchain does not wrap LLM exceptions which means
            # we have to catch all exceptions here
            structlogger.error(
                "enterprise_search_policy._generate_llm_answer.llm_error",
                error=e,
            )
            return None

    def _parse_llm_relevancy_check_response(
        self, llm_answer: str
    ) -> _RelevancyCheckResponse:
        """Checks if the LLM response is relevant by parsing it."""
        answer_relevant = not _ENTERPRISE_SEARCH_ANSWER_NOT_RELEVANT_PATTERN.search(
            llm_answer
        )
        structlogger.debug("")
        return _RelevancyCheckResponse(
            answer=llm_answer if answer_relevant else None,
            relevant=answer_relevant,
        )

    def _create_prediction(
        self,
        domain: Domain,
        tracker: DialogueStateTracker,
        action_metadata: Dict[Text, Any],
    ) -> PolicyPrediction:
        """Create a policy prediction result with ACTION_SEND_TEXT_NAME.

        Args:
            domain: The model's domain.
            tracker: The tracker containing the conversation history up to now.
            action_metadata: The metadata for the predicted action.

        Returns:
            The prediction.
        """
        result = self._prediction_result(ACTION_SEND_TEXT_NAME, domain)
        stack = tracker.stack
        if not stack.is_empty():
            stack.pop()
            events: List[Event] = tracker.create_stack_updated_events(stack)
        else:
            events = []

        return self._prediction(result, action_metadata=action_metadata, events=events)

    def _create_prediction_internal_error(
        self, domain: Domain, tracker: DialogueStateTracker
    ) -> PolicyPrediction:
        return self._create_prediction_for_pattern(
            domain, tracker, InternalErrorPatternFlowStackFrame()
        )

    def _create_prediction_cannot_handle(
        self,
        domain: Domain,
        tracker: DialogueStateTracker,
        reason: Optional[str] = None,
    ) -> PolicyPrediction:
        cannot_handle_stack_frame = (
            CannotHandlePatternFlowStackFrame(reason=reason)
            if reason is not None
            else CannotHandlePatternFlowStackFrame()
        )
        return self._create_prediction_for_pattern(
            domain, tracker, cannot_handle_stack_frame
        )

    def _create_prediction_for_pattern(
        self,
        domain: Domain,
        tracker: DialogueStateTracker,
        pattern_stack_frame: PatternFlowStackFrame,
    ) -> PolicyPrediction:
        """Create a policy prediction result for error.

        We should cancel the current flow (hence ACTION_CANCEL_FLOW) and push a
        pattern stack frame (Internal Error Pattern by default) to start the pattern.

        Args:
            domain: The model's domain.
            tracker: The tracker containing the conversation history up to now.
            pattern_stack_frame: The pattern stack frame to push.

        Returns:
            The prediction.
        """
        # TODO: replace ACTION_CANCEL_FLOW (ATO-2097)
        result = self._prediction_result(ACTION_CANCEL_FLOW, domain)
        stack = tracker.stack
        if not stack.is_empty():
            stack.pop()
            stack.push(pattern_stack_frame)
        events: List[Event] = tracker.create_stack_updated_events(stack)
        return self._prediction(result, action_metadata=None, events=events)

    def _prediction_result(
        self, action_name: Optional[Text], domain: Domain, score: Optional[float] = 1.0
    ) -> List[float]:
        """Creates a prediction result.

        Args:
            action_name: The name of the predicted action.
            domain: The model's domain.
            score: The score of the predicted action.

        Returns:
        The prediction result where the score is used for one hot encoding.
        """
        result = self._default_predictions(domain)
        if action_name:
            result[domain.index_for_action(action_name)] = score  # type: ignore[assignment]
        return result

    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> "EnterpriseSearchPolicy":
        """Loads a trained policy (see parent class for full docstring)."""
        # Perform health checks for both LLM and embeddings client configs
        cls._perform_health_checks(config, "enterprise_search_policy.load")

        prompt_template = None
        try:
            with model_storage.read_from(resource) as path:
                prompt_template = rasa.shared.utils.io.read_file(
                    path / ENTERPRISE_SEARCH_PROMPT_FILE_NAME
                )
        except (FileNotFoundError, FileIOException) as e:
            structlogger.warning(
                "enterprise_search_policy.load.failed", error=e, resource=resource.name
            )

        store_type = config.get(VECTOR_STORE_PROPERTY, {}).get(
            VECTOR_STORE_TYPE_PROPERTY
        )

        embeddings = cls._create_plain_embedder(config)

        structlogger.info("enterprise_search_policy.load", config=config)
        if store_type == DEFAULT_VECTOR_STORE_TYPE:
            # if a vector store is not specified,
            # default to using FAISS with the index stored in the model
            # TODO figure out a way to get path without context manager
            with model_storage.read_from(resource) as path:
                vector_store = FAISS_Store(
                    embeddings=embeddings,
                    index_path=path,
                    docs_folder=None,
                    create_index=False,
                    parse_as_faq_pairs=not config.get(
                        USE_LLM_PROPERTY, DEFAULT_USE_LLM_PROPERTY
                    ),
                )
        else:
            vector_store = create_from_endpoint_config(
                config_type=store_type,
                embeddings=embeddings,
            )  # type: ignore

        return cls(
            config,
            model_storage,
            resource,
            execution_context,
            vector_store=vector_store,
            prompt_template=prompt_template,
        )

    @classmethod
    def _get_local_knowledge_data(cls, config: Dict[str, Any]) -> Optional[List[str]]:
        """This is required only for local knowledge base types.

        e.g. FAISS, to ensure that the graph component is retrained when the knowledge
        base is updated.
        """
        merged_config = {**cls.get_default_config(), **config}

        store_type = merged_config.get(VECTOR_STORE_PROPERTY, {}).get(
            VECTOR_STORE_TYPE_PROPERTY
        )
        if store_type != DEFAULT_VECTOR_STORE_TYPE:
            return None

        source = merged_config.get(VECTOR_STORE_PROPERTY, {}).get(SOURCE_PROPERTY)
        if not source:
            return None

        docs = FAISS_Store.load_documents(source)

        if len(docs) == 0:
            return None

        docs_as_strings = [
            json.dumps(doc.dict(), ensure_ascii=False, sort_keys=True) for doc in docs
        ]
        return sorted(docs_as_strings)

    @classmethod
    def fingerprint_addon(cls, config: Dict[str, Any]) -> Optional[str]:
        """Add a fingerprint of enterprise search policy for the graph."""
        prompt_template = cls._resolve_prompt_template(
            config, LOG_COMPONENT_SOURCE_METHOD_FINGERPRINT_ADDON
        )

        local_knowledge_data = cls._get_local_knowledge_data(config)

        llm_config = resolve_model_client_config(
            config.get(LLM_CONFIG_KEY), EnterpriseSearchPolicy.__name__
        )
        embedding_config = resolve_model_client_config(
            config.get(EMBEDDINGS_CONFIG_KEY), EnterpriseSearchPolicy.__name__
        )
        return deep_container_fingerprint(
            [prompt_template, local_knowledge_data, llm_config, embedding_config]
        )

    @staticmethod
    def post_process_citations(llm_answer: str) -> str:
        """Post-process the LLM answer.

         Re-writes the bracketed numbers to start from 1 and
         re-arranges the sources to follow the enumeration order.

        Args:
            llm_answer: The LLM answer.

        Returns:
            The post-processed LLM answer.
        """
        structlogger.debug(
            "enterprise_search_policy.post_process_citations", llm_answer=llm_answer
        )

        # Split llm_answer into answer and citations
        try:
            answer, citations = llm_answer.rsplit("Sources:", 1)
        except ValueError:
            # if there is no "Sources:" in the llm_answer
            return llm_answer

        # Find all source references in the answer
        pattern = r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]"
        matches = re.findall(pattern, answer)
        old_source_indices = [
            int(num.strip()) for match in matches for num in match.split(",")
        ]

        # Map old source references to the correct enumeration
        renumber_mapping = {num: idx + 1 for idx, num in enumerate(old_source_indices)}

        # remove whitespace from original source citations in answer
        for match in matches:
            answer = answer.replace(f"[{match}]", f"[{match.replace(' ', '')}]")

        new_answer = []
        for word in answer.split():
            matches = re.findall(pattern, word)
            if matches:
                for match in matches:
                    if "," in match:
                        old_indices = [
                            int(num.strip()) for num in match.split(",") if num
                        ]
                        new_indices = [
                            renumber_mapping[old_index]
                            for old_index in old_indices
                            if old_index in renumber_mapping
                        ]
                        if not new_indices:
                            continue

                        word = word.replace(
                            match, f"{', '.join(map(str, new_indices))}"
                        )
                    else:
                        old_index = int(match.strip("[].,:;?!"))
                        new_index = renumber_mapping.get(old_index)
                        if not new_index:
                            continue

                        word = word.replace(str(old_index), str(new_index))
            new_answer.append(word)

        # join the words
        joined_answer = " ".join(new_answer)
        joined_answer += "\nSources:\n"

        new_sources: List[str] = []

        for line in citations.split("\n"):
            pattern = r"(?<=\[)\d+"
            match = re.search(pattern, line)
            if match:
                old_index = int(match.group(0))
                new_index = renumber_mapping[old_index]
                # replace only the first occurrence of the old index
                line = line.replace(f"[{old_index}]", f"[{new_index}]", 1)

                # insert the line into the new_index position
                new_sources.insert(new_index - 1, line)
            elif line.strip():
                new_sources.append(line)

        joined_sources = "\n".join(new_sources)

        return joined_answer + joined_sources

    @classmethod
    def _perform_health_checks(
        cls, config: Dict[Text, Any], log_source_method: str
    ) -> None:
        # Perform health check of the LLM client config
        llm_config = resolve_model_client_config(config.get(LLM_CONFIG_KEY, {}))
        cls.perform_llm_health_check(
            llm_config,
            DEFAULT_LLM_CONFIG,
            log_source_method,
            EnterpriseSearchPolicy.__name__,
        )

        # Perform health check of the embeddings client config
        embeddings_config = resolve_model_client_config(
            config.get(EMBEDDINGS_CONFIG_KEY, {})
        )
        cls.perform_embeddings_health_check(
            embeddings_config,
            DEFAULT_EMBEDDINGS_CONFIG,
            log_source_method,
            EnterpriseSearchPolicy.__name__,
        )

    @classmethod
    def get_system_default_prompt_based_on_config(cls, config: Dict[str, Any]) -> str:
        """
        Resolves the default prompt template for Enterprise Search Policy based on
        the component's configuration.

        - The old prompt is selected when both citation and relevancy check are either
          disabled or not set in the configuration.
        - The citation prompt is used when citation is enabled and relevancy check is
          either disabled or not set in the configuration.
        - The relevancy check prompt is only used when relevancy check is enabled.

        Args:
            config: The component's configuration.

        Returns:
            The resolved jinja prompt template as a string.
        """

        # Get the feature flags
        citation_enabled = config.get(
            CITATION_ENABLED_PROPERTY, DEFAULT_CITATION_ENABLED_PROPERTY
        )
        relevancy_check_enabled = config.get(
            CHECK_RELEVANCY_PROPERTY, DEFAULT_CHECK_RELEVANCY_PROPERTY
        )

        # Based on the enabled features (citation, relevancy check) fetch the
        # appropriate default prompt
        default_prompt = cls._select_default_prompt_template_based_on_features(
            relevancy_check_enabled, citation_enabled
        )

        return default_prompt

    @classmethod
    def _resolve_prompt_template(
        cls,
        config: dict,
        log_source_method: Literal["init", "fingerprint"],
    ) -> str:
        """
        Resolves the prompt template to use for the Enterprise Search Policy's
        generative search.

        Checks if a custom template is provided via component's configuration. If not,
        it selects the appropriate default template based on the enabled features
        (citation and relevancy check).

        Args:
            config: The component's configuration.
            log_source_method: The name of the method or function emitting the log for
                better traceability.
        Returns:
            The resolved jinja prompt template as a string.
        """

        # Read the template path from the configuration if available.
        # The deprecated 'prompt' has a lower priority compared to 'prompt_template'
        config_defined_prompt = (
            config.get(PROMPT_TEMPLATE_CONFIG_KEY)
            or config.get(PROMPT_CONFIG_KEY)
            or None
        )
        # Select the default prompt based on the features set in the config.
        default_prompt = cls.get_system_default_prompt_based_on_config(config)

        return get_prompt_template(
            config_defined_prompt,
            default_prompt,
            log_source_component=EnterpriseSearchPolicy.__name__,
            log_source_method=log_source_method,
        )

    @classmethod
    def _select_default_prompt_template_based_on_features(
        cls,
        relevancy_check_enabled: bool,
        citation_enabled: bool,
    ) -> str:
        """
        Returns the appropriate default prompt template based on the feature flags.

        The selection follows this priority:
        1. If relevancy check is enabled, return the prompt that includes both relevancy
           and citation blocks.
        2. If only citation is enabled, return the prompt with citation blocks.
        3. Otherwise, fall back to the legacy default prompt template.

        Args:
            relevancy_check_enabled: Whether the LLM-generated answer should undergo
                relevancy evaluation.
            citation_enabled: Whether citations should be included in the generated
                answer.

        Returns:
            The default prompt template corresponding to the enabled features.
        """
        if relevancy_check_enabled:
            # ES prompt that has relevancy check and citations blocks
            return DEFAULT_ENTERPRISE_SEARCH_PROMPT_WITH_RELEVANCY_CHECK_AND_CITATION_TEMPLATE  # noqa: E501
        elif citation_enabled:
            # ES prompt with citation's block - backward compatibility
            return DEFAULT_ENTERPRISE_SEARCH_PROMPT_WITH_CITATION_TEMPLATE
        else:
            # Legacy ES prompt - backward compatibility
            return DEFAULT_ENTERPRISE_SEARCH_PROMPT_TEMPLATE
