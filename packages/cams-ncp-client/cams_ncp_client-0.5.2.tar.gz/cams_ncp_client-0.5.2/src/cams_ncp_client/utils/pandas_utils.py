import csv
import json
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Callable, Union
from typing import List, get_args, get_origin
from uuid import UUID

import pandas as pd
from pydantic import BaseModel
from vito.sas.air import logger


def read_small_csv(path_csv: Path, skipinitialspace=True, encoding='utf-8', **kwargs) -> pd.DataFrame:
    """
    Read a small CSV file into a pandas DataFrame, automatically detecting the delimiter.
    """
    return pd.read_csv(path_csv,
                     sep=None,  # Auto-detect separator
                     engine='python',
                     skipinitialspace=skipinitialspace,  # Skip spaces after delimiter
                     encoding=encoding, **kwargs)  # Specify encoding if needed


def read_csv(path_csv: Path, skipinitialspace=True, encoding='utf-8', **kwargs ) -> pd.DataFrame:
    """
    Read a CSV file into a pandas DataFrame, automatically detecting the delimiter.
    """
    sep = find_delimiter(path_csv)
    if sep == ' ':
        return pd.read_csv(path_csv, delim_whitespace=True, skipinitialspace=skipinitialspace, encoding=encoding, **kwargs)
    else :
        return pd.read_csv(path_csv, sep=sep, skipinitialspace=skipinitialspace, encoding=encoding, **kwargs)


def find_delimiter(path_csv: Path):
    sniffer = csv.Sniffer()
    with open(path_csv) as fp:
        delimiter = sniffer.sniff(fp.readline()).delimiter
    return delimiter


def pydantic_data_to_dataframe(data: List[BaseModel]) -> pd.DataFrame:
    """
    Converts a list of Pydantic BaseModel objects to a pandas DataFrame.

    Args:
        data: List of Pydantic BaseModel objects.

    Returns:
        A pandas DataFrame with appropriate dtypes for various field types.

    Raises:
        ValueError: If data is not a list of Pydantic models.
    """
    if not data:
        return pd.DataFrame()

    if not all(isinstance(item, BaseModel) for item in data):
        raise ValueError("All items must be Pydantic BaseModel instances")

    records = [item.model_dump(mode="python") for item in data]
    df = pd.DataFrame(records)

    model = type(data[0])
    field_types = model.model_fields

    for col, field in field_types.items():
        if col not in df.columns:
            continue

        raw_type = field.annotation
        origin = get_origin(raw_type)
        args = get_args(raw_type)
        actual_type = args[0] if origin is Union and type(None) in args else raw_type

        # if actual_type == int:
        #     df[col] = df[col].astype(int)
        # if actual_type == bool:
        #     df[col] = df[col].astype(bool)
        if actual_type == date:
            df[col] = pd.to_datetime(df[col]).dt.normalize()
        elif actual_type == datetime:
            # df[col] = pd.to_datetime(df[col])
            df[col] = pd.to_datetime(df[col], utc=True)
        elif actual_type == Decimal:
            df[col] = df[col].astype(float)
        elif isinstance(actual_type, type) and issubclass(actual_type, Enum):
            df[col] = df[col].apply(lambda x: x.value if x is not None else None)
        elif actual_type == UUID:
            df[col] = df[col].astype(str)
        elif actual_type in (list, dict):
            df[col] = df[col].apply(lambda x: json.dumps(x) if x is not None else None)

    return df


def to_dataframe(find_method: Callable, **kwargs) -> pd.DataFrame:
    """
    Generic method to fetch all pages of results and convert to DataFrame.

    Args:
        find_method: The API method to call for fetching data
        **kwargs: Arguments to pass to the find_method

    Returns:
        DataFrame containing all results
    """
    limit = kwargs.pop('limit', 100)
    max_pages = kwargs.pop('max_pages', 100)
    offset = 0

    # Initial request
    table_data = find_method(limit=limit, offset=offset, **kwargs)
    data = table_data.data

    # Fetch the pages (max max_pages)
    page = 0
    while len(data) < table_data.total and page < max_pages:
        offset += limit
        page += 1
        table_data = find_method(limit=limit, offset=offset, **kwargs)
        data.extend(table_data.data)
    if page == max_pages:
        logger.warning(f"Warning: Reached max pages ({max_pages}) while fetching data. You might not have all data. Use `max_pages` to increase the limit.")
    # Convert to DataFrame
    return pydantic_data_to_dataframe(data)