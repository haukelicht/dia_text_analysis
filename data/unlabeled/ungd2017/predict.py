import pandas as pd
from transformers import pipeline
from datasets import Dataset
from transformers.pipelines.pt_utils import KeyDataset
from tqdm import tqdm

classifier = pipeline("text-classification", model="mljn/unga-climate-classifier")

fp = 'segmented/sentences.csv'
df = pd.read_csv(fp)
ds = Dataset.from_pandas(df[['text']])

# 3. Wrap the dataset in KeyDataset and iterate with batch_size
classifications = []
for pred in tqdm(classifier(KeyDataset(ds, "text"), batch_size=8, truncation="only_first"), total=len(df)):
    classifications.append(pred)

classifications_df = pd.DataFrame(classifications)


meta_cols = ["speech_id", "country_iso", "un_session", "year", "country", "continent", "gdp", "gdp_per_capita"]
meta = pd.read_csv('segmented/speeches.csv', usecols=meta_cols).drop_duplicates()
meta[meta_cols[1:]].drop_duplicates().to_csv('metadata.csv', index=False)

df = df.merge(meta[["speech_id", "country_iso", "un_session", "year"]])

df = df.join(classifications_df)

df = df.rename(columns={'label': 'pred_label', 'score': 'pred_prob'})

df.to_csv('speech_sentences_climate_change.csv', index=False)

