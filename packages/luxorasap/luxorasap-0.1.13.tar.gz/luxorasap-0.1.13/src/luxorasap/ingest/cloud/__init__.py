"""Camada moderna de ingestão: grava / incrementa tabelas em ADLS (Parquet)."""

import pandas as pd
import datetime as dt

from luxorasap.utils.storage import BlobParquetClient
from luxorasap.utils.dataframe import prep_for_save
from luxorasap.datareader import LuxorQuery

__all__ = ["save_table", "incremental_load"]

_client = BlobParquetClient()   # instância única para o módulo


# ────────────────────────────────────────────────────────────────
def save_table(
    table_name: str,
    df,
    *,
    index: bool = False,
    index_name: str = "index",
    normalize_columns: bool = True,
    directory: str = "enriched/parquet",
    override=False
):
    """Salva DataFrame como Parquet em ADLS (sobrescrevendo)."""
    
    if 'Last_Updated' not in df.columns:
        df['Last_Updated'] = dt.datetime.now()
    
    if override == False:
        lq = LuxorQuery()
        if lq.table_exists(table_name):
            return
    
    df = prep_for_save(df, index=index, index_name=index_name, normalize=normalize_columns)
    _client.write_df(df.astype(str), f"{directory}/{table_name}.parquet")


def incremental_load(
    lq: LuxorQuery,
    table_name: str,
    df,
    *,
    increment_column: str = "Date",
    index: bool = False,
    index_name: str = "index",
    normalize_columns: bool = True,
    directory: str = "enriched/parquet",
):
    """Concatena novos dados aos existentes, cortando duplicados pela data."""
    df["Last_Updated"] = dt.datetime.now()
    
    if lq.table_exists(table_name):
        prev = lq.get_table(table_name)
        cutoff = df[increment_column].max()
        prev = prev.query(f"{increment_column} < @cutoff")
        df = pd.concat([prev, df], ignore_index=True)

    save_table(
        table_name,
        df,
        index=index,
        index_name=index_name,
        normalize_columns=normalize_columns,
        directory=directory,
        override=True
    )