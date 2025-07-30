import pandas as pd
from _typeshed import Incomplete
from enum import Enum
from matplotlib.figure import Figure
from predict_backend.validation.type_validation import validate_types
from virtualitics_sdk.assets.asset import Asset as Asset, AssetType as AssetType
from virtualitics_sdk.assets.dataset import DataEncoding as DataEncoding, Dataset as Dataset
from virtualitics_sdk.assets.model import Model as Model
from virtualitics_sdk.elements.image import Image as Image
from virtualitics_sdk.elements.waterfall_plot import WaterfallPlot as WaterfallPlot
from virtualitics_sdk.page.card import Card as Card
from virtualitics_sdk.utils.types import ExtendedEnum as ExtendedEnum

logger: Incomplete

class NLPExplanationMethod(ExtendedEnum):
    LIME: str
    SHAP: str

class ExplanationTypes(ExtendedEnum):
    REGRESSION: str
    CLASSIFICATION: str

class InstanceSelectionMethod(ExtendedEnum):
    SMART: str
    MANUAL: str

class InstanceSet(Enum):
    UNCERTAIN_HIT: str
    UNCERTAIN_MISS: str
    CERTAIN_HIT: str
    CERTAIN_MISS: str

class ExplainerReturnTypes(ExtendedEnum):
    CARDS: str
    IMAGES: str
    PLOTS: str

HASH_ENCODING: Incomplete

class Explainer(Asset):
    '''
    The explainer class aims to take in a model and a dataset and allow the user to easily make NLP and graphical explanations
    of the model\'s behavior. This is primarily done through explaining the importance of different features for a specific
    instance\'s prediction. 

    :param model: A machine learning model. For a classifier, the model must have a ``predict_proba`` function and for regression the
                model must have a ``predict`` function. The data input type to the model is assumed to be the same as the input
                data itself.
    :param training_data: The training set that is used by the explainers. It is recommended to use the same dataset that the model was
            trained on. The dataset should also have been created with any necessary additional parameters to make sure that data conversion
            to ``\'ordinal\'`` encoding is possible (especially if the dataset is one hot encoded).

    :param mode: The type of model and corresponding explanation. Must be either ``\'classification\'`` or ``\'regression\'``.
    :param label: Label for :class:`~virtualitics_sdk.assets.asset.Asset`, see its documentation for more details.
    :param name: Name for :class:`~virtualitics_sdk.assets.asset.Asset`, see its documentation for more details.
    :param feature_names: List of the names of features in the dataset training_data. If feature_names is None, they are inferred from the column
                    names of training_data.
    :param output_names: List of names of output of the model. For classifiers, output_names should be the names of each class output of
                    the model\'s predict_proba function. For regressors, output_names should be a singleton list of the name of the
                    target. If output_names is none, a non-descriptivie output name is used.
    :param explain_class: Only used for classification explainers. This is the index of the model\'s output class which needs to be explained.
    :param kernel_width: Hyperparameter for LimeTabularExplainer. Please refer to lime\'s documentation for details.
    :param use_shap: Boolean to initialize the shap explainer.
    :param use_lime: Boolean to initialize the lime explainer.
    :param n_classes: Only used for classification explainers. Number of output classes of the model\'s predict_proba function.
    :param version: Version of :class:`~virtualitics_sdk.assets.asset.Asset`, see its documentation for more details.
    :param metadata: :class:`~virtualitics_sdk.assets.asset.Asset` metadata, see its documentation for more details.
    
    **EXAMPLE:**

       .. code-block:: python
       
           # Imports
           from virtualitics_sdk import Explainer
           . . .
           # Example usage
           data_train = store_interface.get_dataset(label="example", name="data train")
           train_mins = data_train.get_object().min()
           train_maxs = data_train.get_object().max()
           bounds = {key: [train_mins[key], train_maxs[key]] for key in data_train.get_object().columns}
           data_test = store_interface.get_dataset(label="example", name="data test")
           data_attributes = store_interface.get_input("Data Attributes")
           graph_data = store_interface.get_dataset(label="example", name="graph data")
           kmeans_anomaly = store_interface.get_model(label="example", name="kmeans")
           # explain instance
           explainer = Explainer(model=kmeans_anomaly, training_data=data_train, 
                                label="example code", name="kmeans explainer",
                                feature_names=data_attributes[\'features\'],
                                output_names=[\'Normal\', \'Anomaly\'], 
                                mode=\'classification\', explain_class=1, kernel_width=0.5,
                                use_shap=True)
    '''
    seed: Incomplete
    n_classes: Incomplete
    explain_class: Incomplete
    kernel_width: Incomplete
    instance_sets: dict[str, pd.DataFrame]
    use_shap: Incomplete
    use_lime: Incomplete
    performed_smart_instance_selection: bool
    trained_data_likelihood_model: bool
    @validate_types
    def __init__(self, model: Model, training_data: Dataset, mode: str | ExplanationTypes, label: str, name: str, feature_names: list[str] | None = None, output_names: list[str] | None = None, explain_class: int = 1, kernel_width: float | None = None, use_shap: bool = False, use_lime: bool = False, n_classes: int = 2, description: str | None = None, version: int = 0, metadata: dict | None = {}, seed: int | None = None, **kwargs) -> None: ...
    def check_shap_usage_(self) -> None: ...
    def check_lime_usage_(self) -> None: ...
    mode: Incomplete
    def initialize_explanation_mode(self, exp_type: str | ExplanationTypes) -> None: ...
    model: Incomplete
    training_data: Incomplete
    def initialize_model(self, model: Model | None, training_data: Dataset | None): ...
    categorical_names: Incomplete
    feature_names: Incomplete
    categorical_idx: Incomplete
    def initialize_encodings(self, feature_names: list[str] | None = None) -> None: ...
    output_names: Incomplete
    def initialize_output_names(self, output_names: list[str] | None = None) -> None: ...
    dataset_stats: Incomplete
    def initialize_dataset_model_stats(self) -> None: ...
    def initialize_explainers(self) -> None: ...
    def lime_target_func(self, x): ...
    lime_explainer: Incomplete
    lime_value_cache: Incomplete
    lime_explainer_train_time_: Incomplete
    def initialize_explainer_lime(self) -> None: ...
    def shap_target_func(self, x, preprocess: bool = True): ...
    shap_output_names: Incomplete
    shap_value_cache: Incomplete
    shap_explainer: Incomplete
    shap_explainer_train_time_: Incomplete
    def initialize_explainer_shap(self) -> None: ...
    def model_preprocess(self, X: pd.DataFrame) -> pd.DataFrame: ...
    def filter_features(self, X: pd.DataFrame, encoding: str | DataEncoding | None = None) -> pd.DataFrame: ...
    def smart_instance_selection(self, data: pd.DataFrame | Dataset, n: int = 10, encoding: str | DataEncoding | None = None): ...
    last_spt_explanation: Incomplete
    def explain(self, data: pd.DataFrame | Dataset | None = None, indices: list | None = None, method: str | InstanceSelectionMethod = 'manual', n: int = 10, encoding: str | DataEncoding | None = None, titles: list[str] = None, instance_sets: list[str] = [], num_features_explain: int = 3, nlp_explanation_method: str | NLPExplanationMethod = 'shap', return_as: str = 'plots', waterfall_positive: str | None = None, waterfall_negative: str | None = None, expected_title: str | None = None, predicted_title: str | None = None, top_n: int | None = None, show_title: bool = True, show_description: bool = True) -> list['Image'] | list['Card'] | list['WaterfallPlot']:
        '''Takes in a list of instances and returns a list of cards/images of explanations for each instance. Can also be used to perform smart instance
        selection and describe specific interesting subsets of the input data.

        :param data: Set of data which can be explained. In the case of manual instance selection method, instances are explailned directly from this dataset.
                     The entire dataset will be used unless \'indices\' is also specified, in which case only a subset will be used. In the case
                     of smart instance selection method, this dataset is used to identify relevant subsets of the data according to different criteria. If
                     smart instance selection is performed once, this argument does not need to be specified in subsequent explanations using the smart
                     instance selection method, defaults to None.
        :param indices: Indices of \'data\' to be used in either manual or smart instance selection methods, defaults to None.
        :param method: Can be either \'manual\' or \'smart\'. If \'manual\', the entire \'data\' dataframe will be explained. If \'smart\', smart instance selection is
                       performed. Relevant instance sets which are explaiend can be specified using the \'instance_sets\' argument. defaults to \'smart\'.
        :param n: Parameter for smart instance selection. Number of instances to put in each identified subset, defaults to 10.
        :param encoding: Encoding of \'data\', can be \'ordinal\', \'verbose\', or \'one_hot\'. If not specified, \'data\' is assumed to be in the same encoding format as
                         the model as specified in this classes constructor, defaults to None.
        :param titles: Title of the returned images or cards. If not specified but instance_sets is specified, instance_sets are used as the title instead.
                       Otherwise, non-descriptive titles are used., defaults to None.
        :param instance_sets: Names of subsets to explain created by smart instance selection. Only used when method is \'smart\', defaults to [].
        :param num_features_explain: Number of features to include in the NLP explanation of the instance, defaults to 3.
        :param nlp_explanation_method: Type of NLP explanation to use. Can be either LIME or SHAP. Output explanation will be ordered by the feature importances
                                       attributed by the corresponding explainer, defaults to \'shap\'.
        :param return_as: String to determine whether to return the output as "cards" or "images" or "plots", defaults to "plots".
        :param waterfall_positive: The color of the positive waterfall plot bars, defaults to "#3B82F6".
        :param waterfall_negative: The color of the positive waterfall plot bars, defaults to "#EF4444".
        :param expected_title: The expected title to show for the generated plot from this dashboard, defaults to "Expected Value".
        :param predicted_title: The predicted title to show for the generated plot from this dashboard, defaults to "Final Prediction".
        :param top_n: If set, only return the top N most significant values in the waterfall plot, defaults to None.
        :param show_title: Whether to show the title on the page when rendered, defaults to True.
        :param show_description: Whether to show the description to the page when rendered, defaults to True.
        :raises ValueError: If top_n is an invalid number.
        :raises NotImplementedError: if return_type is not yet supported.
        :return: List of plots/cards/images of explanation of input instances.
        '''
    def pick_instance(self, instance_set, n_pick: int = 1): ...
    @staticmethod
    def make_model_regressor(model_name: str, **kwargs): ...
    def get_shap_explanation(self, instance, encoding: str | None = None): ...
    def get_lime_explanation(self, instance, encoding: str | None = None, n_explanation_features: int = 10, model_name: str = 'BayesianRidge', **kwargs): ...
    def get_text_explanation(self, instance, encoding: str | DataEncoding | None = None, num_features_explain: int = 1, explanation_method: str | NLPExplanationMethod = 'shap', include_importance: bool = True) -> str: ...
    def get_feature_explanation(self, instance, encoding: str | DataEncoding | None = None, explanation_method: str | NLPExplanationMethod | None = None, include_importance: bool = True) -> dict[str, str]:
        """Returns a dictionary mapping feature names to explanations of the relationship to the rest of the training dataset.
           For example, a numerical feature will be described using the quantile it falls under.

        :param instance: The instance for which the function finds the likelihood.
                         Should have all the same features as instances from the training dataset.
        :param encoding: The encoding that the given instance is in.
                         If None, assumes that it is the same encoding as the training dataset. Defaults to None.
        :param explanation_method: The method by which to create an NLP explanation, defaults to  NLPExplanationMethod.SHAP.
        :param include_importance: If true, adds an additional string which describes the impact the feature made on the prediction, defaults to True.
        :return: A dictionary mapping feature names to their explanation strings.
        """
    def plot_waterfall_instance(self, instance, encoding: str | DataEncoding | None = None) -> Figure: ...
    lof: Incomplete
    def train_data_likelihood_model(self, retrain: bool = False, *args, **kwargs) -> None: ...
    def get_data_likelihood(self, instance, encoding: str | DataEncoding | None = None) -> str:
        '''Returns a string indicating the likelihood of the given instance occuring in the training dataset.

        :param instance: The instance for which the function finds the likelihood.
                         Should have all the same features as instances from the training dataset.
        :param encoding: The encoding that the given instance is in.
                         If None, assumes that it is the same encoding as the training dataset. Defaults to None.
        :return: One of two strings, "Unlikely" or "Likely"
        '''
    def show_significant_vars(self, instance, encoding: str | DataEncoding | None = None, title: str = ''): ...
    @staticmethod
    def get_waterfall_explanation(): ...
    def get_instance_hash(self, instance, encoding: str | None = None): ...
    def replace_dataset(self, new_dataset: Dataset, suffix: str = '_copy') -> Explainer: ...
