from typing import List, NoReturn, Tuple, Dict
from collections import defaultdict
from rara_subject_indexer.config import EntityType



class NEREntity:
    """ For unifying NER Taggers' output.
    """
    def __init__(self, entity: dict):
        self.__original_entity: dict = entity
        self.__entity: str = ""
        self.__entity_type: str = ""
        self.__start: int = None
        self.__end: int = None
        self.__spans: Tuple[int, int] = ()
        self.__score: float = None
        
    def _get_value(self, keys: List[str]) -> str | int | float | None:
        value = None
        for key in keys:
            value = self.__original_entity.get(key, None)
            if value:
                break
        return value
  
    @property
    def entity(self) -> str:
        if not self.__entity:
            keys = ["text"]
            self.__entity = self._get_value(keys)
        return self.__entity
    
    @property
    def entity_type(self) -> str:
        if not self.__entity_type:
            keys = ["label", "type"]
            self.__entity_type = self._get_value(keys)
        return self.__entity_type
    
    @property
    def start(self) -> int:
        if not self.__start:
            keys = ["start_char", "start"]
            value = self._get_value(keys)
            self.__start = value if value!=None else 0
        return self.__start
    
    @property
    def end(self) -> int:
        if not self.__end:
            keys = ["end_char", "end"]
            self.__end = self._get_value(keys)
        return self.__end
    
    @property
    def spans(self) -> Tuple[int,int]:
        if not self.__spans:
            self.__spans = (self.start, self.end)
        return self.__spans
    
    @property
    def score(self) -> float | None:
        if not self.__score:
            keys = ["score"]
            self.__score = self._get_value(keys)
        return self.__score
    
    def to_dict(self) -> dict:
        """ Converts all attributes into a dictionary.
        """
        attrs = [
            "entity", "entity_type", "start", 
            "end", "spans", "score"
        ]
        entity_dict = dict(
            [
                (attr_name, getattr(self, attr_name)) 
                for attr_name in attrs
            ]
        )
        return entity_dict
    
    
class NERResult:
    def __init__(
            self, 
            entities: List[NEREntity], 
            entity_type_map: dict,
            clusterers,
    ) -> NoReturn:
        self.entities = entities
        self.entity_type_map = entity_type_map
        self.clusterers = clusterers
        
        self.__entity_clusters: Dict[str, list] = {}
        self.__entity_clusters_dict = {}
        self.__clusters: dict = {}
        
        self.__persons: dict = {}
        self.__organizations: dict = {}
        self.__locations: dict = {}
        self.__titles: dict = {}
        self.__dates: dict = {}
            
            
    def _parse_clusters(self, cluster: Dict[str, List[str]]) -> Dict[str, int]:
        """ Reformats clusters from str: List[str] to str: int.
        
        Parameters
        -----------
        cluster: Dict[str, List[str]]
            Cluster of entities in following format:
            key = base entity, values = variations of this
            entity detected with NER, e.g: 
            {"Uku Tamm": ["Tamm", "Uku Tamm", "Uku Tammele"]}
            
        Returns
        ----------
        parsed_clusters: Dict[str, int]
            Clusters, where values of entity lists are replaced with counts, 
            e.g: {"Uku Tamm": 3}
   
        """
        parsed_clusters = {
            entity: len(matches) 
            for entity, matches in list(cluster.items())
        }
        return parsed_clusters
            
    @property
    def clusters(self) -> Dict[str, List[dict]]:
        """ Returns clusters, where key = entity type and
        value = list of entities as dicts.
        """
        if not self.__clusters:
            for entity_type, entities in self.entity_clusters.items():
                clusterer = self.clusterers.get(entity_type, {})
                if clusterer:
                    self.__clusters[entity_type] = self._parse_clusters(
                        clusterer.cluster(entities)
                    )
                else:
                    self.__clusters[entity_type] = {}
        return self.__clusters

    @property
    def entity_clusters(self) -> Dict[str, List[str]]:
        """ Cluster NER results based on entity types 
        Cluster key = entity type, values = list of entity values.
        """
        if not self.__entity_clusters:
            _entity_clusters = defaultdict(list)
            for ner_entity in self.entities:
                original_label = ner_entity.entity_type
                value = ner_entity.entity
                unified_label = self.entity_type_map.get(original_label, "UNK")
                _entity_clusters[unified_label].append(value)
            self.__entity_clusters = dict(_entity_clusters)
        return self.__entity_clusters
    
    @property
    def entity_clusters_dict(self) -> Dict[str, List[dict]]:
        """ Cluster NER results based on entity types.
        Cluster key = entity type, values = list of entities as 
        NEREntity dicts.
        """
        if not self.__entity_clusters_dict:
            _entity_clusters = defaultdict(list)
            for ner_entity in self.entities:
                original_label = ner_entity.entity_type
                value = ner_entity.to_dict()
                unified_label = self.entity_type_map.get(original_label, "UNK")
                _entity_clusters[unified_label].append(value)
            self.__entity_clusters_dict = dict(_entity_clusters)
        return self.__entity_clusters_dict
               
    @property
    def persons(self) -> Dict[str, int]:
        if not self.__persons:
            self.__persons = self.clusters.get(EntityType.PER, {})
        return self.__persons
                           
    @property
    def organizations(self) -> Dict[str, int]:
        if not self.__organizations:
            self.__organizations = self.clusters.get(EntityType.ORG, {})
        return self.__organizations
      
    @property
    def titles(self) -> Dict[str, int]:
        if not self.__titles:
            self.__titles = self.clusters.get(EntityType.TITLE, {})
        return self.__titles
    
    @property
    def locations(self) -> Dict[str, int]:
        if not self.__locations:
            self.__locations = self.clusters.get(EntityType.LOC, {})
        return self.__locations 
    
    @property
    def dates(self) -> Dict[str, int]:
        if not self.__dates:
            self.__dates = self.clusters.get(EntityType.DATE, {})
        return self.__dates