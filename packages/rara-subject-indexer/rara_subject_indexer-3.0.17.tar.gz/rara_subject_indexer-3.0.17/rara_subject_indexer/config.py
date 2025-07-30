import importlib.resources
import logging
import os
from enum import StrEnum

LOGGER = logging.getLogger("rara-subject-indexer")


def load_lines_from_resource(package: str, resource: str) -> list[str]:
    """
    Load lines from a packaged resource file into a list.

    Parameters
    ----------
    package : str
        The package where the resource is located.
    resource : str
        The resource file name.

    Returns
    -------
    list[str]
        A list of strings from the resource file.
    """
    resource_path = importlib.resources.files(package).joinpath(resource)
    with resource_path.open(encoding="utf-8") as file:
        return [line.strip() for line in file]


# ---------------------------------------------------------------#
# Enum classes
# ---------------------------------------------------------------#

class Language(StrEnum):
    ET = "et"
    EN = "en"


class PreprocessingMethod(StrEnum):
    LEMMATIZE = "lemmatize"
    STEM = "stem"


# TODO: Add to rara-tools.
class KeywordType(StrEnum):
    TOPIC = "Teemamärksõnad"
    LOC = "Kohamärksõnad"
    TIME = "Ajamärksõnad"
    UDK = "UDK Rahvusbibliograafia"
    UDK2 = "UDC Summary"
    GENRE = "Vormimärksõnad"
    CATEGORY = "Valdkonnamärksõnad"
    PER = "Isikunimi"
    ORG = "Kollektiivi nimi"
    TITLE = "Teose pealkiri"
    EVENT = "Ajutine kollektiiv või sündmus"
    NER = "NER"


class NERMethod(StrEnum):
    """ Supported NER methods.
    """
    STANZA = "stanza"
    GLINER = "gliner"
    ENSEMBLE = "ner_ensemble"


class ModelArch(StrEnum):
    OMIKUJI = "omikuji"
    RAKUN = "rakun"
    NER = "ner"
    STANZA = NERMethod.STANZA.value
    GLINER = NERMethod.GLINER.value
    NER_ENSEMBLE = NERMethod.ENSEMBLE.value


class EntityType(StrEnum):
    """ Supported entity types.
    """
    PER = "PER"
    ORG = "ORG"
    TITLE = "TITLE"
    DATE = "DATE"
    LOC = "LOC"
    EVENT = "EVENT"


class EnsembleStrategy(StrEnum):
    """ Supported strategies for
    NERMethod `ensemble`.
    """
    UNION = "union"
    INTERSECTION = "intersection"


class SplitMethod(StrEnum):
    """ Supported split methods
    for TextSplitter.
    """
    DOUBLE_NEWLINE = "DOUBLE_NEWLINE"
    NEWLINE = "NEWLINE"
    WORD_LIMIT = "WORD_LIMIT"
    CHAR_LIMIT = "CHAR_LIMIT"
    CUSTOM = "CUSTOM"


class ThresholdSetting(StrEnum):
    MAX_COUNT = "max_count"
    MIN_SCORE = "min_score"


# ---------------------------------------------------------------#
# Default mappings
# ---------------------------------------------------------------#

SUPPORTED_LANGUAGES = [lang.value for lang in Language]
DEFAULT_RAW_KEYWORDS = 40

ALLOWED_KEYWORD_TYPES = [
    keyword_type.value
    for keyword_type in KeywordType
    if keyword_type.value != "NER"
]
DEFAULT_KEYWORD_TYPES = [
    KeywordType.TOPIC,
    KeywordType.GENRE,
    KeywordType.UDK,
    KeywordType.UDK2,
    KeywordType.TIME,
    KeywordType.PER,
    KeywordType.ORG,
    KeywordType.TITLE,
    KeywordType.LOC,
    KeywordType.EVENT,
    KeywordType.CATEGORY
]

NER_KEYWORDS = [
    KeywordType.PER,
    KeywordType.ORG,
    KeywordType.TITLE,
    KeywordType.LOC,
    KeywordType.EVENT
]
SUPPORTED_LEMMATIZER_LANGUAGES = {"et": "estonian"}
SUPPORTED_STEMMER_LANGUAGES = {"en": "english"}

PREPROCESSING_METHOD_MAP = {
    Language.ET: PreprocessingMethod.LEMMATIZE,
    Language.EN: PreprocessingMethod.STEM
}

# Stopwords for supported languages
SUPPORTED_STOPWORDS = {
    Language.EN: load_lines_from_resource("rara_subject_indexer", "resources/stopwords/en_stopwords.txt"),
    Language.ET: load_lines_from_resource("rara_subject_indexer", "resources/stopwords/et_stopwords_lemmas.txt"),
}

# Stopwords for supported languages used for phrase detection
SUPPORTED_STOPWORDS_PHRASER = {
    Language.EN: load_lines_from_resource("rara_subject_indexer", "resources/stopwords/en_stopwords.txt"),
    Language.ET: load_lines_from_resource("rara_subject_indexer", "resources/stopwords/et_stopwords.txt"),
}

# Supported Phraser model paths
SUPPORTED_PHRASER_MODEL_PATHS = {
    Language.ET: {
        "package": "rara_subject_indexer",
        "resource": "resources/phrasers/phraser_ise_digar_et.model"
    }
}

SPELL_CHECK_DICTIONARIES_CONFIG = {
    Language.ET: {
        "package": "rara_subject_indexer",
        "resource": "resources/spellcheck/et_lemmas.txt",
        "term_index": 1,
        "count_index": 0,
        "separator": " "
    },
    Language.EN: {
        "package": "rara_subject_indexer",
        "resource": "resources/spellcheck/en.txt",
    }
}

POSTAGS_TO_IGNORE = ["V", "A", "D", "Z", "H", "P", "U", "N", "O"]
ALLOWED_EN_POSTAGS = ["NN", "NNS"]

SENTENCE_SPLIT_REGEX = r"(?<!\d\.\d)(?<!\w\.\w)(?<=\.|\?|!)\s"
URL_REGEX = r"(?i)(https?://\S+|www\.\S+|doi(:|\.org/)\s*\S+)"
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b"

SPELLER_DEFAULTS = {
    "max_uppercase": 2,
    "min_word_frequency": 3,
    "preserve_case": True
}

RAKUN_DEFAULTS = {
    "merge_threshold": 0.0,
    "use_phraser": False,
    "correct_spelling": False,
    "preserve_case": True,
    "max_uppercase": 2,
    "min_word_frequency": 3
}

DEFAULT_RAKUN_CONFIG = {
    "use_phraser": False,
    "postags_to_ignore": POSTAGS_TO_IGNORE
}

DEFAULT_OMIKUJI_CONFIG = {
    "lemmatize": False
}

DEFAULT_NER_CONFIG = {
    "lemmatize": False,
    "min_count": 3,
    "ensemble_strategy": EnsembleStrategy.INTERSECTION.value
}

SKLEARN_AVERAGE_FUNCTION = "samples"

NER_DATA_DIR = importlib.resources.files("rara_subject_indexer").joinpath("data/ner_resources")
OMIKUJI_DATA_DIR = importlib.resources.files("rara_subject_indexer").joinpath("data/omikuji_models")

GOOGLE_DRIVE_URL = "https://drive.google.com/drive/u/0/folders/1yKgedNCe9fNAQXvjhiJEo7JI-Yk0ImSD"

TOPIC_KEYWORD_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "teemamarksonad_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "teemamarksonad_eng")
    },
    ModelArch.RAKUN: {
        "stopwords": SUPPORTED_STOPWORDS,
        "n_raw_keywords": 50
    }
}

GENRE_KEYWORD_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "vormimarksonad_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "vormimarksonad_eng")
    },
    ModelArch.RAKUN: {}
}

TIME_KEYWORD_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "ajamarksonad_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "ajamarksonad_eng")
    },
    ModelArch.RAKUN: {}
}

UDK_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "udk_rahvbibl_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "udk_rahvbibl_eng")
    },
    ModelArch.RAKUN: {}
}

UDC_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "udk_general_depth_11_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "udk_general_depth_11_eng")
    },
    ModelArch.RAKUN: {}
}

CATEGORY_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "valdkonnamarksonad_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "valdkonnamarksonad_eng")
    },
    ModelArch.RAKUN: {}
}

GLINER_ENTITY_TYPE_MAP = {
    "Person": EntityType.PER,
    "Organization": EntityType.ORG,
    "Location": EntityType.LOC,
    "Title of a work": EntityType.TITLE,
    "Date": EntityType.DATE,
    "Event": EntityType.EVENT
}

# How to handle potential new entity types
# for different stanza NER models?
STANZA_ENTITY_TYPE_MAP = {
    "PER": EntityType.PER,
    "PERSON": EntityType.PER,
    "EVENT": EntityType.ORG,
    "ORG": EntityType.ORG,
    "LOC": EntityType.LOC,
    "GPE": EntityType.LOC,
    "TITLE": EntityType.TITLE,
    "DATE": EntityType.DATE
}

ENTITY_TYPE_MAPS = {
    NERMethod.STANZA: STANZA_ENTITY_TYPE_MAP,
    NERMethod.GLINER: GLINER_ENTITY_TYPE_MAP
}

# Allowed choices allowed_methods parameter.
# TODO: Add these to rara-tools.
ALLOWED_METHODS_MAP = {
    KeywordType.TOPIC: [ModelArch.OMIKUJI, ModelArch.RAKUN],
    KeywordType.LOC: [ModelArch.STANZA, ModelArch.GLINER, ModelArch.NER_ENSEMBLE],
    KeywordType.TIME: [ModelArch.OMIKUJI],
    KeywordType.UDK: [ModelArch.OMIKUJI],
    KeywordType.UDK2: [ModelArch.OMIKUJI],
    KeywordType.GENRE: [ModelArch.OMIKUJI],
    KeywordType.CATEGORY: [ModelArch.OMIKUJI],
    KeywordType.PER: [ModelArch.STANZA, ModelArch.GLINER, ModelArch.NER_ENSEMBLE],
    KeywordType.ORG: [ModelArch.STANZA, ModelArch.GLINER, ModelArch.NER_ENSEMBLE],
    KeywordType.TITLE: [ModelArch.GLINER],
    KeywordType.EVENT: [ModelArch.GLINER]
}

# Default values.
# TODO: Add to rara-tools.
DEFAULT_KEYWORD_METHOD_MAP = {
    KeywordType.TOPIC: [ModelArch.OMIKUJI, ModelArch.RAKUN],
    KeywordType.LOC: [ModelArch.NER_ENSEMBLE],
    KeywordType.PER: [ModelArch.NER_ENSEMBLE],
    KeywordType.ORG: [ModelArch.NER_ENSEMBLE],
    KeywordType.TIME: [ModelArch.OMIKUJI],
    KeywordType.TITLE: [ModelArch.GLINER],
    KeywordType.UDK: [ModelArch.OMIKUJI],
    KeywordType.UDK2: [ModelArch.OMIKUJI],
    KeywordType.GENRE: [ModelArch.OMIKUJI],
    KeywordType.CATEGORY: [ModelArch.OMIKUJI],
    KeywordType.NER: [ModelArch.NER],
    KeywordType.EVENT: [ModelArch.GLINER]
}

DEFAULT_NER_METHOD_MAP = {
    EntityType.PER: DEFAULT_KEYWORD_METHOD_MAP.get(KeywordType.PER)[0],
    EntityType.ORG: DEFAULT_KEYWORD_METHOD_MAP.get(KeywordType.ORG)[0],
    EntityType.LOC: DEFAULT_KEYWORD_METHOD_MAP.get(KeywordType.LOC)[0],
    # EntityType.DATE: NERMethod.STANZA,
    EntityType.TITLE: DEFAULT_KEYWORD_METHOD_MAP.get(KeywordType.TITLE)[0],
    EntityType.EVENT: DEFAULT_KEYWORD_METHOD_MAP.get(KeywordType.EVENT)[0]
}
# TODO: need väärtused rara-toolsist importida?
SUBJECT_INDEX_MAP = {
    EntityType.PER: KeywordType.PER,
    EntityType.ORG: KeywordType.ORG,
    EntityType.LOC: KeywordType.LOC,
    # EntityType.DATE: KeywordType.TIME,
    EntityType.TITLE: KeywordType.TITLE,
    EntityType.EVENT: KeywordType.EVENT
}

# ---------------------------------------------------------------#
# General
# ---------------------------------------------------------------#

ALLOWED_NER_METHODS = [ner_method.value for ner_method in NERMethod]

# ---------------------------------------------------------------#
# Stanza
# ---------------------------------------------------------------#

# URLs for Custom NER model downloads.
STANZA_CUSTOM_NER_MODELS = {
    "et": "https://packages.texta.ee/texta-resources/ner_models/_estonian_nertagger.pt",
    "lv": "https://packages.texta.ee/texta-resources/ner_models/_latvian_nertagger.pt",
    "lt": "https://packages.texta.ee/texta-resources/ner_models/_lithuanian_nertagger.pt"
}

STANZA_SUPPORTED_LANGUAGES = ["et", "en"]
STANZA_UNKNOWN_LANG_TOKEN = "unk"

STANZA_NER_RESOURCES_DIR = NER_DATA_DIR
# STANZA_RESOURCE_DIR = ""

STANZA_CUSTOM_NER_MODEL_LANGS = ["et"]

# ---------------------------------------------------------------#
# GLiNER
# ---------------------------------------------------------------#

GLINER_MODEL = "urchade/gliner_multi-v2.1"
GLINER_LABELS = list(GLINER_ENTITY_TYPE_MAP.keys())
GLINER_THRESHOLD = 0.5
GLINER_RESOURCE_DIR = NER_DATA_DIR
GLINER_DEVICE = "cpu"
GLINER_ALLOW_MULTI_LABEL = False

# ---------------------------------------------------------------#
# Clusterers
# ---------------------------------------------------------------#

DEFAULT_ORG_SIMILARITY_THRESHOLD = 0.9
DEFAULT_PER_SIMILARITY_THRESHOLD = 0.85
DEFAULT_LOC_SIMILARITY_THRESHOLD = 0.9
DEFAULT_TITLE_SIMILARITY_THRESHOLD = 0.9

# ---------------------------------------------------------------#

STANZA_CONFIG = {
    "resource_dir": STANZA_NER_RESOURCES_DIR,
    "download_resources": False,
    "supported_languages": STANZA_SUPPORTED_LANGUAGES,
    "custom_ner_model_langs": STANZA_CUSTOM_NER_MODEL_LANGS,
    "refresh_data": False,
    "custom_ner_models": STANZA_CUSTOM_NER_MODELS,
    "unknown_lang_token": STANZA_UNKNOWN_LANG_TOKEN
}

GLINER_CONFIG = {
    "labels": GLINER_LABELS,
    "model_name": GLINER_MODEL,
    "multi_label": GLINER_ALLOW_MULTI_LABEL,
    "resource_dir": GLINER_RESOURCE_DIR,
    "threshold": GLINER_THRESHOLD,
    "device": GLINER_DEVICE
}

NER_CONFIG = {
    ModelArch.NER: {
        "stanza_config": STANZA_CONFIG,
        "gliner_config": GLINER_CONFIG,
        "ner_method_map": DEFAULT_NER_METHOD_MAP
    }
}

ALLOWED_THRESHOLD_SETTINGS = [
    setting.value
    for setting in ThresholdSetting
]

THRESHOLD_CONFIG = {
    KeywordType.TOPIC: {
        ModelArch.OMIKUJI: {"max_count": 5, "min_score": 0.1},
        ModelArch.RAKUN: {"max_count": 5, "min_score": 0.01}
    },
    KeywordType.TIME: {
        ModelArch.OMIKUJI: {"max_count": 3, "min_score": 0.2}
    },
    KeywordType.GENRE: {
        ModelArch.OMIKUJI: {"max_count": 3, "min_score": 0.2}
    },
    KeywordType.UDK: {
        ModelArch.OMIKUJI: {"max_count": 1, "min_score": 0.3}
    },
    KeywordType.UDK2: {
        ModelArch.OMIKUJI: {"max_count": 1, "min_score": 0.3}
    },
    KeywordType.PER: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.ORG: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.TITLE: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.LOC: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.CATEGORY: {
        ModelArch.OMIKUJI: {"max_count": 3, "min_score": 0.2}
    },
    KeywordType.EVENT: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.1}
    }
}
