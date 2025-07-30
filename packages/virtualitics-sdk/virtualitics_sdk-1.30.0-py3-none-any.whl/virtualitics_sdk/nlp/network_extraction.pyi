from _typeshed import Incomplete
from virtualitics.api import VIP as VIP
from virtualitics_sdk.app.step import Step as Step, StepType as StepType
from virtualitics_sdk.assets.asset import AssetType as AssetType
from virtualitics_sdk.assets.knowledge_graph import TfIdfBasedKG as TfIdfBasedKG
from virtualitics_sdk.assets.language_processor import LanguageProcessor as LanguageProcessor
from virtualitics_sdk.nlp import EventExtractor as EventExtractor, NerSummarization as NerSummarization
from virtualitics_sdk.nlp.common import build_default_page as build_default_page, build_kg_dashboard as build_kg_dashboard, crop_plot as crop_plot, get_assets_info as get_assets_info
from virtualitics_sdk.nlp.data_upload import DataUpload as DataUpload
from virtualitics_sdk.nlp.pipeline_config import PipelineConfigurationStep as PipelineConfigurationStep
from virtualitics_sdk.nlp.sim_thresh import SimilarityThresholdExperiments as SimilarityThresholdExperiments
from virtualitics_sdk.page import Card as Card, Page as Page, Section as Section
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface

def reload_kg_callback(store_interface: StoreInterface, pyvip_client: VIP | None = None): ...

class ShowGraph(Step):
    main_section: str
    logger: Incomplete
    advanced_dash: Incomplete
    data_upload_step: Incomplete
    pipeline_config_step: Incomplete
    sim_thresh_step: Incomplete
    uses_pyvip: Incomplete
    advanced: Incomplete
    def __init__(self, data_upload_step: DataUpload, pipeline_config_step: PipelineConfigurationStep, sim_thresh_step: SimilarityThresholdExperiments, advanced: bool = False, advanced_dash: bool = False, uses_pyvip: bool = True) -> None: ...
    def run(self, flow_metadata: dict, pyvip_client: VIP | None = None): ...
