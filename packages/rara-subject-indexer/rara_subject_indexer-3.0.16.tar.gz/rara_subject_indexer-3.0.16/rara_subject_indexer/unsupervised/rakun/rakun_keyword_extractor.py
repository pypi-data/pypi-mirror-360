import re
import importlib.resources
from rakun2 import RakunKeyphraseDetector
from rara_subject_indexer.utils.text_preprocessor import (
    TextPreprocessor, ProcessedText
)
from rara_subject_indexer.config import (
    SUPPORTED_STOPWORDS, RAKUN_DEFAULTS, POSTAGS_TO_IGNORE, ALLOWED_EN_POSTAGS,
    Language
)
from typing import Tuple, List, Dict, NoReturn


class RakunKeywordExtractor:
    """
    A class for extracting keywords from the text using unsupervised extraction.
    """

    def __init__(self, 
        text_preprocessor: TextPreprocessor | None = None,
        stopwords: Dict[str, List[str]] = SUPPORTED_STOPWORDS,
        n_raw_keywords: int = 30
    ) -> NoReturn:
        """
        Initialize extractor using config provided in the constants file.
        
        Parameters
        -----------
        text_preprocessor: TextPreprocessor
            A TextPreprocessor object used for various
            text processing operations. If no TextProcessor
            is provided, a TextProcessor with default values
            will be initialized.
        stopwords: Dict[str, List[str]]
            A mapping of stopwords for each supported language.
            key = language code; value = List of stopwords.
        n_raw_keywords: int
            Number of keywords to extract before applying additional
            filtering operations. Should be quite high as some portion
            of keywords will be filtered out. The final number of keywords
            to output is controlled with `predict` functions `top_k` 
            parameter.
        """
        self.stopwords: dict = stopwords
        self.n_raw_keywords: int = n_raw_keywords
            
        self.load_text_preprocessor(text_preprocessor)
            
    def load_text_preprocessor(self, 
        text_preprocessor: TextPreprocessor | None
    ) -> TextPreprocessor:
        """ Loads a TextPreprocessor instance.
        
        Parameters
        -----------
        text_preprocessor: TextPreprocessor | None
            Either a TextPreprocessor object or None.
            If None is passed, a TextPreprocessor object
            with default params will be loaded.
        
        Returns
        -----------
        text_preprocessor: TextPreprocessor
            A TextPreprocessor object.
        """
        if not text_preprocessor:
            text_preprocessor = TextPreprocessor()
        self.text_preprocessor = text_preprocessor
        return text_preprocessor

    def predict(self, text: str | ProcessedText, lang_code: str = None, 
            top_k: int = 10, postags_to_ignore: List[str] = POSTAGS_TO_IGNORE, 
            merge_threshold: float = 0.0, use_phraser: bool = False, 
            correct_spelling: bool = False, preserve_case: bool = True, 
            max_uppercase: int = 2, min_word_frequency: int = 2, **kwargs
    ) -> List[Tuple[str, float]]:
        """
        Extract keywords from the text using unsupervised extraction.

        Parameters
        ----------
        text: str
            Input text.
        lang_code: str, default None
            The language code of the input text.
        top_k: int, default 10
            Number of keywords to extract.
        postags_to_ignore: List[str]
            List of POS-tags to ignore. Keywords corresponding
            to those POS-tags will not be returned.
        merge_threshold: float, default 0.0
            Threshold for merging words into a single keyword.
        use_phraser: bool, default False
            Whether to use phraser or not.
        correct_spelling: bool, default False
            Whether to use spell correction or not.
        preserve_case: bool, default True
            Whether to preserve original case or not.
        max_uppercase: int, default 2
            The maximum number of uppercase letters in the 
            word to allow spelling correction. If the word contains 
            more than `max_uppercase` uppercase letters, it will not 
            be corrected using spelling correction. This helps prevent 
            corrections of words that are intentionally capitalized 
            (like acronyms).
        min_word_frequency: int, default 2
            The minimum frequency of the word in the input text 
            required for it to NOT be corrected. If the word
            appears fewer than `min_word_frequency` times in the 
            `full_text`, it will be corrected using spelling
            correction. This helps prevent corrections of common words 
            that are not likely to need correction.

        Returns
        -------
        keywords: list[str]
            List of keywords extracted from the input text.
        """
        speller_config = {
            "max_uppercase": max_uppercase,
            "min_word_frequency": min_word_frequency,
            "preserve_case": preserve_case
        }
        if isinstance(text, str):
            # If a reguler text is passed, create a ProcessedText
            # class wrapping various preprocessing methods' outputs
            
            text = ProcessedText(
                text=text, 
                text_preprocessor=self.text_preprocessor, 
                correct_spelling=correct_spelling,
                lang_code=lang_code,
                speller_config=speller_config
            )
        else:
            text.speller_config = speller_config
            text.correct_spelling = correct_spelling
       
        lang_code = text.lang_code
        
        # Lemmatized / stemmed text + removing
        # URLs + E-mail addressed
        processed_text = text.processed_and_cleaned_text
        
        # If correct_spelling is enabled, use text
        # with spelling corrections
        if correct_spelling:
            processed_text = text.corrected_text
            
        # If phrased is enaled, use phrased text
        if use_phraser:
            processed_text = text.phrased_text

        keywords = self._extract_keywords(
            text=processed_text, 
            lang_code=lang_code, 
            top_n=self.n_raw_keywords, 
            merge_threshold=merge_threshold, 
            preserve_case=preserve_case
        )

        # Remove duplicates
        keywords = list(dict.fromkeys(keywords))
        
        postags_to_allow = ALLOWED_EN_POSTAGS
        # Filter out keywords corresponding
        # to POS-tags to ignore
        keywords = self._filter_by_postag(
            keywords=keywords, 
            postag_map=text.lemma_postag_map,
            postags_to_ignore=postags_to_ignore,
            postags_to_allow=postags_to_allow,
            lang_code=lang_code
        )
 
        return keywords[:top_k]

  

    def _filter_by_postag(self, keywords: List[Tuple[str, float]], 
        postag_map: Dict[str, List[str]], lang_code: str, 
        postags_to_ignore: List[str] = [], postags_to_allow: List[str] = []
    ) -> Tuple[str, float]:
        """ Filters out keywords corresponding to POS-tags to ignore.
        
        Parameters
        -----------
        keywords: List[Tuple[str, float]]
            List of keyword tuples.
        postag_map: Dict[str, List[str]]
            Dict where key = lemma and value = list of postags corresponding 
            to the lemma. The map is generated based on the input text from
            where the keywords where extracted.
        postags_to_ignore: List[str]
            List of POS-tags to ignore.
        
        Returns
        ----------
        filtered_keywords: List[Tuple[str, float]]
            Filtered keywords.
        """
        filtered_keywords = []
        
        has_intersection = lambda x, y: bool(set(x).intersection(set(y)))
        for keyword, score in keywords:
            keyword_postags = postag_map.get(keyword, [])
            if lang_code == Language.ET:
                if not has_intersection(keyword_postags, postags_to_ignore):
                    filtered_keywords.append((keyword, score))
            elif lang_code == Language.EN:
                if has_intersection(keyword_postags, postags_to_allow):
                    filtered_keywords.append((keyword, score))
        return filtered_keywords
                
        
    def _extract_keywords(self, 
        text: str, lang_code: str, top_n: int, 
        merge_threshold: float, preserve_case: bool
    ) -> List[Tuple[str, float]]:
        """
        Run Rakun2 keyword extraction on the input text.

        Parameters
        ----------
        text: str
            Input text.
        lang_code: str
            The language code of the input text.
        top_n: int
            Number of keywords to extract.
        merge_threshold: float
            Threshold for merging words into a single keyword.
        preserve_case: bool
            Whether to preserve original case or not.

        Returns
        -------
        keywords: List[Tuple[str, float]]
            List of keyword tuples extracted from the input text.
        """
        stopwords = self.stopwords.get(lang_code, [])
        
        rakun_params = {
            "num_keywords": top_n, 
            "merge_threshold": merge_threshold, 
            "stopwords": stopwords
        }
        detector = RakunKeyphraseDetector(
            rakun_params, 
            verbose=False
        )
        keywords = detector.find_keywords(text, input_type="string")

        if preserve_case:
            keywords = self._match_original_case(text, keywords)
        # Some very short texts may have scores >1, 
        # so we limit the score maximally to 1
        results = [
            (keyword, round(min(score, 1.0), 3)) 
            for keyword, score in keywords
        ]
        return results

    def _match_original_case(self, 
            text: str, 
            keywords: list[tuple[str, float]]
        ) -> list[tuple[str, float]]:
        """
        Match keywords to the original case.

        Parameters
        ----------
        text: str
            Input text.
        keywords: str
            List of keywords extracted from the input text.

        Returns
        -------
        original_cased_keywords: list[str]
            List of keywords extracted from the input text 
            matched to the original case in the input text.
        """
        original_cased_keywords = []
        for keyword, score in keywords:
            pattern = rf'\b{re.escape(keyword)}\b'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                original_cased_keywords.append((match.group(0), score))
        return original_cased_keywords
