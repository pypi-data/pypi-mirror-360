import pandas as pd
import numpy as np

# data suppression - remove columns
def attributeSuppression(df, attrs):

    """
    Suppress (remove) specified columns from a DataFrame.

    This function returns a copy of the input DataFrame with the specified
    columns removed, useful for removing sensitive attributes to enhance privacy.

    :param df: The input DataFrame.
    :type df: pandas.DataFrame
    :param attrs: List of column names to suppress (remove).
    :type attrs: list of str
    :return: A DataFrame with the specified columns removed.
    :rtype: pandas.DataFrame

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30], 'email': ['a@example.com', 'b@example.com']})
    >>> attributeSuppression(df, ['email'])
       name  age
    0  Alice   25
    1    Bob   30
    """

    df_copy = df.copy()
    return df_copy.drop(columns=attrs)

# record (row) suppression - remove row
def recordSuppression(df, attr_lst, attr_ex):

    """
    Suppress (remove) records from a DataFrame based on specified attribute conditions.

    This function returns a copy of the DataFrame excluding rows where the values
    in given attributes match any of the specified exclusion lists.

    :param df: The input DataFrame.
    :type df: pandas.DataFrame
    :param attr_lst: List of attribute (column) names to apply conditions on.
    :type attr_lst: list of str
    :param attr_ex: List of lists, where each sublist contains values to exclude for the corresponding attribute.
    :type attr_ex: list of list
    :return: A DataFrame with records suppressed according to the conditions.
    :rtype: pandas.DataFrame
    :raises ValueError: If the DataFrame is empty.
    :raises ValueError: If lengths of attr_lst and attr_ex differ.
    :raises ValueError: If any attribute in attr_lst is not found in the DataFrame.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'age': [25, 30, 35, 40],
    ...     'city': ['NY', 'LA', 'NY', 'SF']
    ... })
    >>> recordSuppression(df, ['age', 'city'], [[30], ['SF']])
       age city
    0   25   NY
    1   35   NY
    """

    df_copy = df.copy()
    if df_copy.empty:
        raise ValueError("Dataframe is empty.")
    if len(attr_lst) != len(attr_ex):
        raise ValueError("Number of attribute(s) and list of the attribute conditions must be the same.")
    for attr, ex in zip(attr_lst, attr_ex):
        if attr not in df_copy.columns:
            raise ValueError(f"Attribute {attr} not found in the dataframe.")
        df_copy = df_copy[~df_copy[attr].isin(ex)]
    return df_copy.reset_index(drop=True)