from typing import NoReturn

from rara_subject_indexer.config import (
    TOPIC_KEYWORD_CONFIG, GENRE_KEYWORD_CONFIG, TIME_KEYWORD_CONFIG,
    CATEGORY_CONFIG, UDK_CONFIG, UDC_CONFIG, NER_CONFIG, ModelArch, KeywordType, DEFAULT_RAW_KEYWORDS
)
from rara_subject_indexer.indexers.keyword_indexers.base_keyword_indexer import BaseKeywordIndexer


class TopicIndexer(BaseKeywordIndexer):
    def __init__(
            self,
            model_arch: str = ModelArch.OMIKUJI,
            config: dict = TOPIC_KEYWORD_CONFIG,
            top_k: int = DEFAULT_RAW_KEYWORDS
            ) -> NoReturn:
        super().__init__(model_arch=model_arch, config=config, top_k=top_k)

    @property
    def keyword_type(self) -> str:
        KeywordType.TOPIC.value


class GenreIndexer(BaseKeywordIndexer):
    def __init__(
            self,
            model_arch: str = ModelArch.OMIKUJI,
            config: dict = GENRE_KEYWORD_CONFIG,
            top_k: int = DEFAULT_RAW_KEYWORDS
            ) -> NoReturn:
        super().__init__(model_arch=model_arch, config=config, top_k=top_k)

    @property
    def keyword_type(self) -> str:
        KeywordType.GENRE.value


class TimeIndexer(BaseKeywordIndexer):
    def __init__(
            self,
            model_arch: str = ModelArch.OMIKUJI,
            config: dict = TIME_KEYWORD_CONFIG,
            top_k: int = DEFAULT_RAW_KEYWORDS
            ) -> NoReturn:
        super().__init__(model_arch=model_arch, config=config, top_k=top_k)

    @property
    def keyword_type(self) -> str:
        KeywordType.TIME.value


class UDCIndexer(BaseKeywordIndexer):
    def __init__(
            self,
            model_arch: str = ModelArch.OMIKUJI,
            config: dict = UDK_CONFIG,
            top_k: int = DEFAULT_RAW_KEYWORDS
            ) -> NoReturn:
        super().__init__(model_arch=model_arch, config=config, top_k=top_k)

    @property
    def keyword_type(self) -> str:
        KeywordType.UDK.value


class UDC2Indexer(BaseKeywordIndexer):
    def __init__(
            self,
            model_arch: str = ModelArch.OMIKUJI,
            config: dict = UDC_CONFIG,
            top_k: int = DEFAULT_RAW_KEYWORDS
            ) -> NoReturn:
        super().__init__(model_arch=model_arch, config=config, top_k=top_k)

    @property
    def keyword_type(self) -> str:
        KeywordType.UDK2.value


class CategoryIndexer(BaseKeywordIndexer):
    def __init__(
            self,
            model_arch: str = ModelArch.OMIKUJI,
            config: dict = CATEGORY_CONFIG,
            top_k: int = DEFAULT_RAW_KEYWORDS
            ) -> NoReturn:
        super().__init__(model_arch=model_arch, config=config, top_k=top_k)

    @property
    def keyword_type(self) -> str:
        KeywordType.CATEGORY.value


class NERKeywordIndexer(BaseKeywordIndexer):
    def __init__(
            self,
            model_arch: str = ModelArch.NER,
            config: dict = NER_CONFIG,
            top_k: int = DEFAULT_RAW_KEYWORDS
            ) -> NoReturn:
        super().__init__(model_arch=model_arch, config=config, top_k=top_k)

    @property
    def keyword_type(self) -> str:
        KeywordType.NER.value
