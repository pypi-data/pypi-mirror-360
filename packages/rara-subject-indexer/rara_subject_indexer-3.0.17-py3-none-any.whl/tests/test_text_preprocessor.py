import pytest
import collections
import importlib.resources
from rara_subject_indexer.config import Language, PreprocessingMethod
from rara_subject_indexer.utils.text_preprocessor import (
    TextPreprocessor, ProcessedText
)
SUPPORTED_LEMMATIZER_LANGUAGES = {"et": "estonian"}
SUPPORTED_STEMMER_LANGUAGES = {"en": "english"}

PREPROCESSING_METHOD_MAP = {
    Language.ET: PreprocessingMethod.LEMMATIZE,
    Language.EN: PreprocessingMethod.STEM
}

SUPPORTED_PHRASER_MODEL_PATHS = {
    "et": {
        "package": "rara_subject_indexer",
        "resource": "resources/phrasers/phraser_ise_digar_et.model"
    }
}


are_equal = lambda x, y: collections.Counter(x) == collections.Counter(y)

def test_lemmatizing():
    text_processor = TextPreprocessor()
                
    text_et = "Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud."
    expected_output_et = "kui Arno isa koolimaja jõudma , olema tund juba alanud ."
    true_output_et = text_processor.lemmatize(text_et, lang_code="et")
    assert expected_output_et == true_output_et
    
    # If lang code != "et" or "en", the original text should be returned
    # as only Estonian and Englisg lemmatization is currently supported
    true_output_ru = text_processor.lemmatize(text_et, lang_code="ru")
    assert text_et == true_output_ru
    
    text_en = "No cats and dogs allowed"
    expected_output_en = "No cat and dog allowed"
    true_output_en = text_processor.lemmatize(text_en, lang_code="en")
    assert expected_output_en == true_output_en
    
    
def test_stemming():
    text_processor = TextPreprocessor(
        stemmer_languages={"en": "english", "fr": "french", "bl": "blah"}
    )
                
    text_en = (
        f"When Arno arrived at the school building with his father, " \
        f"classes had already started."
    )
    expected_output_en = (
        f"when arno arriv at the school build with his father, " \
        f"class had alreadi started."
    )
    true_output_en = text_processor.stem(text_en, lang_code="en")

    assert expected_output_en == true_output_en
    
    text_fr = (
        f"Quand Arno est arrivé à l'école avec son père, " \
        f"les cours avaient déjà commencé."
    )
    expected_output_fr = (
        f"quand arno est arriv à l'écol avec son père, " \
        f"le cour avaient déjà commence."
    )
    true_output_fr = text_processor.stem(text_fr, lang_code="fr")
    
    assert expected_output_fr == true_output_fr
    
    # Trying to apply stemming with language that is not supported
    # by SnowballStemmer (even if it is defined in stemmer_languages)
    # should return the original text
    true_output_bl = text_processor.stem(text_fr, lang_code="bl")
    
    assert true_output_bl == text_fr
    
    # Trying to apply stemming with language that is supported
    # by SnowballStemmer, but is not defined in stemmer_languages
    # should return the original text
    true_output_ru = text_processor.stem(text_fr, lang_code="ru")
    
    assert true_output_ru == text_fr
    
    # Trying to apply stemming with language that is not supported
    # by SnowballStemmer and is not defined in stemmer_languages
    # should return the original text
    true_output_zzz = text_processor.stem(text_fr, lang_code="zzz")
    
    assert true_output_zzz == text_fr
    
def test_tokenizing():
    text_processor = TextPreprocessor()
                
    text = "Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud."
    expected_output = (
        ["Kui", "Arno", "isaga", "koolimajja", "jõudis",
         "olid", "tunnid", "juba", "alanud"]
    )
    true_output = text_processor.tokenize(text)
    true_output_list = [token for token in true_output]
    assert are_equal(expected_output, true_output_list)
    
def test_applying_phraser():
    text_processor = TextPreprocessor(
        lemmatizer_languages={"et": "estonian"},
        phraser_paths=SUPPORTED_PHRASER_MODEL_PATHS
    )
                
    text = (
        f"Lennar Meri pidas Eesti Riigikogus Tartu ülikoolist " \
        f"kõne majandusaasta aruannetest, mida Kaja Kallas huviga kuulas."
    )
    lemmatized_text = text_processor.lemmatize(text, lang_code="et")
    expected_output_1 = (
        f"Lennar Meri pidama Eesti Riigikogu Tartu ülikool " \
        f"kõne majandusaasta_aruanne mis Kaja Kallas huvi kuulama"
    )
    true_output_1 = text_processor.apply_phraser(
        text=lemmatized_text, 
        lang_code="et", 
        lowercase=False
    )
    assert expected_output_1 == true_output_1
    
    expected_output_2 = (
        f"lennar_meri pidama eesti riigikogu tartu_ülikool kõne " \
        f"majandusaasta_aruanne mis kaja_kallas huvi kuulama"
    )
    true_output_2 = text_processor.apply_phraser(
        text=lemmatized_text, 
        lang_code="et", 
        lowercase=True
    )
    assert expected_output_2 == true_output_2
    
    # If phraser model for passed lang_code does not exist,
    # the function should return its input text
    expected_output_3 = lemmatized_text
    true_output_3 = text_processor.apply_phraser(
        text=lemmatized_text, 
        lang_code="en", 
        lowercase=True
    )
    assert expected_output_3 == true_output_3
    
def test_clean():
    # Load text_processor with default email and url patterns.
    text_processor = TextPreprocessor()
    
    text = (
        f"Kui Arno arno.tali@hotmail.com isaga koolimajja " \
        f"http://www.koolimaja.ee jõudis, olid tunnid juba alanud."
    )
    expected_output_1 = (
        f"Kui Arno  isaga koolimajja  " \
        f"jõudis, olid tunnid juba alanud."
    )
    true_output_1 = text_processor.clean(text)
    assert expected_output_1 == true_output_1
    
    # Load text_processor with custom email and url patterns.
    text_processor = TextPreprocessor(
        url_pattern = r"www[.]neti[.]ee",
        email_pattern = r"uku@mail[.]ee"
    )
    
    text = (
        f"Kui Arno arno.tali@hotmail.com isa Ukuga uku@mail.ee " \
        f"koolimajja http://www.koolimaja.ee jõudis, olid tunnid " \
        f"juba alanud. Loe lisaks: www.neti.ee"
    )
    expected_output_2 = (
        f"Kui Arno arno.tali@hotmail.com isa Ukuga  " \
        f"koolimajja http://www.koolimaja.ee jõudis, olid tunnid " \
        f"juba alanud. Loe lisaks: "
    )
    true_output_2 = text_processor.clean(text)
    assert expected_output_2 == true_output_2
    
                                  


    
    