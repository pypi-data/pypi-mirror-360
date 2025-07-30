from virtualitics_sdk.app.step import Step as Step, StepType as StepType
from virtualitics_sdk.elements import Dropdown as Dropdown, NumericRange as NumericRange
from virtualitics_sdk.page import Card as Card, Page as Page, Section as Section
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface

class KGAdvancedConfig(Step):
    main_section: str
    bonferroni_drop_title: str
    alpha_value_drop_title: str
    sim_threshold_drop_title: str
    sim_threshold_drop_range: str
    step_title: str
    def __init__(self) -> None: ...
    @classmethod
    def get_alpha_value_or_default(cls, store_interface: StoreInterface): ...
    @classmethod
    def get_bonferroni_value_or_default(cls, store_interface: StoreInterface): ...
    @classmethod
    def get_sim_threshold_value_or_default(cls, store_interface: StoreInterface): ...
    @classmethod
    def get_sim_threshold_range_or_default(cls, store_interface: StoreInterface): ...
    def create_significant_feature_card(self): ...
    @classmethod
    def create_sim_thresh_config_drop(cls):
        """
        Generate the similarity threshold dropdown that let the user choose if compute the experiment
        Args:
        Returns: A dropdown component that can be added to the page
        """
    def run(self, flow_metadata) -> None: ...
