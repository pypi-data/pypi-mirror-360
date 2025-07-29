from typing import List, Dict

from rara_subject_indexer.indexers.model_indexers.base_indexer import BaseIndexer
from rara_subject_indexer.unsupervised.rakun.rakun_keyword_extractor import RakunKeywordExtractor
from rara_subject_indexer.config import KeywordType
from rara_subject_indexer.utils.text_preprocessor import ProcessedText


class RakunIndexer(BaseIndexer):
    """
    An unsupervised indexer that uses the Rakun (keyword extraction) logic.

    The configuration should include:
      - language: the language code.
      - top_k: how many keywords to extract (optional; default is 5).

    No model_path is required because the extractor is already part of the library.
    """

    def __init__(self, top_k: int = None, **config):
        super().__init__(top_k=top_k, **config)
        self.extractor = RakunKeywordExtractor(**config)
        self.entity_type = KeywordType.TOPIC.value

    def find_keywords(self, text: str, lang: str, top_k: int = None, **kwargs
    ) -> List[Dict]:
        """
        Predict keywords using the unsupervised Rakun-based extractor.

        Parameters
        ----------
        text : str
            Input text.
        lang_code: str
            Language code of the input text.
        top_k: int 
            Number of keywords to return

        Returns
        -------
        List[Dict]
            A list of dictionaries, each with keys "keyword", 
            "entity_type", and "score".
        """
        _top_k = top_k if top_k else self.top_k
        keywords = self.extractor.predict(
            text=text, 
            lang_code=lang,
            top_k=_top_k, 
            **kwargs
        )
        output = [
            {"keyword": kw, "entity_type": self.entity_type, "score": score} 
            for kw, score in keywords
        ]
        return output