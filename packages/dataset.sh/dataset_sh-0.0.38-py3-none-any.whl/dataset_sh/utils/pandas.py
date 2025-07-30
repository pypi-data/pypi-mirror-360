import warnings


def to_dataframe(collection: 'CollectionReader'):
    try:
        import pandas as pd
    except ModuleNotFoundError as e:
        warnings.warn('cannot load module pandas, maybe it is not installed ?', UserWarning)
        return None

    return pd.DataFrame(collection)
