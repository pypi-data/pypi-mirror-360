import pathlib
import shutil
import stanza
from typing import List, NoReturn, Optional
from urllib.parse import urlparse
from urllib.request import urlopen
from rara_subject_indexer.ner.ner_taggers.base_ner_tagger import BaseNERTagger
from rara_subject_indexer.ner.ner_result import NEREntity
from rara_subject_indexer.utils.text_preprocessor import TextPreprocessor
from rara_subject_indexer.exceptions import InvalidLanguageException
from rara_subject_indexer.config import (
    EntityType, 
    STANZA_ENTITY_TYPE_MAP, 
    STANZA_CUSTOM_NER_MODELS, 
    STANZA_SUPPORTED_LANGUAGES, 
    STANZA_UNKNOWN_LANG_TOKEN,
    STANZA_NER_RESOURCES_DIR,
    STANZA_CUSTOM_NER_MODEL_LANGS,
    LOGGER
)

# TODO:
# gpu vs cpu option ?
# cache dir?


class StanzaNERTagger(BaseNERTagger):
    """ Uses Stanza for detecting NER entities.
    """
    def __init__(
        self, 
        resource_dir: str,
        download_resources: bool = False,
        supported_languages: List[str] = STANZA_SUPPORTED_LANGUAGES,
        custom_ner_model_langs: List[str] = STANZA_CUSTOM_NER_MODEL_LANGS,
        refresh_data: bool = False,
        custom_ner_models: dict = STANZA_CUSTOM_NER_MODELS,
        unknown_lang_token: str = STANZA_UNKNOWN_LANG_TOKEN
        
    ) -> NoReturn:

        super().__init__()
        self.resource_dir = resource_dir
        self.stanza_resource_path = pathlib.Path(self.resource_dir) / "stanza" / "resources"
        self.custom_ner_model_path = pathlib.Path(self.resource_dir) / "stanza" / "custom_ner_models"
        self.custom_ner_models = custom_ner_models
        self.custom_ner_model_langs = custom_ner_model_langs
        self.supported_languages = supported_languages
        if download_resources:
            self.prepare_resources(refresh_data)
        self.processors: List[dict] = ["tokenize", "ner"]
        self.pipelines = self.load_pipelines()
        self.unknown_lang_token = unknown_lang_token
   
    
    def prepare_resources(self, refresh_data: bool) -> NoReturn:
        """
        Prepares all resources for NER.
        """
        # Delete data if refresh asked
        if refresh_data:
            shutil.rmtree(self.resource_dir)
        # Download resources
        self.download_custom_ner_models(
            resource_dir=self.resource_dir, 
            custom_ner_model_urls=self.custom_ner_models,
            model_langs=self.custom_ner_model_langs
        )
        self.download_stanza_resources(
            resource_dir=self.resource_dir, 
            supported_languages=self.supported_languages
        )

    @staticmethod
    def download_custom_ner_models(
        resource_dir: str, 
        custom_ner_model_urls: dict = STANZA_CUSTOM_NER_MODELS, 
        model_langs: List[str] = []
    ) -> NoReturn:
        """
        Downloads custom ner models if not present in resources directory.
        """
        ner_resource_dir = pathlib.Path(resource_dir) / "stanza" / "custom_ner_models"

        ner_resource_dir.mkdir(parents=True, exist_ok=True)
        for lang, url in custom_ner_model_urls.items():
            if lang in model_langs:
                file_name = urlparse(url).path.split("/")[-1]
                file_path = ner_resource_dir / lang
                LOGGER.info(
                    f"Downloading custom Stanza ner models for language '{lang}'. " \
                    f"Saving the model into '{str(file_path)}'."
                )
                if not file_path.exists():
                    response = urlopen(url)
                    content = response.read()
                    with open(file_path, "wb") as fh:
                        fh.write(content)

    
    
    @staticmethod
    def download_stanza_resources(resource_dir: str, supported_languages: List[dict]) -> NoReturn:
        """
        Downloads Stanza resources if not present in resources directory.
        By default all is downloaded into data directory under package directory.
        """
        model_types = ["depparse", "lemma", "pos", "tokenize"]
        stanza_resource_path = pathlib.Path(resource_dir) / "stanza" / "resources"
        LOGGER.info(
            f"Downloading Stanza resources {model_types} for languages {supported_languages}. " \
            f"Saving the resources into '{str(stanza_resource_path)}'."
        )
        stanza_resource_path.mkdir(parents=True, exist_ok=True) 
        for language_code in supported_languages:
            # rglob is for recursive filename pattern matching, 
            # then the necessary files do not exist and we 
            # should download them.
            lang_dir_exists = True if list(stanza_resource_path.rglob("{}*".format(language_code))) else False
            model_folders_exists = all(
                [
                    (stanza_resource_path / language_code / model_type).exists() 
                    for model_type in model_types
                ]
            )
            if not (lang_dir_exists and model_folders_exists):
                stanza.download(language_code, str(stanza_resource_path))
                
    def load_pipelines(self):
        """ Load Stanza pipelines.
        """
        pipelines = {}
        for lang in self.supported_languages:
            processors = ",".join(self.processors)
            LOGGER.info(
                f"Loading Stanza pipeline for language '{lang}' with " \
                f"processors {processors}."
            )
            if lang in self.custom_ner_model_langs:
                pipeline = stanza.Pipeline(
                    lang=lang, 
                    dir=str(self.stanza_resource_path),
                    processors=processors, 
                    ner_model_path=f"{self.custom_ner_model_path}/{lang}"
                )
            else:
                pipeline = stanza.Pipeline(
                    lang=lang, 
                    dir=str(self.stanza_resource_path),
                    processors=processors
                )
            pipelines[lang] = pipeline
        return pipelines
     
    def _parse_entities(
        self, 
        stanza_doc: stanza.models.common.doc.Document
    ) -> List[NEREntity]:
        """ Takes processed Stanza Document as an input
        and restructure's its NER entities into a list
        of custom NEREntities.
        
        Parameters:
        ------------
        stanza_doc: stanza.models.common.doc.Document
            Processed Stanza Document.
            
        Returns:
        ------------
        entities: List[NEREntity]
        """
        entities = [
            NEREntity(ent.to_dict())
            for sent in stanza_doc.sentences 
            for ent in sent.ents
        ]
        return entities
        
    
    def apply(self, text: str, lang: str = "") -> List[NEREntity]:
        """ Applies Stanza model onto the text.
        
        Parameters:
        ------------
        text: str
            Text onto which the model is applied.
        lang: str:
            Language code of the input text. If language is
            not specified, langdetect is used for trying
            to detect the language automatically.
        
        Returns:
        ------------
        entities: List[NEREntity]
            List of detected NEREntities.
         
        """
        if not lang or lang == self.unknown_lang_token:
            LOGGER.info(
                f"No language passed or language == '{self.unknown_lang_token}'. " \
                f"Trying to detect language automatically..."
            )
            lang = TextPreprocessor.detect_language(text)
        if lang not in self.supported_languages:
            raise InvalidLanguageException(
                f"Language '{lang}' is not supported. " \
                f"Supported languages are: {self.supported_languages}."  
            )
        
        entities = []
        if lang:
            LOGGER.debug(
                f"Applying Stanza NER Tagger onto text '{text[:50]}...'."
            )
            pipeline = self.pipelines.get(lang)
            stanza_doc = pipeline(text)
            entities = self._parse_entities(stanza_doc)
        return entities
                    