from estnltk import Text
from gensim.utils import tokenize as gensim_tokenize
from gensim.models.phrases import Phraser
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from rara_subject_indexer.utils.spellcorrector import SpellCorrector
from rara_subject_indexer.config import (
    Language, PreprocessingMethod, LOGGER, PREPROCESSING_METHOD_MAP,
    SUPPORTED_STEMMER_LANGUAGES, SUPPORTED_LEMMATIZER_LANGUAGES, POSTAGS_TO_IGNORE,
    SENTENCE_SPLIT_REGEX, URL_REGEX, EMAIL_REGEX, SUPPORTED_PHRASER_MODEL_PATHS,
    SPELLER_DEFAULTS
)

from rara_subject_indexer.exceptions import (
    InvalidLanguageException, StemmerLoadingException, NotImplementedException,
    InvalidInputException
)
from typing import Dict, NoReturn, List, Iterator
import langdetect
import regex as re
import importlib.resources
import nltk

nltk.download("wordnet") 
nltk.download("averaged_perceptron_tagger_eng")

class TextPreprocessor:
    """
    A text preprocessor that performs optional language detection,
    and uses Estnltk for Estonian
    """

    def __init__(self, 
        stemmer_languages: dict = SUPPORTED_STEMMER_LANGUAGES, 
        lemmatizer_languages: dict = SUPPORTED_LEMMATIZER_LANGUAGES,
        preprocessing_method_map: dict = PREPROCESSING_METHOD_MAP,
        phraser_paths: dict = SUPPORTED_PHRASER_MODEL_PATHS,
        url_pattern: str = URL_REGEX,
        email_pattern: str = EMAIL_REGEX
    ) -> NoReturn:
        """ Initializes TextPreprocessor
        
        Parameters
        -----------
        stemmer_languages: dict
            Map of supported stemmer languages, where
            key = ISO 639-1 language code and value = language.
        lemmatizer_languages: dict
            Map of supported lemmatizer languages, where
            key = ISO 639-1 language code and value = language.
        preprocessing_map: dict
            Map of preprocessing methods per language, where
            key = ISO 639-1 language code and value = preprocessing method
            ("stemmer" or "lemmatizer").
        """
        self.stemmer_languages: dict = stemmer_languages
        self.lemmatizer_languages: dict = lemmatizer_languages
        self.preprocessing_method_map: dict = preprocessing_method_map
        self.phraser_paths: dict = phraser_paths
        self.url_pattern: str = url_pattern
        self.email_pattern: str = email_pattern
        self.__stemmers: dict = {}
        self.__phrasers: dict = {}

    
    def _get_stemmer(self, lang_code: str) -> SnowballStemmer | None: 
        """ Loads stemmers on the go, if they are needed. Once a stemmer
        is loaded for a specific language, it will not be loaded again; 
        if a language is in self.stemmer_languages, but the stemmer for that
        language is not actually used, it will not be loaded.
        
        Parameters
        -----------
        lang_code: str
            ISO 639-1 language code.
        """
        LOGGER.info(f"Trying to load a stemmer for language '{lang_code}'.")
        if lang_code in self.stemmer_languages:
            if lang_code not in self.__stemmers:
                language = self.stemmer_languages.get(lang_code)
                try:
                    self.__stemmers[lang_code] = SnowballStemmer(language)
                except Exception as e:
                    error_msg = (
                        f"Failed loading stemmer for language '{language}' " \
                        f"with error: {e}."
                    )
                    LOGGER.error(error_msg)
                    #raise StemmerLoadingException(error_msg)
        else:
            error_msg = (
                f"Language '{lang_code}' is not in the list of " \
                f"supported stemmer languages. Supported stemmmer " \
                f"languages are: {self.stemmer_languages}."
            )
            LOGGER.error(error_msg)
            #raise StemmerLoadingException(error_msg)
        stemmer = self.__stemmers.get(lang_code, None)
        if stemmer:
            LOGGER.info(
                f"Successfully loaded stemmer for language '{lang_code}'."
            )
        return stemmer
    
    
    def _get_phraser(self, lang_code: str) -> Phraser | None:
        """ Loads phrasers on the go, if they are needed. Once a phraser
        is loaded for a specific language, it will not be loaded again; 
        if a language is in self.phraser_paths, but the phraser for that
        language is not actually used, it will not be loaded.
        
        Parameters
        -----------
        lang_code: str
            ISO 639-1 language code.
        """
        LOGGER.info(f"Trying to load a phraser for language '{lang_code}'.")
        if lang_code in self.phraser_paths:
            if lang_code not in self.__phrasers:
                try:
                    package = self.phraser_paths[lang_code]["package"]
                    resource = self.phraser_paths[lang_code]["resource"]
                    resource_path = str(
                        importlib.resources.files(package).joinpath(resource)
                    )
                    self.__phrasers[lang_code] = Phraser.load(resource_path)
                    
                except Exception as e:
                    error_msg = (
                        f"Failed loading phraser for language '{lang_code}' " \
                        f"with error: {e}."
                    )
                    LOGGER.error(error_msg)

        else:
            error_msg = (
                f"No phraser model for language '{lang_code}'. " \
                f"Map of currently accessible phraser models: " \
                f"{self.phraser_paths}."
            )
            LOGGER.error(error_msg)

        phraser = self.__phrasers.get(lang_code, None)
        if phraser:
            LOGGER.info(
                f"Successfully loaded phraser for language '{lang_code}'!"
            )
        return phraser
               
        
    @staticmethod
    def detect_language(text: str | Text) -> str | None:
        """
        Detects language of input text.
        If language not in supported list, language is 
        defaulted or exception raised.
        
        Parameters
        -----------
        text: str
            Text to be analyzed.
        
        Returns
        -----------
        str
            Language code in ISO 639-1 standard.
        """
        if not isinstance(text, str):
            text = text.text
        try:
            lang = langdetect.detect(text)
        except:
            lang = None
        LOGGER.debug(f"Detected language for text '{text[:20]}...': '{lang}'.")
        return lang
    
    def get_tag_layer(self, text: str, lang_code: str, 
                      analyzers: List[str] = []
    ) -> Text | None:
        """ Retrieves tag layer of the input text.
        NB! Currently only supports Estonian!
        
        Parameters
        ----------
        text : str
            The raw tex.
        lang_code: str
            Language code in ISO 639-1 standard.
            
        Returns
        -------
        Text | None
            EstNLTK Tag layer.
        """
    
        if lang_code == Language.ET:
            LOGGER.debug(
                f"Extracting tag layer from text '{text[:20]}'."
            )
            if analyzers:
                tag_layer = Text(text).tag_layer(analyzers)
            else:
                tag_layer = Text(text).tag_layer()
        else:
            error_msg = (
                f"Tag layer extraction for language '{lang_code}' is " \
                f"not implemented. Returning None."
            )
            LOGGER.error(error_msg)
            tag_layer = None
        return tag_layer
    
    def clean(self, text: str) -> str:
        """ Removes URLs and E-mail addresses from text.
        
        Parameters
        -----------
        text: str
            Text to clean.
        
        Returns
        -----------
        str
            Cleaned text.
        """
        LOGGER.debug(
            f"Removing URLs and E-mail addresses from text '{text[:20]}...'."
        )
        text = re.sub(self.url_pattern, "", text)
        text = re.sub(self.email_pattern, "", text)
        return text
    
    def get_postags(self, text: str | Text, lang_code: str) -> List[List[str]]:
        """ Applies POS-tag extraction to the input text / tag layer.
        NB! Currently only supports Estonian!
        
        Parameters
        ----------
        text : str | Text
            The raw text to extract POS-tags from or EstNLTK tag layer.
        lang_code: str
            Language code in ISO 639-1 standard.
            
        Returns
        -------
        List[List[str]]
            Extracted postags.
        """
 
        if lang_code == Language.ET:
            if isinstance(text, str):
                tag_layer = self.get_tag_layer(text, lang_code)
            else:
                tag_layer = text
                
            text = tag_layer.text
            
            LOGGER.debug(
                f"Extracting POS-tags from text '{text[:20]}'."
            )
            postags = tag_layer.partofspeech

        else:
            error_msg = (
                f"Postag extraction for language '{lang_code}' is " \
                f"not implemented. Returning an empty list."
            )
            LOGGER.error(error_msg)
            postags = []
        return postags
    
    def get_lemmas(self, text: str | Text, lang_code: str) -> List[List[str]]:
        """ Applies lemma extraction to the input text / tag layer.
        NB! Currently only supports Estonian and English!
        
        Parameters
        ----------
        text : str | Text
            The raw text to extract lemmas from or EstNLTK tag layer.
        lang_code: str
            Language code in ISO 639-1 standard.
            
        Returns
        -------
        List[List[str]]
            Extracted lemmas.
        """
 
        if lang_code == Language.ET:
            if isinstance(text, str):
                tag_layer = self.get_tag_layer(text, lang_code)
            else:
                tag_layer = text
                
            text = tag_layer.text
            
            LOGGER.debug(
                f"Extracting lemmas from text '{text[:20]}'."
            )
            lemmas = tag_layer.lemma
        
        elif lang_code == Language.EN:
            if not isinstance(text, str):
                LOGGER.error(
                    f"Text type {type(text)} is not supported " \
                    f"for language '{lang_code}'. Please use plaintext " \
                    f"for lemmatizing. Returning and empty list."
                )
                lemmas = []
            else:
                try:            
                    wnl = WordNetLemmatizer()
                    tokens = self.tokenize(text)
                    lemmas = [wnl.lemmatize(t) for t in tokens]
                except Exception as e:
                    LOGGER.error(
                        f"Lemmatization failed for language '{lang_code}' " \
                        f"with error: {e}. Returning and empty list."
                    )
                    lemmas = []
                      
        else:
            error_msg = (
                f"Lemma extraction for language '{lang_code}' is " \
                f"not implemented. Returning an empty list."
            )
            LOGGER.error(error_msg)
            lemmas = []
        return lemmas
    
    def lemmatize(self, text: str | Text, lang_code: str) -> str:
        """ Applies lemmatizer to the input text / tag layer.
        NB! Currently only supports Estonian and English!
        
        Parameters
        ----------
        text : str | Text
            The raw text to lemmatize or EstNLTK tag layer.
        lang_code: str
            Language code in ISO 639-1 standard.
            
        Returns
        -------
        str
            The lemmatized text.
        """
 
        if lang_code == Language.ET:
            lemmas = self.get_lemmas(text=text, lang_code=lang_code)
            lemmatized_text = " ".join(
                lemma[0] for lemma in lemmas
            )
        elif lang_code == Language.EN:
            lemmas = self.get_lemmas(text=text, lang_code=lang_code)
            if lemmas:
                lemmatized_text = " ".join(lemmas)
            else:
                LOGGER.error(
                    f"Lemmatization failed for language '{lang_code}'. " \
                    f"Returning the original text."
                )
                lemmatized_text = text
              
        else:
            error_msg = (
                f"Lemmatization for language '{lang_code}' is not implemented. " \
                f"Returning the original text."
            )
            LOGGER.error(error_msg)
            lemmatized_text = text
        return lemmatized_text
   
    
    def stem(self, text: str, lang_code: str) -> str:
        """
        Apply stemming on the text.

        Parameters
        ----------
        text: str
            Input text.
        lang_code: str
            Language code in ISO 639-1 standard.

        Returns
        -------
        str
            The stemmed text.
        """
        LOGGER.debug(f"Stemming text '{text[:20]}...'.")
        stemmer = self._get_stemmer(lang_code)
        if stemmer:
            stemmed_text = " ".join(
                stemmer.stem(token) 
                for token in text.split()
            )
        else:
            stemmed_text = text
            LOGGER.error(
                f"Could not load stemmer for language '{lang_code}' " \
                f"Returning the original text."
            )

        return stemmed_text
    
    def tokenize(self, text: str) -> Iterator[str]:
        """
        Apply tokenizer on the text.

        Parameters
        ----------
        text: str
            Input text.

        Returns
        -------
        Iterator[str]
            Generator for tokens.
        """
        LOGGER.debug(f"Tokenizing text '{text[:20]}'.")
        
        tokens = gensim_tokenize(text)
        return tokens
        
    def apply_phraser(self, text: str, lang_code: str, 
                      lowercase: bool = False
    ) -> str:
        """
        Apply phraser on the input text.

        Parameters
        ----------
        text:
            Input text.
        lang_code: str
            Language code in ISO 639-1 standard.

        Returns
        -------
        str
            Text, where found phrases are joined together using underscore.
        """
        LOGGER.debug(f"Trying to apply a phraser on text '{text[:20]}...'.")
        phraser = self._get_phraser(lang_code)
        
        if phraser:
            if lowercase:
                text = text.lower()
            tokens = self.tokenize(text)
            phrased_tokens = phraser[tokens]
            phrased_text = " ".join(phrased_tokens)
        else:
            phrased_text = text
            LOGGER.error(
                f"Could not load phraser for language '{lang_code}' " \
                f"Returning the original text."
            )
        return phrased_text
    
    def preprocess(self, text: str | Text, lang_code: str = "") -> str:
        """
        Detect language and lemmatize accordingly.

        Parameters
        ----------
        text : str
            The raw text to preprocess or an EstNLTK tag layer.
        lang_code: str
            Language code in ISO 639-1 standard.

        Returns
        -------
        str
            The lemmatized/stemmed text.
        """
        if not isinstance(text, str):
            text_str = text.text
        else:
            text_str = text
        LOGGER.debug(f"Applying preprocessing on text '{text_str[:20]}...'.")
        if not text:
            return ""
        if not lang_code:
            lang_code = TextPreprocessor.detect_language(text)
            
        method = self.preprocessing_method_map.get(lang_code, "")
        if method == PreprocessingMethod.LEMMATIZE:
            LOGGER.debug(
                f"Detected preprocessing method for '{lang_code}' " \
                f"is '{PreprocessingMethod.LEMMATIZE}'."
            )
            preprocessed_text = self.lemmatize(text, lang_code=lang_code)
        elif method == PreprocessingMethod.STEM:
            LOGGER.debug(
                f"Detected preprocessing method for '{lang_code}' " \
                f"is '{PreprocessingMethod.STEM}'."
            )
            preprocessed_text = self.stem(text, lang_code=lang_code)
        else:
            raise InvalidLanguageException(
                f"Unsupported language: {lang_code}. " \
                f"Before using this language, add preprocessing logic. " \
                f"Currently supported languages are: " \
                f"{list(self.preprocessing_method_map.keys())}."
            )

        return preprocessed_text
    
    
class ProcessedText:
    def __init__(self, 
        text: str, 
        text_preprocessor: TextPreprocessor, 
        lang_code: str = "",
        correct_spelling: bool = False,
        speller_config: dict = {
            "max_uppercase": SPELLER_DEFAULTS.get("max_uppercase"),
            "min_word_frequency": SPELLER_DEFAULTS.get("min_word_frequency"),
            "preserve_case": SPELLER_DEFAULTS.get("preserve_case")
        }
           
    ) -> NoReturn:
        self.original_text: str = text
        self.text_preprocessor: TextPreprocessor = text_preprocessor
        self.correct_spelling: bool = correct_spelling
        self.speller_config: dict =  speller_config
       
        self.__analyzers: List[str] = []
        self.__tag_layer: Text | None = None
            
        self.__processed_text: str = ""
        self.__cleaned_text: str = ""
        self.__processed_and_cleaned_text: str = ""
        self.__places: set | None = set()
        self.__lang_code: str = lang_code
        self.__phrased_text: str = ""
        self.__corrected_text: str = ""
        self.__speller: SpellCorrector | None = None
        self.__lemma_postag_map: dict = {}
        
    
    @property
    def speller(self) -> SpellCorrector:
        if not self.__speller:
            self.__speller = SpellCorrector()
        return self.__speller
    
    @property
    def analyzers(self) -> List[str]:
        if not self.__analyzers:
            self.__analyzers = ["morph_analysis"]
            if self.correct_spelling:
                self.__analyzers.append("ner")
        return self.__analyzers
    
    @property
    def tag_layer(self) -> Text | str:
        if not self.__tag_layer:
            self.__tag_layer = self.text_preprocessor.get_tag_layer(
                text=self.original_text,
                lang_code=self.lang_code,
                analyzers=self.analyzers
            )
            if not self.__tag_layer:
                self.__tag_layer = self.original_text
        return self.__tag_layer
    
    @property
    def lemma_postag_map(self) -> dict:
        if not self.__lemma_postag_map:
            if self.lang_code == Language.ET:
                lemmas = self.text_preprocessor.get_lemmas(
                    text=self.tag_layer,
                    lang_code=self.lang_code
                )
                postags = self.text_preprocessor.get_postags(
                    text=self.tag_layer,
                    lang_code=self.lang_code
                )
                self.__lemma_postag_map = {
                    lemma[0]: postag
                    for lemma, postag in zip(lemmas, postags)
                }
            elif self.lang_code == Language.EN:
                lemmas = self.text_preprocessor.get_lemmas(
                    text=self.original_text,
                    lang_code = self.lang_code
   
                )
                postags = nltk.pos_tag(lemmas)
                self.__lemma_postag_map = {
                    lemma: [postag]
                    for lemma, postag in postags
                }
            else:
                LOGGER.error(
                    f"POS-tag map generation not supported for language '{lang_code}'."
                )
            
        return self.__lemma_postag_map
    
    
    @property
    def processed_text(self) -> str:
        """ Returns lemmatized or stemmed text.
        """
        if not self.__processed_text:
            text = self.tag_layer if self.tag_layer else self.original_text
            self.__processed_text = self.text_preprocessor.preprocess(
                text=self.tag_layer, 
                lang_code=self.lang_code
            )
        return self.__processed_text
        
    @property
    def processed_and_cleaned_text(self) -> str:
        if not self.__processed_and_cleaned_text:
            if self.lang_code == Language.EN:
                self.__processed_and_cleaned_text = self.text_preprocessor.lemmatize(
                    text=self.cleaned_text, 
                    lang_code=self.lang_code, 
                )
            else:
                self.__processed_and_cleaned_text = self.text_preprocessor.preprocess(
                    text=self.cleaned_text, 
                    lang_code=self.lang_code, 
                )
        return self.__processed_and_cleaned_text
    
    @property
    def cleaned_text(self) -> str:
        if not self.__cleaned_text:
            self.__cleaned_text = self.text_preprocessor.clean(
                text=self.original_text
            )
        return self.__cleaned_text
    
    @property
    def corrected_text(self) -> str:
        if not self.__corrected_text:
            self.__corrected_text = self.speller.correct_text(
                text=self.processed_and_cleaned_text,
                lang_code=self.lang_code,
                max_uppercase=self.speller_config.get("max_uppercase"),
                min_word_frequency=self.speller_config.get("min_word_frequency"),
                preserve_case=self.speller_config.get("preserve_case"),
                places=self.places
            )
        return self.__corrected_text
 

    @property
    def phrased_text(self) -> str:
        if not self.__phrased_text:
            if self.correct_spelling:
                LOGGER.info(
                    f"Spell-correction enabled, applying spellcorrector " \
                    f"before phraser."
                )
                text = self.corrected_text
            else:
                text = self.processed_and_cleaned_text
            self.__phrased_text = self.text_preprocessor.apply_phraser(
                text=text,
                lang_code=self.lang_code
            )
        return self.__phrased_text
    
    @property
    def places(self) -> set:
        """ Returns all place names ocurring in the
        original text. NB! Currently supports only Estonian.
        """
        if self.__places is None:
            if self.lang_code == Language.ET:
                # Update analyzers and tag layer,
                # if ner isn't previously present.
                if "ner" not in self.analyzers:
                    self.analyzers.append("ner")
                    self.__tag_layer = self.text_preprocessor.get_tag_layer(
                        text=self.original_text,
                        lang_code=self.lang_code,
                        analyzers=self.analyzers
                    )
                places = set()

                for entity in self.tag_layer.ner:
                    if entity.nertag == "LOC":
                        for token in entity:
                            places.add(token.lemma[0])
                self.__places = places
                    
            else:
                error_msg = (
                    f"Place extraction for language '{self.lang_code}' " \
                    f"is not implemented. " \
                    f"Returning an empty set."
                )
                LOGGER.error(error_msg)
                self.__places = {}
        return self.__places
    
    @property
    def lang_code(self) -> str:
        """ Returns language code in ISO 639-1 standard.
        """
        if not self.__lang_code:
            self.__lang_code = TextPreprocessor.detect_language(
                text=self.original_text
            )
        return self.__lang_code
    
    
if __name__ == "__main__":
    tp = TextPreprocessor()
    from time import time
    start = time()
    text="Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud."
    text_en = "When I go home, I wanna go to sleep"
    tl = tp.get_tag_layer(text, "et", analyzers=["morph_analysis"])
    lemmatized_text = " ".join(
        lemma[0] for lemma in tl.lemma
    )
    print(lemmatized_text)
    dur = time() - start
    print(dur)
    print(dir(tl))
    print(tl.partofspeech)
    pr = ProcessedText(text=text, text_preprocessor=tp)
    print(pr.lemma_postag_map)