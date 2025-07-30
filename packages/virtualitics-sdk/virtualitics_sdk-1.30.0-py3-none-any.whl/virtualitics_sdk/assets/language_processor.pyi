import collections
import pandas as pd
from _typeshed import Incomplete
from predict_backend.validation.type_validation import validate_types
from spacy.tokens import DocBin
from virtualitics_sdk.app.flow_metadata import FlowMetadata as FlowMetadata
from virtualitics_sdk.assets.asset import Asset as Asset, AssetType as AssetType
from virtualitics_sdk.assets.model import Model as Model
from virtualitics_sdk.nlp.entity_extractor import NerSummarization as NerSummarization
from virtualitics_sdk.nlp.event_extractor import EventExtractor as EventExtractor

def counter_to_str_repr(c: collections.Counter) -> list[str]:
    """ Constructs a list of tokens from a counter, with each token appearing as many times as its count in the counter.

    :param c:
    :return: List of tokens
    """

class LanguageProcessor(Asset):
    '''NLP Pipeline responsible to extract features like entities, events from raw text.
    It extends Asset, this way it can be easily stored and retrieved.
    It provides an easy interface to ingest documents and store their metadata.
    
    :param model_name: The spacy model use under the hood
    :param asset_label: Asset parameter
    :param asset_name: Asset parameter
    :param document_identifier: The dataset feature to use as document id
    :param narrative_feature: The dataset feature that contains the text to process
    :param feature_names: The list of dataset features to store together with the doc extracted features
    :param pipeline_task: List of task names to use inside the pipeline
    :param description: Asset parameter
    :param version: Asset parameter
    :param metadata: Asset parameter
    :param remove_model_after: Remove the model after the ingestion process
    :param seed: numpy seed value

    **EXAMPLE:**

       .. code-block:: python
       
           # Imports 
           from virtualitics_sdk import LanguageProcessor
           . . .
           # Example usage
           selected_model = "en_core_web_lg"
           pipeline_config = ["Event Extraction", "Entity Extraction", "Corpus Statistics"]
           feature_names = [
               "Unnamed: 0",
               "DATE RAISE ANNOUNCED",
               "COMPANY",
               "AMOUNT",
               "HQ Location",
               "TOP INVESTORS (in this round)",
               "LINK",
               "Website",
               "Round ",
               "Category",
               "NOTES",
               "Expansion Plans",
               "Founder First Name",
               "Founder Last Name",
               "Founder LinkedIn",
               "Founder Twitter",
               "Founder AngelList",
               "Unnamed: 16",
           ]
           asset_label = \'17181175-32-1f4a-442c-8f91-4d32e2b905fd_lp\'
           asset_name = \'_lp\'
           id_col = \'COMPANY\'
           narr_col = \'COMPANY\'
           nlp_module = LanguageProcessor(
               model_name=selected_model,
               pipeline_task=pipeline_config,
               feature_names=feature_names,
               asset_label=asset_label,
               asset_name=asset_name,
               document_identifier=id_col,
               narrative_feature=narr_col,
           )
    '''
    available_models: Incomplete
    DATASET_UUID: int
    model_name: Incomplete
    vip: Incomplete
    model: Incomplete
    corpus: Incomplete
    alias_resolution_model: Incomplete
    kg: Incomplete
    last_ingestion_elapsed: Incomplete
    remove_model_after: Incomplete
    seed: Incomplete
    pipeline_task: Incomplete
    pipeline_task_cls: Incomplete
    document_identifier: Incomplete
    narrative_feature: Incomplete
    feature_names: Incomplete
    persistance_h: Incomplete
    @validate_types
    def __init__(self, model_name: str, asset_label: str, asset_name: str, document_identifier: str, narrative_feature: str, feature_names: list[str] | None = None, pipeline_task: list[str] = None, description: str | None = None, version: int = 0, metadata: Incomplete | None = None, remove_model_after: bool = True, seed: int | None = None, **kwargs) -> None: ...
    def initialize_model(self, model_name: str):
        """Initialize the internal Spacy model with the provided model name and save it as instance attribute.

        :param model_name:
        """
    def ingest(self, data: pd.DataFrame, flow_metadata: FlowMetadata | None = None, extract_doc_bin: bool = False, starting_progress: int | float | None = None, target_progress: int | float | None = None) -> None | DocBin:
        """It runs the whole pipeline on the pd dataframe provided.
        For validation purpose, it will check if the init params provided are present inside the data df.
        For store, starting_progress and target_progress params docs, check StepProgressTqdm docs.

        :param data: Mandatory. The data used to feed the pipeline.
        :param flow_metadata: The flow metadata necessary to create a store interface.
        :param extract_doc_bin: If true, the method return a DocBin.
        :param starting_progress: Used to init a StepProgressTqdm. Mandatory if store provided.
        :param target_progress:  Used to init a StepProgressTqdm.
        :return: A DocBin object, if requested.
        """
    @staticmethod
    def available_tasks(model: str) -> list:
        """Returns the available task (registered components) available with the specified model

        :param model: The model name
        :return: List of available tasks
        """
    def get_single_doc_nlp_features(self, doc_number):
        """
        Produce a Counter of string->count for entities and events.
        """
    @staticmethod
    def events2features(events: pd.DataFrame) -> pd.DataFrame | None:
        """
        Transform the events df into features that can be passed to the tf-idf Vectorizer.

        :param events: LanguageProcessor events table
        :return: The same df with the output features
        """
    @staticmethod
    def entities2features(entities: pd.DataFrame) -> pd.DataFrame | None:
        """
        Transform the entities df into features that can be passed to the tf-idf Vectorizer.

        :param entities: LanguageProcessor entities table
        :return: The same df with the output features
        """
    def get_doc_nlp_features(self) -> tuple[list[str], list[str]]:
        """It extracts computed features from the docs. It also returns a list of docs name

        :return: List that represent the doc names, List that represent the extracted features
        """
    def get_table(self, table: str) -> pd.DataFrame:
        """ Useful if you want to access a specific language processor internal table.
        Available tables:
            - doc_data, where there are the dataset original features
            - entities,
            = events

        :param table: table name
        :return: pd.DataFrame
        """
    def get_doc_numbers(self):
        """

        :return: A list with doc names
        """
    def get_doc_ids_and_dates(self):
        """

        :return: List of tuples of format (doc_number, date)
        """
    def get_doc_node_attributes(self, doc_number) -> dict:
        """ Return the base information of a doc_number doc.

        :param doc_number: The doc name
        :return: a dict with the format {'feature1': 'val1', 'feature2': 'val2'}
        """
