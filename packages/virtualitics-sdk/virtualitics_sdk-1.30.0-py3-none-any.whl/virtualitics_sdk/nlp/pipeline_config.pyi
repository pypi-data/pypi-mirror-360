import pandas as pd
from _typeshed import Incomplete
from virtualitics_sdk.app.step import Step as Step, StepType as StepType
from virtualitics_sdk.assets.language_processor import LanguageProcessor as LanguageProcessor
from virtualitics_sdk.elements import Dropdown as Dropdown, TextInput as TextInput
from virtualitics_sdk.nlp.common import build_default_page as build_default_page
from virtualitics_sdk.nlp.data_upload import DataUpload as DataUpload
from virtualitics_sdk.page import Card as Card, Page as Page, Section as Section
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface

class NoDatasetIdxException(Exception):
    def __init__(self) -> None: ...

class PipelineConfigurationStep(Step):
    available_tasks_drop_title: str
    step_title: str
    identifier_dropdown_title: str
    narrative_dropdown_title: str
    kpi_dropdown_title: str
    dt_dropdown_title: str
    dt_format_input: str
    default_pipeline_tasks: Incomplete
    @classmethod
    def create_pipeline_config_drop(cls, default_model: str):
        """
        Generate the pipeline task dropdown based on a selected model
        Args:
            default_model: The spacy model to use to fetch the available spacy tasks
        Returns: A dropdown component that can be added to the page
        """
    @classmethod
    def create_feature_selection_card(cls, pandas_df: pd.DataFrame): ...
    @classmethod
    def create_date_filtering_components(cls, pandas_df: pd.DataFrame): ...
    show_date_filtering_selection: Incomplete
    show_pipeline_dropdown: Incomplete
    show_threshold_exp_drop: Incomplete
    data_upload: Incomplete
    def __init__(self, data_upload_step: DataUpload, show_date_filtering_selection: bool = False, show_pipeline_dropdown: bool = False, show_thresold_exp_drop: bool = False) -> None: ...
    def run(self, flow_metadata: dict): ...
    @classmethod
    def get_idx(cls, store_interface: StoreInterface): ...
    def get_pipe_config_or_default(self, store_interface: StoreInterface):
        """
        In advanced mode, user can configure the spacy pipeline.
        This method can be called from other steps to get the selected value from the user
        or the default one.
        Args:
            store_interface:
        Returns: user input or default list of tasks
        """
