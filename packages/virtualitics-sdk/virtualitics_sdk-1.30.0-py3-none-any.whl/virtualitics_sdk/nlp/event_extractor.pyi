import pandas as pd
from _typeshed import Incomplete
from spacy.tokens import Doc
from typing import Any
from virtualitics_sdk.nlp.compliants import PandasCompliant as PandasCompliant, SqlCompliant as SqlCompliant

class EventExtractor(SqlCompliant, PandasCompliant):
    """
    Spacy custom component responsible for extracting events from spacy docs.
    It will set events_summary as a custom extension to the doc object.
    It also implements PandasCompliant and SqlCompliant so that it is
    compatible with the various persistence handlers.
    """
    name: str
    beautiful_name: str
    requires: Incomplete
    depends_on: Incomplete
    assigns: Incomplete
    table_name: str
    sql_cols: Incomplete
    pandas_cols: Incomplete
    feature_columns: Incomplete
    nlp: Incomplete
    def __init__(self, nlp: Any) -> None:
        """Initialize the custom component.

        :param nlp: The spacy nlp object
        """
    @classmethod
    def get_feature_columns(cls) -> list[str]:
        """
        :return: Return the pandas columns names of the feature it extracts
        """
    @classmethod
    def init_dataframe(cls) -> pd.DataFrame:
        """
        :return: An empty dataframe with the necessary columns to store the information extracted by this component.
        """
    @classmethod
    def to_df(cls, doc: Doc, idx_col: str) -> pd.DataFrame:
        """
        :param doc: Spacy doc object.
        :param idx_col: The column to use as idx.

        :return: Extract a dict with the events_summary information attached to a document.
        """
    @classmethod
    def to_dict(cls, doc: Doc, idx_col: str) -> list[dict]:
        """
        :param doc: Spacy doc object.
        :param idx_col: The column to use as idx.

        :return: Extract a dict with the events_summary information attached to a document.
        """
    @classmethod
    def get_df_table_name(cls) -> str:
        """
        :return: The table name of the component.
        """
    @classmethod
    def init_extension(cls) -> None:
        """
        Register the doc extension used by this component.
        """
    def __call__(self, doc: Doc) -> Doc:
        """
        Extract events from a document.

        :param doc: Input doc

        :return: Doc with events_summary extension
        """
    @classmethod
    def transform_sql(cls, doc, idx_col: str, value_placeholder: str = '%s') -> tuple[str, list]:
        """
        :param doc: The spacy doc object
        :param idx_col: The column to use as id
        :param value_placeholder: The type of placeholder to use (it can vary based on the client you're using)

        :return: A list elements ready to be inserted into a db
        """
    @classmethod
    def get_sql_table_name(cls) -> str:
        """
        :return: The table neme of the table that should contain the information extracted by this component.
        """
    @classmethod
    def init_sql_db(cls) -> list[str]:
        """
        :return: A list with the necessary columns to store the information extracted by this component.
        """
    @classmethod
    def get_default(cls):
        """
        :return: The default configuration for the component
        """
    @staticmethod
    def create_component(nlp: Any, name: str, depends_on: list[str]):
        """Factory function. Create a new instance of this component.
        
        :param nlp: The spacy nlp object
        :param name: Useless. Just to give an example of registered params
        :param depends_on: Useless. Just to give an example of registered params

        :return: A new instance of the EventExtractor component
        """
