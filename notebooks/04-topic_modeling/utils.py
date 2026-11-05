"""Supplied Block 2 mechanics. Research choices are documented in the lesson guide.

No reference categories are used for encoding, reduction, clustering or topics.
"""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'data/examples/cap_teaching'
RESULTS = ROOT / 'output/cap_teaching'
MODEL_ID = 'sentence-transformers/all-MiniLM-L6-v2'

def display_coordinates(embeddings):
    """Separate 2D display, not the representation used to fit HDBSCAN."""
    from umap import UMAP
    return UMAP(n_components=2, n_neighbors=15, min_dist=0.1,
                metric='cosine', random_state=42, n_jobs=1).fit_transform(embeddings)


def plot_clusters(coordinates, labels=None, title='Sentence map'):
    """Display arbitrary cluster numbers; labels never affect coordinates."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 6))
    if labels is None:
        ax.scatter(*np.asarray(coordinates).T, s=45, color='#777777')
    else:
        labels = np.asarray(labels)
        palette = plt.get_cmap('tab10')
        for group in sorted(set(labels)):
            mask = labels == group
            color = '#888888' if group == -1 else palette(int(group) % 10)
            ax.scatter(*np.asarray(coordinates)[mask].T, s=45, color=color,
                       marker='x' if group == -1 else 'o',
                       label=f'Group {group} (n={mask.sum()})' if group != -1 else f'Unassigned (n={mask.sum()})')
        ax.legend(frameon=False)
    ax.set_title(title)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.tight_layout()
    # Return one rich notebook display, without a second automatic inline copy.
    plt.close(fig)
    return fig



def load_prepared_embeddings(texts, filename):
    """Check exact original text and order before using a supplied cache."""
    saved = np.load(RESULTS / filename, allow_pickle=False)
    if saved['texts'].tolist() != list(texts):
        raise ValueError('Prepared embeddings do not match these texts in this order.')
    return saved['embeddings']


def get_bertopic_model(embedding_model, minimum_group_size=8, return_probabilities=False):    
    from sentence_transformers import SentenceTransformer
    from bertopic import BERTopic
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import CountVectorizer
    from umap import UMAP

    if embedding_model is None:
        pass
    elif embedding_model is str:
        embedding_model = SentenceTransformer(embedding_model)
    elif not isinstance(embedding_model, SentenceTransformer):
        raise ValueError('embedding_model must be a string or a SentenceTransformer instance.')
    
    reducer = UMAP(n_components=10, n_neighbors=15, min_dist=0, metric='cosine', random_state=42, n_jobs=1)
    clusterer = HDBSCAN(min_cluster_size=minimum_group_size, min_samples=2, metric='euclidean', cluster_selection_method='eom', approx_min_span_tree=False, prediction_data=True, core_dist_n_jobs=1)
    vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words='english', min_df=2)

    model = BERTopic(
        embedding_model=embedding_model,
        umap_model=reducer,
        hdbscan_model=clusterer,
        vectorizer_model=vectorizer,
        top_n_words=8, 
        calculate_probabilities=return_probabilities,
        nr_topics=None # avoid merging; no reference labels to guide merging
    )
    return model


def fit_topics(texts, embeddings, minimum_group_size=8):
    """Fit BERTopic with the same grouping rule as meeting 1; add c-TF-IDF.

    Supplied normalized MiniLM vectors; no labels, topic-count target or merging.
    Topic descriptions use English stopwords and unigrams/bigrams, min_df=1.
    min_df refers to concatenated topic documents, not original sentences.
    """
    if len(texts) != len(embeddings):
        raise ValueError('Texts and embeddings must contain the same number of rows.')

    model = get_bertopic_model(embedding_model=None, minimum_group_size=minimum_group_size)
    return model.fit_transform(list(texts), embeddings=np.asarray(embeddings).copy())


def topic_overview(model):
    """Counts and characteristic terms; no reference labels."""
    return model.get_topic_info()[['Topic', 'Count', 'Representation']].rename(columns={'Representation': 'Distinctive terms'})


def representative_documents(model, topic):
    """Actual model-selected representative texts, not a random sample."""
    return pd.DataFrame({'text': model.get_representative_docs(topic) or []})

