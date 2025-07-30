import pandas as pd
from abc import ABC
from spacy.tokens import Doc

class SqlCompliant(ABC):
    """
        Interface with a relational db.
    """
    @classmethod
    def transform_sql(cls, doc: Doc, idx_col: str, value_placeholder: str = '%s') -> tuple[str, list]:
        """
        Returns a list elements ready to be inserted into a db

        :param doc: The spacy doc object
        :param idx_col: The column to use as id
        :param value_placeholder: The type of placeholder to use (it can vary based on the client you're using)

        """
    @classmethod
    def init_sql_db(cls) -> list[str]:
        """
        Returns a list with the necessary columns to store the information extracted by this component.
        """
    @classmethod
    def get_sql_table_name(cls) -> str:
        """
        Returns the table neme of the table that should contain the information extracted by this component.
        """

class PandasCompliant(ABC):
    """
        Interface for a pd DataFrame.
    """
    @classmethod
    def init_dataframe(cls) -> pd.DataFrame:
        """
        Returns an empty dataframe with the necessary columns to store the information extracted by this component.
        """
    @classmethod
    def to_df(cls, doc: Doc, idx_col: str) -> pd.DataFrame:
        """
        Extract a dict with the ents_summary information attached to a document.

        :param doc: Spacy doc object.
        :param idx_col: the column to use as idx.
        """
    @classmethod
    def get_df_table_name(cls) -> str:
        """
        Returns the table name of the component.
        """
    @classmethod
    def to_dict(cls, doc: Doc, idx_col: str) -> list[dict]:
        """
        Extract a dict with the corpus_stats information attached to a document

        :param doc: Spacy doc object.
        :param idx_col: The column to use as idx.
        """
    @classmethod
    def get_feature_columns(cls) -> list:
        """
        Returns the pandas columns names of the feature it extracts
        """
