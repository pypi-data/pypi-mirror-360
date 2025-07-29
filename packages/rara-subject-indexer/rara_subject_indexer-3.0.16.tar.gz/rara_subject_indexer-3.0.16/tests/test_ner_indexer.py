from rara_subject_indexer.ner.ner_subject_indexer import NERIndexer
from rara_subject_indexer.ner.ner_taggers.gliner_tagger import GLiNERTagger
from rara_subject_indexer.ner.ner_taggers.stanza_ner_tagger import StanzaNERTagger
from rara_subject_indexer.config import (
    GLINER_ENTITY_TYPE_MAP, 
    EntityType, 
    KeywordType,
    EnsembleStrategy, 
    NERMethod
)
from rara_subject_indexer.exceptions import InvalidLanguageException
from typing import List
from time import sleep, time

import pytest
import shutil
import os
import pathlib
import collections
import logging
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = os.path.join(ROOT_DIR, "tests", "test_data")

TEST_TEXT_FILE_PATHS = {
    "text_1": os.path.join(TEST_DATA_DIR, "text_1.txt"),
    "text_2": os.path.join(TEST_DATA_DIR, "text_2.txt"),
    "text_3": os.path.join(TEST_DATA_DIR, "text_3.txt"),
    "text_4": os.path.join(TEST_DATA_DIR, "text_4.txt")
}

TEMP_RESOURCES_DIR = os.path.join(".", "data", "ner_resources")

STANZA_CUSTOM_NER_MODELS = {
    "et": "https://packages.texta.ee/texta-resources/ner_models/_estonian_nertagger.pt",
    "lv": "https://packages.texta.ee/texta-resources/ner_models/_latvian_nertagger.pt",
    "lt": "https://packages.texta.ee/texta-resources/ner_models/_lithuanian_nertagger.pt"
}



STANZA_TEST_CONFIG = {
    "resource_dir": TEMP_RESOURCES_DIR,
    "download_resources": False,
    "supported_languages": ["et", "en"],
    "custom_ner_model_langs": ["et"],
    "refresh_data": False,
    "custom_ner_models": STANZA_CUSTOM_NER_MODELS,
    "unknown_lang_token": "unk"  
}


GLINER_MODEL_NAME = "urchade/gliner_multi-v2.1"
NORMALIZED_GLINER_MODEL_NAME = GLiNERTagger.normalize_name(GLINER_MODEL_NAME)

GLINER_TEST_LABELS = [
    "Person",
    "Organization",
    "Location",
    "Title of a work",
    "Date"
]

GLINER_TEST_CONFIG = {
    "resource_dir": TEMP_RESOURCES_DIR,
    "labels": GLINER_TEST_LABELS, 
    "model_name": GLINER_MODEL_NAME,
    "multi_label": False,
    "threshold": 0.5,
    "device": "cpu"
}

TEST_METHOD_MAP = {
    EntityType.PER: NERMethod.ENSEMBLE, 
    EntityType.ORG: NERMethod.ENSEMBLE,
    EntityType.LOC: NERMethod.ENSEMBLE,
    EntityType.DATE: NERMethod.STANZA,
    EntityType.TITLE: NERMethod.GLINER
}

GLINER_MODEL_PATH = os.path.join(TEMP_RESOURCES_DIR, "gliner", NORMALIZED_GLINER_MODEL_NAME)


STANZA_RESOURCES_PATH = os.path.join(TEMP_RESOURCES_DIR, "stanza", "resources")
STANZA_CUSTOM_NER_MODELS_PATH = os.path.join(TEMP_RESOURCES_DIR, "stanza", "custom_ner_models")
                                      

                                                                            
RELEVANT_STANZA_CUSTOM_NER_MODEL_FILES = [
    os.path.join(STANZA_CUSTOM_NER_MODELS_PATH, "et")
]
                                                                            
RELEVANT_GLINER_MODEL_FILES = [
    os.path.join(GLINER_MODEL_PATH, "added_tokens.json"),
    os.path.join(GLINER_MODEL_PATH, "gliner_config.json"),
    os.path.join(GLINER_MODEL_PATH, "pytorch_model.bin"),
    os.path.join(GLINER_MODEL_PATH, "special_tokens_map.json"),
    os.path.join(GLINER_MODEL_PATH, "spm.model"),
    os.path.join(GLINER_MODEL_PATH, "tokenizer.json"),
    os.path.join(GLINER_MODEL_PATH, "tokenizer_config.json")    
]

# Some helper functions
are_equal = lambda x, y: collections.Counter(x) == collections.Counter(y)

def get_all_files(root_dir: str) -> List[str]:
    file_paths = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def load_text(file_path: str) -> str:
    with open(file_path, "r") as f:
        text = f.read()
    return text
    
    
@pytest.fixture(scope="module")
def temp_directory():
    temp_dir = TEMP_RESOURCES_DIR
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    yield temp_dir

    shutil.rmtree(temp_dir)


#@pytest.mark.order(1)                                 
def test_stanza_resources_download(temp_directory):
    StanzaNERTagger.download_stanza_resources(
        resource_dir=STANZA_TEST_CONFIG["resource_dir"], 
        supported_languages=STANZA_TEST_CONFIG["supported_languages"]
    )
    
    for lang in STANZA_TEST_CONFIG["supported_languages"]:
        file_path = os.path.join(STANZA_RESOURCES_PATH, lang)
        print(f"File path: {file_path}")
        assert os.path.exists(file_path)
        assert os.path.isdir(file_path)
        
        
        downloaded_resources = get_all_files(file_path)
        print(f"Downloaded resources: {downloaded_resources}")
        assert len(downloaded_resources) > 5
    resources_json_file_path = os.path.join(STANZA_RESOURCES_PATH, "resources.json")
    assert os.path.exists(resources_json_file_path)

       
#@pytest.mark.order(2)
def test_custom_stanza_model_download(temp_directory):
    StanzaNERTagger.download_custom_ner_models(
        resource_dir=STANZA_TEST_CONFIG["resource_dir"], 
        custom_ner_model_urls=STANZA_TEST_CONFIG["custom_ner_models"],
        model_langs=STANZA_TEST_CONFIG["custom_ner_model_langs"]
    )
    #sleep_time = 15
    #print(f"Waiting {sleep_time} seconds for the model to download...")
    #LOGGER.info(f"Waiting {sleep_time} seconds for the model to download...")
    #sleep(sleep_time)
    downloaded_files = get_all_files(STANZA_CUSTOM_NER_MODELS_PATH)
    print(f"Downloaded files: {downloaded_files}")
    assert are_equal(RELEVANT_STANZA_CUSTOM_NER_MODEL_FILES, downloaded_files)   


#@pytest.mark.order(3)
def test_gliner_models_download(temp_directory):
    GLiNERTagger.download_gliner_resources(
        resource_dir=GLINER_TEST_CONFIG["resource_dir"],
        model_name=GLINER_TEST_CONFIG["model_name"]
    )
    downloaded_files = get_all_files(GLINER_MODEL_PATH)
    assert are_equal(RELEVANT_GLINER_MODEL_FILES, downloaded_files)   
    

#@pytest.mark.order(4)
def test_applying_stanza_ner(temp_directory):
    stanza_tagger = StanzaNERTagger(**STANZA_TEST_CONFIG)
    text = "Andrus Ansip (sündinud 1. oktoobril 1956 Tartus) on Eesti poliitik, Euroopa Parlamendi liige."
    ents_ = stanza_tagger.apply(text)
    ents = [ent.to_dict() for ent in ents_]
    _expected_output = [
        {
            'entity': 'Andrus Ansip', 
            'entity_type': 'PER', 
            'start': 0, 
            'end': 12, 
            'spans': (0, 12), 
            'score': None
        },   
        {
            'entity': '1. oktoobril 1956', 
            'entity_type': 'DATE', 
            'start': 23, 
            'end': 40, 
            'spans': (23, 40), 
            'score': None
        }, 
        {
            'entity': 'Tartus', 
            'entity_type': 'GPE', 
            'start': 41, 
            'end': 47, 
            'spans': (41, 47), 
            'score': None
        }, 
        {
            'entity': 'Eesti', 
            'entity_type': 'GPE', 
            'start': 52, 
            'end': 57, 
            'spans': (52, 57), 
            'score': None
        }, 
        {
            'entity': 'Euroopa Parlamendi', 
            'entity_type': 'ORG', 
            'start': 68, 
            'end': 86, 
            'spans': (68, 86), 
            'score': None
        }
    ]
    print(f"Extracted entities: {ents}")
    true_output = [json.dumps(ent) for ent in ents]
    expected_output = [json.dumps(ent) for ent in _expected_output]
    assert are_equal(true_output, expected_output)
    
    
#@pytest.mark.order(5)
def test_applying_stanza_ner_tagger_with_invalid_lang_raises_exception():
    # Should NOT return matches
    stanza_tagger = StanzaNERTagger(**STANZA_TEST_CONFIG)
    text_et = "Andrus Ansip (sündinud 1. oktoobril 1956 Tartus) on Eesti poliitik, Euroopa Parlamendi liige."
    text_fr = "Andrus Ansip (né le 1er octobre 1956 à Tartu) est un homme politique estonien, membre du Parlement européen."
    
    # Test text in supported language with invalid lang param
    with pytest.raises(InvalidLanguageException) as e:
        stanza_tagger.apply(text_et, lang="ru")
        
    # Test text in unsupported language
    with pytest.raises(InvalidLanguageException) as e:
        stanza_tagger.apply(text_fr)

#@pytest.mark.order(6)
def test_applying_gliner(temp_directory):
    gliner_tagger = GLiNERTagger(**GLINER_TEST_CONFIG)
    text = "Andrus Ansip (sündinud 1. oktoobril 1956 Tartus) on Eesti poliitik, Euroopa Parlamendi liige. Tema lemmikteos on 'Tõde ja õigus'."
    ents_ = gliner_tagger.apply(text)
    ents = [ent.to_dict() for ent in ents_]
    print(f"Extracted entities: {ents}")
    
    # Remove scores just in case they are not deterministic
    for ent in ents:
        del ent["score"]
        
    _expected_output = [
        {
            'entity': 'Andrus Ansip', 
            'entity_type': 'Person', 
            'start': 0, 
            'end': 12, 
            'spans': (0, 12)
        }, 
        {
            'entity': '1. oktoobril 1956', 
            'entity_type': 'Date', 
            'start': 23, 
            'end': 40, 
            'spans': (23, 40)
        }, 
        {
            'entity': 'Tartus', 
            'entity_type': 'Location', 
            'start': 41, 
            'end': 47, 
            'spans': (41, 47)
        }, 
        {
            'entity': 'Eesti', 
            'entity_type': 
            'Location', 
            'start': 52, 
            'end': 57, 
            'spans': (52, 57)
        }, 
        {
            'entity': 'Euroopa Parlamendi', 
            'entity_type': 'Organization', 
            'start': 68, 
            'end': 86, 
            'spans': (68, 86)
        },
        {
            'entity': 'Tõde ja õigus',
            'entity_type': 'Title of a work', 
            'start': 114, 
            'end': 127, 
            'spans': (114, 127)
        }
    ]

    true_output = [json.dumps(ent) for ent in ents]
    expected_output = [json.dumps(ent) for ent in _expected_output]
    assert are_equal(true_output, expected_output)
    
#@pytest.mark.order(7)    
def test_ner_indexer(temp_directory):
    ner_indexer = NERIndexer(
        stanza_config = STANZA_TEST_CONFIG,
        gliner_config = GLINER_TEST_CONFIG,
        method_map = TEST_METHOD_MAP,
        download_resources = False
    )
    text = load_text(TEST_TEXT_FILE_PATHS.get("text_3"))
    #keywords = ner_indexer.find_keywords(text=text, min_score=0.5, min_count=2)
    ner_indexer.apply_ner_taggers(text)
    all_keywords = ner_indexer.get_keywords(ensemble_strategy=EnsembleStrategy.INTERSECTION)
    keywords = all_keywords.filter_keywords(min_score=0.5, min_count=2)
    print(f"Extracted entities: {keywords}")

    _expected_output = [
        {
            'count': 3,
            'entity_type': KeywordType.PER,
            'keyword': 'Sean Baker',
            'method': NERMethod.ENSEMBLE,
            'score': 1.0
        },
        {
            'count': 6,
            'entity_type': KeywordType.TITLE,
            'keyword': 'Anora',
            'method': NERMethod.GLINER,
            'score': 1.0
        },
        {
            'count': 5,
            'entity_type': KeywordType.TITLE,
            'keyword': 'Wicked',
            'method': NERMethod.GLINER,
            'score': 0.83
        },
        {
            'count': 2,
            'entity_type': KeywordType.PER,
            'keyword': 'Cynthia Erivo',
            'method': NERMethod.ENSEMBLE,
            'score': 0.67
        },
        {
            'count': 2,
            'entity_type': KeywordType.PER,
            'keyword': 'Adrien Brody',
            'method': NERMethod.ENSEMBLE,
            'score': 0.67
        },
        {
            'count': 2,
            'entity_type': KeywordType.PER,
            'keyword': 'Kieran Culkin',
            'method': NERMethod.ENSEMBLE,
            'score': 0.67
        },
        {
            'count': 2,
            'entity_type': KeywordType.PER,
            'keyword': 'Mikey Madison',
            'method': NERMethod.ENSEMBLE,
            'score': 0.67
        },
        {
            'count': 2,
            'entity_type': KeywordType.PER,
            'keyword': "Conan O'Brien",
            'method': NERMethod.ENSEMBLE,
            'score': 0.67
        },
        {
            'count': 3,
            'entity_type': KeywordType.TITLE,
            'keyword': 'Brutalist',
            'method': NERMethod.GLINER,
            'score': 0.5
        },
        {
            'count': 3,
            'entity_type': KeywordType.TITLE,
            'keyword': 'Nosferatu',
            'method': NERMethod.GLINER,
            'score': 0.5
        }
    ]
    true_output = [
        json.dumps(sorted(list(ent.items()))) 
        for ent in keywords
    ]
    expected_output = [
        json.dumps(sorted(list(ent.items()))) 
        for ent in _expected_output
    ]
    
    assert are_equal(true_output, expected_output)
    
    
#@pytest.mark.order(8)    
def test_ner_indexer_find_keywords(temp_directory):
    ner_indexer = NERIndexer(
        stanza_config = STANZA_TEST_CONFIG,
        gliner_config = GLINER_TEST_CONFIG,
        method_map = TEST_METHOD_MAP,
        download_resources = False
    )
    text_1 = load_text(TEST_TEXT_FILE_PATHS.get("text_1"))
    text_3 = load_text(TEST_TEXT_FILE_PATHS.get("text_3"))
    
    
    # First function call should take longer; 
    # calling the same function with the same text
    # should take a lot less time
    start_1 = time()
    
    keywords_1 = ner_indexer.find_keywords(
        text=text_1, 
        ensemble_strategy=EnsembleStrategy.INTERSECTION,
        min_score=0.5,
        min_count=2
    )
    
    dur_1 = time() - start_1
    
    
    print(f"First function call took: {round(dur_1, 5)}s")
    
    start_2 = time()
    keywords_2 = ner_indexer.find_keywords(
        text=text_1, 
        ensemble_strategy=EnsembleStrategy.UNION,
        min_score=0.1,
        min_count=1
    )
    dur_2 = time() - start_2
    print(f"Second function call took: {round(dur_2, 5)}s")
          
    assert len(keywords_1) < len(keywords_2)
    assert dur_2 < dur_1
    
    # If text has changed, the function call should take longer again:
    start_3 = time()
    keywords_3 = ner_indexer.find_keywords(
        text=text_3, 
        ensemble_strategy=EnsembleStrategy.UNION,
        min_score=0.1,
        min_count=1
    )
    dur_3 = time() - start_3
    print(f"Third function call took: {round(dur_3, 5)}s")
    assert len(keywords_3) > 0
    assert dur_2 < dur_3
    
    # The fourth call with the same text should take less again:
    start_4 = time()
    keywords_4 = ner_indexer.find_keywords(
        text=text_3, 
        ensemble_strategy=EnsembleStrategy.UNION,
        min_score=0.1,
        min_count=1
    )
    dur_4 = time() - start_4
    print(f"Fourth function call took: {round(dur_4, 5)}s")
    assert len(keywords_3) == len(keywords_4)
    assert dur_4 < dur_3
    
    
    
    
    
    