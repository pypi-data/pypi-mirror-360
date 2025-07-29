import logging
import os
from typing import Tuple

import numpy as np
from omikuji import Model
from scipy.sparse import csr_matrix
from rara_subject_indexer.config import LOGGER
from rara_subject_indexer.exceptions import InvalidInputException


def write_omikuji_train_file(X: csr_matrix, Y: csr_matrix, file_path: str):
    """
    Write a file that Omikuji can train on, including the required header line.

    Data format looks something like this:

    num_examples num_features num_labels
    label1,label2,...labelk ft1:ft1_val ft2:ft2_val ft3:ft3_val ... ftd:ftd_val
    ...
    label1,label2,...labelk ft1:ft1_val ft2:ft2_val ft3:ft3_val ... ftd:ftd_val

    Parameters
    ----------
    X : csr_matrix
        TF-IDF feature matrix of shape (n_docs, n_features).
    Y : csr_matrix
        Binarized label matrix of shape (n_docs, n_labels).
    file_path : str
        File path to write the output the file.
    """
    num_examples, num_features = X.shape
    _, num_labels = Y.shape

    temp_file = os.path.splitext(file_path)[0] + ".tmp"
    count_valid = 0

    with open(temp_file, "w", encoding="utf-8") as f_out:
        for i in range(num_examples):
            label_indices = Y[i].nonzero()[1]
            if label_indices.size == 0:
                continue

            row = X.getrow(i)
            feat_indices = row.nonzero()[1]
            if feat_indices.size == 0:
                continue

            label_str = ",".join(map(str, label_indices))
            feat_strs = []
            for j in feat_indices:
                val = row[0, j]
                feat_strs.append(f"{j}:{val:.6f}")
            line = f"{label_str} {' '.join(feat_strs)}\n"
            f_out.write(line)
            count_valid += 1

    with open(temp_file, "r", encoding="utf-8") as f_tmp, \
         open(file_path, "w", encoding="utf-8") as f_final:
        header = f"{count_valid} {num_features} {num_labels}\n"
        f_final.write(header)
        for line in f_tmp:
            f_final.write(line)

    os.remove(temp_file)
    LOGGER.info(
        f"Wrote {count_valid} lines (header: " \
        f"{num_examples}, {num_features}, {num_labels}) to '{file_path}'"
    )


def assert_both_files_same_length(text_file: str, label_file: str):
    """
    Assert that two files have the same number of non-empty lines.

    Parameters
    ----------
    text_file : str
        Path to the text file.
    label_file : str
        Path to the label file.

    Raises
    ------
    ValueError
        If the number of non-empty lines in the files do not match.
    """
    def count_lines(file_path: str) -> int:
        """Count the number of non-empty lines in a file."""
        count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    num_texts = count_lines(text_file)
    num_labels = count_lines(label_file)

    if num_texts != num_labels:
        raise InvalidInputException(
            f"Number of non-empty lines in text file ({num_texts}) " \
            f"does not match the number in label file ({num_labels})."
        )


def split_indices(num_samples: int, eval_split: float, random_seed: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Splits indices randomly into training and evaluation sets.

    Parameters
    ----------
    num_samples : int
        The total number of samples.
    eval_split : float
        The fraction of samples to include in the evaluation set (0 < eval_split < 1).
    random_seed : int, optional
        A seed for the random number generator to ensure reproducibility, by default None.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        A tuple containing two arrays: train_indices and eval_indices.
    """
    if not (0 < eval_split < 1):
        raise InvalidInputException(
            f"eval_split must be between 0 and 1 (exclusive)."
        )

    np.random.seed(random_seed)

    indices = np.arange(num_samples)
    np.random.shuffle(indices)

    eval_size = int(num_samples * eval_split)
    eval_indices = indices[:eval_size]
    train_indices = indices[eval_size:]

    return train_indices, eval_indices

def train_omikuji(omikuji_train_file_path: str) -> Model:
    """
    Train an Omikuji model from a file.

    Parameters
    ----------
    omikuji_train_file_path : str
        Path to the Omikuji-compatible training file.

    Returns
    -------
    Model
        The trained Omikuji model.
    """
    hyper_param = Model.default_hyper_param()
    LOGGER.info(f"Started training a new Omikuji model.")
    model = Model.train_on_data(omikuji_train_file_path, hyper_param)
    return model
