from _typeshed import Incomplete
from virtualitics_sdk.app.step import Step as Step, StepType as StepType
from virtualitics_sdk.assets.language_processor import LanguageProcessor as LanguageProcessor
from virtualitics_sdk.elements import DataSource as DataSource, Dropdown as Dropdown, TextInput as TextInput
from virtualitics_sdk.page import Card as Card, Page as Page, Section as Section
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface

class DataUpload(Step):
    step_title: str
    main_section: str
    corpus_name_textinput_title: str
    corpus_name_textinput_placeholder: str
    corpus_requirements: str
    data_source_title: str
    model_selection_title: str
    model_selection_default: str
    show_model_drop: Incomplete
    def __init__(self, show_model_drop: bool = False) -> None: ...
    def run(self, flow_metadata) -> None: ...
    def get_corpus_name(self, flow_metadata: dict):
        """
        The corpus name parameter is used as final kg output name.
        It is used once imported into Explore
        Args:
            flow_metadata:
        Returns: The value selected by the user or the default one
        """
    def get_model_or_default(self, store_interface: StoreInterface):
        """
        In advanced mode, user can select the spacy model to use from a dropdown list.
        This method can be called from other steps to get the selected value from the user
        or the default one.
        Args:
            store_interface:
        Returns: user spacy model input or the default one
        """
