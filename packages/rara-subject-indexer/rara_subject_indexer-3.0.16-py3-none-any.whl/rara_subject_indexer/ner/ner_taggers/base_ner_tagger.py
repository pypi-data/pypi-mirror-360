import abc
from rara_subject_indexer.ner.ner_result import NEREntity
from typing import List

class BaseNERTagger:
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def apply(self) -> List[NEREntity]:
        pass
    
    