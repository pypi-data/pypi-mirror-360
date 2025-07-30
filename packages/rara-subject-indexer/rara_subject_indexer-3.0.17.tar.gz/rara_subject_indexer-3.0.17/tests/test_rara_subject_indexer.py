import collections
import json
import os
import shutil

import pytest

from rara_subject_indexer.config import (
    KeywordType,
    ModelArch,
    Language,
    SUPPORTED_STOPWORDS
)
from rara_subject_indexer.exceptions import (
    InvalidMethodException, InvalidKeywordTypeException
)
from rara_subject_indexer.rara_indexer import RaraSubjectIndexer

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = os.path.join(ROOT_DIR, "tests", "test_data")

TEST_TEXT_FILE_PATHS = {
    "text_1": os.path.join(TEST_DATA_DIR, "text_1.txt"),
    "text_2": os.path.join(TEST_DATA_DIR, "text_2.txt"),
    "text_3": os.path.join(TEST_DATA_DIR, "text_3.txt"),
    "text_4": os.path.join(TEST_DATA_DIR, "text_4.txt")
}

TEST_KEYWORD_METHOD_MAP = {
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

TEST_KEYWORD_TYPES = [
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

TEMP_RESOURCES_DIR = os.path.join(".", "data", "indexer_resources")

OMIKUJI_DATA_DIR = os.path.join(TEMP_RESOURCES_DIR, "omikuji_models")
NER_DATA_DIR = os.path.join(TEMP_RESOURCES_DIR, "ner")

# NER_DATA_DIR = importlib.resources.files("rara_subject_indexer").joinpath("data/ner_resources")

# OMIKUJI_DATA_DIR = importlib.resources.files("rara_subject_indexer").joinpath("data/omikuji_models")

TOPIC_CONFIG = {
    ModelArch.OMIKUJI.value: {
        Language.ET.value: os.path.join(OMIKUJI_DATA_DIR, "teemamarksonad_est"),
        Language.EN.value: os.path.join(OMIKUJI_DATA_DIR, "teemamarksonad_eng")
    },
    ModelArch.RAKUN.value: {
        "stopwords": SUPPORTED_STOPWORDS,
        "n_raw_keywords": 30
    }
}

GENRE_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "vormimarksonad_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "vormimarksonad_eng")
    },
    ModelArch.RAKUN: {}
}

TIME_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "ajamarksonad_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "ajamarksonad_eng")
    },
    ModelArch.RAKUN: {}
}

UDC_CONFIG = {
    ModelArch.OMIKUJI: {
        Language.ET: os.path.join(OMIKUJI_DATA_DIR, "udk_rahvbibl_est"),
        Language.EN: os.path.join(OMIKUJI_DATA_DIR, "udk_rahvbibl_eng")
    },
    ModelArch.RAKUN: {}
}

UDC2_CONFIG = {
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

NER_CONFIG = {
    ModelArch.NER.value: {
        "stanza_config": {
            "resource_dir": NER_DATA_DIR,
            "download_resources": False,
            "supported_languages": ["et", "en"],
            "custom_ner_model_langs": ["et"],
            "refresh_data": False,
            "custom_ner_models": {
                "et": "https://packages.texta.ee/texta-resources/ner_models/_estonian_nertagger.pt"
            },
            "unknown_lang_token": "unk"
        },
        "gliner_config": {
            "labels": ["Person", "Organization", "Location", "Title of a work", "Date", "Event"],
            "model_name": "urchade/gliner_multi-v2.1",
            "multi_label": False,
            "resource_dir": NER_DATA_DIR,
            "threshold": 0.5,
            "device": "cpu"
        },
        "ner_method_map": {
            "PER": "ner_ensemble",
            "ORG": "ner_ensemble",
            "LOC": "ner_ensemble",
            "TITLE": "gliner",
            "EVENT": "gliner"
        }

    }
}

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

THRESHOLD_CONFIG_1 = {
    KeywordType.TOPIC: {
        ModelArch.OMIKUJI: {"max_count": 10, "min_score": 0.1},
        ModelArch.RAKUN: {"max_count": 10, "min_score": 0.01}
    },
    KeywordType.TIME: {
        ModelArch.OMIKUJI: {"max_count": 10, "min_score": 0.2}
    },
    KeywordType.GENRE: {
        ModelArch.OMIKUJI: {"max_count": 10, "min_score": 0.2}
    },
    KeywordType.UDK: {
        ModelArch.OMIKUJI: {"max_count": 10, "min_score": 0.3}
    },
    KeywordType.UDK2: {
        ModelArch.OMIKUJI: {"max_count": 10, "min_score": 0.3}
    },
    KeywordType.PER: {
        ModelArch.NER: {"max_count": 10, "min_score": 0.3}
    },
    KeywordType.ORG: {
        ModelArch.NER: {"max_count": 10, "min_score": 0.3}
    },
    KeywordType.TITLE: {
        ModelArch.NER: {"max_count": 10, "min_score": 0.3}
    },
    KeywordType.LOC: {
        ModelArch.NER: {"max_count": 10, "min_score": 0.3}
    },
    KeywordType.CATEGORY: {
        ModelArch.OMIKUJI: {"max_count": 10, "min_score": 0.2}
    },
    KeywordType.EVENT: {
        ModelArch.NER: {"max_count": 10, "min_score": 0.1}
    }
}

THRESHOLD_CONFIG_2 = {
    KeywordType.TOPIC: {
        ModelArch.OMIKUJI: {"max_count": 5, "min_score": 0.1},
        ModelArch.RAKUN: {"max_count": 15, "min_score": 0.01}
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
        ModelArch.NER: {"max_count": 6, "min_score": 0.1}
    },
    KeywordType.TITLE: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.LOC: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.CATEGORY: {
        ModelArch.OMIKUJI: {"max_count": 2, "min_score": 0.2}
    },
    KeywordType.EVENT: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.1}
    }
}

are_equal = lambda x, y: collections.Counter(x) == collections.Counter(y)
are_equal_json = lambda x, y: are_equal(
    sorted(
        [
            json.dumps(sorted(list(d.items())))
            for d in x
        ]
    ),
    sorted(
        [
            json.dumps(sorted(list(d.items())))
            for d in y
        ]
    )
)
are_equal_dict = lambda x, y: are_equal(
    json.dumps(sorted(list(x.items()))),
    json.dumps(sorted(list(y.items())))
)


def load_text(file_path: str) -> str:
    with open(file_path, "r") as f:
        text = f.read()
    return text


def check_equality(true_config, expected_config):
    for keyword_type, model_arches in expected_config.items():
        for model_arch, expected_settings in model_arches.items():
            true_settings = true_config.get(keyword_type, {}).get(model_arch, {})
            assert are_equal_dict(true_settings, expected_settings)


@pytest.fixture(scope="module")
def temp_directory():
    temp_dir = TEMP_RESOURCES_DIR
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        os.makedirs(NER_DATA_DIR)
        os.makedirs(OMIKUJI_DATA_DIR)

    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.mark.order(1)
def test_downloading_resources(temp_directory):
    RaraSubjectIndexer.download_resources(
        ner_data_dir=NER_DATA_DIR,
        omikuji_dir=OMIKUJI_DATA_DIR
    )
    assert len(os.listdir(OMIKUJI_DATA_DIR)) > 10
    ner_subdirs = os.listdir(NER_DATA_DIR)
    for subdir in ner_subdirs:
        assert len(os.listdir(os.path.join(NER_DATA_DIR, subdir))) > 0


@pytest.mark.order(2)
def test_apply_indexers_change_min_score():
    global rara_indexer_1
    rara_indexer_1 = RaraSubjectIndexer(
        methods=TEST_KEYWORD_METHOD_MAP,
        keyword_types=TEST_KEYWORD_TYPES,
        topic_config=TOPIC_CONFIG,
        time_config=TIME_CONFIG,
        genre_config=GENRE_CONFIG,
        category_config=CATEGORY_CONFIG,
        udk_config=UDC_CONFIG,
        udc_config=UDC2_CONFIG,
        ner_config=NER_CONFIG,
        omikuji_data_dir=OMIKUJI_DATA_DIR,
        ner_data_dir=NER_DATA_DIR
    )
    text = load_text(TEST_TEXT_FILE_PATHS["text_3"])
    subject_indices = rara_indexer_1.apply_indexers(
        text=text,
        min_score=0.8
    )
    # pprint(subject_indices)
    assert subject_indices
    expected_output = {
        'durations': [{
            'duration': 8.73723,
            'keyword_type': 'Teemamärksõnad',
            'model_arch': 'omikuji'
        },
            {
                'duration': 1.37879,
                'keyword_type': 'Teemamärksõnad',
                'model_arch': 'rakun'
            },
            {
                'duration': 0.09064,
                'keyword_type': 'Ajamärksõnad',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.13511,
                'keyword_type': 'Vormimärksõnad',
                'model_arch': 'omikuji'
            },
            {
                'duration': 21.35023,
                'keyword_type': 'NER',
                'model_arch': 'ner'
            },
            {
                'duration': 0.27533,
                'keyword_type': 'UDK Rahvusbibliograafia',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.41806,
                'keyword_type': 'UDC Summary',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.18271,
                'keyword_type': 'Valdkonnamärksõnad',
                'model_arch': 'omikuji'
            }],
        'keywords': [{
            'entity_type': 'Teemamärksõnad',
            'keyword': 'filmid (teosed)',
            'model_arch': 'omikuji',
            'score': 0.979
        },
            {
                'entity_type': 'Vormimärksõnad',
                'keyword': 'filmiarvustused',
                'model_arch': 'omikuji',
                'score': 0.905
            },
            {
                'count': 3,
                'entity_type': 'Isikunimi',
                'keyword': 'Sean Baker',
                'method': 'ner_ensemble',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 5,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Wicked',
                'method': 'gliner',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 5,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Brutalist',
                'method': 'gliner',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 4,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Anora',
                'method': 'gliner',
                'model_arch': 'ner',
                'score': 0.8
            },
            {
                'entity_type': 'UDK Rahvusbibliograafia',
                'keyword': '791',
                'model_arch': 'omikuji',
                'score': 1.0
            },
            {
                'entity_type': 'Valdkonnamärksõnad',
                'keyword': 'FOTOGRAAFIA. FILM. KINO',
                'model_arch': 'omikuji',
                'score': 1.0
            },
            {
                'entity_type': 'Valdkonnamärksõnad',
                'keyword': 'KOHANIMED',
                'model_arch': 'omikuji',
                'score': 0.944
            }]
    }

    expected_durations = expected_output.get("durations")
    expected_keywords = expected_output.get("keywords")

    # Remove actual duration as it is not deterministic

    for duration in expected_durations:
        duration.pop("duration")

    true_durations = subject_indices.get("durations")
    true_keywords = subject_indices.get("keywords")

    for duration in true_durations:
        duration.pop("duration")

    # assert are_equal_json(expected_durations, true_durations)
    # assert are_equal_json(expected_keywords, true_keywords)


@pytest.mark.order(3)
def test_apply_indexers_default():
    text = load_text(TEST_TEXT_FILE_PATHS["text_3"])
    subject_indices = rara_indexer_1.apply_indexers(
        text=text,
        threshold_config=THRESHOLD_CONFIG
    )
    assert subject_indices
    expected_output = {
        'durations': [{
            'duration': 8.45696,
            'keyword_type': 'Teemamärksõnad',
            'model_arch': 'omikuji'
        },
            {
                'duration': 1.42031,
                'keyword_type': 'Teemamärksõnad',
                'model_arch': 'rakun'
            },
            {
                'duration': 0.10458,
                'keyword_type': 'Ajamärksõnad',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.14018,
                'keyword_type': 'Vormimärksõnad',
                'model_arch': 'omikuji'
            },
            {
                'duration': 21.67658,
                'keyword_type': 'NER',
                'model_arch': 'ner'
            },
            {
                'duration': 0.30305,
                'keyword_type': 'UDK Rahvusbibliograafia',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.43842,
                'keyword_type': 'UDC Summary',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.18672,
                'keyword_type': 'Valdkonnamärksõnad',
                'model_arch': 'omikuji'
            }],
        'keywords': [{
            'entity_type': 'Teemamärksõnad',
            'keyword': 'filmid (teosed)',
            'model_arch': 'omikuji',
            'language': 'et',
            'score': 0.979
        },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'mängufilmid',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 0.573
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'filmiauhinnad',
                'model_arch': 'omikuji',
                'language': 'et',
                'score': 0.164
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'film',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.32
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'metsatulekahju',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.025
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'austusavaldus',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.023
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'valu',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.02
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'muusik',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.02
            },
            {
                'entity_type': 'Vormimärksõnad',
                'keyword': 'filmiarvustused',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 0.905
            },
            {
                'count': 3,
                'entity_type': 'Isikunimi',
                'keyword': 'Sean Baker',
                'language': 'et',
                'method': 'ner_ensemble',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 5,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Wicked',
                'language': 'et',
                'method': 'gliner',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 5,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Brutalist',
                'language': 'et',
                'method': 'gliner',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 4,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Anora',
                'language': 'et',
                'method': 'gliner',
                'model_arch': 'ner',
                'score': 0.8
            },
            {
                'count': 3,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Nosferatu',
                'language': 'et',
                'method': 'gliner',
                'model_arch': 'ner',
                'score': 0.6
            },
            {
                'count': 3,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Vooluga kaasa',
                'language': 'et',
                'method': 'gliner',
                'model_arch': 'ner',
                'score': 0.6
            },
            {
                'entity_type': 'UDK Rahvusbibliograafia',
                'keyword': '791',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 1.0
            },
            {
                'entity_type': 'Valdkonnamärksõnad',
                'keyword': 'FOTOGRAAFIA. FILM. KINO',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 1.0
            },
            {
                'entity_type': 'Valdkonnamärksõnad',
                'keyword': 'KOHANIMED',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 0.944
            },
            {
                'entity_type': 'Valdkonnamärksõnad',
                'language': 'et',
                'keyword': 'AJAKIRJANDUS. KOMMUNIKATSIOON. MEEDIA. REKLAAM',
                'model_arch': 'omikuji',
                'score': 0.449
            }]
    }

    expected_durations = expected_output.get("durations")
    expected_keywords = expected_output.get("keywords")

    # Remove actual duration as it is not deterministic

    for duration in expected_durations:
        duration.pop("duration")

    true_durations = subject_indices.get("durations")
    true_keywords = subject_indices.get("keywords")

    for duration in true_durations:
        duration.pop("duration")

    # assert are_equal_json(expected_durations, true_durations)
    # assert are_equal_json(expected_keywords, true_keywords)


@pytest.mark.order(4)
def test_apply_indexers_change_method_params():
    text = load_text(TEST_TEXT_FILE_PATHS["text_3"])
    subject_indices = rara_indexer_1.apply_indexers(
        text=text,
        threshold_config=THRESHOLD_CONFIG,
        rakun_config={"use_phraser": True, "postags_to_ignore": "V"},
        ner_config={"lemmatize": True, "min_count": 2}
    )

    # pprint(subject_indices)
    assert subject_indices
    expected_output = {
        'durations': [{
            'duration': 0.03089,
            'keyword_type': 'Teemamärksõnad',
            'model_arch': 'omikuji'
        },
            {
                'duration': 1.3078,
                'keyword_type': 'Teemamärksõnad',
                'model_arch': 'rakun'
            },
            {
                'duration': 0.01059,
                'keyword_type': 'Ajamärksõnad',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.01231,
                'keyword_type': 'Vormimärksõnad',
                'model_arch': 'omikuji'
            },
            {
                'duration': 4.16057,
                'keyword_type': 'NER',
                'model_arch': 'ner'
            },
            {
                'duration': 0.0123,
                'keyword_type': 'UDK Rahvusbibliograafia',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.01058,
                'keyword_type': 'UDC Summary',
                'model_arch': 'omikuji'
            },
            {
                'duration': 0.00765,
                'keyword_type': 'Valdkonnamärksõnad',
                'model_arch': 'omikuji'
            }],
        'keywords': [{
            'entity_type': 'Teemamärksõnad',
            'keyword': 'filmid (teosed)',
            'language': 'et',
            'model_arch': 'omikuji',
            'score': 0.979
        },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'mängufilmid',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 0.573
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'filmiauhinnad',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 0.164
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'film',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.323
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'parim',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.173
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'tundmatu',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.117
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'esimene',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.064
            },
            {
                'entity_type': 'Teemamärksõnad',
                'keyword': 'pöörama_tähelepanu',
                'language': 'et',
                'model_arch': 'rakun',
                'score': 0.033
            },
            {
                'entity_type': 'Vormimärksõnad',
                'keyword': 'filmiarvustused',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 0.905
            },
            {
                'count': 2,
                'entity_type': 'Isikunimi',
                'keyword': 'Mikey Madison',
                'language': 'et',
                'method': 'ner_ensemble',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 2,
                'entity_type': 'Isikunimi',
                'keyword': 'Adrien Brody',
                'language': 'et',
                'method': 'ner_ensemble',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 2,
                'entity_type': 'Isikunimi',
                'keyword': 'Cynthia Erivo',
                'language': 'et',
                'method': 'ner_ensemble',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 2,
                'entity_type': 'Isikunimi',
                'keyword': 'Kieran Culkin',
                'language': 'et',
                'method': 'ner_ensemble',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 9,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Brutal',
                'method': 'gliner',
                'language': 'et',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 4,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Wicke',
                'method': 'gliner',
                'language': 'et',
                'model_arch': 'ner',
                'score': 0.44
            },
            {
                'count': 3,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Anora',
                'method': 'gliner',
                'language': 'et',
                'model_arch': 'ner',
                'score': 0.33
            },
            {
                'count': 3,
                'entity_type': 'Teose pealkiri',
                'keyword': 'vool kaasa',
                'method': 'gliner',
                'language': 'et',
                'model_arch': 'ner',
                'score': 0.33
            },
            {
                'count': 3,
                'entity_type': 'Teose pealkiri',
                'keyword': 'Emilia Perez',
                'method': 'gliner',
                'language': 'et',
                'model_arch': 'ner',
                'score': 0.33
            },
            {
                'count': 6,
                'entity_type': 'Ajutine kollektiiv või sündmus',
                'keyword': 'Oscari',
                'method': 'gliner',
                'language': 'et',
                'model_arch': 'ner',
                'score': 1.0
            },
            {
                'count': 2,
                'entity_type': 'Ajutine kollektiiv või sündmus',
                'keyword': 'gala',
                'method': 'gliner',
                'language': 'et',
                'model_arch': 'ner',
                'score': 0.33
            },
            {
                'entity_type': 'UDK Rahvusbibliograafia',
                'keyword': '791',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 1.0
            },
            {
                'entity_type': 'Valdkonnamärksõnad',
                'keyword': 'FOTOGRAAFIA. FILM. KINO',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 1.0
            },
            {
                'entity_type': 'Valdkonnamärksõnad',
                'keyword': 'KOHANIMED',
                'language': 'et',
                'model_arch': 'omikuji',
                'score': 0.944
            },
            {
                'entity_type': 'Valdkonnamärksõnad',
                'language': 'et',
                'keyword': 'AJAKIRJANDUS. KOMMUNIKATSIOON. MEEDIA. REKLAAM',
                'model_arch': 'omikuji',
                'score': 0.449
            }]
    }

    expected_durations = expected_output.get("durations")
    expected_keywords = expected_output.get("keywords")

    # Remove actual duration as it is not deterministic

    for duration in expected_durations:
        duration.pop("duration")

    true_durations = subject_indices.get("durations")
    true_keywords = subject_indices.get("keywords")

    for duration in true_durations:
        duration.pop("duration")

    # assert are_equal_json(expected_durations, true_durations)
    # assert are_equal_json(expected_keywords, true_keywords)


@pytest.mark.order(5)
def test_updating_threshold_config():
    rara_indexer_1._set_threshold_config()
    true_config = rara_indexer_1.threshold_config
    expected_config = THRESHOLD_CONFIG

    check_equality(true_config, expected_config)

    rara_indexer_1._set_threshold_config(default_max_count=10)
    true_config = rara_indexer_1.threshold_config
    expected_config = THRESHOLD_CONFIG_1

    check_equality(true_config, expected_config)

    new_config = {
        KeywordType.TOPIC: {
            ModelArch.RAKUN: {
                "max_count": 15
            }
        },
        KeywordType.ORG: {
            ModelArch.NER: {
                "max_count": 6,
                "min_score": 0.1
            }
        },
        KeywordType.CATEGORY: {
            ModelArch.OMIKUJI: {
                "max_count": 2
            }
        }
    }

    rara_indexer_1._set_threshold_config(threshold_config=new_config)
    true_config = rara_indexer_1.threshold_config
    expected_config = THRESHOLD_CONFIG_2
    check_equality(true_config, expected_config)


@pytest.mark.order(6)
def test_ignore_max_count_for_equal_scores():
    text = (
        f"Lennart Meri pidas eile kõne. Seal rõhutas Lennart Meri lugemise tähtsust. " \
        f"Oskar Luts kiitis tema kõne heaks. Oskar Lutsu väitel polnud ta nii head kõne kuulnudki. " \
        f"Lennart Meri tänas Oskar Lutsu südamest."
    )
    # Test ignore_for_equal_scores=True
    rara_indexer_1._set_threshold_config()
    subject_indices = rara_indexer_1.apply_indexers(
        text=text, max_count=1, min_score=0, flat=False,
        ner_config={"min_count": 1}, ignore_for_equal_scores=True
    )
    keywords = subject_indices.get("keywords", [])

    for keyword_batch in keywords:
        print(keyword_batch)
        keyword_type = keyword_batch.get("keyword_type")
        model_arch = keyword_batch.get("model_arch")
        kws = keyword_batch.get("keywords")

        # The model should detect 2 persons, "Oskar Luts" and "Lennart Meri"
        # with equal counts (3) and thus scores (1.0). If `ignore_for_equal_scores`
        # is enabled, both these persos should be returned, even if 
        # max_count is set lower.
        if keyword_type in [KeywordType.PER.value, KeywordType.CATEGORY.value] or model_arch == ModelArch.RAKUN:
            assert len(kws) >= 2
        else:
            assert len(kws) == 1

    # Test ignore_for_equal_scores=False
    subject_indices = rara_indexer_1.apply_indexers(
        text=text, max_count=1, min_score=0, flat=False,
        ner_config={"min_count": 1}, ignore_for_equal_scores=False
    )
    keywords = subject_indices.get("keywords", [])
    for keyword_batch in keywords:
        keyword_type = keyword_batch.get("keyword_type")
        kws = keyword_batch.get("keywords")

        assert len(kws) == 1


@pytest.mark.order(7)
def test_updating_methods():
    INVALID_NEW_METHOD_MAP = {
        "blalala": [ModelArch.RAKUN],
        KeywordType.LOC: [ModelArch.STANZA],
        KeywordType.PER: [ModelArch.GLINER],
        KeywordType.ORG: [ModelArch.NER_ENSEMBLE],
        KeywordType.TIME: [ModelArch.OMIKUJI]
    }

    with pytest.raises(InvalidKeywordTypeException) as e:
        rara_indexer_2 = RaraSubjectIndexer(
            methods=INVALID_NEW_METHOD_MAP,
            keyword_types=TEST_KEYWORD_TYPES,
            topic_config=TOPIC_CONFIG,
            time_config=TIME_CONFIG,
            genre_config=GENRE_CONFIG,
            category_config=CATEGORY_CONFIG,
            udk_config=UDC_CONFIG,
            udc_config=UDC2_CONFIG,
            ner_config=NER_CONFIG,
            omikuji_data_dir=OMIKUJI_DATA_DIR,
            ner_data_dir=NER_DATA_DIR
        )

    INVALID_NEW_METHOD_MAP = {
        KeywordType.TOPIC: [ModelArch.RAKUN, "grr"],
        KeywordType.LOC: [ModelArch.STANZA],
        KeywordType.PER: [ModelArch.GLINER],
        KeywordType.ORG: [ModelArch.NER_ENSEMBLE],
        KeywordType.TIME: [ModelArch.OMIKUJI]
    }

    with pytest.raises(InvalidMethodException) as e:
        rara_indexer_2 = RaraSubjectIndexer(
            methods=INVALID_NEW_METHOD_MAP,
            keyword_types=TEST_KEYWORD_TYPES,
            topic_config=TOPIC_CONFIG,
            time_config=TIME_CONFIG,
            genre_config=GENRE_CONFIG,
            category_config=CATEGORY_CONFIG,
            udk_config=UDC_CONFIG,
            udc_config=UDC2_CONFIG,
            ner_config=NER_CONFIG,
            omikuji_data_dir=OMIKUJI_DATA_DIR,
            ner_data_dir=NER_DATA_DIR
        )

    NEW_METHOD_MAP = {
        KeywordType.TOPIC: [ModelArch.RAKUN],
        KeywordType.LOC: [ModelArch.STANZA],
        KeywordType.PER: [ModelArch.GLINER],
        KeywordType.ORG: [ModelArch.NER_ENSEMBLE],
        KeywordType.TIME: [ModelArch.OMIKUJI]
    }
    rara_indexer_2 = RaraSubjectIndexer(
        methods=NEW_METHOD_MAP,
        keyword_types=TEST_KEYWORD_TYPES,
        topic_config=TOPIC_CONFIG,
        time_config=TIME_CONFIG,
        genre_config=GENRE_CONFIG,
        category_config=CATEGORY_CONFIG,
        udk_config=UDC_CONFIG,
        udc_config=UDC2_CONFIG,
        ner_config=NER_CONFIG,
        omikuji_data_dir=OMIKUJI_DATA_DIR,
        ner_data_dir=NER_DATA_DIR
    )

    text = (
        f"Lennart Meri pidas eile kõne. Seal rõhutas Lennart Meri lugemise tähtsust. " \
        f"Oskar Luts kiitis tema kõne heaks. Oskar Lutsu väitel polnud ta nii head kõne kuulnudki. " \
        f"Lennart Meri tänas Oskar Lutsu südamest."
    )
    subject_indices = rara_indexer_2.apply_indexers(text=text)
    assert subject_indices


@pytest.mark.order(8)
def test_keyword_language():
    text = (
        f"Rail Baltic Estonia on Friday signed the largest infrastructure construction contracts " \
        f"in Estonian history, with a total value potentially reaching nearly €1 billion. " \
        f"Project teams led by companies from Finland and France will complete the Estonian section " \
        f"of the Rail Baltica railway by 2030."
    )
    rara_indexer_1._set_threshold_config()
    subject_indices = rara_indexer_1.apply_indexers(
        text=text, max_count=10, min_score=0, flat=False,
        ner_config={"min_count": 1}, ignore_for_equal_scores=True
    )
    keywords = subject_indices.get("keywords", [])

    for keyword_batch in keywords:
        model_arch = keyword_batch.get("model_arch")
        kws = keyword_batch.get("keywords")

        for kw in kws:
            if model_arch == ModelArch.OMIKUJI:
                assert kw.get("language") == Language.ET
            else:
                assert kw.get("language") == Language.EN
