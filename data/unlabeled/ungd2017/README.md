# UN General Debate speeches, 2017

This corpus contains **196 English-language speeches** from the **72nd session
of the United Nations General Assembly in 2017**, prepared from
`data_corpus_ungd2017` in the R package `quanteda.corpora`. The course files
provide full speeches, **4,626 paragraphs**, and **16,952 sentences**, together
with speech metadata and sentence-level climate-change predictions.

The classified sentence file includes the full sentence corpus. Its model labels
can help select climate-related material for further analysis, while the
segmented files make it possible to recover the surrounding paragraph or speech.

## Files

| File | Rows | Contents |
| --- | ---: | --- |
| `speech_sentences_climate_change.csv` | 16,952 | Sentences, IDs, country/session/year, and climate predictions |
| `metadata.csv` | 196 | Country/delegation metadata, continent, GDP, and GDP per capita |
| `segmented/speeches.csv` | 196 | Complete speech texts, IDs, and all source document metadata |
| `segmented/paragraphs.csv` | 4,626 | Paragraph texts with speech IDs and paragraph numbers |
| `segmented/sentences.csv` | 16,952 | Sentence texts with speech and paragraph IDs and sentence numbers |
| `data_corpus_ungd2017.rda` | 196 speeches | Original R corpus object used for preparation |
| `predict.py` | — | Preparation script for the sentence classifications |

The CSV files can be read directly in Python with pandas. All speeches are from
2017 and session 72. Countries/delegations appear once each at the speech level.
The geographic coverage includes the European Union, Palestine, and the Holy See
(recorded as Vatican City), alongside UN member states. Country and continent
names follow the supplied metadata.

## Geographic coverage

| Continent | Speeches | Paragraphs | Sentences | Predicted climate sentences |
| --- | ---: | ---: | ---: | ---: |
| Africa | 54 | 1,153 | 3,726 | 198 |
| Americas | 35 | 964 | 3,471 | 191 |
| Asia | 48 | 1,194 | 4,504 | 112 |
| Europe | 45 | 989 | 4,003 | 140 |
| Oceania | 14 | 326 | 1,248 | 164 |

Counts reflect the supplied texts and automatic segmentation. Longer speeches
contribute more sentences to the sentence-level corpus. The continent column
uses the source's grouping, including a combined Americas category. There is one
English text version per speech. The files do not identify the language in which
each speech was originally delivered.

## Climate-change classification

The model `mljn/unga-climate-classifier` assigns a label to each sentence. It is
based on DeBERTa-v3-base and was trained on 5,600 annotated English sentences
from the UN General Assembly corpus. See the model card for the training task
and evaluation. [Model documentation](https://huggingface.co/mljn/unga-climate-classifier)

| Prediction | Sentences | Share of all sentences |
| --- | ---: | ---: |
| `climate` | 805 | 4.7% |
| `other` | 16,147 | 95.3% |
| Total | 16,952 | 100.0% |

At least one sentence is predicted as `climate` in **163 of 196 speeches** and
**474 of 4,626 paragraphs**. These counts describe model-selected material.

**The labels are model-based predictions.** They can support subsetting and
prefiltering for a term paper. Classification errors and ambiguous cases are
possible, so substantive interpretation should include reading the selected
texts and their context.

| Column | Meaning |
| --- | --- |
| `pred_label` | Predicted class, either `climate` or `other` |
| `pred_prob` | Model score for the class in `pred_label` |

For a row labeled `other`, `pred_prob` is the score for `other`. Select
climate-related rows by their label before applying a confidence threshold.
Model scores may be poorly calibrated as probabilities of correctness.

The supplied CSV contains `pred_label` and `pred_prob` **twice in its header**.
Both label copies and both score copies are identical throughout the file.
Pandas names the second pair `pred_label.1` and `pred_prob.1`. The example below
selects one copy of each prediction column when reading.

The supplied inference script uses batches of eight sentences and
`truncation="only_first"`. Inputs exceeding the model's input limit are
truncated during classification, while the exported `text` retains the complete
sentence. The model revision and number of truncated inputs are not recorded.

## Reading and selecting sentences in Python

Run this example from the course repository root. Only pandas is required to
read the CSVs.

```python
from pathlib import Path

import pandas as pd

folder = Path("data/unlabeled/ungd2017")
columns = [
    "speech_id", "paragraph_id", "sentence_id", "sentence_number", "text",
    "country_iso", "un_session", "year", "pred_label", "pred_prob",
]
sentences = pd.read_csv(
    folder / "speech_sentences_climate_change.csv", usecols=columns
)
speeches = pd.read_csv(folder / "segmented/speeches.csv")
paragraphs = pd.read_csv(folder / "segmented/paragraphs.csv")

# Add the country name, continent, and economic metadata to each sentence.
speech_metadata = speeches[
    ["speech_id", "country", "continent", "gdp", "gdp_per_capita"]
]
sentences = sentences.merge(
    speech_metadata, on="speech_id", how="left", validate="many_to_one"
)
climate_sentences = sentences.loc[sentences["pred_label"].eq("climate")].copy()
print(climate_sentences[["country", "text", "pred_prob"]].head())
```

To inspect entire paragraphs containing at least one predicted climate sentence,
continue with the following code. Each selected paragraph appears once, including
its sentences that received `other` predictions.

```python
climate_paragraphs = paragraphs.loc[
    paragraphs["paragraph_id"].isin(climate_sentences["paragraph_id"])
].copy()
climate_paragraphs = climate_paragraphs.merge(
    speech_metadata, on="speech_id", how="left", validate="many_to_one"
)
print(climate_paragraphs[["country", "paragraph_number", "text"]].head())

# Recover complete speeches for additional context.
climate_speeches = speeches.loc[
    speeches["speech_id"].isin(climate_sentences["speech_id"])
].copy()
```

The raw sentence segmentation is also available without predictions via
`pd.read_csv(folder / "segmented/sentences.csv")`.

## Segmentation and identifiers

Paragraphs were created by splitting speech texts at newline breaks, trimming
outer whitespace, and omitting empty lines. Sentences were split within each
paragraph using the English sentence-boundary rules in R's `stringi` package
(`locale="en@ss=standard"`). Automatic boundaries may require adjustment for an
individual analysis. The preparation script is available in the course repository.
[Segmentation script](../../../scripts/ungd2017/prepare.R)

| Column | Meaning and use |
| --- | --- |
| `speech_id` | Unique speech key, such as `speech_001`, shared by the segmented and classified files |
| `paragraph_id` | Unique paragraph key, such as `speech_001_p001`, shared by paragraphs and sentences |
| `sentence_id` | Unique sentence key, such as `speech_001_p001_s001`, shared by raw and classified sentences |
| `paragraph_number` | Paragraph position within its speech, beginning at 1 |
| `sentence_number` | Sentence position within its paragraph, beginning at 1 |
| `text` | Text of the unit represented by the row |

Use the IDs for joins. `sentence_number` restarts in each paragraph.
For ordering sentences within a speech, join `paragraph_number` from the paragraph
file and sort by `speech_id`, `paragraph_number`, and `sentence_number`.

## Speech metadata

| Column | Contents |
| --- | --- |
| `country_iso` | Country/delegation code as supplied by the source |
| `country` | Country/delegation name |
| `un_session`, `year` | UN General Assembly session (72) and year (2017) |
| `continent` | Source continent grouping |
| `gdp`, `gdp_per_capita` | Economic indicators retained from the source |
| `docname_`, `docid_`, `segid_` | Internal document identifiers retained from the R corpus in `speeches.csv` |

`country_iso` uses three-letter codes for most entries. The European Union is
recorded as `EC`. `metadata.csv` contains one row per country/delegation and
can be joined using `country_iso`, `un_session`, and `year`. For the segmented
files, `speech_id` connects directly to the full metadata in `speeches.csv`.

Both GDP columns are missing for nine delegations. Their units, reference year,
and economic-data source are not documented in these CSVs. Consult the original
corpus documentation before using these indicators in an analysis. All other
columns in the supplied CSVs are populated.

## Sources and citation

The speech texts and source metadata come from the UN General Debate corpus
as distributed in `quanteda.corpora`. Cite the original corpus when using the
texts and metadata. The original corpus article is Baturo, Alexander, Niheer
Dasandi, and Slava Mikhaylov (2017), “Understanding state preferences with text
as data: Introducing the UN General Debate corpus.”
[quanteda.corpora](https://github.com/quanteda/quanteda.corpora) ·
[Corpus article](https://doi.org/10.1177/2053168017712821)

For the climate classifier, cite Grossman, Emiliano, and Malo Jan (2025),
“Executive Climate Change Attention: Toward an Indicator of Comparative Climate
Change Attention,” as requested in the model card.
[Model card and citation](https://huggingface.co/mljn/unga-climate-classifier) ·
[Classifier article](https://doi.org/10.1162/glep.a.1)

The counts and file relationships in this README were checked against the
supplied files on 18 November 2026.
