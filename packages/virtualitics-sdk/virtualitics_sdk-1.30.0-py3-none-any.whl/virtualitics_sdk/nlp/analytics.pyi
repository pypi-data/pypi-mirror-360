from _typeshed import Incomplete
from virtualitics_sdk.app.step import Step as Step, StepType as StepType
from virtualitics_sdk.assets.asset import AssetType as AssetType
from virtualitics_sdk.assets.knowledge_graph import TfIdfBasedKG as TfIdfBasedKG, analyze_entity_proportions as analyze_entity_proportions
from virtualitics_sdk.assets.language_processor import LanguageProcessor as LanguageProcessor
from virtualitics_sdk.elements import Image as Image, Table as Table
from virtualitics_sdk.nlp.advanced import KGAdvancedConfig as KGAdvancedConfig
from virtualitics_sdk.nlp.common import build_default_page as build_default_page, get_assets_info as get_assets_info
from virtualitics_sdk.nlp.entity_extractor import NerSummarization as NerSummarization
from virtualitics_sdk.nlp.pipeline_config import PipelineConfigurationStep as PipelineConfigurationStep
from virtualitics_sdk.page import Card as Card, Page as Page, Section as Section
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface

class LouvainCommunityEntities(Step):
    main_section: str
    def __init__(self) -> None: ...
    def run(self, flow_metadata): ...

class HistogramInsightsStep(Step):
    main_section: str
    pipeline_config_step: Incomplete
    uses_pyvip: Incomplete
    def __init__(self, pipeline_config_step: PipelineConfigurationStep, uses_pyvip: bool = True) -> None: ...
    def run(self, flow_metadata, pyvip_client: Incomplete | None = None): ...
