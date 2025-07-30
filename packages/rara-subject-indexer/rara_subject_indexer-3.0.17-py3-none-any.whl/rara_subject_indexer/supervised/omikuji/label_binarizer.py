import pickle
from typing import List

from sklearn.preprocessing import MultiLabelBinarizer


class LabelBinarizer:
    """
    Wraps scikit-learn's MultiLabelBinarizer, using sparse output
    to reduce memory usage for large label sets.
    """

    def __init__(self):
        """Initialize the MultiLabelBinarizer with sparse output."""
        self.mlb = MultiLabelBinarizer(sparse_output=True)

    def fit_transform(self, all_labels: List[List[str]]):
        """
        Fit and transform labels in one pass.

        Parameters
        ----------
        all_labels : List[List[str]]
            A list of label-lists, one per document.

        Returns
        -------
        scipy.sparse.spmatrix
            The binarized label matrix of shape (n_docs, n_unique_labels).
        """
        return self.mlb.fit_transform(all_labels)

    def transform(self, labels: List[List[str]]):
        """
        Transform a list of label-lists using the already-fitted binarizer.

        Parameters
        ----------
        labels : List[List[str]]
            A list of label-lists, one per document.

        Returns
        -------
        scipy.sparse.spmatrix
            The binarized label matrix of shape (len(labels), n_unique_labels).
        """
        return self.mlb.transform(labels)

    def save(self, path: str):
        """
        Pickle the MultiLabelBinarizer to disk.

        Parameters
        ----------
        path : str
            File path to store the pickled MLB.
        """
        with open(path, "wb") as f:
            pickle.dump(self.mlb, f)

    def load(self, path: str):
        """
        Load a pickled MultiLabelBinarizer from disk.

        Parameters
        ----------
        path : str
            File path where the MLB is stored.
        """
        with open(path, "rb") as f:
            self.mlb = pickle.load(f)

    @property
    def classes_(self):
        """
        The array of label classes discovered by the MultiLabelBinarizer.

        Returns
        -------
        numpy.ndarray
            Array of label class names.
        """
        return self.mlb.classes_
