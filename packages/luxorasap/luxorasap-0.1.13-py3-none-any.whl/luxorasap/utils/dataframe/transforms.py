import pandas as pd

def text_to_lowercase(t: pd.DataFrame) -> pd.DataFrame:
    """
    Converte todas as colunas de texto para lowercase
    Args:
        t (pd.DataFrame): pandas DataFrame
    Returns:
        pd.DataFrame
    """

    return t.map(lambda x: x.lower().strip() if isinstance(x, str) else x)


def persist_column_formatting(t: pd.DataFrame, columns_to_persist_override : set = {}) -> pd.DataFrame:
    """
    Persiste a formatacao de algumas colunas, e transforma o resto em lowercase
    Args:
        t (pd.DataFrame): pandas DataFrame
    Returns:
        pd.DataFrame
    """

    columns_to_persist = {"Name", "Class", "Vehicles", "Segment"}
    columns_to_persist = columns_to_persist.union(columns_to_persist_override)

    if len(set(t.columns).intersection(columns_to_persist)) > 0:
        # Vamos persistir a formatacao de algumas colunas
        columns_order = list(t.columns)
        columns_to_persist = list(set(t.columns).intersection(columns_to_persist))
        persistent_data = t[columns_to_persist].copy()

        columns_to_normalize = list(set(columns_order) - set(columns_to_persist))
        t = text_to_lowercase(t[columns_to_normalize])
        t.loc[:,columns_to_persist] = persistent_data
        return t[columns_order]
    
    # Nos outros casos, transformaremos tudo em lowercase
    return text_to_lowercase(t)


def prep_for_save(
    df: pd.DataFrame,
    *,
    index: bool = False,
    index_name: str = "index",
    normalize: bool = False,
):
    if index:
        name = df.index.name or index_name
        df = df.reset_index().rename(columns={"index": name})
    return persist_column_formatting(df) if normalize else df