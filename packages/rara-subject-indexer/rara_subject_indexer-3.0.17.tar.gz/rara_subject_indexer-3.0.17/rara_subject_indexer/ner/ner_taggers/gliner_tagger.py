from typing import List, Dict, NoReturn
from gliner import GLiNER, GLiNERConfig
from rara_subject_indexer.ner.ner_taggers.base_ner_tagger import BaseNERTagger
from rara_subject_indexer.ner.ner_result import NEREntity
from rara_subject_indexer.config import (
    GLINER_ENTITY_TYPE_MAP, 
    GLINER_MODEL, 
    GLINER_LABELS, 
    GLINER_DEVICE,
    GLINER_THRESHOLD,
    LOGGER
)
import regex as re
import pathlib


DEFAULT_LABELS = list(GLINER_ENTITY_TYPE_MAP.keys())

# TODO: cache dir? device?
# https://github.com/urchade/GLiNER/blob/main/gliner/model.py
class GLiNERTagger(BaseNERTagger):
    """ Uses GLiNER (https://github.com/urchade/GLiNER) 
    for extracting entities.
    """
    def __init__(
        self, 
        labels: List[str] = GLINER_LABELS, 
        model_name: str = GLINER_MODEL,
        multi_label: bool = False,
        resource_dir: str | None = None,
        threshold: float = GLINER_THRESHOLD,
        device: str | int | None = GLINER_DEVICE
    ) -> NoReturn:
        """ Initializes GLiNERTagger object.
        
        Parameters:
        -----------
        labels: List[str]
            List of labels (NER entities) to search. NB! The label names
            have to be informative (e.g. use "Person" instead of "PER").
        model_name: str
            Name of the GLiNER model to use.
        multi_label: bool
            Whether to allow multiple labels per entity.
        resource_dir: str | None
            Directory of previously downloaded GLiNER resources.
        threshold: float
            Confidence threshold for predictions.
        device: str | int
            Device to use.
            
        """      
        super().__init__()
        
        self.device = device
        self.model_name: str = model_name
        self.multi_label: bool = multi_label
        self.resource_dir: str | None = resource_dir
        self.model: GLiNER = self.load_pretrained()
        self.threshold: float = threshold
        self.labels: List[str] = labels
        
            
    @staticmethod
    def normalize_name(model_name: str) -> str:
        """ Normalizes GLiNER model name to make it usable as a file name.

        Parameters:
        -----------
        model_name: str
            Name of the GLiNER model to normalize.
        
        Returns:
        -----------
        normalized_name: str
            Normalized GLiNER model name.
        """
        normalized_name = re.sub("[/]", "_slash_", model_name)
        return normalized_name


    @staticmethod
    def restore_name(normalized_name: str) -> str:
        """ Restores original GLiNER model name from the normalized version.

        Parameters:
        -----------
        normalized_name: str
            Normalized GLiNER model name.
            
        Returns:
        -----------
        model_name: str
            Original GLiNER model name.
            
        """
        model_name = re.sub("_slash_", "/", normalized_name)
        return model_name


            
    @staticmethod
    def download_gliner_resources(resource_dir: str, model_name: str, **model_kwargs) -> NoReturn:
        """ Downloads and saves a GLiNER model.
        
        Parameters:
        -----------
        resource_dir: str
            Directory where to save the model.
        model_name: str
            GLiNER model to download and save.
            
        Returns:
        -----------
        None
        """
        normalized_name = GLiNERTagger.normalize_name(model_name)
        gliner_resource_dir = pathlib.Path(resource_dir) / "gliner" / normalized_name
        LOGGER.info(
            f"Downloading GLiNER model `{model_name}` and " \
            f"saving it into '{str(gliner_resource_dir)}'."
        )
        gliner_resource_dir.mkdir(parents=True, exist_ok=True)
        model = GLiNER.from_pretrained(model_name, **model_kwargs)
        model.save_pretrained(gliner_resource_dir)
        

    def load_pretrained(self) -> GLiNER:
        """ Loads a pretrained GLiNER model. If resource dir was provided
        during the object initialization, the model is loaded from there. 
        
        Returns:
        ---------
        model: GLiNER
            A loaded GLiNER model object.
        """
        if self.resource_dir:
            normalized_name = GLiNERTagger.normalize_name(self.model_name)
            gliner_resource_dir = pathlib.Path(self.resource_dir) / "gliner" / normalized_name
            LOGGER.info(
                f"Loading pretrained GLiNER model `{self.model_name}` from " \
                f"{str(gliner_resource_dir)}'."
            )
            model = GLiNER.from_pretrained(gliner_resource_dir)
        else:
            model = GLiNER.from_pretrained(self.model_name)
    
        model.to(self.device)
        return model

        
    def apply(self, text: str) -> List[NEREntity]: 
        """ Applies GLiNER model onto the text. NB! The input text
        length is restricted and for longer texts, it is expected that the
        segmentation is implemented before calling out this function.
        
        Parameters:
        ------------
        text: str
            Text onto which the model is applied.
        
        Returns:
        ------------
        entities: List[NEREntity]
            List of detected NEREntities.
         
        """
        LOGGER.debug(
            f"Applying GLiNER Tagger onto text '{text[:50]}...'."
        )
        raw_entities = self.model.predict_entities(
            text=text, 
            labels=self.labels, 
            threshold=self.threshold,
            multi_label=self.multi_label
        )
        entities = [
            NEREntity(ent)#.to_dict() 
            for ent in raw_entities
        ]
        return entities
    
    