"""Feature preprocessing, clustering, PCA, and segment labeling."""

from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


DEFAULT_SEGMENT_NAMES: Dict[int, str] = {
    0: "Recent Low-Value Customers",
    1: "High-Value Loyal Customers",
    2: "At-Risk Valuable Customers",
    3: "Inactive Customers",
}


def transform_and_scale_rfm(rfm: pd.DataFrame) -> Tuple[pd.DataFrame, StandardScaler]:
    """
    Log-transform skewed RFM features and standardize them for clustering.
    Returns a scaled DataFrame and fitted scaler.
    """
    rfm_log = rfm.copy()
    for col in ["Recency", "Frequency", "Monetary"]:
        rfm_log[col] = np.log1p(rfm_log[col])

    scaler = StandardScaler()
    scaled = scaler.fit_transform(rfm_log[["Recency", "Frequency", "Monetary"]])
    scaled_df = pd.DataFrame(scaled, columns=["Recency", "Frequency", "Monetary"])
    return scaled_df, scaler


def evaluate_kmeans_k_range(
    rfm_scaled: pd.DataFrame,
    k_values=range(2, 10),
    random_state: int = 42,
) -> pd.DataFrame:
    """Compute inertia and silhouette score across a range of k values."""
    rows = []
    for k in k_values:
        model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = model.fit_predict(rfm_scaled)
        rows.append({
            "k": k,
            "inertia": model.inertia_,
            "silhouette": silhouette_score(rfm_scaled, labels),
        })
    return pd.DataFrame(rows)


def fit_customer_segments(
    rfm: pd.DataFrame,
    rfm_scaled: pd.DataFrame,
    n_clusters: int = 4,
    random_state: int = 42,
    segment_names: Dict[int, str] | None = None,
) -> Tuple[pd.DataFrame, KMeans]:
    """Fit KMeans and attach cluster IDs and segment names."""
    if segment_names is None:
        segment_names = DEFAULT_SEGMENT_NAMES

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    out = rfm.copy()
    out["Cluster"] = model.fit_predict(rfm_scaled)
    out["Segment"] = out["Cluster"].map(segment_names)
    return out, model


def add_pca_projection(rfm: pd.DataFrame, rfm_scaled: pd.DataFrame) -> Tuple[pd.DataFrame, PCA]:
    """Add 2D PCA coordinates for visualization."""
    pca = PCA(n_components=2)
    coords = pca.fit_transform(rfm_scaled)

    out = rfm.copy()
    out["PC1"] = coords[:, 0]
    out["PC2"] = coords[:, 1]
    return out, pca


def cluster_profile(rfm_segmented: pd.DataFrame) -> pd.DataFrame:
    """Summarize segment-level size and mean RFM values."""
    return (
        rfm_segmented.groupby(["Cluster", "Segment"])
        .agg(
            Customers=("CustomerID", "count"),
            Recency=("Recency", "mean"),
            Frequency=("Frequency", "mean"),
            Monetary=("Monetary", "mean"),
            TotalRevenue=("Monetary", "sum"),
        )
        .reset_index()
        .sort_values("TotalRevenue", ascending=False)
    )
