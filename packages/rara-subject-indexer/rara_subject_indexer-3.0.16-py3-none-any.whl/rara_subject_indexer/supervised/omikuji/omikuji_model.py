import json
import logging
import os
from datetime import datetime
from typing import Optional, List, Tuple, NoReturn

import numpy as np
from omikuji import Model
from scipy.sparse import lil_matrix, csr_matrix
from sklearn.metrics import precision_recall_fscore_support
from tqdm import tqdm

from rara_subject_indexer.supervised.omikuji.data_loader import DataLoader
from rara_subject_indexer.supervised.omikuji.feature_extractor import TfidfFeatureExtractor
from rara_subject_indexer.supervised.omikuji.label_binarizer import LabelBinarizer
from rara_subject_indexer.supervised.omikuji.omikuji_helpers import (
    write_omikuji_train_file, train_omikuji, split_indices
)
from rara_subject_indexer.utils.text_preprocessor import (
    TextPreprocessor, ProcessedText
)
from rara_subject_indexer.config import (
    SKLEARN_AVERAGE_FUNCTION, LOGGER
)
from rara_subject_indexer.exceptions import (
    ModelNotLoadedException, ModelExistsException, 
    MissingValueException, MissingFileException
)
#logger = logging.getLogger(__name__)


class OmikujiModel:
    """
    A high-level pipeline that coordinates:
      1) (Optional) lemmatization if the text is not already preprocessed.
      2) Fitting TF-IDF from a file with one doc per line.
      3) One-pass label binarization with MultiLabelBinarizer (sparse).
      4) Writing an Omikuji training file and training the model.
      5) Saving/Loading the model, vectorizer, binarizer.
      6) Predicting labels for new text.
      7) Evaluating performance on a small dataset in memory.
    """

    def __init__(
        self,
        model_artifacts_path: Optional[str] = None,
        text_preprocessor: Optional[TextPreprocessor] = None
    ):
        """
        Parameters
        ---------.
        model_artifacts_path : str, optional
            Path to a saved Omikuji model, by default None
        text_preprocessor: TextPreprocessor
            A TextPreprocessor object.
        """
        self.model = None
        self.feature_extractor = TfidfFeatureExtractor()
        self.label_binarizer = LabelBinarizer()
        self.model_save_prefix = None
        self.train_indices = None
        self.eval_indices = None
        self.language: str | None = str
        self.text_preprocessor: TextPreprocessor = text_preprocessor if text_preprocessor else TextPreprocessor()

        if model_artifacts_path:
            self.load(model_artifacts_path)

    def train(
        self,
        text_file: str,
        label_file: str,
        language: str,
        entity_type: str,
        lemmatization_required: bool = True,
        max_features: Optional[int] = 15000,
        keep_train_file: Optional[bool] = False,
        eval_split: Optional[float] = 0.1
    ):
        """
        Train the pipeline and leave out a portion of samples for evaluation.

        Parameters
        ----------
        text_file : str
            Path to the text file (raw or already lemmatized).
        label_file : str
            Path to the label file (semicolon-separated per line).
        language : str
            Language code for the text preprocessor.
        lemmatization_required : bool
            Whether to lemmatize the text file, by default True
        max_features : int, optional
            Max TF-IDF features, by default 15000
        keep_train_file : bool, optional
            Whether to keep the intermediate training file, by default False
        eval_split : float, optional
            Proportion of data to leave out for evaluation, by default 0.1
        """
        if self.model:
            raise ModelExistsException(
                f"Model already trained or loaded. Initialize " \
                f"a new instance for training."
            )

        if not self.model_save_prefix:
            self.model_save_prefix = os.path.join(
                "model_artifacts", datetime.now().strftime("%Y%m%d_%H%M%S")
            )

        if not os.path.exists(self.model_save_prefix):
            os.makedirs(self.model_save_prefix, exist_ok=True)
            
        self.language = language
        self.entity_type = entity_type

        lemma_text_file, all_labels = self._prepare_text_and_labels(
            text_file, label_file, lemmatization_required
        )

        X_all, y_all = self._vectorize_and_binarize(
            lemma_text_file, all_labels, max_features
        )
        self.train_indices, self.eval_indices = split_indices(
            X_all.shape[0], eval_split
        )

        self._train_model(
            X_all[self.train_indices], 
            y_all[self.train_indices], 
            keep_train_file
        )
        self._evaluate_model(
            X_all[self.eval_indices], 
            y_all[self.eval_indices]
        )

    def _prepare_text_and_labels(
        self, text_file: str, label_file: str, lemmatization_required: bool
    ) -> Tuple[str, List[List[str]]]:
        """
        Prepare the text and labels for training.
        If lemmatization is required, write lemmatized texts to a file.
        If not, just read the labels and verify line counts.

        Parameters
        ----------
        text_file : str
            Path to the text file (raw or already lemmatized).
        label_file : str
            Path to the label file (semicolon-separated per line).
        lemmatization_required : bool
            Whether to lemmatize the text file.

        Returns
        -------
        Tuple[str, List[List[str]]]
            The path to the lemmatized text file and all labels in memory.
        """
        loader = DataLoader(text_file, label_file)

        if not lemmatization_required:
            LOGGER.info(
                f"Already-lemmatized workflow: storing labels " \
                f"in memory and verifying lines."
            )
            all_labels = loader.read_lemmatized()
            lemma_text_file = text_file
        else:
            LOGGER.info("Raw text workflow: lemmatizing into lemma_text_file.")
            lemma_text_file = f"{self.model_save_prefix}/lemma_texts.txt"
            all_labels = loader.write_lemmatized_texts(
                output_file=lemma_text_file,
                preprocess_fn=self.text_preprocessor.preprocess,
                language=self.language
            )

        return lemma_text_file, all_labels

    def _vectorize_and_binarize(
            self, lemma_text_file: str, all_labels: List[List[str]], 
            max_features: int
    ) -> Tuple[csr_matrix, csr_matrix]:
        """
        Vectorize the lemmatized texts and binarize the labels.

        Parameters
        ----------
        lemma_text_file : str
            Path to the file containing lemmatized texts.
        all_labels : List[List[str]]
            A list of label-lists, one per document.
        max_features : int
            Maximum number of TF-IDF features to use.

        Returns
        -------
        Tuple[csr_matrix, csr_matrix]
            The (X_all, y_all) matrices for training.
        """
        self.feature_extractor = TfidfFeatureExtractor(max_features=max_features)
        X_all = self.feature_extractor.fit_transform_file(lemma_text_file)
        y_all = csr_matrix(self.label_binarizer.fit_transform(all_labels))
        LOGGER.info(f"X_all shape: {X_all.shape}, y_all shape: {y_all.shape}")
        return X_all, y_all

    def _train_model(self, X_train: csr_matrix, y_train: csr_matrix,
            keep_train_file: bool
    ) -> None:
        """
        Train the Omikuji model and save the artifacts.

        Parameters
        ----------
        X_train : csr_matrix
            Training set feature matrix.
        y_train : csr_matrix
            Training set label matrix.
        keep_train_file : bool
            Whether to keep the intermediate training file.

        Returns
        -------
        None
        """
        omikuji_train_file = f"{self.model_save_prefix}/omikuji_train_file.txt"
        if os.path.exists(omikuji_train_file):
            LOGGER.info(f"Found existing training file at '{omikuji_train_file}'")
        else:
            write_omikuji_train_file(X_train, y_train, omikuji_train_file)
        self.model = train_omikuji(omikuji_train_file)

        if not keep_train_file and os.path.exists(omikuji_train_file):
            os.remove(omikuji_train_file)

        self.save(
            model_path=os.path.join(self.model_save_prefix, "omikuji_model"),
            vectorizer_path=os.path.join(self.model_save_prefix, "vectorizer.pkl"),
            binarizer_path=os.path.join(self.model_save_prefix, "binarizer.pkl")
        )
        LOGGER.info(
            f"Training complete. Artifacts saved with prefix " \
            f"'{self.model_save_prefix}'"
        )

    def _evaluate_model(self, X_eval: csr_matrix, y_eval: csr_matrix):
        """
        Evaluate the model on a held-out evaluation set.

        Parameters
        ----------
        X_eval : csr_matrix
            Evaluation set feature matrix.
        y_eval : csr_matrix
            Evaluation set label matrix.

        Returns
        -------
        Tuple[float, float, float]
            The (precision, recall, F1) scores using 'samples' average.
        """
        LOGGER.info("Evaluating on held-out evaluation set")

        precision, recall, f1 = self.evaluate(X_eval, y_eval)
        
        LOGGER.info(
            f"Evaluation Results - Precision: {precision:.4f}, " \
            f"Recall: {recall:.4f}, F1: {f1:.4f}"
        )


    def predict(self, text: str | ProcessedText, top_k: int = 5,
            lemmatization_required: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Predict labels for a single text.

        Parameters
        ----------
        text : str | ProcessedText
            The raw text to be lemmatized & vectorized.
        top_k : int, optional
            How many top labels to return, by default 5.
        lemmatization_required: bool
            If true, preprocessing (either stemming or lemmatization)
            if applied to the input text.

        Returns
        -------
        List[Tuple[str, float]]
            A list of (label_name, score) pairs.
        """
        if not self.model:
            raise ModelNotLoadedException("Model not trained or loaded.")
            
        if lemmatization_required:
            if isinstance(text, str):
                processed_text = self.text_preprocessor.preprocess(
                    text=text, 
                    lang_code=self.language
                )
            else:
                processed_text = text.processed_text
        else: 
            if isinstance(text, str):
                processed_text = text
            else:
                processed_text = text.original_text
                
        X_row = self.feature_extractor.transform_texts([processed_text])
        fv_pairs = [
            (j, X_row[0, j]) 
            for j in X_row[0].nonzero()[1]
        ]
        label_score_pairs = self.model.predict(fv_pairs, top_k=top_k)
        label_score_pairs = sorted(
            label_score_pairs, key=lambda x: x[1], reverse=True
        )
        labels = [
            (self.label_binarizer.classes_[idx], round(score, 3)) 
            for idx, score in label_score_pairs
        ]
        return labels

    def evaluate(
        self,
        X_eval: csr_matrix,
        y_eval: csr_matrix,
        top_k: int = 5,
        batch_size: int = 1000
    ) -> Tuple[float, float, float]:
        """
        Evaluate precision, recall, and F1 on a small in-memory dataset.

        Parameters
        ----------
        X_eval : csr_matrix
            A list of raw text documents.
        y_eval : csr_matrix
            A list of label-lists, parallel to 'texts'.
        top_k : int, optional
            How many top labels to consider, by default 5
        batch_size : int, optional
            Number of documents to process at once, by default 1000

        Returns
        -------
        Tuple[float, float, float]
            The (precision, recall, F1) scores using 'samples' average.
        """
        if not self.model:
            raise ModelNotLoadedException("Model not loaded or trained.")

        num_samples, num_labels = y_eval.shape
        Y_pred_sparse = lil_matrix((num_samples, num_labels), dtype=int)

        for start in tqdm(range(0, num_samples, batch_size), desc="Evaluating"):
            end = min(start + batch_size, num_samples)
            X_batch = X_eval[start:end]

            for i in range(X_batch.shape[0]):
                fv_pairs = [
                    (j, X_batch[i, j]) 
                    for j in X_batch[i].nonzero()[1]
                ]
                label_score_pairs = self.model.predict(
                    fv_pairs, top_k=top_k
                )
                pred_indices = [p[0] for p in label_score_pairs]
                row_pred = np.zeros(num_labels, dtype=int)
                row_pred[pred_indices] = 1
                Y_pred_sparse[start + i] = row_pred

        Y_pred_csr = Y_pred_sparse.tocsr()
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_eval, Y_pred_csr, average=SKLEARN_AVERAGE_FUNCTION
        )
        return precision, recall, f1

    def save(self, model_path: str, vectorizer_path: str, 
            binarizer_path: str
    ) -> NoReturn:
        """
        Save the Omikuji model, TfidfVectorizer, and 
        MultiLabelBinarizer to disk.

        Parameters
        ----------
        model_path : str
            Path to save the Omikuji model (omikuji.Model).
        vectorizer_path : str
            Path to save the pickled TfidfVectorizer.
        binarizer_path : str
            Path to save the pickled MultiLabelBinarizer.
        """
        if not self.model:
            raise ModelNotLoadedException("Model not trained or loaded.")
            
        LOGGER.info(f"Saving Omikuji model to {model_path}")
        self.model.save(str(model_path))
        
        LOGGER.info(f"Saving TF-IDF vectorizer to {vectorizer_path}")
        self.feature_extractor.save(vectorizer_path)
        
        LOGGER.info(f"Saving binarizer to {binarizer_path}")
        self.label_binarizer.save(binarizer_path)

        config = {
            "language": self.language, 
            "entity_type": self.entity_type
        }
        
        config_path = os.path.join(
            os.path.dirname(model_path), "config.json"
        )
        
        with open(config_path, "w") as f:
            json.dump(config, f)

    def load(self, artifacts_folder: str):
        """
        Load Omikuji model, TfidfVectorizer, and 
        MultiLabelBinarizer from disk.

        Parameters
        ----------
        artifacts_folder : str
            Path to the folder containing model artifacts.
        """
        model_path = os.path.join(artifacts_folder, "omikuji_model")
        vectorizer_path = os.path.join(artifacts_folder, "vectorizer.pkl")
        binarizer_path = os.path.join(artifacts_folder, "binarizer.pkl")

        LOGGER.info(f"Loading Omikuji model from {model_path}")
        self.model = Model.load(model_path)
        
        LOGGER.info(f"Loading TF-IDF vectorizer from {vectorizer_path}")
        self.feature_extractor.load(vectorizer_path)
        
        LOGGER.info(f"Loading binarizer from {binarizer_path}")
        self.label_binarizer.load(binarizer_path)

        config_path = os.path.join(artifacts_folder, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)

            self.language = config.get("language")
            if self.language is None:
                raise MissingValueException(
                    f"Config file does not contain 'language' key."
                )

            self.entity_type = config.get("entity_type")
            if self.entity_type is None:
                raise MissingValueException(
                    "Config file does not contain 'entity_type' key."
                )
        else:
            raise MissingFileException(
                "config.json file not found in model artifacts folder."
            )
