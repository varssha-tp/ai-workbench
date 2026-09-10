import numpy as np
import pandas as pd


def to_records(df: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame to JSON-safe records (no inf/NaN, which break JSON encoding)."""
    clean = df.replace([np.inf, -np.inf], np.nan)
    clean = clean.astype(object).where(pd.notnull(clean), None)
    return clean.to_dict("records")
