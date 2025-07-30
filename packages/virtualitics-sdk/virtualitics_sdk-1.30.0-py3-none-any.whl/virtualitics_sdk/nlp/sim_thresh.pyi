import networkx as nx
import pandas as pd
from _typeshed import Incomplete
from virtualitics.api import VIP as VIP
from virtualitics_sdk.app.step import Step as Step, StepType as StepType
from virtualitics_sdk.assets.asset import AssetType as AssetType
from virtualitics_sdk.assets.knowledge_graph import TfIdfBasedKG as TfIdfBasedKG, similarity_threshold_experiment as similarity_threshold_experiment
from virtualitics_sdk.assets.language_processor import LanguageProcessor as LanguageProcessor
from virtualitics_sdk.elements import Column as Column, Dashboard as Dashboard, NumericRange as NumericRange, Row as Row
from virtualitics_sdk.nlp.advanced import KGAdvancedConfig as KGAdvancedConfig
from virtualitics_sdk.nlp.common import build_default_page as build_default_page, build_kg_dashboard as build_kg_dashboard, crop_plot as crop_plot, get_assets_info as get_assets_info
from virtualitics_sdk.nlp.data_upload import DataUpload as DataUpload
from virtualitics_sdk.nlp.pipeline_config import PipelineConfigurationStep as PipelineConfigurationStep
from virtualitics_sdk.page import Card as Card, Page as Page, Section as Section
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface
from virtualitics_sdk.utils.viz_utils import create_line_plot as create_line_plot

def round_to_multiple(number, multiple): ...
def augment_nodes_with_extra_features(kg: nx.Graph, store_interface: StoreInterface):
    """
    Add extra features to a networkX graph.
    It uses the feature matrix and the feature names stored in the KG asset
    and the nlp features computed by the LanguageProcessor.
    Args:
        kg: nx.Graph
        store_interface:
    Returns:
        kg: nx.Graph
    """
def compute_relevant_entities(network_df: pd.DataFrame, nlp_module: LanguageProcessor, community: str): ...
def slider_callback(store_interface: StoreInterface, pyvip_client: VIP | None = None): ...

class SimilarityThresholdExperiments(Step):
    step_title: str
    main_section: str
    sim_thresh_step_description: str
    numeric_range_title: str
    logger: Incomplete
    data_upload_step: Incomplete
    advanced: Incomplete
    similarity_threshold_range: Incomplete
    def __init__(self, data_upload_step: DataUpload, advanced: bool = False) -> None: ...
    def run(self, flow_metadata, pyvip_client: Incomplete | None = None): ...
