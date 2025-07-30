import pandas as pd
from _typeshed import Incomplete
from spacy.tokens import Doc, Token
from typing import Any
from virtualitics_sdk.nlp.compliants import PandasCompliant as PandasCompliant

class CorpusStats(PandasCompliant):
    """Spacy custom component responsible for extracting some statistics from the data.
     It will set corpus_stats as a custom extension to the doc object.
     It also implements PandasCompliant and SqlCompliant so that it is
     compatible with the various persistence handlers.
    """
    name: str
    beautiful_name: str
    requires: Incomplete
    depends_on: Incomplete
    assigns: Incomplete
    table_name: str
    feature_columns: Incomplete
    pandas_cols: Incomplete
    nlp: Incomplete
    def __init__(self, nlp: Any) -> None:
        """Initialize the custom component.

        :param nlp: The spacy nlp object
        """
    @classmethod
    def get_feature_columns(cls) -> list:
        """
        :return: Return the pandas columns names of the feature it extracts
        """
    @classmethod
    def init_dataframe(cls) -> pd.DataFrame:
        """
        :return: An empty dataframe with the necessary columns to store the information extracted by this component.
        """
    @classmethod
    def get_df_table_name(cls) -> str:
        """
        :return: The table neme of the component.
        """
    @classmethod
    def to_df(cls, doc: Doc, idx_col: str) -> pd.DataFrame:
        """
        :param doc: Spacy doc object.
        :param idx_col: The column to use as idx.

        :return: Extract a dict with the corpus_stats information attached to a document.
        """
    @classmethod
    def to_dict(cls, doc: Doc, idx_col: str) -> list[dict]:
        """
        :param doc: Spacy doc object.
        :param idx_col: The column to use as idx.

        :return: Extract a dict with the corpus_stats information attached to a document
        """
    @classmethod
    def init_extension(cls) -> None:
        """
        Register the doc extension used by this component.
        """
    def __call__(self, doc: Doc) -> Doc:
        """
        Extract useful statistics from a document.

        :param doc: Input doc

        :return: Doc with stats extension
        """
    def __walk_tree__(self, node: Token, depth: int = 0):
        """
        Navigate the node three.

        :param node: The input node
        :param depth: The input depth

        :return: A node or the depth reached if there are no nodes left
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

        :return: A new instance of the CorpusStats component
        """
