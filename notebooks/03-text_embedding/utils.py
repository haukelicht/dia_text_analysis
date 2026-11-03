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


def load_encoder(model_id: str, **kwargs):
    """Load the course encoder from its local cache; no download during class."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_ID, device='cpu', **kwargs)


def load_triplet(number):
    """Return original A/B/C texts without scores or proposed selection labels."""
    table = pd.read_csv(DATA / 'intro_triplets.csv')
    row = table.loc[table.triplet.eq(number)].iloc[0]
    return pd.DataFrame({'text': [row.anchor_text, row.b_text, row.c_text]}, index=['A', 'B', 'C'])


def clustering_representation(embeddings):
    """Fixed teaching reduction: 10D UMAP, cosine, 15 neighbors, min_dist=0, seed 42."""
    from umap import UMAP
    return UMAP(n_components=10, n_neighbors=15, min_dist=0.0, metric='cosine', random_state=42, n_jobs=1).fit_transform(embeddings)


def cluster_sentences(coordinates, minimum_group_size=8):
    """External HDBSCAN: min_samples=2, Euclidean, eom, exact spanning tree."""
    from hdbscan import HDBSCAN
    return HDBSCAN(min_cluster_size=minimum_group_size, min_samples=2,
                   metric='euclidean', cluster_selection_method='eom',
                   approx_min_span_tree=False, core_dist_n_jobs=1).fit_predict(coordinates)


def display_coordinates(embeddings):
    """Separate 2D display, not the representation used to fit HDBSCAN."""
    from umap import UMAP
    return UMAP(n_components=2, n_neighbors=15, min_dist=0.1,
                metric='cosine', random_state=42, n_jobs=1).fit_transform(embeddings)


def plot_groups(coordinates, labels=None, title='Sentence map'):
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
