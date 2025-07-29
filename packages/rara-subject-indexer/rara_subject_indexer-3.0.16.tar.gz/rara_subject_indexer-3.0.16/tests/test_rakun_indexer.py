import pytest
import nltk
from rara_subject_indexer.indexers.model_indexers.rakun_indexer import RakunIndexer
from rara_subject_indexer.unsupervised.rakun.rakun_keyword_extractor import RakunKeywordExtractor

nltk.download("punkt_tab")

def test_rakun_kw_extraction():
    text_content = "ühed dokumendid on siin\naga mõni teine on seal\n"\
                   "mõned hoopis aga taamal\nmõned olid kaugel\nmõned olid lähedal"
    expected_keywords = [('dokument',1.0)]#, ('kaugel', 0.4), ('taamal', 0.4)]
    kw_extractor = RakunKeywordExtractor()
    keywords = kw_extractor.predict(text_content, use_phraser=False, correct_spelling=False, preserve_case=False)
    assert sorted(expected_keywords) == sorted(keywords)
    
    
def test_rakun_indexer():
    config = {
        "lang": "et",
        "merge_threshold": 0.0,
        "use_phraser": False,
        "correct_spelling": False,
        "preserve_case": True,
        "max_uppercase": 2,
        "min_word_frequency": 3
    }

    indexer = RakunIndexer()#**config)
    preds = indexer.find_keywords("Tantsime kõik lapaduud, lapaduud", **config)

    assert all({"keyword", "score", "entity_type"} == set(pred.keys()) for pred in preds)

    expected_output = [{"keyword": "lapaduu", "entity_type": "Teemamärksõnad", "score": 1.0}]
    assert preds == expected_output