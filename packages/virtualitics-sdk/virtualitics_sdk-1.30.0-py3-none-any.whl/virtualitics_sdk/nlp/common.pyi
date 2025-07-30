import networkx as nx
from PIL import Image as PILImage
from virtualitics_sdk.assets.asset import AssetType as AssetType
from virtualitics_sdk.store.store_interface import StoreInterface as StoreInterface

PLOT_MARGIN_DEFAULT: int

def build_default_page(store_interface: StoreInterface, title: str, descr: str): ...
def get_assets_info(store_interface: StoreInterface, asset_type: AssetType) -> dict:
    """
    Responsible for generating asset names that are related to a specific flow execution.
    It will create the asset name using joining info like the flow id and the type of asset you're interested in.

    :param store_interface: The StoreInterface to pass metadata about the flow execution environment.
    :param asset_type: AssetType enum value (one between NLPROCESSOR, KNOWLEDGE_GRAPH, EXPLAINER)
    :param as_dict: Whether the function should return just the asset name or the whole dict for
           later retrieving the asset

    :return: str that represent the asset name or a dict that can be passed for retrieving the asset
             store_interface.get_asset(**asset_info)
    """
def crop_plot(img: PILImage, plot_margin_default_top=..., plot_margin_default_side=...): ...
def compute_topk_communities(kg: nx.Graph, community_attr: str = 'Segments', topk: int = 15): ...
def build_kg_dashboard(kg, img_obj: PILImage, graph_statistics: nx.Graph | None = None, latest_louvain: bool = False, df_columns: list | None = None, advanced: bool = False, return_topk_communities: bool = False): ...
def base_stats2infographics(kg_stats: dict, as_dict: bool = False): ...
def topk_stats2infographics(kg_stats: dict, topk: int = 16): ...
