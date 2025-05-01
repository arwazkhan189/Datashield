import pandas as pd
from collections import defaultdict


def apply_anonymization(original_df, record_chunks, sensitive_columns):
    """
    Reconstruct an anonymized version of the original DataFrame
    using record_chunks generated from the kmt-anonymity algorithm.

    Params:
    - original_df: Original DataFrame
    - record_chunks: List of sets of non-sensitive terms that passed km-anonymity
    - sensitive_columns: List of column names to preserve as-is (not anonymized)

    Returns:
    - anonymized_df: A DataFrame with generalized values
    """
    # Make a copy of the original
    df = original_df.copy()

    # Normalize column names
    df.columns = [col.strip().lower() for col in df.columns]
    sensitive_columns = [col.strip().lower() for col in sensitive_columns]

    # Flatten all record_chunks into a single safe term set
    safe_terms = set()
    for chunk in record_chunks:
        safe_terms.update(chunk)

    # Convert all cells to string for uniform comparison
    for col in df.columns:
        df[col] = df[col].astype(str)

    # Mask non-sensitive terms not in safe list
    for col in df.columns:
        if col not in sensitive_columns:
            df[col] = df[col].apply(lambda val: val if val in safe_terms else "***")

    return df
