import pandas as pd
from ..utils.logger import logger


def validate_quality(df_map: dict) -> dict:
    issues = {}
    for name, df in df_map.items():
        missing = df.isna().sum().sum()
        duplicates = df.duplicated().sum() if not df.empty else 0
        issues[name] = {
            'rows': int(len(df)),
            'missing_values': int(missing),
            'duplicate_rows': int(duplicates),
        }
    logger.info(f"Validation summary: {issues}")
    return issues