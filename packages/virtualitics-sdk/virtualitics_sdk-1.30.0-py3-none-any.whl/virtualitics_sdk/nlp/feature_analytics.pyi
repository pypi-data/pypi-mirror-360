import pandas as pd
from _typeshed import Incomplete
from virtualitics.api import VIP as VIP
from virtualitics_sdk.app.step import Step as Step, StepType as StepType
from virtualitics_sdk.assets.asset import Asset as Asset, AssetType as AssetType
from virtualitics_sdk.assets.language_processor import LanguageProcessor as LanguageProcessor
from virtualitics_sdk.elements import AssetDownloadCustomEvent as AssetDownloadCustomEvent, Dashboard as Dashboard, Dropdown as Dropdown, Table as Table
from virtualitics_sdk.nlp.entity_extractor import NerSummarization as NerSummarization
from virtualitics_sdk.nlp.event_extractor import EventExtractor as EventExtractor
from virtualitics_sdk.nlp.pipeline_config import PipelineConfigurationStep as PipelineConfigurationStep
from virtualitics_sdk.nlp.sim_thresh import compute_relevant_entities as compute_relevant_entities
from virtualitics_sdk.page import Card as Card, Page as Page, Section as Section
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface
from virtualitics_sdk.utils.viz_utils import create_bar_plot as create_bar_plot

class FeatureExploration(Step):
    allow_download: Incomplete
    task_cls: Incomplete
    feature_name: Incomplete
    pipeline_config_step: Incomplete
    main_section_name: Incomplete
    def __init__(self, pipeline_config_step: PipelineConfigurationStep, task_cls: type[EventExtractor] | type[NerSummarization], feature_name: str, allow_download: bool = True, **kwargs) -> None: ...
    @staticmethod
    def produce_frequencies(feature_df: pd.DataFrame, groupby): ...
    @staticmethod
    def counting_occurrences_plot(feature_df: pd.DataFrame, feature_name: str): ...
    @staticmethod
    def create_distrib_unique_feature_in_doc(feature_df: pd.DataFrame, feature_name: str): ...
    @staticmethod
    def create_distrib_num_doc_f_appears(feature_df: pd.DataFrame, feature_name: str, task_cls): ...
    @staticmethod
    def produce_download_btn(store_interface: StoreInterface, current_page: Page, feature_df: pd.DataFrame, feature_name: str, idx: int, section_title: str): ...
    def run(self, flow_metadata) -> None: ...

def dropdown_updater(store_interface: StoreInterface, pyvip_client: VIP | None = None): ...

class SimplifiedRelevantEntities(Step):
    step_title: str
    main_section: str
    def __init__(self) -> None: ...
    def run(self, flow_metadata: dict, pyvip_client: VIP | None = None): ...
