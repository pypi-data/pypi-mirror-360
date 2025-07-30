from _typeshed import Incomplete
from virtualitics_sdk.nlp.corpus_stats import CorpusStats as CorpusStats
from virtualitics_sdk.nlp.entity_extractor import NerSummarization as NerSummarization
from virtualitics_sdk.nlp.event_extractor import EventExtractor as EventExtractor

to_init: Incomplete
registered_components: Incomplete

def init_custom_components(components: list[EventExtractor | NerSummarization | CorpusStats]):
    """
    Register spacy components.
    At the moment it works only on the english language.

    :param components: List of classes.

    """
