import pandas as pd
import numpy as np
from collections import Counter

# calculate the K-anonymity score
def calculateKAnonymity(df, quasi_identifier):

    """
    Calculate the k-anonymity score of a dataset based on the given quasi-identifiers.

    K-anonymity is a privacy metric that measures the minimum number of records that share 
    the same combination of quasi-identifiers. A higher k-value indicates stronger protection 
    against re-identification.

    :param df: The dataset to evaluate.
    :type df: pandas.DataFrame
    :param quasi_identifier: List of column names to use as quasi-identifiers.
    :type quasi_identifier: list of str
    :return: The k-anonymity score (minimum group size).
    :rtype: int
    :raises ValueError: If any quasi-identifier is not in the dataframe.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'age': [34, 34, 45, 45, 52],
    ...     'zipcode': ['12345', '12345', '12345', '12345', '67890'],
    ...     'gender': ['M', 'F', 'M', 'F', 'F']
    ... })
    >>> calculateKAnonymity(df, ['age', 'zipcode'])
    1
    """

    if not all(item in df.columns for item in quasi_identifier):
        wrgCol = list(set(quasi_identifier) - set(df.columns))
        raise ValueError(f"Quasi identifier {wrgCol} not found in collumn name of dataframe.")

    quasi_df = df[quasi_identifier]
    tuple_rows = [tuple(row) for row in quasi_df.values]
    combination_counts = Counter(tuple_rows)
    k_anonymity = min(combination_counts.values())
    return k_anonymity