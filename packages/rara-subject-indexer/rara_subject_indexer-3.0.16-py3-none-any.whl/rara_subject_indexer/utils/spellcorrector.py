import string
from importlib.resources import files

from langdetect import detect
from symspellpy import SymSpell, Verbosity

from rara_subject_indexer.config import SPELL_CHECK_DICTIONARIES_CONFIG


class SpellCorrector:
    """
    A class for correcting spelling mistakes.
    """

    def __init__(self, max_edit_distance: int = 2, prefix_length: int = 7, count_threshold: int = 1):
        """
        Initialize corrector class by loading language specific frequency dictionaries.

        Parameters
        ----------
        max_edit_distance: int, default 2
            Maximum edit distance for doing lookups.
        prefix_length: int, default 7
            The length of word prefixes used for spell checking.
        count_threshold: int, default 1
            The minimum frequency count for dictionary words to be considered correct spellings.
        """
        self.max_edit_distance = max_edit_distance
        self.prefix_length = prefix_length
        self.count_threshold = count_threshold
        self.sym_spell_cache = self._load_dictionaries()

    def _load_dictionaries(self):
        """
        Load frequency dictionaries for supported languages based on the constants file.
        """
        sym_spell_cache = {}
        for lang_code, config in SPELL_CHECK_DICTIONARIES_CONFIG.items():
            sym_spell = SymSpell(self.max_edit_distance, self.prefix_length, self.count_threshold)

            # Use default values if not specified in the config
            term_index = config.get("term_index", 0)  # Default term_index is 0
            count_index = config.get("count_index", 1)  # Default count_index is 1
            separator = config.get("separator", " ")  # Default separator is a space

            package = config["package"]
            resource = config["resource"]

            resource_path = files(package).joinpath(resource)
            if not sym_spell.load_dictionary(
                str(resource_path), term_index=term_index, count_index=count_index, separator=separator
            ):
                raise FileNotFoundError(f"Dictionary file not found at {resource_path}")

            sym_spell_cache[lang_code] = sym_spell
        return sym_spell_cache

    def _get_word_frequencies(self, text: str) -> dict[str, int]:
        """
        Calculate word frequencies for given text.

        Parameters
        ----------
        text: str
            The input text.

        Returns
        -------
        dict
            A dictionary containing word frequencies.
        """
        words = text.split()
        return {word: words.count(word) for word in set(words)}

    def _prepare_for_correction(self, places: set[str], word_counts: dict[str, int],
                                preserve_case: bool) -> tuple[set[str], dict[str, int]]:
        """
        Pre-process places and word_counts based on preserve_case.

        Parameters
        ----------
        places:  set[str]
            The set of place names.
        word_counts: dict[str, int]
            The dictionary containing word frequencies.
        preserve_case: bool
            Whether to preserve original case or not.

        Returns
        -------
        tuple[set[str], dict[str, int]]
            The places set and word count dictionary.
        """
        if not preserve_case:
            places = {place.lower() for place in places}
            word_counts = {k.lower(): v for k, v in word_counts.items()}
        return places, word_counts

    def _has_few_uppercase_letters(self, word: str, max_uppercase: int) -> bool:
        """
        Check if the word exceeds the maximum number of uppercase letters.

        Parameters
        ----------
        word: str
            The input word.
        max_uppercase: int
            The maximum number of allowed uppercase letters.

        Returns
        -------
        bool
            Whether word exceeds the maximum number of uppercase letters.
        """
        return sum(1 for c in word if c.isupper()) <= max_uppercase

    def _is_correction_needed(self, word: str, word_counts: dict[str, int], places: set[str], min_word_frequency: int,
                              max_uppercase: int, preserve_case: bool) -> bool:
        """
        Check if the word should be corrected using spelling correction.

        Parameters
        ----------
        word: str
            The input word.
        word_counts: dict[str, int]
            The dictionary containing word frequencies.
        places: set[str]
            The set of place names.
        min_word_frequency: int
            The minimum frequency of the word in the input text required for it to NOT be corrected. If the word
            appears fewer than `min_word_frequency` times in the `full_text`, it will be corrected using spelling
            correction. This helps prevent corrections of common words that are not likely to need correction.
        max_uppercase: int
            The maximum number of uppercase letters in the word to allow spelling correction. If the word contains more
            than `max_uppercase` uppercase letters, it will not be corrected using spelling correction.
            This helps prevent corrections of words that are intentionally capitalized (like acronyms).
        preserve_case: bool
             Whether to preserve original case or not.

        Returns
        -------
        bool
            Whether the word should be corrected using spelling correction.
        """
        word_to_check = word.lower() if not preserve_case else word
        if all(char in string.punctuation for char in word):
            return False
        if word_to_check in places:
            return False
        if word_counts.get(word_to_check, 0) >= min_word_frequency:
            return False
        if self._has_few_uppercase_letters(word, max_uppercase):
            return True
        return True

    def correct_text(self, text: str, lang_code: str, max_uppercase: int, min_word_frequency: int, preserve_case: bool,
                 places: set[str] = set()) -> str:
        """
        Function for correcting spelling mistakes in a string.
    
        Parameters
        ----------
        text: str
            The text to be corrected.
        lang_code: str
            The language code of the text to be corrected.
        max_uppercase: int
            The maximum number of uppercase letters in the word to allow spelling correction.
        min_word_frequency: int
            The minimum frequency of the word in the input text required for it to NOT be corrected.
        preserve_case: bool
            Whether to preserve original case or not.
        places: set[str], default set()
            The set of place names.
            
        Returns
        -------
        str
            The corrected text.
        """
        lang_code = lang_code or detect(text)
        sym_spell = self.sym_spell_cache.get(lang_code)
        if not sym_spell:
            return text
        places, word_counts = self._prepare_for_correction(places, self._get_word_frequencies(text), preserve_case)
        corrected_words = self._correct_words(
            words=text.split(),
            sym_spell=sym_spell,
            min_word_frequency=min_word_frequency,
            max_uppercase=max_uppercase,
            preserve_case=preserve_case,
            word_counts=word_counts,
            places=places
        )
    
        return " ".join(corrected_words)
    
    
    def correct_text_list(self, texts: list[str], full_text: str, lang_code: str,
                          max_uppercase: int, min_word_frequency: int, preserve_case: bool,
                          places: set[str] = set()):
        """
        Function for correcting spelling mistakes in a list of strings.
    
        Parameters
        ----------
        texts: list[str]
            The input list of strings.
        full_text: str
            The input full text.
        lang_code: str
            The language code of the text to be corrected.
        max_uppercase: int
            The maximum number of uppercase letters in the word to allow spelling correction.
        min_word_frequency: int
            The minimum frequency of the word in the input text required for it to NOT be corrected.
        preserve_case: bool
            Whether to preserve original case or not.
        places: set[str], default = set()
            The set of place names.
            
        Returns
        -------
        list[str]
            The list of corrected strings.
        """
        lang_code = lang_code or detect(full_text)
        sym_spell = self.sym_spell_cache.get(lang_code)
        if not sym_spell:
            return texts
        places, word_counts = self._prepare_for_correction(places, self._get_word_frequencies(full_text), preserve_case)
        corrected_texts = self._correct_words(
            words=texts,
            sym_spell=sym_spell,
            min_word_frequency=min_word_frequency,
            max_uppercase=max_uppercase,
            preserve_case=preserve_case,
            word_counts=word_counts, 
            places=places
        )
    
        return corrected_texts
    
    
    def _correct_words(self, words: list[str], sym_spell: SymSpell,
                       min_word_frequency: int, max_uppercase: int, preserve_case: bool,
                       word_counts: dict[str, int], places: set[str] = set()) -> list[str]:
        """
        Correct spelling mistakes.
    
        Parameters
        ----------
        words: list[str]
            The input word list.
        sym_spell: SymSpell
            The initialised SymSpell object.
        min_word_frequency: int
            The minimum frequency of the word in the input text required for it to NOT be corrected. If the word
            appears fewer than `min_word_frequency` times in the `full_text`, it will be corrected using spelling
            correction. This helps prevent corrections of common words that are not likely to need correction.
        max_uppercase: int
            The maximum number of uppercase letters in the word to allow spelling correction. If the word contains more
            than `max_uppercase` uppercase letters, it will not be corrected using spelling correction.
            This helps prevent corrections of words that are intentionally capitalized (like acronyms).
        preserve_case: bool
            Whether to preserve original case or not.
        word_counts: dict[str, int]
            The dictionary of word counts, pre-calculated from the full text.
        places: set[str], default = set()
            The set of place names.
    
        Returns
        -------
        corrected_words: list[str]
            List of words with corrected spelling mistakes.
        """
        corrected_words = []
        for word in words:
            if self._is_correction_needed(word, word_counts, places, min_word_frequency, max_uppercase, preserve_case):
                suggestions = sym_spell.lookup(word, verbosity=Verbosity.TOP, max_edit_distance=self.max_edit_distance,
                                               include_unknown=True)
                corrected_words.append(suggestions[0].term)
            else:
                corrected_words.append(word)
        return corrected_words