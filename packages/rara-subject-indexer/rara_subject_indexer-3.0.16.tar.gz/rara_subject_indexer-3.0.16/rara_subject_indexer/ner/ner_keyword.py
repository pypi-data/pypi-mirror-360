from typing import List, Dict, NoReturn
from enum import Enum
from rara_subject_indexer.ner.ner_result import NERResult
from rara_subject_indexer.config import (
    SUBJECT_INDEX_MAP, LOGGER, EnsembleStrategy, NERMethod
)

class Keyword:
    def __init__(self, value: str, count: int, 
                 method: str, max_count: int, entity_type: str
    ) -> NoReturn:
        self.value: str = value
        self.method: str = method.value if isinstance(method, Enum) else method
        self.count: int = count
        self.max_count: int = max_count
        self.entity_type: str = entity_type
        self.__score: float | None = None
        self.__keyword_type: str = ""          
            
    @property
    def score(self) -> float:
        if not self.__score:
            self.__score = round(self.count/float(self.max_count),2)
        return self.__score
    
    @property
    def keyword_type(self) -> str:
        if not self.__keyword_type:
            keyword_type = SUBJECT_INDEX_MAP.get(self.entity_type)
            self.__keyword_type = keyword_type.value if isinstance(keyword_type, Enum) else keyword_type
        return self.__keyword_type
    
    def to_dict(self) -> dict:
        keyword_dict = {
            "keyword": self.value,
            "entity_type": self.keyword_type,
            "score": self.score,
            "count": self.count,
            "method": self.method
        }
        return keyword_dict

    
class Keywords:
    def __init__(self, ner_results: Dict[str, NERResult], method_map: dict, ensemble_strategy: str):
        """
        Parameters
        -----------
        keywords: Dict[str, dict]
            Dictionary of extracted entities, where key=entity_type and
            values = dict with keys 'values' and 'method',
            where type 'method': str and type 'values': dict.
            Example: {
                "PER": {
                    "values": {
                        "Jaan Tamm": 7, 
                        "Uku Saar": 3
                     }, 
                     "method": "ensemble"
                }
        """
        self.ensemble_strategy: str = ensemble_strategy
        self.ner_results: dict = ner_results
        self.method_map: dict = method_map
            
        self.__raw_keywords: Dict[str, dict] = {}
        self.__keywords: List[dict] = []
        self.__filtered_keywords: List[dict] = []
     
    def _get_max_count(self, result: dict) -> int:
        counts = list(result.get("values").values())
        max_count = max(counts) if counts else 0
        return max_count
       
                               
    def _merge_different_method_outputs(
        self, 
        entity_type: str,
        ner_results: Dict[str, NERResult]
    ) -> Dict[str, List[str]]:
        """ Merges output of Stanza and GLiNER models
        for entities using method `ensemble`.

        Parameters
        -----------
        TODO: Update this!
        entities_per_method: Dict[str, dict]
            Dictionary where key = method (e.g. 'stanza') and
            values = output of the method formatted as dicts, where
            keys = extracted entities and values = counts of the entity,
            e.g. {"Lennart Meri": 7, "Arnold Rüütel: 2}
        """
        entities_per_method = {
            method: result.clusters.get(entity_type, {})
            for method, result in ner_results.items()
        }
        LOGGER.debug(
            f"Filtered only relevant entities for entity type '{entity_type}' "\
            f"{entities_per_method}."
        )

        merged = {}

        entities_per_method_list = list(entities_per_method.values())
        base_dict = entities_per_method_list[0]

        for d in entities_per_method_list[1:]:
            for value, count in list(d.items()):
                if value in merged:
                    prev_count = merged.get(value)
                elif value in base_dict:
                    prev_count = base_dict.get(value)
                else:
                    base_dict[value] = count
                    continue

                if self.ensemble_strategy == EnsembleStrategy.INTERSECTION:
                    new_count = min(count, prev_count)
                else:
                    new_count = max(count, prev_count)
                merged[value] = new_count
                
        # If ensemble strategy == Union, add all the values 
        # from base dict that have not yet been added:
        if self.ensemble_strategy == EnsembleStrategy.UNION:
            for value, count in list(base_dict.items()):
                if value not in merged:
                    merged[value] = count
        LOGGER.debug(
            f"Merged results for entity type '{entity_type}':\n{merged}."
        )
        return merged
    
    @property
    def raw_keywords(self):
        if not self.__raw_keywords:
            for entity_type, method in list(self.method_map.items()):
                if method != NERMethod.ENSEMBLE:
                    results = self.ner_results.get(method).clusters.get(entity_type, {})

                else:
                    results = self._merge_different_method_outputs(
                        entity_type=entity_type,
                        ner_results=self.ner_results
                    )

                LOGGER.debug(
                    f"Results for entity_type='{entity_type}' "\
                    f"and method='{method}':\n{results}."
                )

                self.__raw_keywords[entity_type] = {
                    "values": results,
                    "method": method
                }
        return self.__raw_keywords
            
    @property 
    def keywords(self) -> List[Keyword]:
        if not self.__keywords:
            for entity_type, result in list(self.raw_keywords.items()):
                method = result.get("method")
                max_count = self._get_max_count(result)
            
                for value, count in list(result["values"].items()):
                    new_keyword = Keyword(
                        value=value, 
                        count=count, 
                        method=method, 
                        max_count=max_count,
                        entity_type=entity_type
                    )
                    self.__keywords.append(new_keyword)
        return self.__keywords
    
    
    def filter_keywords(self, min_score: float = 0.5,
                        min_count: int = 2
    ) -> List[dict]:
        _filtered_keywords = []
        if self.keywords:
            for keyword in self.keywords:
                if (
                    keyword.score >= min_score and 
                    keyword.count >= min_count
                ):
                    _filtered_keywords.append(keyword)
        _filtered_keywords.sort(key=lambda x: x.score, reverse=True)
        filtered_keywords = [
            kw.to_dict() 
            for kw in _filtered_keywords
        ]
        return filtered_keywords
      
    