# RaRa Subject Indexer

![Py3.10](https://img.shields.io/badge/python-3.10-green.svg)
![Py3.11](https://img.shields.io/badge/python-3.11-green.svg)
![Py3.12](https://img.shields.io/badge/python-3.12-green.svg)

**`rara-subject-indexer`** is a  Python library for predicting subject indices (keywords) for textual inputs.

---

## ✨ Features  

- Predict subject indices of following types: **personal names**, **organizations**, **titles of work**, **locations**, **events**, **topics**, **UDC Summary**, **UDC National Bibliography**, **times**, **genres/form**, **EMS categories**.
- Supports subject indexing texts in **Estonian** and **English**.
- Use [Omikuji](https://github.com/tomtung/omikuji) for supervised subject indexing.
- Use [RaKUn](https://github.com/SkBlaz/rakun2) for unsupervised subject indexing.
- Use [StanzaNER](https://stanfordnlp.github.io/stanza/ner.html) and/or [GLiNER](https://github.com/urchade/GLiNER) for NER-based subject indexing.
- Train new Omikuji models.

---

## ⚡ Quick Start  

Get started with `rara-subject-indexer` in just a few steps:

1. **Install the Package**  
   Ensure you're using Python 3.10 or above, then run:  
   ```bash
   pip install rara-subject-indexer
   ```

2. **Import and Use**  
   Example usage for finding subject indices with default configuration:

   ```python
   from rara_subject_indexer.rara_indexer import RaraSubjectIndexer
   from pprint import pprint

   # If this is your first usage, download relevant models:
   # NB! This has to be done only once!
   RaraSubjectIndexer.download_resources()
   
   # Initialize the instance with default configuration
   rara_indexer = RaraSubjectIndexer()
   
   # Just a dummy text, use a longer one to get some meaningful results
   text = "Kui Arno isaga koolimajja jõudis, olid tunnid juba alanud."

   subject_indices = rara_indexer.apply_indexers(text=text)
   pprint(subject_indices)
   ```

---

---

## ⚙️ Installation Guide

Follow the steps below to install the `rara-subject-indexer` package, either via `pip` or locally.

---

### Installation via `pip`

<details><summary>Click to expand</summary>

1. **Set Up Your Python Environment**  
   Create or activate a Python environment using Python **3.10** or above.

2. **Install the Package**  
   Run the following command:  
   ```bash
   pip install rara-subject-indexer
   ```
</details>

---

### Local Installation

Follow these steps to install the `rara-subject-indexer` package locally:  

<details><summary>Click to expand</summary>


1. **Clone the Repository**  
   Clone the repository and navigate into it:  
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Python Environment**  
   Create or activate a Python environment using Python 3.10 or above. E.g:
   ```bash
   conda create -n py310 python==3.10
   conda activate py310
   ```

3. **Install Build Package**  
   Install the `build` package to enable local builds:  
   ```bash
   pip install build
   ```

4. **Build the Package**  
   Run the following command inside the repository:  
   ```bash
   python -m build
   ```

5. **Install the Package**  
   Install the built package locally:  
   ```bash
   pip install .
   ```

</details>

---

## 📝 Testing

<details><summary>Click to expand</summary>

1. **Clone the Repository**  
   Clone the repository and navigate into it:  
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Python Environment**  
   Create or activate a Python environment using Python 3.10 or above.

3. **Install Build Package**  
   Install the `build` package:  
   ```bash
   pip install build
   ```

4. **Build the Package**  
   Build the package inside the repository:  
   ```bash
   python -m build
   ```

5. **Install with Testing Dependencies**  
   Install the package along with its testing dependencies:  
   ```bash
   pip install .[testing]
   ```

6. **Run Tests**  
   Run the test suite from the repository root:  
   ```bash
   python -m pytest -v tests
   ```
---

</details>

## 📚 Documentation

<details><summary>Click to expand</summary>


### 🔍 RaraSubjectIndexer Class

#### Overview

`RaraSubjectIndexer` wraps all logic of different models and keyword types.

#### Parameters


| Name           | Type                 | Optional | Default                 | Description                                                                                                               |
|----------------|----------------------|----------|-------------------------|---------------------------------------------------------------------------------------------------------------------------|
| methods        | Dict[str, List[str]] | True     | DEFAULT_METHOD_MAP      | Methods to use per each keyword type. See ALLOWED_METHODS for a list of supported methods of each keyword type.           |
| keyword_types  | List[str]            | True     | DEFAULT_KEYWORD_TYPES   | Keyword (subject index) types to predict. See ALLOWED_KEYWORD_TYPES for a list of supported methods of each keyword type. |
| topic_config   | dict                 | True     | DEFAULT_TOPIC_CONFIG    | Configuration for topic subject indexing models. |
| time_config    | dict                 | True     | DEFAULT_TIME_CONFIG     | Configuration for time subject indexing models. |
| genre_config   | dict                 | True     | DEFAULT_GENRE_CONFIG    | Configuration for genre/form subject indexing models. |
| category_config| dict                 | True     | DEFAULT_CATEGORY_CONFIG | Configuration for EMS category prediction models. |
| udc_config     | dict                 | True     | DEFAULT_UDC_CONFIG      | Configuration for UDC (National Bibliography) prediction models.|
| udc2_config    | dict                 | True     | DEFAULT_UDC2_CONFIG     | Configuration for UDC Summary models.|
| ner_config     | dict                 | True     | DEFAULT_NER_CONFIG      | Configuration for NER-based subject indexing models.|
| omikuji_data_dir | string             | True     | OMIKUJI_DATA_DIR        | Path to directory storing Omikuji models. |
| ner_data_dir     | string             | True     | NER_DATA_DIR            | Path to directory storing NER models.     |


##### Allowed keyword types

| Enum object          | String value                     | 
|----------------------|----------------------------------|
| KeywordType.TOPIC    | "Teemamärksõnad"                 | 
| KeywordType.EVENT    | "Ajutine kollektiiv või sündmus" |
| KeywordType.LOC      | "Kohamärksõnad"                  |
| KeywordType.TIME     | "Ajamärksõnad"                   |
| KeywordType.GENRE    | "Vormimärksõnad"                 |
| KeywordType.PER      | "Isikunimi"                      |
| KeywordType.ORG      | "Kollektiivi nimi"               |
| KeywordType.TITLE    | "Teose pealkiri"                 |
| KeywordType.UDK      | "UDK Rahvusbibliograafia"        |
| KeywordType.UDK2     | "UDC Summary"                    |
| KeywordType.CATEGORY | "Valdkonnamärksõnad"             |

##### Allowed methods

| Keyword type (Enum object)| Keyword type (string value)      | Allowed methods                    |
|---------------------------|----------------------------------|------------------------------------|
| KeywordType.TOPIC         | "Teemamärksõnad"                 | "omikuji", "rakun"                 |
| KeywordType.EVENT         | "Ajutine kollektiiv või sündmus" | "gliner"                           |
| KeywordType.LOC           | "Kohamärksõnad"                  | "gliner", "stanza", "ner_ensemble" |
| KeywordType.TIME          | "Ajamärksõnad"                   | "omikuji"                          |
| KeywordType.GENRE         | "Vormimärksõnad"                 | "omikuji"                          |
| KeywordType.PER           | "Isikunimi"                      | "gliner", "stanza", "ner_ensemble" |
| KeywordType.ORG           | "Kollektiivi nimi"               | "gliner", "stanza", "ner_enseble"  |
| KeywordType.TITLE         | "Teose pealkiri"                 | "gliner"                           |
| KeywordType.UDK           | "UDK Rahvusbibliograafia"        | "omikuji"                          |
| KeywordType.UDK2          | "UDC Summary"                    | "omikuji"                          |
| KeywordType.CATEGORY      | "Valdkonnamärksõnad"             | "omikuji"                          |


##### Default configurations
<details><summary>Default configurations</summary>


DEFAULT_KEYWORD_TYPES:

```json 
[
    "Teemamärksõnad",
    "Kohamärksõnad",
    "Isikunimi",
    "Kollektiivi nimi",
    "Kohamärksõnad",
    "Ajamärksõnad",
    "Teose pealkiri",
    "UDK Rahvusbibliograafia",
    "UDC Summary",
    "Vormimärksõnad",
    "Valdkonnamärksõnad",
    "Ajutine kollektiiv või sündmus"
]
```

DEFAULT_METHOD_MAP:

```json
 {
    "Teemamärksõnad": ["omikuji", "rakun"],
    "Kohamärksõnad": ["ner_ensemble"],
    "Isikunimi": ["ner_ensemble"], 
    "Kollektiivi nimi": ["ner_ensemble"],
    "Kohamärksõnad": ["ner_ensemble"],
    "Ajamärksõnad": ["omikuji"],
    "Teose pealkiri": ["gliner"],
    "UDK Rahvusbibliograafia": ["omikuji"],
    "UDC Summary": ["omikuji"],
    "Vormimärksõnad": ["omikuji"],
    "Valdkonnamärksõnad": ["omikuji"],
    "NER": ["ner"],
    "Ajutine kollektiiv või sündmus": ["gliner"]     
}
```
DEFAULT_TOPIC_CONFIG:

```json
 {
    "omikuji": {
        "et": "./rara_subject_indexer/data/omikuji_models/teemamarksonad_est"
        "en": "./rara_subject_indexer/data/omikuji_models/teemamarksonad_eng"
    }
    "rakun": {
        "stopwords": {
            "et": <list of stopwords loaded from "rara_subject_indexer/resources/stopwords/et_stopwords_lemmas.txt">,
            "en": <list of stopwords loaded from "rara_subject_indexer/resources/stopwords/et_stopwords.txt">,
        },
        "n_raw_keywords": 50
    }
}
```


DEFAULT_TIME_CONFIG:

```json
 {
    "omikuji": {
        "et": "./rara_subject_indexer/data/omikuji_models/ajamarksonad_est"
        "en": "./rara_subject_indexer/data/omikuji_models/ajamarksonad_eng"
    }
    "rakun": {}
}
```

DEFAULT_GENRE_CONFIG:

```json
 {
    "omikuji": {
        "et": "./rara_subject_indexer/data/omikuji_models/vormimarksonad_est"
        "en": "./rara_subject_indexer/data/omikuji_models/vormimarksonad_eng"
    }
    "rakun": {}
}
```

DEFAULT_CATEGORY_CONFIG:

```json
 {
    "omikuji": {
        "et": "./rara_subject_indexer/data/omikuji_models/valdkonnamarksonad_est"
        "en": "./rara_subject_indexer/data/omikuji_models/valdkonnamarksonad_eng"
    }
    "rakun": {}
}
```

DEFAULT_UDC_CONFIG:

```json
 {
    "omikuji": {
        "et": "./rara_subject_indexer/data/omikuji_models/udk_rahvbibl_est"
        "en": "./rara_subject_indexer/data/omikuji_models/udk_rahvbibl_eng"
    }
    "rakun": {}
}
```

DEFAULT_UDC2_CONFIG:

```json
 {
    "omikuji": {
        "et": "./rara_subject_indexer/data/omikuji_models/udk_general_depth_11_est"
        "en": "./rara_subject_indexer/data/omikuji_models/udk_general_depth_11_eng"
    }
    "rakun": {}
}
```

DEFAULT_NER_CONFIG:

```json
 {
    "ner": {
        "stanza_config": {
            "resource_dir": "./rara_subject_indexer/data/ner_resources/",
            "download_resources": False,
            "supported_languages": ["et", "en"],
            "custom_ner_model_langs": ["et"],
            "refresh_data": False,
            "custom_ner_models": {
                "et": "https://packages.texta.ee/texta-resources/ner_models/_estonian_nertagger.pt"
            },
            "unknown_lang_token": "unk"   
        },
        "gliner_config": {
            "labels": ["Person", "Organization", "Location", "Title of a work", "Date", "Event"], 
            "model_name": "urchade/gliner_multi-v2.1",
            "multi_label": False,
            "resource_dir": "./rara_subject_indexer/data/ner_resources/",
            "threshold": 0.5,
            "device": "cpu"
        },
        "ner_method_map": {
            "PER": "ner_ensemble",
            "ORG": "ner_ensemble",
            "LOC": "ner_ensemble",
            "TITLE": "gliner",
            "EVENT": "gliner"
        }
    }
}
```
OMIKUJI_DATA_DIR = `"./rara_subject_indexer/data/omikuji_models/"`

NER_DATA_DIR = `"./rara_subject_indexer/data/ner_resources/"`

</details>

#### Key Functions

##### `apply_indexers`

`apply_indexers` takes plaintext as an input and outputs predicted subject indices for all keyword types and methods defined during initiating the class instance.

###### Parameters

| Name           | Type                 | Optional | Default                 | Description                                    |
|----------------|----------------------|----------|-------------------------|---------------------------------------------------------------------------------------------------------------------------|
| text        | str | False    | -     | Text for which to find the subject indices. |
| lang             | str | False    | ""    | Language code indicating the language of the text. If not specified, the language of the text is detected automatically. |
| threshold_config  | dict | False    | DEFAULT_THRESHOLD_CONFIG     | Can be used to overwrite default threshold settings for each keyword type separately. |
| min_score        | float | False    | None    | If not None, defaults to min threshold score for all keyword types that are NOT specifically set via `threshold_config`. Has to be a float between 0 and 1. |
| max_count        | int | False    | None     | If not None, defaults to max keyword count for all keyword types that are NOT specifically set via `threshold_config`.|
| ignore_for_equal_scores | bool | True | False | If enabled, param `max_count` is ignored for keywords with equal scores. E.g. max_count = 2, scores = {k1: 0.9, k2: 0.8, k3: 0.8, k4: 0.7}. By default, only the top two keywords (k1, k2) are returned, eventhough k3 has exactly the same score as k2. If `ignore_for_equal_scores` if enabled, k3 will be returned along with k1 and k2.|
| flat       |bool | False    | True     | If enabled, keywords are returned in a flat list of dicts; otherwise with more nested structure. |
| rakun_config       | dict | False    | DEFAULT_RAKUN_CONFIG   | Configuration parameters for Rakun. |
| omikuji_config        | dict | False    | DEFAULT_OMIKUJI_CONFIG    | Configuration parameters for Omikuji. |
| ner_config       | dict | False    | DEFAULT_NER_CONFIG     | Configuration parameters for NER-based indexers. |


Allowed options along with default configurations for `rakun_config`, `omikuji_config`, `ner_config` can be seen below.

**Rakun config**

|Name | Type | Optional | Default | Description |
|-----|------|----------|---------|-------------|
|use_phraser| bool | True | False | If enabled, two-word keyphrases can be extracted from the text. Otherwise, only single words will be returned as keywords / subject indices. NB! Using phraser is currently **supported only for Estonian**. |
| postags_to_ignore | List[str] | True | ["V", "A", "D", "Z", "H", "P", "U", "N", "O"] | List of part-of-speech tags to ignore while detecting keywords / subject_indices. List of possible POS-tags can be found from her:  https://www.sketchengine.eu/estonian-filosoft-part-of-speech-tagset. NB! Ignoring POS-tags is currently **supported only for Estonian**. |

DEFAULT_RAKUN_CONFIG:

```json
{
    "use_phraser": False, 
    "postags_to_ignore": ["V", "A", "D", "Z", "H", "P", "U", "N", "O"]
}
```

**Omikuji config**

|Name | Type | Optional | Default | Description |
|-----|------|----------|---------|-------------|
|lemmatize | bool | True | False | Is enabled, text is lemmatized/stemmed (depending on the language) in `OmikujiModel` class. Default value is False as text in this workflow is actually lemmatized before passing it to the `OmikujiModel` class.|

DEFAULT_OMIKUJI_CONFIG:

```json
{
    "lemmatize": False
}
```

**NER config**

|Name | Type | Optional | Default | Description |
|-----|------|----------|---------|-------------|
|lemmatize | bool | True | False | Is enabled, text is lemmatized/stemmed (depending on the language) in `NERIndexer` class. Default and recommended value is False as lemmatizing/stemming might lead to incorrect NER entities, especially for titles, events and organizations.|
|min_count | int | True | 3 | The minimum number of times an entity has to appear in the text to be considered as a potential subject index (before applying additional score-based filtering). |
|ensemble_strategy | string | True| "intersection" | The strategy used, is selected NER method = "ner_ensemble". Allowed options are: ["intersection", "union"]. "intersection" outputs the intersection of Stanza and GLiNER method outputs; "union" outputs the union of Stanza and GLiNER method outputs. "interection" is recommended for more precise results, while "union" is recommended for higher recall |


DEFAULT_NER_CONFIG:

```json
{
    "lemmatize": False, 
    "min_count": 3, 
    "ensemble_strategy": "intersection"
}     
```
**threshold_config**

Specifying a threshold_config will overwrite default configurations of all keyword and method types occuring in the configuration. 

DEFAULT_THREHOLD_CONFIG:

```json
{
    KeywordType.TOPIC: {
        ModelArch.OMIKUJI: {"max_count": 5, "min_score": 0.1},
        ModelArch.RAKUN: {"max_count": 5, "min_score": 0.01}
    },
    KeywordType.TIME: {
        ModelArch.OMIKUJI: {"max_count": 3, "min_score": 0.2}
    },
    KeywordType.GENRE: {
        ModelArch.OMIKUJI: {"max_count": 3, "min_score": 0.2}
    },
    KeywordType.UDK: {
        ModelArch.OMIKUJI: {"max_count": 1, "min_score": 0.3}
    },
    KeywordType.UDK2: {
        ModelArch.OMIKUJI: {"max_count": 1, "min_score": 0.3}
    },
    KeywordType.PER: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.ORG: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.TITLE: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.LOC: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.3}
    },
    KeywordType.CATEGORY: {
        ModelArch.OMIKUJI: {"max_count": 3, "min_score": 0.2}
    },
    KeywordType.EVENT: {
        ModelArch.NER: {"max_count": 5, "min_score": 0.1}
    }
}
```

---
 

### Training Supervised and Unsupervised Models

If necessary, you can train the supervised and unsupervised models from scratch using the provided pipelines. 
The training process involves reading text and label files, preprocessing the text, and training the models 
using the extracted features.

#### Training an Omikuji Model for Supervised Keyword Extraction

A sample code snippet to train and predict using the Omikuji model is provided below:

```python
from rara_subject_indexer.supervised.omikuji.omikuji_model import OmikujiModel

model = OmikujiModel()

model.train(
    text_file="texts.txt",         # File with one document per line
    label_file="labels.txt",       # File with semicolon-separated labels for each document
    language="et",                 # Language of the text, in ISO 639-1 format
    entity_type="Teemamärksõnad",  # Entity type for the keywords
    lemmatization_required=True,   # (Optional) Whether to lemmatize the text - only set False if text_file is already lemmatized
    max_features=20000,            # (Optional) Maximum number of features for TF-IDF extraction
    keep_train_file=False,         # (Optional) Whether to retain intermediate training files
    eval_split=0.1                 # (Optional) Proportion of the dataset used for evaluation
)

predictions = model.predict(
    text="Kui Arno isaga koolimajja jõudis",  # Text to classify
    top_k=3  # Number of top predictions to return
)  # Output: [('koolimajad', 0.262), ('isad', 0.134), ('õpilased', 0.062)]
```

##### 📂 Data Format

The files provided to the train function should be in the following format:
- A **text file** (`.txt`) where each line is a document.
    ```
    Document one content.
    Document two content.
    ```
- A **label file** (`.txt`) where each line contains semicolon-separated labels corresponding to the text file.
    ```
    label1;label2
    label3;label4
    ```



---

#### Training Phraser for Unsupervised Keyword Extraction


A sample code snippet to train and predict using the Phraser model is provided below:

```python
from rara_subject_indexer.utils.phraser_model import PhraserModel

model = PhraserModel()

model.train(
    train_data_path=".../train.txt",  # File with one document per line, text should be lemmatised.
    lang_code="et",                   # Language of the text, in ISO 639-1 format
    min_count=5,                      # (Optional) Minimum word frequency for phrase formation.
    threshold=10.0                    # (Optional) Score threshold for forming phrases.
)

predictions = model.predict(
    text="'vabariik aastapäev sööma kiluvõileib'",  # Lemmatised text for phrase detection
)  # Output: ['vabariik_aastapäev', 'sööma', kiluvõileib']
```

##### 📂 Data Format

The file provided to the PhraserModel train function should be in the following format:

- A **text file** (`.txt`) where each line is a document.
    ```
    Document one content.
    Document two content.
    ```

</details>

## 🔍 Usage Examples

<details><summary>Click to expand</summary>
    
### Test  texts

<details><summary>TEXT_ET</summary>

```
Los Angeleses jagatakse 97. korda Ameerika filmiakadeemia auhindu ehk Oscareid. Parima täispika animatsiooni kategoorias pälvis Oscari Läti režissööri Gints Zilbalodise film "Vooluga kaasa". Õhtu suurim võitja oli aga Sean Bakeri "Anora", mis läks koju viie auhinnaga, nende hulgas ka aasta filmi preemia.

Läti võitis filmiga "Vooluga kaasa" oma esimese Oscari. Režissöör Gints Zilbalodis ütles, et ta on väga liigutatud sellest, kui hästi nende film on vastu võetud. "Ma loodan, et see avab ka teistele sõltumatutele filmitegijatele uksi," ütles ta ja lisas, et see on esimene kord, kui Läti film on olnud nomineeritud Oscarile. "See tähendab meie jaoks väga palju, loodame varsti siin tagasi olla." "Vooluga kaasa" võidu peale ütles õhtujuht Conan O'Brien, et "pall on nüüd teie väljakupoolel, Eesti".

Auhinnagala algas pühendusega Los Angelesele, kus möllasid tänavu jaanuaris rasked metsatulekahjud, mis puudustasid ka paljusid filmitegijaid. Sellele järgnes Ariana Grande laulunumber, kus ta kandis ette filmist "Võlur Oz" tuntuks saanud loo "Over the Rainbow". Näitleja ja muusik Cynthia Erivo, kes astus koos Grandega üles filmis "Wicked", esitas pärast teda Diana Rossi loo "Home", mis kõlas esmakordselt 1975. aastal Broadway muusikalis "The Wiz".

Teine suurem muusikanumber toimus keset galat, kui tehti austusavaldus James Bondile. Tantsunumbriga astus laval üles näitleja Margaret Qualley, muusikutest astusid üles Blackpinki liige Lisa, kes esitas loo "Live and Let Die"; Doja Cat, kes kandis ette pala "Diamonds are Forever" ning Raye, kelle esituses kõlas "Skyfall".

Oma avakõnes ütles õhtujuht Conan O'Brien, et Los Angelese inimesed on viimasel ajal palju läbi elanud ja sellised auhinnagalad võivad tunduda seejuures tühised. "Me tunnustame siin küll palju näitlejaid, aga samas pöörame tähelepanu ka inimestele, kes tegutsevad kaamera taga ning kes on pühendanud oma elu sellele, et filmidega tegeleda, kuigi paljud neist ei ole tuntud ega rikkad," sõnas ta.


Funk: Eesti anima on kaootiliselt mitmekülgne, Oscarid vajavad lihtsamaid lugusid
Gala lõpuosas ütles O'Brien, et on rõõm näha, et "Anora" on võitnud juba kaks auhinda. "Ameeriklastel on ilmselt hea näha, et keegi astub lõpuks võimsa venelase vastu."

Näitleja Kieran Culkin pälvis rolli eest filmis "Tõeline valu" oma esimese Oscari. "Mul ei ole mingit aimu, kuidas ma jõudsin siia, sest ma olen näidelnud terve oma elu," ütles ta ja lisas, et Jesse Eisenberg on geenius. "Ma ei ole seda kunagi varem sulle öelnud ja ei ütle enam kunagi uuesti."

Oma esimese Oscari pälvis tänavu ka Zoe Saldana rolli eest filmis "Emilia Perez". Tänukõnes rõhutas ta, et 1961. aastal kolis ta vanaema Ameerikasse ning ta on uhkusega immigrantide perekonnast pärit. "Ma olen ka esimene dominikaani juurtega ameeriklane, kes on võitnud Oscari, aga ma olen kindel, et mitte viimane."

22 aastat tagasi filmiga "Pianist" oma esimese Oscari võitnud Adrien Brody pälvis tänavu oma teise auhinna. "Näitlemine on väga habras elukutse, mis tundub väga glamuurne ja mingitel hetkedel kindlasti on, kuid aastate jooksul olen mõistnud, et kõik, mida sa oled oma karjääri jooksul saavutanud, võib kaduda," ütles ta ja lisas, et see auhind näitab talle, et tal on võimalus alustada uuesti. "See annab mulle võimaluse ka järgmised 20 aastat oma elust näidata, et olen suuri ja tähenduslikke rolle väärt."

Rolli eest filmis "Anora" pälvis näitleja Mikey Madison. "Ma kasvasin üles Los Angeleses, aga Hollywood tundus minust alati nii kaugel, seega võimalus seista siin ruumis on täiesti uskumatu," kinnitas ta ja lisas, et see on unistuse täitumine.


Galerii: Ameerika filmiakadeemia auhindade punane vaip
Parim film
"Anora", režissöör Sean Baker
"Brutalist" ("The Brutalist"), režissöör Brady Corbet
"Täiesti tundmatu" ("A Complete Unknown"), režissöör James Mangold
"Konklaav" ("Conclave"), režissöör Edward Berger
"Düün: teine osa" ("Dune: Part Two"), režissöör Denis Villeneuve
"Emilia Perez", režissöör Jacques Audiard
"Olen veel siin" ("I'm Still Here"), režissöör Walter Salles
"Nickel Boys", režissöör RaMell Ross
"Protseduur" ("The Subtance"), režissöör Coralie Fargeat
"Wicked", režissöör Jon M. Chu

Parim naispeaosa
Cynthia Erivo rolli eest filmis "Wicked"
Karla Sofia Garcon rolli eest filmis "Emilia Perez"
Mikey Madison rolli eest filmis "Anora"
Demi Moore rolli eest filmis "Protseduur"
Fernanda Torres rolli eest filmist "Olen veel siin"

Parim lavastaja
Sean Baker filmiga "Anora"
Brady Corbet filmiga "Brutalist"
James Mangold filmiga "Täiesti tundmatu"
Jacques Audiard filmiga "Emilia Perez"
Coralie Fargeat filmiga "Protseduur"

Parim meespeaosa
Adrien Brody rolli eest filmis "Brutalist"
Timothee Chalamet rolli eest filmist "Täiesti tundmatu"
Colman Domingo rolli eest filmis "Sing Sing"
Ralph Fiennes rolli eest filmis "Konklaav"
Sebastian Stan rolli eest filmist "Mantlipärija: Trumpi lugu"

Parim originaalmuusika
"Brutalist"
"Konklaav"
"Emilia Perez"
"Wicked"
"Pöörane robot" ("The Wild Robot")

Parim rahvusvaheline film
"Olen veel siin", Brasiilia
"Tüdruk nõelaga" ("The Girl With the Needle"), Taani
"Emilia Perez", Prantsusmaa
"The Seed of the Sacred Fig", Saksamaa
"Flow", Läti

Parim operaatoritöö
"Brutalist"
"Düün: teine osa"
"Emilia Perez"
"Maria"
"Nosferatu"


Briti filmiauhindade jagamisel võidutsesid "Konklaav" ja "Brutalist"
Parim lühimängufilm
"A Lien"
"Anuja"
"I'm Not A Robot"
"The Last Ranger"
"The Man Who Could Not Remain Silent"

Parimad eriefektid
"Alien: Romulus"
"Better Man"
"Düün: teine osa"
"Ahvide planeedi kuningriik" ("Kingdom of the Planet of the Apes")
"Wicked"

Parim heli
"Täiesti tundmatu"
"Düün: teine osa"
"Emilia Perez"
"Wicked"
"Pöörane robot"

Parim dokumentaalfilm
"Black Box Diaries"
"Pole muud maad" ("No Other Land")
"Portselanist sõda" ("Porcelain War")
"Soundtrack to a Coup d'etat"
"Sugarcane"

Parim lühidokumentaal
"Death by Numbers"
"I Am Ready, Warden"
"Incident"
"Instruments of a Beating Heart"
"Only Girl in the Orchestra"

Parim originaallugu
"El Mal" filmist "Emilia Perez"
"The Journey" filmist "Six Triple Eight"
"Like a Bird" filmist "Sing Sing"
"Mi Camino" filmist "Emilia Perez"
"Never Too Late" filmist "Elton John: Never Too Late"

Parim kunstnikutöö
"Brutalist"
"Konklaav"
"Düün: teine osa"
"Nosferatu"
"Wicked"

Parim naiskõrvalosa
Monica Barbaro rolli eest filmis "Täiesti tundmatu"
Ariana Grande rolli eest filmis "Wicked"
Felicity Jones rolli eest filmis "Brutalist"
Isabella Rossellini rolli eest filmis "Konklaav"
Zoe Saldana rolli eest filmis "Emilia Perez"

Parim montaaž
"Anora"
"Brutalist"
"Konklaav"
"Emilia Perez"
"Wicked"

Parim grimm
"A Different Man"
"Emilia Perez"
"Nosferatu"
"Protseduur"
"Wicked"

Parim kohandatud stsenaarium
"Täiesti tundmatu"
"Konklaav"
"Emilia Perez"
"Nickel Boys"
"Sing Sing"

Parim originaalstsenaarium
"Anora"
"Brutalist"
"Tõeline valu"
"5. september" ("September 5")
"Protseduur"

Parim kostüümidisain
"Täiesti tundmatu"
"Konklaav"
"Gladiaator II"
"Nosferatu"
"Wicked"

Parim lühianimatsioon
"Beautiful Man"
"In The Shadow of the Cypress"
"Magic Candies"
"Wander to Wonder"
"Yuck!"

Parim täispikk animatsioon
"Vooluga kaasa"
"Pahupidi 2"
"Memoir of a Snail"
"Wallace and Gromit: Vengence Most Fowl"
"Pöörane robot"

Parim meeskõrvalosa
Yuri Borissov rolli eest filmis "Anora"
Kieran Culkin rolli eest filmis "Tõeline valu" ("A Real Pain")
Edward Norton rolli eest filmis "Täiesti tundmatu"
Guy Pierce rolli eest filmis "Brutalist"
Jeremy Strong rolli eest filmis "Mantlipärija: Trumpi lugu" ("The Apprentice")    
```
</details>

<details><summary>TEXT_EN</summary>

```
Easter marks the start of spring, the triumph of life and renewal and is a time of festivities and tradition in Estonia.

Easter is known by many names in Estonia, including lihavõtted (a direct reference to the return of meat on menus after Lent), munadepüha (egg holiday) and kiigepüha (swing holiday, pointing to the tradition of taking to traditional wooden village swings on Easter Sunday).

In the old folk calendar, the spring holiday started on the next Sunday after the first full moon following the spring equinox, falling between March 23 and April 26. The holiday week was important for household chores, such as spring cleaning after a long winter. According to tradition, the weather during this week could be used to predict conditions for the entire summer. If it rained, a wet summer would follow, and if there was fog, a hot summer could be expected.

Maundy Thursday was considered a semi-holiday, during which people prepared for Good Friday. Lighter meals were eaten, such as soup. The types of soup varied by region, but one thing was certain: everyone rested on Good Friday. It was very rare for anyone to even leave the house on that day.

Easter Sunday, much like today, was a festive occasion. On this day, people traditionally exchanged eggs or gave them as gifts. Young people would gather by the village swing and girls would give decorated Easter eggs to the boys as thanks for building the swing, where they would then spend the afternoon together. People gathered in their homes or at the local tavern and exchanged eggs as gifts. Eggs were also used in food, most commonly as egg butter or egg spread.


Singers in Sõrve national dress on a traditional village swing. Source: Margus Muld/ERR
Pussy willows brought indoors were and are an inseparable part of the holiday. Those who hadn't gotten them earlier would place them in a vase by the time egg dyeing began. When liverworts started to bloom, people would also bring in moss and the first spring flowers. In the 20th century, it became customary to sprout grass on a plate or in a bowl for Easter, creating a bed on which to place decorated eggs. Nests made of twigs and moss were also crafted to hold the colorful eggs. Additionally, budding branches of various kinds were placed indoors and used to decorate rooms.

Easter customs and springtime traditions varied across different regions of Estonia. Some of these old Easter traditions are celebrated each year at the Estonian Open Air Museum in Tallinn. Visitors can also travel to Setomaa in southern Estonia to gain a deeper understanding of the local customs there.

These days, Easter Sunday is usually celebrated by having a long lunch, dyeing and swapping eggs and a traditional Easter hunt. Eggs are usually colored using natural dies, such as those from onion peels or beets. The multicolored eggs are a mandatory part of any Easter spread and the natural colorings mean they're perfectly edible.

While rooms can be decorated with artificial eggs, real eggs are needed for the traditional egg tapping competition, which crowns a new champion each year. The rules are simple — tap the tip of your egg against your opponent's, and whoever's shell remains unbroken wins! Some families keep the fun going all year round — it's just that enjoyable. If natural dyes are used, the extra layer of the one with the cracked egg having to eat it is sometimes added to the competition, making ultimate victory dependent not only on the best tapping tactic but also one's capacity for boiled eggs.

Many Easter customs still practiced today originate from old folk traditions. One such game, popular especially in Setomaa, is egg rolling, which shares the same goal as egg tapping: to crack the opponent's eggshell. Players roll their eggs down a sand mound, aiming to hit other eggs. The difficulty of the slope is entirely up to the player. The winner is the one whose egg stays intact.

Traditional Easter food covers everything to do with eggs, but also curd and cottage cheese dishes, including salads, desserts and pastries utilizing these ingredients. Prime examples include deviled eggs and egg salad, Of meats, veal, hare and rabbit are revered during this period, while it's no good turning your nose up at fish, pork, chicken or lamb either.

Porridge and all manner of baked goodness, including homemade white bread, pastries and cakes, are also held in high esteem around the holiday. However, among Easter desserts, paskha is widely considered a favorite.    
```
</details>

<details><summary>TEXT_RU</summary>

```
Министр иностранных дел Ирана Аббас Аракчи выразил надежду
что Россия примет участие в переговорах по ядерной программе Ирана.

До сих пор переговоры проходили в двустороннем формате между Ираном и США. Следующий раунд состоится завтра в Риме, передает "Актуальная камера".

По словам главы иранского МИДа, переговоры до сих пор были конструктивными и стороны могут прийти к согласию по ядерной программе.   
```
</details>

### Apply with default configuration

#### Estonian input text

```python
from rara_subject_indexer.rara_indexer import RaraSubjectIndexer
from pprint import pprint

# If this is your first usage, download relevant models:
# NB! This has to be done only once!
RaraSubjectIndexer.download_resources()

# Initialize the instance with default configuration
rara_indexer = RaraSubjectIndexer()

subject_indices = rara_indexer.apply_indexers(text=TEXT_ET)
pprint(subject_indices)
```

<details><summary>Output</summary>
    
```json

{"durations": [{"duration": 0.0283,
                "keyword_type": "Teemamärksõnad",
                "model_arch": "omikuji"},
               {"duration": 1.22906,
                "keyword_type": "Teemamärksõnad",
                "model_arch": "rakun"},
               {"duration": 0.00891,
                "keyword_type": "Ajamärksõnad",
                "model_arch": "omikuji"},
               {"duration": 0.01025,
                "keyword_type": "Vormimärksõnad",
                "model_arch": "omikuji"},
               {"duration": 5.44328,
                "keyword_type": "NER",
                "model_arch": "ner"},
               {"duration": 0.01392,
                "keyword_type": "UDK Rahvusbibliograafia",
                "model_arch": "omikuji"},
               {"duration": 0.0177,
                "keyword_type": "UDC Summary",
                "model_arch": "omikuji"},
               {"duration": 0.00761,
                "keyword_type": "Valdkonnamärksõnad",
                "model_arch": "omikuji"}],
 "keywords": [{"entity_type": "Teemamärksõnad",
               "keyword": "filmid (teosed)",
               "model_arch": "omikuji",
               "score": 0.979},
              {"entity_type": "Teemamärksõnad",
               "keyword": "mängufilmid",
               "model_arch": "omikuji",
               "score": 0.573},
              {"entity_type": "Teemamärksõnad",
               "keyword": "filmiauhinnad",
               "model_arch": "omikuji",
               "score": 0.164},
              {"entity_type": "Teemamärksõnad",
               "keyword": "film",
               "model_arch": "rakun",
               "score": 0.32},
              {"entity_type": "Teemamärksõnad",
               "keyword": "ameeriklane",
               "model_arch": "rakun",
               "score": 0.039},
              {"entity_type": "Teemamärksõnad",
               "keyword": "metsatulekahju",
               "model_arch": "rakun",
               "score": 0.025},
              {"entity_type": "Teemamärksõnad",
               "keyword": "kostüümidisain",
               "model_arch": "rakun",
               "score": 0.025},
              {"entity_type": "Teemamärksõnad",
               "keyword": "austusavaldus",
               "model_arch": "rakun",
               "score": 0.023},
              {"entity_type": "Vormimärksõnad",
               "keyword": "filmiarvustused",
               "model_arch": "omikuji",
               "score": 0.905},
              {"count": 3,
               "entity_type": "Isikunimi",
               "keyword": "Sean Baker",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 5,
               "entity_type": "Teose pealkiri",
               "keyword": "Wicked",
               "method": "gliner",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 5,
               "entity_type": "Teose pealkiri",
               "keyword": "Brutalist",
               "method": "gliner",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 4,
               "entity_type": "Teose pealkiri",
               "keyword": "Anora",
               "method": "gliner",
               "model_arch": "ner",
               "score": 0.8},
              {"count": 3,
               "entity_type": "Teose pealkiri",
               "keyword": "Nosferatu",
               "method": "gliner",
               "model_arch": "ner",
               "score": 0.6},
              {"count": 3,
               "entity_type": "Teose pealkiri",
               "keyword": "Vooluga kaasa",
               "method": "gliner",
               "model_arch": "ner",
               "score": 0.6},
              {"entity_type": "UDK Rahvusbibliograafia",
               "keyword": "791",
               "model_arch": "omikuji",
               "score": 1.0},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "FOTOGRAAFIA. FILM. KINO",
               "model_arch": "omikuji",
               "score": 1.0},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "KOHANIMED",
               "model_arch": "omikuji",
               "score": 0.944},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "AJAKIRJANDUS. KOMMUNIKATSIOON. MEEDIA. REKLAAM",
               "model_arch": "omikuji",
               "score": 0.449}]}
```

</details>

#### English input text

```python
from rara_subject_indexer.rara_indexer import RaraSubjectIndexer
from pprint import pprint

# If this is your first usage, download relevant models:
# NB! This has to be done only once!
# RaraSubjectIndexer.download_resources()

# Initialize the instance with default configuration
rara_indexer = RaraSubjectIndexer()

subject_indices = rara_indexer.apply_indexers(text=TEXT_EN)
pprint(subject_indices)
```

<details><summary>Output</summary>
    
```json
{"durations": [{"duration": 0.06654,
                "keyword_type": "Teemamärksõnad",
                "model_arch": "omikuji"},
               {"duration": 0.02818,
                "keyword_type": "Teemamärksõnad",
                "model_arch": "rakun"},
               {"duration": 0.01287,
                "keyword_type": "Ajamärksõnad",
                "model_arch": "omikuji"},
               {"duration": 0.01382,
                "keyword_type": "Vormimärksõnad",
                "model_arch": "omikuji"},
               {"duration": 2.80652,
                "keyword_type": "NER",
                "model_arch": "ner"},
               {"duration": 0.01278,
                "keyword_type": "UDK Rahvusbibliograafia",
                "model_arch": "omikuji"},
               {"duration": 0.01117,
                "keyword_type": "UDC Summary",
                "model_arch": "omikuji"},
               {"duration": 0.00898,
                "keyword_type": "Valdkonnamärksõnad",
                "model_arch": "omikuji"}],
 "keywords": [{"entity_type": "Teemamärksõnad",
               "keyword": "ülestõusmispühad",
               "model_arch": "omikuji",
               "score": 1.0},
              {"entity_type": "Teemamärksõnad",
               "keyword": "kombed",
               "model_arch": "omikuji",
               "score": 0.296},
              {"entity_type": "Teemamärksõnad",
               "keyword": "kirikukalendrid",
               "model_arch": "omikuji",
               "score": 0.218},
              {"entity_type": "Teemamärksõnad",
               "keyword": "munad",
               "model_arch": "omikuji",
               "score": 0.207},
              {"entity_type": "Teemamärksõnad",
               "keyword": "kirikupühad",
               "model_arch": "omikuji",
               "score": 0.163},
              {"entity_type": "Teemamärksõnad",
               "keyword": "easter",
               "model_arch": "rakun",
               "score": 0.118},
              {"entity_type": "Teemamärksõnad",
               "keyword": "egg",
               "model_arch": "rakun",
               "score": 0.095},
              {"entity_type": "Teemamärksõnad",
               "keyword": "holiday",
               "model_arch": "rakun",
               "score": 0.071},
              {"entity_type": "Teemamärksõnad",
               "keyword": "also",
               "model_arch": "rakun",
               "score": 0.042},
              {"entity_type": "Teemamärksõnad",
               "keyword": "swing",
               "model_arch": "rakun",
               "score": 0.038},
              {"count": 4,
               "entity_type": "Kohamärksõnad",
               "keyword": "Estonia",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 14,
               "entity_type": "Ajutine kollektiiv või sündmus",
               "keyword": "Easter Sunday",
               "method": "gliner",
               "model_arch": "ner",
               "score": 1.0},
              {"entity_type": "UDK Rahvusbibliograafia",
               "keyword": "39",
               "model_arch": "omikuji",
               "score": 0.76},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "ETNOLOOGIA. KULTUURIANTROPOLOOGIA",
               "model_arch": "omikuji",
               "score": 1.0},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "RELIGIOON. TEOLOOGIA. ESOTEERIKA",
               "model_arch": "omikuji",
               "score": 0.99},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "KODUMAJANDUS. TOITLUSTUS. TOIDUAINETETÖÖSTUS. OLME",
               "model_arch": "omikuji",
               "score": 0.911}]}
```

</details>

#### Russian input text

```python
from rara_subject_indexer.rara_indexer import RaraSubjectIndexer
from pprint import pprint

# If this is your first usage, download relevant models:
# NB! This has to be done only once!
# RaraSubjectIndexer.download_resources()

# Initialize the instance with default configuration
rara_indexer = RaraSubjectIndexer()

subject_indices = rara_indexer.apply_indexers(text=TEXT_RU)
pprint(subject_indices)
```

<details><summary>Output</summary>
    
`InvalidLanguageException: The text appears to be in language 'ru', which is not supported. Supported languages are: ['et', 'en'].`

</details>

### Modify thresholds


```python
from rara_subject_indexer.rara_indexer import RaraSubjectIndexer
from pprint import pprint

# If this is your first usage, download relevant models:
# NB! This has to be done only once!
RaraSubjectIndexer.download_resources()

# Initialize the instance with default configuration
rara_indexer = RaraSubjectIndexer()

# Change ensemble strategy for NER-based methods

ner_config = {"ensemble_strategy": "union"}

# Change min_score threshold for 
# keyword_type="Teemamärksõnad", method = "rakun"
threshold_config = {
    "Teemamärksõnad": {
        "rakun": {"min_score": 0.02}
    }
}

# max_count and min_score will overwrite
# thresholds for all keyword types in the default
# configuration, which are not specified
# with threshold_config

subject_indices = rara_indexer.apply_indexers(
    text=TEXT_ET,
    threshold_config=threshold_config,
    max_count=10,
    min_score=0.1,
    ner_config=ner_config
)
pprint(subject_indices)
```

<details><summary>Output</summary>
    
```json
{"durations": [{"duration": 0.03303,
                "keyword_type": "Teemamärksõnad",
                "model_arch": "omikuji"},
               {"duration": 1.79884,
                "keyword_type": "Teemamärksõnad",
                "model_arch": "rakun"},
               {"duration": 0.00897,
                "keyword_type": "Ajamärksõnad",
                "model_arch": "omikuji"},
               {"duration": 0.01052,
                "keyword_type": "Vormimärksõnad",
                "model_arch": "omikuji"},
               {"duration": 0.00057,
                "keyword_type": "NER",
                "model_arch": "ner"},
               {"duration": 0.0082,
                "keyword_type": "UDK Rahvusbibliograafia",
                "model_arch": "omikuji"},
               {"duration": 0.01001,
                "keyword_type": "UDC Summary",
                "model_arch": "omikuji"},
               {"duration": 0.00709,
                "keyword_type": "Valdkonnamärksõnad",
                "model_arch": "omikuji"}],
 "keywords": [{"entity_type": "Teemamärksõnad",
               "keyword": "filmid (teosed)",
               "model_arch": "omikuji",
               "score": 0.979},
              {"entity_type": "Teemamärksõnad",
               "keyword": "mängufilmid",
               "model_arch": "omikuji",
               "score": 0.573},
              {"entity_type": "Teemamärksõnad",
               "keyword": "filmiauhinnad",
               "model_arch": "omikuji",
               "score": 0.164},
              {"entity_type": "Teemamärksõnad",
               "keyword": "film",
               "model_arch": "rakun",
               "score": 0.32},
              {"entity_type": "Teemamärksõnad",
               "keyword": "ameeriklane",
               "model_arch": "rakun",
               "score": 0.039},
              {"entity_type": "Teemamärksõnad",
               "keyword": "metsatulekahju",
               "model_arch": "rakun",
               "score": 0.025},
              {"entity_type": "Teemamärksõnad",
               "keyword": "kostüümidisain",
               "model_arch": "rakun",
               "score": 0.025},
              {"entity_type": "Teemamärksõnad",
               "keyword": "austusavaldus",
               "model_arch": "rakun",
               "score": 0.023},
              {"entity_type": "Vormimärksõnad",
               "keyword": "filmiarvustused",
               "model_arch": "omikuji",
               "score": 0.905},
              {"entity_type": "Vormimärksõnad",
               "keyword": "e-raamatud",
               "model_arch": "omikuji",
               "score": 0.104},
              {"count": 12,
               "entity_type": "Isikunimi",
               "keyword": "Emilia Perez",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 3,
               "entity_type": "Isikunimi",
               "keyword": "Sean Baker",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 0.25},
              {"count": 3,
               "entity_type": "Isikunimi",
               "keyword": "Conan O'Brien",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 0.25},
              {"count": 3,
               "entity_type": "Kollektiivi nimi",
               "keyword": "Läti",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 3,
               "entity_type": "Kollektiivi nimi",
               "keyword": "Anora",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 4,
               "entity_type": "Kohamärksõnad",
               "keyword": "Los Angeleses",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 4,
               "entity_type": "Kohamärksõnad",
               "keyword": "Los",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 3,
               "entity_type": "Kohamärksõnad",
               "keyword": "Läti",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 0.75},
              {"count": 3,
               "entity_type": "Kohamärksõnad",
               "keyword": "Angeleses",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 0.75},
              {"count": 3,
               "entity_type": "Kohamärksõnad",
               "keyword": "Ameerika",
               "method": "ner_ensemble",
               "model_arch": "ner",
               "score": 0.75},
              {"count": 5,
               "entity_type": "Teose pealkiri",
               "keyword": "Wicked",
               "method": "gliner",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 5,
               "entity_type": "Teose pealkiri",
               "keyword": "Brutalist",
               "method": "gliner",
               "model_arch": "ner",
               "score": 1.0},
              {"count": 4,
               "entity_type": "Teose pealkiri",
               "keyword": "Anora",
               "method": "gliner",
               "model_arch": "ner",
               "score": 0.8},
              {"count": 3,
               "entity_type": "Teose pealkiri",
               "keyword": "Nosferatu",
               "method": "gliner",
               "model_arch": "ner",
               "score": 0.6},
              {"count": 3,
               "entity_type": "Teose pealkiri",
               "keyword": "Vooluga kaasa",
               "method": "gliner",
               "model_arch": "ner",
               "score": 0.6},
              {"entity_type": "UDK Rahvusbibliograafia",
               "keyword": "791",
               "model_arch": "omikuji",
               "score": 1.0},
              {"entity_type": "UDC Summary",
               "keyword": "821.111",
               "model_arch": "omikuji",
               "score": 0.156},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "FOTOGRAAFIA. FILM. KINO",
               "model_arch": "omikuji",
               "score": 1.0},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "KOHANIMED",
               "model_arch": "omikuji",
               "score": 0.944},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "AJAKIRJANDUS. KOMMUNIKATSIOON. MEEDIA. REKLAAM",
               "model_arch": "omikuji",
               "score": 0.449},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "TÖÖTINGIMUSED. TÖÖHÕIVE. AMETID",
               "model_arch": "omikuji",
               "score": 0.324},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "INFORMAATIKA. INFOTEHNOLOOGIA. AUTOMAATIKA",
               "model_arch": "omikuji",
               "score": 0.181},
              {"entity_type": "Valdkonnamärksõnad",
               "keyword": "TEATER. TANTS",
               "model_arch": "omikuji",
               "score": 0.154}]}    
```
</details>
    

</details>