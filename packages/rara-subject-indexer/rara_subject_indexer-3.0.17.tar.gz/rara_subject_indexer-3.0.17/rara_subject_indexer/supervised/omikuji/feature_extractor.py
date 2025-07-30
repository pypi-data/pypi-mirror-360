import pickle

from sklearn.feature_extraction.text import TfidfVectorizer


class TfidfFeatureExtractor:
    """
    A wrapper around TfidfVectorizer that can fit from a file
    (treating each line as a separate document).
    """

    def __init__(self, max_features: int = 15000):
        """
        Parameters
        ----------
        max_features : int, optional
            Maximum number of features to keep in TF-IDF, by default 5000
        """
        self.max_features = max_features
        self.vectorizer = None

    def fit_transform_file(self, file_path: str):
        """
        Fit and transform TF-IDF using a file where each line is a document.

        Parameters
        ----------
        file_path : str
            Path to the file containing one doc per line.

        Returns
        -------
        scipy.sparse.csr_matrix
            The TF-IDF matrix of shape (n_docs, n_features).
        """
        self.vectorizer = TfidfVectorizer(max_features=self.max_features)
        with open(file_path, "r", encoding="utf-8") as f:
            X = self.vectorizer.fit_transform(f)
        return X

    def transform_texts(self, texts):
        """
        Transform a list of text documents using the fitted TF-IDF vectorizer.

        Parameters
        ----------
        texts : List[str]
            A list of preprocessed text documents.

        Returns
        -------
        scipy.sparse.csr_matrix
            The TF-IDF matrix of shape (len(texts), n_features).
        """
        if not self.vectorizer:
            raise ValueError("Vectorizer has not been fit yet!")
        return self.vectorizer.transform(texts)

    def save(self, path: str):
        """
        Save the fitted TfidfVectorizer to disk.

        Parameters
        ----------
        path : str
            The file path to store the pickled vectorizer.
        """
        with open(path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def load(self, path: str):
        """
        Load a pickled TfidfVectorizer from disk.

        Parameters
        ----------
        path : str
            The file path where the pickled vectorizer is stored.
        """
        with open(path, "rb") as f:
            self.vectorizer = pickle.load(f)

    @property
    def vocabulary_size(self) -> int:
        """
        The size of the learned vocabulary (number of features).

        Returns
        -------
        int
            Number of features in the vectorizer.
        """
        if not self.vectorizer:
            return 0
        return len(self.vectorizer.get_feature_names_out())
