import io
import base64
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")


def pca_scatter_base64(embedding: np.ndarray, labels: List[int]) -> str:
    plt.figure(figsize=(6, 5))
    unique = sorted(set(labels))
    palette = sns.color_palette("Set2", n_colors=len(unique))
    for cid, color in zip(unique, palette):
        mask = np.array(labels) == cid
        plt.scatter(embedding[mask, 0], embedding[mask, 1], label=f"Cluster {cid}", s=25, alpha=0.8, color=color)
    plt.title("PCA Projection of Student Features")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend(loc="best")
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    return b64
