# Executive tweets

This dataset contains **71,924 Twitter posts from 23 leader identifiers in 13
European countries**, dated **4 January 2010 to 20 June 2023**. Each row is one
post, identified by a unique `tweet_uid`. The file includes the original text,
an English text version, country and language information, engagement counts,
and model predictions that can help select material for a term paper.

The accompanying `leaders.csv` contains the **23 leaders represented in these
tweets**, with their names, account handles, and offices. Join the files on
`leader_id` to identify the author of each post.

The corpus is a prepared subset of Juan S. Gómez Cruces's Executive Social Media
Database. The course preparation adds English text versions and the policy/CAP
model predictions described below. [Original dataset repository](https://github.com/juangomezcruces/Executive-Social-Media-Database)

The preparation selected European countries and the language
codes listed below. It retained posts with a missing tweet-type value and
excluded those marked as replies, those with a reply target, and those beginning
with `RT @`. These rules produced the 71,924 posts in this file. They operationalize
standalone posts using the available metadata. Some unrecognized quote posts
may remain.

## Reading the file in Python

The file uses Apache Feather format. The example requires pandas and pyarrow,
which are available in the course's neural environment. Run it from the course
repository root.

```python
from pathlib import Path

import pandas as pd

folder = Path("data/unlabeled/executive_tweets")
tweets = pd.read_feather(folder / "tweets.feather")

print(tweets.shape)
print(tweets[["country", "lang", "text", "is_policy", "cap_topic"]].head())

# Example selection using the policy model's prediction.
policy_tweets = tweets.loc[tweets["is_policy"]].copy()

# CAP labels are populated for part of the file.
cap_labeled = tweets.loc[tweets["cap_topic"].notna()].copy()
```

## Adding leader information

`leaders.csv` contains one row per `leader_id` in the course tweet file. This
example continues from the preceding code and adds the leader's name, account
handle, and office to each tweet.

```python
leaders = pd.read_csv(folder / "leaders.csv")
leader_metadata = leaders[["leader_id", "name", "handle", "office"]]
tweets_with_leaders = tweets.merge(
    leader_metadata, on="leader_id", how="left", validate="many_to_one"
)

print(tweets_with_leaders[["name", "handle", "office", "text"]].head())
```

All 71,924 tweets match a leader entry. The names and handles come from the
source database, which may record a historical account handle.

| Columns in `leaders.csv` | Contents |
| --- | --- |
| `leader_id` | Unique key shared with the tweet file |
| `name`, `handle` | Leader's name and account handle |
| `country`, `country_iso3` | Country name and three-letter code |
| `office` | Office recorded for the leader in the source database |
| `n_tweets`, `first_tweet`, `last_tweet` | Number of posts and collection window in the source dataset |
| `total_retweets`, `total_replies`, `total_likes`, `total_quotes`, `mean_engagement` | Engagement summaries from the source dataset |
| `source_id_reliable`, `has_sentiment` | Source-ID reliability and availability of source sentiment annotations |
| `populist`, `source_files` | Additional source classification and original filenames |

The counts, date windows, and engagement summaries in this table refer to the
source dataset before the course filters. Calculate summaries from
`tweets.feather` when describing the course subset. `office` identifies the
position associated with a leader, and the table provides no term dates for
checking whether each post falls within that leader's time in office.
`populist` is missing for all 23 selected leaders.

## Original and English texts

`text` contains the original post and `text_en` its English version. Both are
populated throughout the file. For all 16,872 posts marked as English, the two
text columns are identical. The preparation includes machine translation into
English for non-English material. The translation model and its version are
not recorded in the file. The `lang` column identifies the original text's
language using two-letter codes, including `no` for Norwegian.

## Country coverage

| Country | Tweets | Share |
| --- | ---: | ---: |
| Italy | 15,040 | 20.9% |
| Czech Republic | 8,942 | 12.4% |
| Belgium | 7,306 | 10.2% |
| Ireland | 6,402 | 8.9% |
| United Kingdom | 6,194 | 8.6% |
| Spain | 5,546 | 7.7% |
| Netherlands | 4,870 | 6.8% |
| France | 4,440 | 6.2% |
| Poland | 3,225 | 4.5% |
| Germany | 3,150 | 4.4% |
| Norway | 2,940 | 4.1% |
| Switzerland | 2,442 | 3.4% |
| Austria | 1,427 | 2.0% |

## Original languages

| Language | Tweets | Share |
| --- | ---: | ---: |
| English (`en`) | 16,872 | 23.5% |
| Italian (`it`) | 15,094 | 21.0% |
| Czech (`cs`) | 8,691 | 12.1% |
| Dutch (`nl`) | 8,549 | 11.9% |
| French (`fr`) | 6,495 | 9.0% |
| Spanish (`es`) | 5,544 | 7.7% |
| German (`de`) | 5,029 | 7.0% |
| Polish (`pl`) | 2,905 | 4.0% |
| Norwegian (`no`) | 2,414 | 3.4% |
| Danish (`da`) | 259 | 0.4% |
| Portuguese (`pt`) | 30 | <0.1% |
| Swedish (`sv`) | 19 | <0.1% |
| Finnish (`fi`) | 13 | <0.1% |
| Hungarian (`hu`) | 10 | <0.1% |

Country and language are separate attributes. A leader may post in several
languages, and the same language appears in multiple countries. The tables count
posts in this prepared file. Posting frequency and collection coverage influence
the distributions.

## Coverage over time

| Year | Tweets | Share |
| --- | ---: | ---: |
| 2010 | 696 | 1.0% |
| 2011 | 1,602 | 2.2% |
| 2012 | 2,002 | 2.8% |
| 2013 | 2,788 | 3.9% |
| 2014 | 3,513 | 4.9% |
| 2015 | 4,327 | 6.0% |
| 2016 | 4,279 | 5.9% |
| 2017 | 4,036 | 5.6% |
| 2018 | 8,352 | 11.6% |
| 2019 | 9,567 | 13.3% |
| 2020 | 8,649 | 12.0% |
| 2021 | 9,024 | 12.5% |
| 2022 | 9,294 | 12.9% |
| 2023 | 3,795 | 5.3% |

The 2023 coverage ends on 20 June. Countries and accounts have different posting
histories and collection coverage, so annual counts alone cannot establish changes
in leaders' communication activity.

## Model-based classifications

Two classification steps were used in the preparation. The policy classifier
identifies policy-related posts. The CAP classifier assigns policy-topic labels.
The intended workflow applies the CAP classifier to the policy-related subset.

**These columns contain model predictions.** Classification errors and ambiguous
cases are possible. Use them primarily to subset or prefilter the corpus for
further analysis, with substantive interpretation and reading of the selected
texts. A prediction score expresses the model's output and may be poorly
calibrated as a probability of correctness.

| Column | Meaning |
| --- | --- |
| `is_policy` | Boolean prediction of whether the post is policy-related |
| `is_policy_prob` | Model score for the policy-related class, between 0 and 1 |
| `cap_topic` | Predicted CAP topic label, where available |
| `cap_topic_prob` | Score accompanying the predicted CAP label, where available |

The policy model used in the preparation is `mljn/policy-vs-other-v2`. The exact
CAP model identifier, model revisions, and inference settings are not stored in
this file. Consult the model documentation when interpreting the policy label.
[Policy classifier model card](https://huggingface.co/mljn/policy-vs-other-v2)

The policy classifier marks **42,936 posts (59.7%)** as policy-related and
**28,988 (40.3%)** as other content. In the supplied file, CAP predictions are
present for **4,600 posts (6.4%)**. Both CAP columns are missing for the other
**67,324 posts**. The observed coverage crosses both policy predictions.

| Policy prediction | CAP label present | CAP label missing | Total |
| --- | ---: | ---: | ---: |
| `True` | 2,851 | 40,085 | 42,936 |
| `False` | 1,749 | 27,239 | 28,988 |
| Total | 4,600 | 67,324 | 71,924 |

This pattern differs from the intended workflow described above. The file alone
cannot establish whether it results from an incomplete classification run or
from how predictions were joined to the tweets. Treat missing CAP labels as
unavailable predictions. The populated labels also include `No Policy Content`
for 2,083 posts. That is an explicit predicted class. It is separate from a
missing CAP label.

## Other columns and missing values

| Columns | Contents |
| --- | --- |
| `tweet_uid` | Unique post identifier in the prepared dataset |
| `leader_id` | Leader/account identifier as supplied by the source |
| `country`, `country_iso3` | Country name and three-letter ISO country code |
| `created_at`, `date` | UTC timestamp and calendar date |
| `lang` | Original language code |
| `text`, `text_en` | Original post and English version |
| `retweet_count`, `reply_count`, `like_count`, `quote_count` | Engagement counts supplied by the source |
| `engagement` | Sum of these four engagement counts |
| `is_deleted` | Deletion indicator, missing for every row in this file |
| `possibly_sensitive` | Sensitivity flag supplied by the source |
| `source_tweet_id`, `source_id_reliable` | Source post identifier and its reliability flag |
| `source_file` | Original source filename retained during preparation |

`source_tweet_id` is missing in 20,672 rows. Apart from this column, `is_deleted`,
and the two CAP columns, all fields are populated. Engagement counts describe
the source data's recorded values. The file contains no collection timestamp
for interpreting them as counts at a common observation time.

## Data source and citation

Please cite the original Executive Social Media Database when using this course
subset, and describe the course-specific selection, translation, and model
classification steps in your methods section.

Gómez Cruces, Juan S. (n.d.). *Executive Social Media Database* [Dataset].
GitHub. [Repository](https://github.com/juangomezcruces/Executive-Social-Media-Database)

The repository asks users to include the release tag they used. The release tag
of the source file used for this course subset is not recorded in the supplied
file. Add it to the citation if it can be established from the original download.
[Source citation guidance](https://github.com/juangomezcruces/Executive-Social-Media-Database#licence-and-reuse)

The accompanying leader metadata was downloaded through the official
`leaders_tweets` Python package on 18 November 2026 from **release v2.0.0**.
The saved `leaders.csv` retains only entries matching the course tweet file.
When using this table, cite Gómez Cruces's dataset above with release v2.0.0.

The statistics in this README were calculated from the supplied `tweets.feather`
on 18 November 2026.
