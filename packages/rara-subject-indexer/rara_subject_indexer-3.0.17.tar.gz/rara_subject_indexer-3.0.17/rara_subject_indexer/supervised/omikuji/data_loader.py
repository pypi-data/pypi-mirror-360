# data_loader.py
import logging
import os
from typing import List, Callable

from rara_subject_indexer.supervised.omikuji.omikuji_helpers import assert_both_files_same_length

logger = logging.getLogger(__name__)


class DataLoader:
    """
    A class to read parallel text and label files, either in chunks for lemmatization
    or directly if the file is already lemmatized.
    Each line in 'text_file' corresponds to one document,
    and each line in 'label_file' has semicolon-separated labels for that document.
    """

    def __init__(self, text_file: str, label_file: str):
        """
        Parameters
        ----------
        text_file : str
            Path to the text file (one document per line).
        label_file : str
            Path to the label file (semicolon-separated labels per line).
        """
        if os.path.splitext(text_file)[1] != ".txt" or os.path.splitext(label_file)[1] != ".txt":
            raise ValueError("Both files must have the '.txt' extension.")

        self.text_file = text_file
        self.label_file = label_file


    def write_lemmatized_texts(self, output_file: str, preprocess_fn: Callable, language: str) -> List[List[str]]:
        """
        Read text & labels line by line,
        apply a lemmatization/preprocessing function,
        and write the lemmatized texts to 'output_file'.
        Collect all labels in memory.

        Parameters
        ----------
        output_file : str
            File where lemmatized texts will be written, one doc per line.
        preprocess_fn : callable
            A function that takes raw text and returns a preprocessed 
            (lemmatized) text.
        language: str
            Language code in ISO 639-1 standard.
            

        Returns
        -------
        List[List[str]]
            All labels, in the same order as the lines written out.
        """
        logger.info("Verifying line counts")
        assert_both_files_same_length(self.text_file, self.label_file)

        logger.info(f"Writing lemmatized texts to '{output_file}' + collecting labels in memory")
        all_labels = []
        doc_count = 0

        with open(self.text_file, "r", encoding="utf-8") as f_text, \
                open(self.label_file, "r", encoding="utf-8") as f_label, \
                open(output_file, "w", encoding="utf-8") as out_f:

            for text_line, label_line in zip(f_text, f_label):
                try:
                    text_line = text_line.strip()
                    label_line = label_line.strip()

                    if not text_line or not label_line:
                        continue

                    label_list = [lbl.strip() for lbl in label_line.split(";") if lbl.strip()]
                    lemma = preprocess_fn(text_line, language)

                    out_f.write(lemma + "\n")
                    all_labels.append(label_list)
                    doc_count += 1
                except Exception as e:
                    logger.info(f"Encountered problem when lemmatizing this document: {text_line}. Exception: {e}.")

        logger.info(f"Finished lemmatizing. Wrote {doc_count} lines to '{output_file}'")
        return all_labels

    def read_lemmatized(self) -> List[List[str]]:
        """
        Read an already-lemmatized text file in parallel with its label file in a memory-safe manner.
        We only store the labels in memory, while verifying that the text and label files
        have the same number of valid lines.

        Returns
        -------
        List[List[str]]
            All labels (one list of strings per document) in memory.
            The text file is *not* read into memory; it's only validated.

        Raises
        ------
        ValueError
            If there's a mismatch in line counts between the text file and label file.
        """

        logger.info("Verifying line counts")
        assert_both_files_same_length(self.text_file, self.label_file)

        logger.info("Reading lemmatized texts (storing labels only)")
        all_labels = []

        with open(self.text_file, "r", encoding="utf-8") as f_text, \
             open(self.label_file, "r", encoding="utf-8") as f_label:

            for text_line, label_line in zip(f_text, f_label):
                text_line = text_line.strip()
                label_line = label_line.strip()
                if not text_line or not label_line:
                    continue

                label_list = [lbl.strip() for lbl in label_line.split(";") if lbl.strip()]
                all_labels.append(label_list)

        return all_labels
