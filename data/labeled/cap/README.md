# CAP party manifestos and platforms

These course files contain English-language text segments from UK party
manifestos and US presidential party platforms, with their original topic
assignments in the course data. Each row is a coded text unit. Some units are
quasi-sentences, such as a clause within a longer sentence.

- [sentences_gbr.csv](sentences_gbr.csv) contains 36,255 UK text units.
- [sentences_usa.csv](sentences_usa.csv) contains 39,809 US text units.
- [cap_topic_labels.csv](cap_topic_labels.csv) maps major topic codes to labels.
- [cap_subtopic_labels.csv](cap_subtopic_labels.csv) maps subtopic codes to labels
  and includes each subtopic's parent major topic in `codebook_cap_topic`.

## Coverage

| Country | Party as recorded | Elections covered | Text units |
| --- | --- | --- | ---: |
| UK | Conservative Party | All eight UK elections in the files, 1983–2015 | 11,426 |
| UK | Labour Party | All eight UK elections in the files, 1983–2015 | 11,490 |
| UK | Liberal Democrat | All eight UK elections in the files, 1983–2015 | 11,959 |
| UK | UKIP | 2015 only | 1,380 |
| USA | Democratic Party | Every four years, 1948–2024 (20 elections) | 19,653 |
| USA | Republican Party | Every four years, 1948–2024, with a gap in 2020 (19 elections) | 20,156 |

The eight UK election years are 1983, 1987, 1992, 1997, 2001, 2005, 2010,
and 2015. The country files overlap in calendar time from 1983 to 2015,
with different election years. The counts describe the files supplied for the
course. For source documentation and citations, see the [CAP dataset
catalogue](https://www.comparativeagendas.net/datasets_codebooks),
the [UK manifesto codebook](https://minio.la.utexas.edu/compagendas/codebookfiles/UK_manifestos_codebook_v1.1.pdf)
and the [US party platform codebook](https://minio.la.utexas.edu/compagendas/codebookfiles/PartyPlatformsCodebookJuly2016.pdf).

## Key columns

| Column | Meaning |
| --- | --- |
| `text_id`, `text` | Text-unit identifier and English text |
| `country_iso3c` | Country code (`GBR` or `USA`) |
| `party_code`, `party_name` | Party identifier and name as recorded in the file |
| `year`, `election_date` | Election year and date |
| `cap_topic`, `cap_subtopic` | Numeric codes as supplied in the course files |

Both CAP code columns are populated in every row. For document-level grouping,
use `country_iso3c`, `party_code`, and `election_date` together.
The `manifesto_id` column is empty in both CSVs.

## Join the CAP labels in Python

Run this example from the course repository root with pandas. The two left
joins preserve each text unit alongside its original numeric codes.

```python
from pathlib import Path

import pandas as pd

folder = Path("data/labeled/cap")
sentences = pd.concat(
    [
        pd.read_csv(folder / "sentences_gbr.csv"),
        pd.read_csv(folder / "sentences_usa.csv"),
    ],
    ignore_index=True,
)
topics = pd.read_csv(folder / "cap_topic_labels.csv")
subtopics = pd.read_csv(folder / "cap_subtopic_labels.csv")

labeled = sentences.merge(
    topics, on="cap_topic", how="left", validate="many_to_one"
).merge(
    subtopics, on="cap_subtopic", how="left", validate="many_to_one"
)

print(labeled[["text", "cap_topic_label", "cap_subtopic_label"]].head())
```

The lookup tables reproduce the labels listed in the CAP Master Topics Codebook
v1.1. Cite the Master Codebook when using the labels. CAP coding variables are
distributed under CC BY-NC-SA 4.0. [Master Codebook](https://www.comparativeagendas.net/pages/master-codebook) ·
[Citation guidance](https://www.comparativeagendas.net/pages/How-to-cite) ·
[CAP terms](https://www.comparativeagendas.net/pages/Copyright-and-Legal)

Codes absent from the Master Codebook have a missing label after the join.
This affects both labels for 3,649 UK rows (code `0`). In the US file,
2,167 rows have an unmatched major topic and 2,372 have an unmatched subtopic,
including records with codes `0` or `-555`. A further 11 rows across the two
files have a recognized subtopic whose `codebook_cap_topic` differs from the
recorded `cap_topic`. Review these rows before using both levels of the
hierarchy in the same analysis. Consult the source documentation when
interpreting country-specific coding. For example, the UK codebook documents
a narrower use of subtopic `1910` for the 2015 manifestos.

## Optional foreign-policy crosswalk for Session 2

### Purpose

`cap_subtopic_policy_issue_crosswalk.tsv` maps selected Comparative Agendas
Project (CAP) subtopics to the policy-issue classifications used in Session 2
of the course. It supports selecting real policy statements and adapting CAP
labels to the course's foreign-policy scope.

The course uses four substantive classifications:

- Security/defence
- Diplomacy
- International trade
- Aid

It also uses **Other/unclear** for foreign-policy content outside these
categories or unresolved cases, and **Not foreign policy** for statements
without a substantive cross-border policy issue.

This is a proposed course-specific crosswalk, not an official CAP classification
or a dataset of annotated statements. CAP topic codes identify policy subjects;
they do not always establish whether a statement meets the course's scope or
which course label applies.

### File structure

The file is a UTF-8, tab-separated table with a header row and one row per CAP
subtopic. It contains 41 unique subtopics: all subtopics in main topics 16
(Defense), 18 (Foreign Trade), and 19 (International Affairs), plus selected
extensions from Agriculture (401), Immigration (900), and Technology (1705).
It is not a complete mapping of the CAP codebook.

| Column | Meaning |
| --- | --- |
| `cap_major_topic_code` | CAP main-topic identifier. |
| `cap_major_topic_name` | CAP main-topic name. |
| `cap_subtopic_code` | CAP subtopic identifier; the unique key for joining to CAP-coded data. |
| `cap_subtopic_name` | CAP subtopic name. |
| `proposed_policy_issue_classification` | Suggested course label, subject to the mapping status and coding notes. |
| `mapping_status` | Whether the proposed label can be used directly, requires a condition, or requires case-by-case review. |
| `coding_notes` | Scope conditions, category-priority rules, and alternative labels for particular statements. |

Treat topic codes as identifiers rather than quantities. When joining data,
ensure the subtopic-code columns use the same type in both tables.

### Mapping status and application

- **`direct`**: the subtopic generally corresponds to the proposed course label.
  Apply the course scope and dominant-issue rules to the statement as well.
- **`conditional`**: use the proposed label only when the statement satisfies
  the conditions in `coding_notes`; otherwise assign the indicated alternative
  or review the substantive issue.
- **`review`**: the code alone is insufficient. Read the statement and assign
  the course label from its content; the proposed label is a placeholder for
  review, not a gold annotation.

Classify by the dominant substantive object rather than the instrument. For
example, trade negotiations remain International trade, while military aid and
arms-transfer controls take Security/defence rather than Aid or International
trade. Aid covers civilian development assistance and humanitarian relief
abroad.

A foreign-country reference alone does not make a statement foreign policy.
Domestic defence administration can therefore take Not foreign policy even
though its CAP main topic is Defense. Similarly, developing-country and
international-finance codes do not automatically imply Aid.

No row assigns Not foreign policy as its proposed label: the file contains
candidate foreign-policy subtopics. Exclusions are described in `coding_notes`
and must be applied to individual statements. Subtopics absent from this file
are unmapped, not automatically Not foreign policy.

Preserve the original CAP code, the proposed label, and the final statement-level
classification separately. Record uncertainty in a separate field so that an
uncertain decision can be distinguished from substantive content outside the
four categories. Check that the source dataset uses master subtopic codes rather
than country-specific or historical codes before joining.

### US data: PAP versus CAP columns

The US data shown for the course contain both US-specific Policy Agendas
Project (PAP) codes and harmonized Comparative Agendas Project (CAP) codes:

| Columns in the US file | Coding scheme | Use |
| --- | --- | --- |
| `pap_majortopic`, `pap_subtopic` | US-specific PAP codes | Preserve as the original country-specific coding. |
| `majortopic`, `subtopic` | Harmonized CAP codes | Use for the course crosswalk and US–UK comparisons. |

The [US CAP dataset documentation](https://www.comparativeagendas.net/project/us/datasets)
states that US datasets contain both coding schemes and recommends CAP codes
for comparisons across projects and countries.

Join the US file's **`subtopic`** column to the crosswalk's
**`cap_subtopic_code`**. Use `majortopic` for comparisons at the main-topic level.
Do not apply historical PAP-to-CAP conversions again to these harmonized
columns. Keep the PAP columns alongside them for provenance and checking.

#### Special and unmatched values

The displayed US data include `majortopic = 0` and `subtopic = -555`. These
values are outside the substantive master-topic crosswalk. Their precise
meaning must be checked against the codebook for the specific party-platform
dataset and release; it has not been verified for the displayed file.

Preserve these values and flag them for separate handling. A failed crosswalk
join, a missing code, or a special code must not automatically receive
**Not foreign policy**: non-policy content, missing coding, an unmapped
substantive issue, and domestic policy are different cases.

For UK data, verify the coding columns and any remaining dataset-specific
extensions against the relevant release's codebook before applying the same
crosswalk. The US column names alone do not establish the scheme used in a UK
file.

### Sources

- [CAP Master Codebook](https://www.comparativeagendas.net/pages/master-codebook):
  source of the topic identifiers and names used in the crosswalk; consulted
  October 7, 2026.
- [Session 2 instructor exercise guide](../../../slides/02-computational_text_analysis/exercises_notes.md):
  source of the course labels, scope definition, and substantive-object rule.
- [US CAP datasets](https://www.comparativeagendas.net/project/us/datasets):
  documentation distinguishing PAP and CAP codes and recommending CAP for
  cross-country comparisons; consulted October 7, 2026. Column names and special
  values above reflect the US data screenshot supplied for the course.

The proposed mappings and coding notes adapt these sources for teaching and
require statement-level review where indicated.
