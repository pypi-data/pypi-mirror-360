from abc import abstractmethod
from typing import Dict

from rara_subject_indexer.config import ModelArch, LOGGER
from rara_subject_indexer.indexers.model_indexers.omikuji_indexer import OmikujiIndexer
from rara_subject_indexer.indexers.model_indexers.rakun_indexer import RakunIndexer
from rara_subject_indexer.ner.ner_subject_indexer import NERIndexer
from rara_subject_indexer.utils.text_preprocessor import ProcessedText


class BaseKeywordIndexer:
    def __init__(
            self,
            model_arch: str,
            config: dict,
            top_k: int = 30
            ):
        self.model_arch: str = model_arch
        self.config: dict = config
        self.top_k: int = top_k
        self.__omikuji_indexers: dict = {}
        self.__rakun_indexer = {}
        self.__ner_indexer: NERIndexer = {}
        self.__indexer: Dict[str, OmikujiIndexer] | RakunIndexer | NERIndexer | None = None

    @abstractmethod
    def keyword_type(self) -> str:
        pass

    @property
    def omikuji_indexers(self) -> dict:
        if not self.__omikuji_indexers:
            omikuji_config = self.config.get(ModelArch.OMIKUJI)
            self.__omikuji_indexers = {
                lang_code: OmikujiIndexer(
                    {
                        "model_path": omikuji_config.get(lang_code),
                        "language": lang_code,
                        "top_k": self.top_k
                    }
                )
                for lang_code in omikuji_config
            }

        return self.__omikuji_indexers

    @property
    def rakun_indexer(self) -> RakunIndexer:
        if not self.__rakun_indexer:
            # TODO: config like stopwords etc
            rakun_config = self.config.get(ModelArch.RAKUN)
            self.__rakun_indexer = RakunIndexer(top_k=self.top_k, **rakun_config)
        return self.__rakun_indexer

    @property
    def ner_indexer(self) -> NERIndexer:
        if not self.__ner_indexer:
            ner_config = self.config.get(ModelArch.NER)
            ner_indexer = NERIndexer(
                stanza_config=ner_config.get("stanza_config"),
                gliner_config=ner_config.get("gliner_config"),
                method_map=ner_config.get("ner_method_map")
            )
            self.__ner_indexer = ner_indexer
            LOGGER.info(f"Loaded a new NERIndexer")
        return self.__ner_indexer

    @property
    def indexer(self) -> Dict[str, OmikujiIndexer] | RakunIndexer | NERIndexer:
        if not self.__indexer:
            if self.model_arch == ModelArch.OMIKUJI:
                LOGGER.info(f"Loading an Omikuji indexer.")
                self.__indexer = self.omikuji_indexers

            elif self.model_arch == ModelArch.RAKUN:
                LOGGER.info(f"Loading a Rakun indexer.")
                self.__indexer = self.rakun_indexer

            elif self.model_arch == ModelArch.NER:
                LOGGER.info(f"Loading a NER indexer.")
                self.__indexer = self.ner_indexer

            else:
                LOGGER.error(
                    f"Model architecture {self.model_arch} is not supported."
                )
        return self.__indexer

    def find_keywords(
            self, text: ProcessedText, lang: str = "",
            omikuji_kwargs: dict = {}, ner_kwargs: dict = {},
            rakun_kwargs: dict = {}
            ):
        if not lang:
            lang = text.lang_code
        LOGGER.info(
            f"Extracting keywords with model arch '{self.model_arch}'."
        )
        if isinstance(self.indexer, dict):
            indexer = self.indexer.get(lang)
        else:
            indexer = self.indexer

        if self.model_arch == ModelArch.OMIKUJI:
            kwargs = omikuji_kwargs
        elif self.model_arch == ModelArch.RAKUN:
            kwargs = rakun_kwargs
        elif self.model_arch == ModelArch.NER:
            kwargs = ner_kwargs

        keywords = indexer.find_keywords(text, lang=lang, **kwargs)
        for keyword in keywords:
            keyword["model_arch"] = getattr(self.model_arch, "value", str(self.model_arch))

        return keywords
