import collections
import json
import os
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from time import time
from typing import NoReturn, List, Dict

from rara_subject_indexer.config import (
    NERMethod, ModelArch, KeywordType, ThresholdSetting, Language,
    ALLOWED_METHODS_MAP, ALLOWED_KEYWORD_TYPES, ALLOWED_THRESHOLD_SETTINGS,
    SUPPORTED_LANGUAGES, DEFAULT_KEYWORD_METHOD_MAP, DEFAULT_KEYWORD_TYPES,
    TOPIC_KEYWORD_CONFIG, GENRE_KEYWORD_CONFIG, TIME_KEYWORD_CONFIG,
    CATEGORY_CONFIG, NER_KEYWORDS, UDK_CONFIG, UDC_CONFIG, NER_CONFIG,
    LOGGER, NER_DATA_DIR, OMIKUJI_DATA_DIR, GOOGLE_DRIVE_URL, THRESHOLD_CONFIG,
    DEFAULT_RAKUN_CONFIG, DEFAULT_OMIKUJI_CONFIG, DEFAULT_NER_CONFIG
)
from rara_subject_indexer.exceptions import (
    InvalidLanguageException, MissingDataException, InvalidInputException,
    InvalidKeywordTypeException, InvalidMethodException
)
from rara_subject_indexer.indexers.keyword_indexers.indexers import (
    TopicIndexer, TimeIndexer, GenreIndexer, NERKeywordIndexer,
    UDCIndexer, CategoryIndexer, UDC2Indexer
)
from rara_subject_indexer.ner.ner_subject_indexer import NERIndexer
from rara_subject_indexer.utils.downloader import Downloader
from rara_subject_indexer.utils.text_preprocessor import (
    TextPreprocessor, ProcessedText
)

intersection = lambda x, y: set(x).intersection(set(y))
has_intersection = lambda x, y: bool(intersection(x, y))
load_keyword_model = lambda x, y: bool(
    x in y or x == KeywordType.NER and has_intersection(NER_KEYWORDS, y)
)
intersection_size = lambda x, y: len(intersection(x, y))
difference = lambda x, y: set(x) - set(y)
are_equal = lambda x, y: collections.Counter(x) == collections.Counter(y)
are_equal_json = lambda x, y: are_equal(
    json.dumps(sorted(list(x.items()))),
    json.dumps(sorted(list(y.items())))
)
is_subset = lambda x, y: set(x).issubset(set(y))


class RaraSubjectIndexer:
    def __init__(
            self,
            methods: dict = DEFAULT_KEYWORD_METHOD_MAP,
            keyword_types: list = DEFAULT_KEYWORD_TYPES,
            topic_config: dict = TOPIC_KEYWORD_CONFIG,
            time_config: dict = TIME_KEYWORD_CONFIG,
            genre_config: dict = GENRE_KEYWORD_CONFIG,
            category_config: dict = CATEGORY_CONFIG,
            udk_config: dict = UDK_CONFIG,
            udc_config: dict = UDC_CONFIG,
            ner_config: dict = NER_CONFIG,
            omikuji_data_dir: str = OMIKUJI_DATA_DIR,
            ner_data_dir: str = NER_DATA_DIR
    ) -> NoReturn:

        self.methods = self._update_methods(methods)
        self.keyword_types = json.loads(json.dumps(keyword_types))
        self.omikuji_data_dir = omikuji_data_dir
        self.ner_data_dir = ner_data_dir

        self.indexers_map = {
            KeywordType.TOPIC: {"class": TopicIndexer, "config": topic_config},
            KeywordType.TIME: {"class": TimeIndexer, "config": time_config},
            KeywordType.GENRE: {"class": GenreIndexer, "config": genre_config},
            KeywordType.NER: {"class": NERKeywordIndexer, "config": ner_config},
            KeywordType.UDK: {"class": UDCIndexer, "config": udk_config},
            KeywordType.UDK2: {"class": UDC2Indexer, "config": udc_config},
            KeywordType.CATEGORY: {"class": CategoryIndexer, "config": category_config},
        }

        self.__text_preprocessor: TextPreprocessor = TextPreprocessor()
        self.__text: ProcessedText | None = None
        self.__lang: str = ""
        self.__keywords: List[dict] = []
        self.__durations: List[dict] = []

        self.threshold_config: dict = {}
        self.__ner_config: dict = {}
        self.__omikuji_config: dict = {}
        self.__rakun_config: dict = {}

        self.__default_model_configs: Dict[str, dict] = {
            ModelArch.RAKUN: DEFAULT_RAKUN_CONFIG,
            ModelArch.OMIKUJI: DEFAULT_OMIKUJI_CONFIG,
            ModelArch.NER: DEFAULT_NER_CONFIG
        }

        self.indexers = {
            keyword_type: self._load_indexers(keyword_type)
            for keyword_type in self.indexers_map
            if load_keyword_model(keyword_type, self.keyword_types)
        }

    def _update_methods(self, methods: dict) -> dict:
        """ Checks, if all user-passed methods are allowed
        and updates the default method.
        """
        # check that all methods are valid:
        for keyword_type, _methods in methods.items():
            if keyword_type == KeywordType.NER:
                continue
            if keyword_type not in ALLOWED_METHODS_MAP:
                error_msg = (
                    f"Keyword type '{str(keyword_type)}' is not supported."
                )
                LOGGER.error(error_msg)
                raise InvalidKeywordTypeException(error_msg)
            allowed_methods = [
                str(getattr(_method, "value", None) or _method) for _method in ALLOWED_METHODS_MAP.get(keyword_type)
            ]
            _methods = [str(getattr(_method, "value", None) or _method) for _method in _methods]
            if not is_subset(_methods, allowed_methods):
                error_msg = (
                    f"At least one methods from {_methods} is not supported " \
                    f"for keyword type '{keyword_type}'. Supported methods " \
                    f"for this keyword type are: {allowed_methods}."
                )
                LOGGER.error(error_msg)
                raise InvalidMethodException(error_msg)

        updated_methods = deepcopy(DEFAULT_KEYWORD_METHOD_MAP)
        updated_methods.update(methods)
        return json.loads(json.dumps(updated_methods))

    def _load_indexers(self, keyword_type: str):
        indexer_info = self.indexers_map.get(keyword_type)
        indexer_class = indexer_info.get("class")
        indexer_config = indexer_info.get("config")
        LOGGER.info(
            f"Loading indexers for keyword type {keyword_type}: " \
            f"{self.methods.get(keyword_type)}."
        )
        indexers = {
            model_arch: indexer_class(
                model_arch=model_arch,
                config=indexer_config
            )
            for model_arch in self.methods.get(keyword_type)
        }
        return indexers

    @staticmethod
    def download_resources(
            drive_url: str = GOOGLE_DRIVE_URL,
            gliner: bool = True, stanza: bool = True, omikuji: bool = True,
            ner_data_dir: str = NER_DATA_DIR, omikuji_dir: str = OMIKUJI_DATA_DIR
    ) -> NoReturn:
        if stanza or gliner:
            NERIndexer.download_model_resources(
                resource_dir=ner_data_dir,
                gliner=gliner,
                stanza=stanza
            )
        if omikuji:
            RaraSubjectIndexer.download_models_from_gdrive(
                drive_url=drive_url,
                output_dir=omikuji_dir
            )

    @staticmethod
    def download_models_from_gdrive(drive_url: str, output_dir: str) -> NoReturn:
        """ Downloads all files from a Google drive folder. NB! Expects 
        the files to be .zips.
        
        Parameters
        -----------
        drive_url: str
            Google Drive folder full URL or folder ID.
        output_dir: str
            Directory, where to save the models.
            
        """
        gdrive_downloader = Downloader(
            drive_url=drive_url,
            output_dir=output_dir
        )
        gdrive_downloader.download_folder()

    def _filter_ner_keywords(self, keywords: List[dict]) -> List[dict]:
        """ Filters out NER-based keyword types that were
        not chosen for extraction.
        
        Parameters
        -----------
        keywords: List[dict]
            NER-based keywords.
        
        Returns
        ----------
        List[dict]
            Extracted NER keywords.
        """
        if intersection_size(NER_KEYWORDS, self.keyword_types) < len(NER_KEYWORDS):
            LOGGER.debug(
                f"Filtering out the following NER-based keywords as " \
                f"they were not selected for extraction: " \
                f"{difference(NER_KEYWORDS, self.keyword_types)}."
            )
            filtered_keywords = []
            for keyword in keywords:
                if keyword.get("entity_type") in self.keyword_types:
                    filtered_keywords.append(keyword)
        else:
            filtered_keywords = keywords
        return filtered_keywords

    def _keywords_to_dict(self, keywords: List[dict]) -> Dict[str, Dict[str, List]]:
        keywords_dict = defaultdict(lambda: defaultdict(list))
        for keyword in keywords:
            keyword_type = keyword.get("entity_type")
            model_arch = keyword.get("model_arch")
            keywords_dict[keyword_type][model_arch].append(keyword)
        return keywords_dict

    def _filter_by_score_and_count(
            self,
            keywords: List[dict], threshold_config: dict, min_score: float, max_count: int,
            ignore_for_equal_scores: bool
    ) -> List[dict]:
        keywords_dict = self._keywords_to_dict(keywords)
        filtered_keywords = []

        for keyword_type, model_arches in keywords_dict.items():
            for model_arch, keywords in model_arches.items():
                _filtered_keywords = []

                keywords = keywords_dict[keyword_type][model_arch]

                scores = threshold_config.get(keyword_type, {}).get(model_arch, {})

                _min_score = scores.get("min_score", min_score)
                _max_count = scores.get("max_count", max_count)

                for keyword in keywords:
                    if keyword.get("score") >= _min_score:
                        _filtered_keywords.append(keyword)
                if not ignore_for_equal_scores:
                    filtered_keywords.extend(_filtered_keywords[:_max_count])
                else:
                    last_score = None
                    to_extend = []
                    for kw in _filtered_keywords:
                        current_score = kw.get("score")
                        if len(to_extend) < _max_count or current_score == last_score:
                            to_extend.append(kw)
                        else:
                            break
                        last_score = current_score
                    filtered_keywords.extend(to_extend)

        return filtered_keywords

    def _check_relevant_data_exists(self):
        data_exists = True
        if not os.path.exists(self.omikuji_data_dir) or not os.path.exists(self.ner_data_dir):
            data_exists = False
        elif not os.listdir(self.omikuji_data_dir) or not os.listdir(self.ner_data_dir):
            data_exists = False
        if not data_exists:
            error_msg = (
                f"Missing relevant Omikuji models from '{self.omikuji_data_dir}' " \
                f"and/or NER models from '{self.ner_data_dir}'. Please make " \
                f"sure to download them first!"
            )
            LOGGER.error(error_msg)
            raise MissingDataException(error_msg)

    def _validate_threshold_config(self, threshold_config: dict) -> bool:
        for keyword_type, model_arches in threshold_config.items():
            if keyword_type not in ALLOWED_KEYWORD_TYPES:
                error_msg = (
                    f"Invalid keyword type '{keyword_type}' in " \
                    f"threshold_config. Supported keyword types are: " \
                    f"{ALLOWED_KEYWORD_TYPES}."
                )
                LOGGER.error(error_msg)
                raise InvalidInputException(error_msg)
            allowed_methods = [
                method.value if isinstance(method, Enum) else method
                for method in ALLOWED_METHODS_MAP.get(keyword_type, [])
            ]
            ner_methods = [method.value for method in NERMethod]
            if set(ner_methods).intersection(set(allowed_methods)):
                allowed_methods = [ModelArch.NER.value]
            for model_arch in model_arches.keys():
                if model_arch not in allowed_methods:
                    error_msg = (
                        f"Invalid model arch '{model_arch}' for keyword type " \
                        f"'{keyword_type}'. Allowed model arches are: " \
                        f"{allowed_methods}."
                    )
                    LOGGER.error(error_msg)
                    raise InvalidInputException(error_msg)
        return True

    def _set_threshold_config(
            self,
            threshold_config: dict = {},
            default_min_score: float = None,
            default_max_count: int = None
    ) -> NoReturn:
        """ Sets thersholds for different keyword_type / model_arch
        combinations using the following logic:
        
        1. If the user hasn't defined threshold_config,
        default_min_score nor default_max_count -> use default threshold
        config defined in config.py.
        2. If the user has passed a non-empty threshold_config, 
        update the settings accordingly. 
        3. If the user has defined default_min_score and / or
        default_max_count, use them for ALL the keyword_type / model_arch
        combinations that are NOT present in the user-defined threshold config.
        
        Parameters
        -----------
        threshold_config: dict
            A dictionary of keyword_type + model_arch settings formatted
            followingly: 
            {
                keyword_type: {
                    model_arch: {
                        "max_count": 3, 
                        "min_score": 0.1
                    },
                    ...
               }, 
               ...
            }
            NB! All the keyword types don't have to be filled, just the 
            ones to update.
        
        Returns
        ----------
        None
        """
        self._validate_threshold_config(threshold_config)
        base_config = deepcopy(THRESHOLD_CONFIG)
        if threshold_config or default_min_score != None or default_max_count != None:
            for keyword_type, model_arches in base_config.items():
                for model_arch, settings in model_arches.items():
                    new_settings = threshold_config.get(
                        keyword_type, {}
                    ).get(model_arch, {})
                    for setting, value in new_settings.items():
                        if setting in ALLOWED_THRESHOLD_SETTINGS:
                            base_config[keyword_type][model_arch][setting] = value
                    if default_min_score != None and ThresholdSetting.MIN_SCORE not in new_settings:
                        base_config[keyword_type][model_arch][ThresholdSetting.MIN_SCORE.value] = default_min_score
                    if default_max_count != None and ThresholdSetting.MAX_COUNT not in new_settings:
                        base_config[keyword_type][model_arch][ThresholdSetting.MAX_COUNT.value] = default_max_count
        self.threshold_config = base_config

    def _update_config(self, new_config: dict, model_arch: str) -> dict:
        config = deepcopy(self.__default_model_configs.get(model_arch))
        config.update(new_config)
        return config

    def _add_languages(self, keywords: List[dict], text_lang: str) -> List[dict]:
        """ Adds language to each keyword
        """
        # NB! This is a bit hacky and might need changing, if additional
        # methods and/or languages are added
        for keyword in keywords:
            if keyword.get("model_arch") == ModelArch.OMIKUJI:
                keyword["language"] = Language.ET.value
            else:
                keyword["language"] = text_lang
        return keywords

    def apply_indexers(
            self,
            text: str,
            lang: str = "",
            threshold_config: dict = {},
            min_score: float | None = None,
            max_count: int | None = None,
            ignore_for_equal_scores: bool = False,
            flat: bool = True,
            rakun_config=DEFAULT_RAKUN_CONFIG,
            omikuji_config: dict = DEFAULT_OMIKUJI_CONFIG,
            ner_config: dict = DEFAULT_NER_CONFIG
    ):
        """
        Apply all indexers corresponding to selected methods and
        keyword types in class init. 
        
        Parameters
        -----------
        text: str
            Text for which to find the subject indices.
        lang: str
            Language code indicating the language of the text.
        min_score: float | None
            If not None, defaults to min threshold score for
            all keyword types that are NOT specifically set 
            via `threshold_config`.
        max_count: int | None
            If not None, defaults to max keyword count for
            all keyword types that are NOT specifically set 
            via `threshold_config`.
        ignore_for_equal_scores: bool 
            If enabled, max_count is ignored for keywords with
            equal scores. E.g. max_count = 2, 
            scores = {k1: 0.9, k2: 0.8, k3: 0.8, k4: 0.7}. By default,
            only the top two keywords (k1, k2) are returned, eventhough
            k3 has exactly the same score as k2. If `ignore_for_equal_scores`
            if enabled, k3 will be returned along with k1 and k2.
        threshold_config: dict
            Can be used to overwrite default threshold settings
            for each keyword type separately.
        flat: bool
            If enabled, keywords are returned in a flat list
            of dicts; otherwise with more nested structure.
        rakun_config: dict
            Configuration parameters for Rakun.
        omikuji_config: dict
            Configuration parameters for Omikuji.
        ner_config: dict
            Configuration parameters for NER-based indexers.
        
        """
        self._check_relevant_data_exists()

        self._set_threshold_config(
            threshold_config=threshold_config,
            default_min_score=min_score,
            default_max_count=max_count,

        )
        rakun_config = self._update_config(rakun_config, ModelArch.RAKUN)
        omikuji_config = self._update_config(omikuji_config, ModelArch.OMIKUJI)
        ner_config = self._update_config(ner_config, ModelArch.NER)

        if (
                self.__text and text == self.__text.original_text
                and are_equal_json(rakun_config, self.__rakun_config)
                and are_equal_json(omikuji_config, self.__omikuji_config)
                and are_equal_json(ner_config, self.__ner_config)
        ):
            keywords = self.__keywords
            durations = self.__durations
            lang = self.__lang



        else:
            if not lang:
                lang = TextPreprocessor.detect_language(text)

            if lang not in SUPPORTED_LANGUAGES:
                error_msg = (
                    f"The text appears to be in language '{lang}', "
                    f"which is not supported. Supported " \
                    f"languages are: {SUPPORTED_LANGUAGES}."
                )
                LOGGER.error(error_msg)
                raise InvalidLanguageException(error_msg)

            keywords = []

            processed_text = ProcessedText(
                text=text,
                lang_code=lang,
                text_preprocessor=self.__text_preprocessor
            )
            durations = []
            for keyword_type in self.indexers:
                for model_arch, indexer in self.indexers[keyword_type].items():
                    LOGGER.info(
                        f"Applying indexer '{indexer.__class__.__name__}' " \
                        f"with model arch '{model_arch}' for keyword type " \
                        f"'{keyword_type}'"
                    )
                    start = time()
                    _keywords = indexer.find_keywords(
                        text=processed_text,
                        lang=lang,
                        omikuji_kwargs=omikuji_config,
                        rakun_kwargs=rakun_config,
                        ner_kwargs=ner_config
                    )
                    duration = time() - start

                    if keyword_type == KeywordType.NER:
                        _keywords = self._filter_ner_keywords(_keywords)

                    keywords.extend(_keywords)
                    durations.append(
                        {
                            "duration": round(duration, 5),
                            "model_arch": model_arch.value if isinstance(model_arch, Enum) else model_arch,
                            "keyword_type": keyword_type.value if isinstance(keyword_type, Enum) else keyword_type
                        }
                    )
            self.__text = processed_text
            self.__lang = lang

        self.__keywords = deepcopy(keywords)
        self.__durations = deepcopy(durations)
        self.__rakun_config = deepcopy(rakun_config)
        self.__ner_config = deepcopy(ner_config)
        self.__omikuji_config = deepcopy(omikuji_config)

        # Filtering
        final_keywords = self._filter_by_score_and_count(
            keywords=keywords, threshold_config=self.threshold_config,
            min_score=min_score, max_count=max_count,
            ignore_for_equal_scores=ignore_for_equal_scores
        )

        # Add language for each keyword
        final_keywords = self._add_languages(final_keywords, text_lang=lang)

        if not flat:
            nested_keywords = []
            keywords_dict = self._keywords_to_dict(final_keywords)
            for keyword_type, model_arches in keywords_dict.items():
                for model_arch, _keywords in model_arches.items():
                    for kw in _keywords:
                        kw.pop("model_arch", "")
                        kw.pop("entity_type", "")
                    keyword_batch = {
                        "keyword_type": keyword_type,
                        "model_arch": model_arch,
                        "keywords": _keywords
                    }
                    nested_keywords.append(keyword_batch)
            final_keywords = nested_keywords

        results = {"keywords": final_keywords, "durations": durations}
        return results
