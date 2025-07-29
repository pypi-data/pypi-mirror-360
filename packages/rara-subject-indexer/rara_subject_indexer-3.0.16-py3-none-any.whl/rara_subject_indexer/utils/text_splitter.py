import regex as re
from typing import List, Dict, Union, Tuple
from rara_subject_indexer.exceptions import InvalidSplitMethodError
from rara_subject_indexer.config import SplitMethod, LOGGER

SPLIT_OPTIONS = [
    SplitMethod.DOUBLE_NEWLINE, 
    SplitMethod.NEWLINE, 
    SplitMethod.WORD_LIMIT, 
    SplitMethod.CHAR_LIMIT, 
    SplitMethod.CUSTOM
]


class TextSplitter:
    """ Split text into subsections based on given character/word limit.
    """
    def __init__(
        self, 
        split_by: str = SplitMethod.CHAR_LIMIT, 
        split_pattern: str = "", 
        strip_whitespaces: bool = True, 
        keep_whitespace_formatting: bool = True,
        word_limit: int = 500,
        char_limit: int = 3000
    ):
        """
        Parameters
        ----------
        split_by : str
            Method used for splitting the text.
        split_pattern : str
            Custom character/string_pattern for splitting the text.
            Has effect only if split_by = 'CUSTOM'.
        strip_whitespaces : bool
            If enabled, whitespaces (newlines etc.) are stripped from each page.
        keep_whitespace_formatting : bool
            If enabled, whitespace characters in the middle of each 
            text chunk are left untouched, otherwise they will be 
            removed, which will impacting the format.

        Attributes
        ------------
        split_by : str
            Stores parameter `split_by`.
        split_pattern : str
            Stores parameter `split_pattern`.
        strip_whitespaces : bool
            Stores parameter `strip_whitespaces`.
        keep_whitespace_formatting : bool
            Stores parameter `keep_whitespace_formatting`
        word_limit : int
           Max number of words per one chunk.
        default_char_limit : int
            Max number of characters per one chunk.
        """
        self.split_by = self._validate_split_option(split_by)
        self.split_pattern = split_pattern
        self.strip_whitespaces = strip_whitespaces
        self.keep_whitespace_formatting = keep_whitespace_formatting
        self.word_limit = word_limit
        self.char_limit = char_limit
    

    def _validate_split_option(self, split_by: str) -> str:
        if split_by not in SPLIT_OPTIONS:
            raise exceptions.InvalidSplitMethodError(
                f"Invalid argument for param `split_by`: `{split_by}`. \
                Make sure to use one of the following: {SPLIT_OPTIONS}")
        return split_by

    def get_split_options(self) -> List[str]:
        """ Retrieve list of available options for splitting the text.
        """
        return SPLIT_OPTIONS

    def _preprocess_text(self, text: str) -> str:
        """ Apply enabled text processing methods.

        Parameters
        ------------
        text : str
            Text on which to apply preprocessors.
        """
        if not self.keep_whitespace_formatting:
            # Remove extra whitespaces
            text = re.sub(r"\s+", " ", text)
        return text

    def _split_by_pattern(
        self, 
        text: str, 
        split_pattern: str
    ) -> List[str]:
        """ Split by string pattern specified with param `split_pattern`.

        Parameters
        ----------
        text : str
            Text to split.
        split_pattern : str
            Pattern used for splitting.
        """
        text_chunks = []
        
        for text_chunk in text.split(split_pattern):
            if text_chunk.strip():
                if self.strip_whitespaces:
                    text_chunk = text_chunk.strip()
                text_chunks.append(text_chunk)   
        return text_chunks

    def _split_by_word_limit(
        self, 
        text: str, 
        max_limit: int
    ) -> List[str]:
        """ Split into chunks of length `max_limit` 
           (each chunk consists of `max_limit` words).

        Parameters
        ----------
        text : str
            Text to split.
        max_limit: int
            Maximum number of words per one chunk.
        """
        chunks = []
        words = [t for t in text.split()]

        n_chunks = int(len(words)/max_limit)

        if self.keep_whitespace_formatting:
            separators = re.findall(r"\s+", text)

        w_index = 0
        page = 1
        for i in range(n_chunks+1):
            slice_start = i*max_limit
            slice_end = i*max_limit + max_limit

            chunk_words = words[slice_start:slice_end]

            if self.keep_whitespace_formatting:
                chunk = ""
                for word in chunk_words:
                    chunk+=word
                    if w_index < len(separators):
                        chunk+=separators[w_index]
                        w_index+=1

            else:
                chunk = " ".join(chunk_words)

            # Remove trailing whitespaces
            if self.strip_whitespaces:
                chunk = chunk.strip()

            if chunk:
                chunks.append(chunk)
        return chunks

    def _split_by_char_limit(
        self, 
        text: str, 
        max_limit: int
    ) -> List[str]:
        """ Split into chunks of length `max_limit` 
            (each chunk consists of `max_limit` characters).

        Parameters
        ----------
        text : str
            Text to split.
        max_limit: int
            Maximum number of characters per one chunk.
        """
        chunks = []
        n_chunks = int(len(text)/max_limit)

        offset = 0
        for i in range(n_chunks+1):
            slice_start = i*max_limit + offset
            slice_end = i*max_limit + max_limit + offset

            chunk = text[slice_start:slice_end]

            # Add non-whitespace characters from the begging of next chunk
            # to avoid splitting words:
            for c in text[slice_end:]:
                if not re.match(r"\s", c):
                    chunk+=c
                    offset+=1
                else:
                    break

            # Remove trailing whitespaces
            if self.strip_whitespaces:
                chunk = chunk.strip()

            if chunk:
                chunks.append(chunk)

        return chunks

    def split(self, text: str) -> List[str]:
        """ Split text into smaller chunks.

        Parameters
        ----------
        text : str
            Text to split.
        max_limit : int
            Max number of words or characters per each chunk. 
            Has effect only if `split_by == 'WORD_LIMIT'` or
            `split_by == 'CHAR_LIMIT'`.

        Returns
        --------
        chunks: List[str]
            List of text chunks.

        """
        # Apply enabled preprocessors
        text = self._preprocess_text(text)
        LOGGER.debug(
            f"Applying TextSplitter with split method = " \
            f"`{self.split_by}`."
        )
        match self.split_by:
            case SplitMethod.DOUBLE_NEWLINE:
                chunks = self._split_by_pattern(
                    text=text, 
                    split_pattern="\n\n"
                )
            case SplitMethod.NEWLINE:
                chunks = self._split_by_pattern(
                    text=text, 
                    split_pattern="\n"
                )
            case SplitMethod.WORD_LIMIT:
                LOGGER.debug(
                    f"TextSplitter word limit is set to {self.word_limit}."
                )
                chunks = self._split_by_word_limit(
                    text=text, 
                    max_limit=self.word_limit
                )
            case SplitMethod.CHAR_LIMIT:
                LOGGER.debug(
                    f"TextSplitter char limit is set to {self.char_limit}."
                )
                chunks = self._split_by_char_limit(
                    text=text, 
                    max_limit=self.char_limit
                )
            case SplitMethod.CUSTOM:
                chunks = self._split_by_pattern(
                    text=text, 
                    split_pattern=self.split_pattern
                )
        return chunks
   
