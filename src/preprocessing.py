"""Data loading, cleaning, and RFM feature engineering for customer segmentation."""

from __future__ import annotations
import pandas as pd


def load_retail_data(csv_path: str) -> pd.DataFrame:
    """Load the Online Retail CSV."""
    return pd.read_csv(csv_path)


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw transaction data.

    Steps:
    - drop rows missing CustomerID
    - cast CustomerID to int
    - parse InvoiceDate
    - remove cancellations (InvoiceNo starts with 'C')
    - remove non-positive Quantity / UnitPrice
    - create TotalPrice
    """
    df_clean = df.copy()

    df_clean = df_clean.dropna(subset=["CustomerID"])
    df_clean["CustomerID"] = df_clean["CustomerID"].astype(int)
    df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])

    df_clean = df_clean[~df_clean["InvoiceNo"].astype(str).str.startswith("C")]
    df_clean = df_clean[df_clean["Quantity"] > 0]
    df_clean = df_clean[df_clean["UnitPrice"] > 0]

    df_clean["TotalPrice"] = df_clean["Quantity"] * df_clean["UnitPrice"]
    return df_clean


def build_rfm(df_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Build customer-level RFM table:
    - Recency: days since most recent purchase
    - Frequency: number of unique invoices
    - Monetary: total spend
    """
    snapshot_date = df_clean["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df_clean.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
        "InvoiceNo": "nunique",
        "TotalPrice": "sum",
    })

    rfm.columns = ["Recency", "Frequency", "Monetary"]
    return rfm.reset_index()
