import logging
from typing import Dict, Optional, Text

from rasa.shared.core.domain import Domain
from rasa.shared.core.flows import FlowsList
from rasa.shared.core.training_data.structures import StoryGraph
from rasa.shared.importers.importer import TrainingDataImporter
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.utils.common import cached_method

logger = logging.getLogger(__name__)


class StaticTrainingDataImporter(TrainingDataImporter):
    """Static `TrainingFileImporter` implementation."""

    def __init__(
        self,
        domain: Domain,
        stories: Optional[StoryGraph] = None,
        flows: Optional[FlowsList] = None,
        nlu_data: Optional[TrainingData] = None,
        config: Optional[Dict] = None,
    ):
        self.domain = domain
        self.stories = stories or StoryGraph([])
        self.flows = flows or FlowsList(underlying_flows=[])
        self.nlu_data = nlu_data or TrainingData()
        self.config = config or {}

    @cached_method
    def get_config(self) -> Dict:
        """Retrieves model config (see parent class for full docstring)."""
        return self.config

    def get_config_file_for_auto_config(self) -> Optional[Text]:
        """Returns config file path for auto-config only if there is a single one."""
        return None

    @cached_method
    def get_stories(self, exclusion_percentage: Optional[int] = None) -> StoryGraph:
        """Retrieves training stories / rules (see parent class for full docstring)."""
        return self.stories

    @cached_method
    def get_flows(self) -> FlowsList:
        """Retrieves training stories / rules (see parent class for full docstring)."""
        return self.flows

    @cached_method
    def get_conversation_tests(self) -> StoryGraph:
        """Retrieves conversation test stories (see parent class for full docstring)."""
        return StoryGraph([])

    @cached_method
    def get_nlu_data(self, language: Optional[Text] = "en") -> TrainingData:
        """Retrieves NLU training data (see parent class for full docstring)."""
        return self.nlu_data

    @cached_method
    def get_domain(self) -> Domain:
        """Retrieves model domain (see parent class for full docstring)."""
        return self.domain
