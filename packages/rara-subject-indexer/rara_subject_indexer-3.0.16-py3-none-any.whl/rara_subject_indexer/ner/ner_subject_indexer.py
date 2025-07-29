from rara_subject_indexer.ner.ner_taggers.stanza_ner_tagger import StanzaNERTagger
from rara_subject_indexer.ner.ner_taggers.gliner_tagger import GLiNERTagger
from rara_subject_indexer.ner.ner_result import NEREntity, NERResult
from rara_subject_indexer.ner.ner_keyword import Keywords
from rara_subject_indexer.utils.clusterers.per_clusterer import PersonaClusterer
from rara_subject_indexer.utils.clusterers.org_clusterer import OrganizationClusterer
from rara_subject_indexer.utils.clusterers.loc_clusterer import LocationClusterer
from rara_subject_indexer.utils.clusterers.title_clusterer import TitleClusterer
from rara_subject_indexer.utils.text_splitter import TextSplitter
from rara_subject_indexer.utils.text_preprocessor import TextPreprocessor, ProcessedText
from rara_subject_indexer.config import (
    STANZA_CONFIG, GLINER_CONFIG, DEFAULT_NER_METHOD_MAP, ALLOWED_NER_METHODS,
    ENTITY_TYPE_MAPS, LOGGER, EnsembleStrategy, NERMethod, EntityType, SplitMethod
)

from typing import List, Dict, NoReturn
import logging
import os
import numpy as np

     

class NERIndexer:
    def __init__(self, 
            stanza_config: dict = STANZA_CONFIG,
            gliner_config: dict = GLINER_CONFIG,
            method_map: dict = DEFAULT_NER_METHOD_MAP,
            download_resources: bool = False,
            **kwargs
    ):
        """ Initializes NERIndexer instance.
        
        Parameters
        -----------
        stanza_config: dict
            Arguments to use while creating a new StanzaNERTagger instance.
        gliner_config: dict
            Arguments to use while creating a new GLiNERTagger instance.
        method_map: dict:
            Map of methods to use per entity type. 
            key = entity_type (e.g. "PER") and 
            value = Method to use for extracting that type
                of entity. Currently supported options are
                "stanza", "gliner" and "ensemble", which
                combines the results of both methods.
        download_resources: bool
            If enabled, necessary stanza and gliner resources are
            downloaded.
        """
        
        if download_resources:
            NERIndexer.download_model_resources()
 
        self.method_map: dict = method_map
        self.stanza_config: dict = stanza_config
        self.gliner_config: dict = gliner_config
            
            
            
        for entity_type, method in list(self.method_map.items()):
            if method not in ALLOWED_NER_METHODS:
                raise ValueError(
                    f"Selected method '{method}' for entity type '{entity_type}'is not allowed. \
                    Supported methods are: {ALLOWED_NER_METHODS}."
                )
            
        self.__methods: List[str] = []
        self.__base_methods: List[str] = []
        self.__stanza_ner_tagger: StanzaNERTagger | None = None
        self.__gliner_tagger: GLiNERTagger | None = None
        self.__text_splitter: TextSplitter | None = None
        self.__tagger_map: dict = {}
        self.__clusterers: dict = {}
            
        self.ner_result: Dict[str, NERResult] = {}
        self.keywords: Keywords | None = None
        self.text: str = ""


    @property
    def methods(self) -> List[str]:
        """ Returns all supported methods for
        entity extraction.
        """
        if not self.__methods:
            self.__methods = list(set(self.method_map.values()))
        return self.__methods
    
    @property
    def base_methods(self) -> List[str]:
        """ Returns all base methods for entity
        extraction ("ensemble" is excluded).
        """
        if not self.__base_methods:
            self.__base_methods = list(
                set(self.methods)-set([NERMethod.ENSEMBLE])
            )
        return self.__base_methods
    
    @property
    def tagger_map(self) -> dict:
        if not self.__tagger_map:
            if (
                NERMethod.STANZA in self.methods or 
                NERMethod.ENSEMBLE in self.methods
            ):
                self.__tagger_map[NERMethod.STANZA] = self.stanza_ner_tagger
                
            if (
                NERMethod.GLINER in self.methods or 
                NERMethod.ENSEMBLE in self.methods
            ):
                self.__tagger_map[NERMethod.GLINER] = self.gliner_tagger
        return self.__tagger_map
    
    @property
    def stanza_ner_tagger(self) -> StanzaNERTagger:
        if not self.__stanza_ner_tagger:
            LOGGER.debug(
                f"Initiating Stanza NER Tagger with the " \
                f"following configuration: {self.stanza_config}."
            )
            self.__stanza_ner_tagger = StanzaNERTagger(**self.stanza_config)
        return self.__stanza_ner_tagger
    
    @property
    def gliner_tagger(self) -> GLiNERTagger:
        if not self.__gliner_tagger:
            LOGGER.debug(
                f"Initiating GLiNER Tagger with the " \
                f"following configuration: {self.gliner_config}."
            )
            self.__gliner_tagger = GLiNERTagger(**self.gliner_config)
        return self.__gliner_tagger 
    
    @property
    def clusterers(self) -> dict:
        if not self.__clusterers:
            self.__clusterers = {
                EntityType.PER: PersonaClusterer(),
                EntityType.ORG: OrganizationClusterer(),
                EntityType.TITLE: TitleClusterer(),
                EntityType.LOC: LocationClusterer(),
                EntityType.EVENT: TitleClusterer()
            }
            LOGGER.debug(
                f"Loaded clusterers for the following entity types:" \
                f"{list(self.__clusterers.keys())}."
            )
        return self.__clusterers
    
    @property
    def text_splitter(self) -> TextSplitter:
        # Text splitting is necessary for GLiNER as 
        # its input size is limited.
        if not self.__text_splitter:
            self.__text_splitter = TextSplitter(
                split_by=SplitMethod.WORD_LIMIT, 
                word_limit=200
            )
        return self.__text_splitter
        
           
    @staticmethod
    def download_model_resources(
        stanza: bool = True, gliner: bool = True, resource_dir: str = "",
        stanza_supported_languages: List[str] = STANZA_CONFIG["supported_languages"], 
        stanza_custom_ner_model_urls: dict = STANZA_CONFIG["custom_ner_models"],
        stanza_custom_ner_model_langs: List[str] = STANZA_CONFIG["custom_ner_model_langs"], 
        gliner_model_name: str = GLINER_CONFIG["model_name"]
    ) -> NoReturn:
        """ Downloads relevant resources for running Stanza and/or
        GLiNER models.
        
        Parameters
        -----------
        stanza: bool
            If enabled, all relevant Stanza resources defined 
            in self.stanza_config are downloaded.
            
        gliner: bool
            If enabled, all relevant GLiNER resources defined
            in self.gliner_config are downloaded.
            
        """
        LOGGER.info(f"Downloading relevant resources for NER Subject Indexer...")
        if stanza:
            StanzaNERTagger.download_stanza_resources(
                resource_dir = resource_dir if resource_dir else STANZA_CONFIG["resource_dir"], 
                supported_languages=stanza_supported_languages
            )
            StanzaNERTagger.download_custom_ner_models(
                resource_dir= resource_dir if resource_dir else STANZA_CONFIG["resource_dir"], 
                custom_ner_model_urls=stanza_custom_ner_model_urls,
                model_langs=stanza_custom_ner_model_langs
            )
        if gliner:
            GLiNERTagger.download_gliner_resources(
                resource_dir=resource_dir if resource_dir else GLINER_CONFIG["resource_dir"],
                model_name=gliner_model_name
            )
    
   
    def _apply_taggers(self, text: str, lang: str = "") -> Dict[str, NERResult]:
        """
        Apply all taggers that have been selected for extracting
        at least one type of entity and store the results per method 
        in a dictionary.
        
        Parameters
        -----------
        text: str
            Text from where to extract entites.
        lang: str
            Language of the input text.
            
        Returns
        -----------
        results: Dict[str, NERResult]
            Results formatted as dict, where
            key = extraction method ("stanza", "gliner") and
            value = Extracted entities as a NERResult instance.
        """
        method_kwargs = {
            NERMethod.STANZA: {"lang": lang},
            NERMethod.GLINER: {}  
        }
        text_splits = {
            NERMethod.STANZA: [text],
            NERMethod.GLINER: []
        }
        
        # GLiNER has limited input length and thus extracting 
        # from longer texts requires previous text chunking
        if (
            NERMethod.GLINER in self.methods or 
            NERMethod.ENSEMBLE in self.methods
        ):
            text_chunks = self.text_splitter.split(text) 
            text_splits[NERMethod.GLINER] = text_chunks
            LOGGER.debug(f"Split input text into {len(text_chunks)} chunks for GLiNER.")
                     
        results = {}
        
        # Apply all taggers that have been selected for extracting
        # at least one type of entity and store the results
        # per method in a dictionary
        for method, tagger in self.tagger_map.items():
            texts = text_splits.get(method, [text])
            kwargs = method_kwargs.get(method, {})
            
            entities = []
            for text in texts:
                entities.extend(tagger.apply(text, **kwargs))
                
            ner_result = NERResult(
                entities=entities,
                entity_type_map=ENTITY_TYPE_MAPS.get(method),
                clusterers=self.clusterers
            )
            results[method] = ner_result
        return results

    def apply_ner_taggers(self, text: str | ProcessedText, lang: str = "") -> Dict[str, NERResult]:
        if not isinstance(text, str):
            text = text.original_text
        LOGGER.debug(f"Detecting NER subject indices from text: '{text[:50]}...'")
        LOGGER.debug(
            f"Using the following methods for detecting different types "\
            f"of NER entities: {self.method_map}."
        )
        ner_results = self._apply_taggers(text=text, lang=lang)
        self.ner_results = ner_results
        return ner_results
    
    def get_keywords(self, ensemble_strategy: str = EnsembleStrategy.INTERSECTION
    ) -> Keywords:
        #TODO: raise error, if invalid ensemblestrategy or no NER results
        if NERMethod.ENSEMBLE in self.methods:
            LOGGER.debug(
                f"Using strategy '{ensemble_strategy}' for ensemble methods."
            )
        keywords = Keywords(
            ner_results=self.ner_results,
            method_map=self.method_map,
            ensemble_strategy=ensemble_strategy
        )
        self.keywords = keywords
        return keywords
    
    def find_keywords(self, text: str | ProcessedText, lang: str = "",
                      ensemble_strategy: str = EnsembleStrategy.INTERSECTION,
                      lemmatize: bool = False,
                      min_score: float = 0.0, min_count: int = 2, **kwargs
    ) -> List[dict]:
        if not isinstance(text, str):
            if lemmatize:
                text = text.processed_text
            else:
                text = text.original_text
            
        if self.text != text:
            self.apply_ner_taggers(text=text, lang=lang)
            self.text = text
        
        keywords = self.get_keywords(ensemble_strategy=ensemble_strategy)
        results = keywords.filter_keywords(
            min_score=min_score, min_count=min_count
        )
        return results
        
        
    