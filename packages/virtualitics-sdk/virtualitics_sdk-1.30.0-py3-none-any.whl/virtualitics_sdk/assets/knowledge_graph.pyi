import networkx as nx
import pandas as pd
import scipy
from _typeshed import Incomplete
from predict_backend.validation.type_validation import validate_types
from sklearn.feature_extraction.text import TfidfVectorizer
from virtualitics_sdk.app.flow_metadata import FlowMetadata as FlowMetadata
from virtualitics_sdk.assets.asset import Asset as Asset, AssetType as AssetType
from virtualitics_sdk.assets.language_processor import LanguageProcessor as LanguageProcessor
from virtualitics_sdk.nlp.common import get_assets_info as get_assets_info
from virtualitics_sdk.utils.tqdm import StepProgressTqdm as StepProgressTqdm

def tokenizer(x): ...
def preprocessor(x): ...

class TfIdfBasedKG(Asset):
    '''Provide an interface to create, store and manipulate a TF-IDF based knowledge graph.
    It extends Asset, so that it can be stored and retrieved from the store.
    It also uses the Store to independently store internal assets like the created TF-IDF model,
    the KG corpus and finally the feature matrix generated with the TF-IDF model. This means that
    if you want to get the TF-IDF model you should use the provided getter that will query the
    store and return the original object. 
    
    :param asset_label: Asset parameter
    :param asset_name: Asset parameter
    :param asset_metadata: Asset parameter
    :param asset_version: Asset parameter
    :param min_df: TF-IDF model parameter
    :param max_df: TF-IDF model parameter
    :param description: Asset parameter
    :param stopwords: TF-IDF model parameter

    **EXAMPLE:**

       .. code-block:: python
       
           # Imports 
           from virtualitics_sdk import TfIdfBasedKG
           . . .
           # Example usage
           store_interface = StoreInterface(**flow_metadata)
           # Knowledge Graph
           tfidf_basedkg = TfIdfBasedKG(asset_label="label", asset_name="name", min_df=2)
    '''
    doc2ids: Incomplete
    kg: Incomplete
    doc_ids: Incomplete
    min_df: Incomplete
    max_df: Incomplete
    stopwords: Incomplete
    tfidf_model_id: Incomplete
    corpus_id: Incomplete
    corpus_vectors_id: Incomplete
    @validate_types
    def __init__(self, asset_label: str, asset_name: str, asset_metadata: dict | None = None, asset_version: int | float = 1, min_df: int = 1, max_df: float = 1.0, description: str | None = None, stopwords: list[str] | None = None, **kwargs) -> None: ...
    def set_tfidif_model(self, tfidf_model: TfidfVectorizer):
        """Store the TF-IDF model in the persistence and save its id as object param

        :param tfidf_model: Sklearn tfidf model
        """
    def get_tfidif_model(self) -> TfidfVectorizer:
        """Retrieve from the store persistence the TF-IDF model and returns it

        :return: tf-idf model
        """
    def set_kg_corpus(self, corpus: pd.DataFrame):
        """Store the kg corpus in the persistence and save its id as object param

        :param corpus: The corpus to store
        """
    def get_kg_corpus(self) -> pd.DataFrame:
        """Retrieve from the store persistence the KG corpus and returns it

        :return: The stored kg corpus
        """
    def set_f_vectors(self, feature_vectors) -> None:
        """Store the kg feature vectors in the persistence and save its id as object param

        :param feature_vectors: sparse matrix
        """
    def get_f_vectors(self):
        """Retrieve from the store persistence the feature vector matrix and returns it

        :return: sparse matrix
        """
    def compute_nlp_feature_vectors(self, nlp_module: LanguageProcessor, return_out: bool = False) -> tuple[TfidfVectorizer, scipy.sparse.csr_matrix] | None:
        """Create a TF-IDF model using the extracted features stored in the nlp_module object.
        This function can be used outside the context of the asset, using the return_out
        parameter.

        :param nlp_module: used to retrieve the feature in order to build a TF-IDF model
        :param return_out: control whether store in the Asset the outputs or return them
        :return: If return_out, return the created TF-IDF model and feature vector matrix
        """
    def construct_knowledge_graph(self, nlp_module, similarity_threshold, drop_singletons: bool = False, num_top_entities: int = 10, num_top_events: int = 5, include_nlp_features: bool = True, save_kg: bool = False) -> nx.Graph | None: ...
    def add_extra_features(self, kg: nx.Graph, corpus_vectors, feature_names: list[str], nlp_module: LanguageProcessor, num_top_entities: int = 10, num_top_events: int = 5) -> nx.Graph:
        """Add extra (from the original dataset) features to the kg nodes

        :param kg: The input networkX graph
        :param corpus_vectors: Sparse Matrix
        :param feature_names: List of feature names
        :param nlp_module: LanguageProcessor from which extract the extra features
        :param num_top_entities: Number of top-entities to add to every node
        :param num_top_events: Number of top-events to add to every node
        :return: The networkX object with the augmented nodes

        """

def similarity_threshold_experiment(tfidf_basedkg: TfIdfBasedKG | None, nlp_module: LanguageProcessor, thresholds: list[float], flow_metadata: FlowMetadata | None = None, starting_progress: int | float | None = None, target_progress: int | float | None = None, tfidf_model: TfidfVectorizer | None = None, corpus_vectors: Incomplete | None = None) -> tuple[Asset, pd.DataFrame]:
    """Compute a Similarity Threshold experiment. For testing purpose or to work with this function outside VAIP
    you can use this function passing a tfidf_model and corpus_vectors params instead of a tfidf_basedkg object.
    This let you store them in memory or somewhere and not use the store interface

    :param tfidf_basedkg: Optional. TfIdfBasedKG object
    :param tfidf_model: TF-IDF model, in order to extract the feature names
    :param nlp_module: LanguageProcessor
    :param thresholds: Thresholds to use in the Similarity Threshold experiment
    :param flow_metadata: The flow_metadata dict
    :param starting_progress: Base progress percentage
    :param target_progress: Target progress percentage
    :param tfidf_model: TF-IDF model, in order to extract the feature names
    :param corpus_vectors: Sparse matrix with the score for every doc and feature
    :return: Return a Tuple with the experiment asset and an output pandas DataFrame
    """
def compute_opt_sim_mat(corpus_vectors):
    """It computes the matrix's lower triangle filtering out everything below the diagonal (included).
    This way we only have (a,b) and we filter out (b,a), (a,a), (b,b).

    :param corpus_vectors: Sparse matrix.
    :return: Coo Scipy sparse matrix.
    """
def get_ranked_nlp_features(feature_index, feature_vector_mapping, feature_names): ...
def analyze_entity_proportions(tf_idf_kg: TfIdfBasedKG, nlp_module: LanguageProcessor, feature: str = 'Segments', min_group_entity_count: int = 10, min_group_entity_total: int = 10, min_complement_group_entity_count: int = 3, min_complement_group_entity_total: int = 10, entity_ratio_difference: float = 0.3, alpha: float = 0.05, apply_bonferroni_correction: bool = False, verbose: bool = False):
    """Apply the difference of proportions test to identify, for each feature value,
    those entities that appear in a higher proportion of documents associated with
    that feature value than do appear in all the other documents in the corpus.
    """
def difference_of_proportion_test(p1, n1, p2, n2, verbose: bool = False):
    """A two-tailed difference of proportion test - for more details, see:
    https://stattrek.com/hypothesis-test/difference-in-proportions.aspx
    """
