import os
import shutil
import tempfile
import pytest
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

from rara_subject_indexer.indexers.model_indexers.omikuji_indexer import OmikujiIndexer
from rara_subject_indexer.supervised.omikuji.label_binarizer import LabelBinarizer
from rara_subject_indexer.supervised.omikuji.omikuji_model import OmikujiModel
from rara_subject_indexer.supervised.omikuji.omikuji_helpers import (
    assert_both_files_same_length, split_indices, write_omikuji_train_file
)
from rara_subject_indexer.utils.downloader import Downloader
from rara_subject_indexer.exceptions import InvalidInputException

nltk.download("punkt_tab")



@pytest.fixture
def temp_files():
    text_content = "ühed dokumendid on siin\naga mõni teine on seal\n"\
                   "mõned hoopis aga taamal\nmõned olid kaugel\nmõned olid lähedal"
    label_content = """label1;label2\nlabel3\nlabel4;label5\nlabel6\nlabel7;label8"""
    with tempfile.TemporaryDirectory() as temp_dir:
        text_file = f"{temp_dir}/texts.txt"
        label_file = f"{temp_dir}/labels.txt"
        with open(text_file, "w", encoding="utf-8") as tf:
            tf.write(text_content)
        with open(label_file, "w", encoding="utf-8") as lf:
            lf.write(label_content)
        yield text_file, label_file

def test_assert_both_files_same_length(temp_files):
    text_file, label_file = temp_files
    assert_both_files_same_length(text_file, label_file)

    with tempfile.NamedTemporaryFile() as temp_invalid:
        temp_invalid.write(b"Extra line\n")
        temp_invalid_path = temp_invalid.name

        with pytest.raises(InvalidInputException):
            assert_both_files_same_length(text_file, temp_invalid_path)

def test_split_indices():
    train_indices, eval_indices = split_indices(num_samples=100, eval_split=0.2, random_seed=42)
    assert len(train_indices) == 80
    assert len(eval_indices) == 20
    assert not set(train_indices).intersection(eval_indices)

def test_write_omikuji_train_file(temp_files):
    text_file, label_file = temp_files

    vectorizer = TfidfVectorizer(max_features=10)
    with open(text_file, "r", encoding="utf-8") as f:
        X = vectorizer.fit_transform(f)

    label_binarizer = LabelBinarizer()
    with open(label_file, "r", encoding="utf-8") as f:
        labels = [[lbl.strip() for lbl in line.strip().split(";") if lbl.strip()] for line in f]
    y = label_binarizer.fit_transform(labels)

    with tempfile.NamedTemporaryFile() as temp_output:
        output_file = temp_output.name
        write_omikuji_train_file(X, y, output_file)
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Should have header: num_samples num_features num_labels
        assert lines[0].startswith("5 10 8")  # Header with counts

def test_omikuji_model_workflow(temp_files):
    omikuji_model = OmikujiModel()
    text_file, label_file = temp_files

    omikuji_model.train(
        text_file=str(text_file),
        label_file=str(label_file),
        language="et",
        entity_type="Testmärksõnad",
        lemmatization_required=True,
        max_features=10,
        keep_train_file=False,
        eval_split=0.2,
    )

    # Make sure lemmatized text file is created
    lemma_text_file = f"{omikuji_model.model_save_prefix}/lemma_texts.txt"
    with open(lemma_text_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert lines == ["üks dokument olema siin\n", "aga mõni teine olema seal\n",
                     "mõni hoopis aga taamal\n", "mõni olema kaugel\n", "mõni olema lähedal\n"]

    # Make sure model train file is deleted
    train_file = f"{omikuji_model.model_save_prefix}/omikuji_train_file.txt"
    assert not os.path.exists(train_file)
    loaded_model = OmikujiModel(model_artifacts_path=omikuji_model.model_save_prefix)
    assert loaded_model.language == "et"
    shutil.rmtree(omikuji_model.model_save_prefix)

    omikuji_model = OmikujiModel()
    omikuji_model.train(
        text_file=str(text_file),
        label_file=str(label_file),
        language="et",
        entity_type="Testmärksõnad",
        lemmatization_required=False,
        max_features=10,
        keep_train_file=True,
        eval_split=0.2,
    )

    # Make sure lemmatized text file is not created, instead user-provided train file is used
    lemma_text_file = temp_files[0]
    with open(lemma_text_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert lines == ["ühed dokumendid on siin\n", "aga mõni teine on seal\n",
                     "mõned hoopis aga taamal\n", "mõned olid kaugel\n", "mõned olid lähedal"]

    # Make sure model train file is not deleted
    train_file = f"{omikuji_model.model_save_prefix}/omikuji_train_file.txt"
    assert os.path.exists(train_file)
    shutil.rmtree(omikuji_model.model_save_prefix)


def test_omikuji_indexer():
    drive_url = "https://drive.google.com/file/d/1tbgv9av_rfAKHPkrXgsejnzo-kn0hGMW/view?usp=drive_link"
    downloader = Downloader(drive_url)
    downloader.download()

    config = {
        "language": "et",
        "top_k": 5,
        "model_path": os.path.join(downloader.output_dir, "udk_rahvbibl_est")
    }

    indexer = OmikujiIndexer(config)
    preds = indexer.find_keywords(
        text="Tantsime kõik lapaduud, lapaduud", 
        lemmatize=True
    )

    assert preds[0]["entity_type"] == "UDK Rahvusbibliograafia"
    assert "793" in [el["keyword"] for el in preds]  # 793 == "Rahvapeod. Koreograafia. Tants"
    assert all({"keyword", "score", "entity_type"} == set(pred.keys()) for pred in preds)

    shutil.rmtree(os.path.join(downloader.output_dir, "udk_rahvbibl_est"))