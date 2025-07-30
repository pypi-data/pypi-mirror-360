import pandas as pd
import numpy as np

# date generalization
def dateGeneralization(df, attr, verbose=True):

    """
    Generalize a datetime column in a DataFrame by reducing its granularity.

    This function anonymizes temporal information by converting a datetime column
    to either a year-month ("YYYY-MM") or year-only ("YYYY") format. This helps reduce 
    identifiability while retaining useful date-related patterns.

    :param df: The input DataFrame containing the datetime column.
    :type df: pandas.DataFrame
    :param attr: The name of the column to generalize. Must be of datetime type.
    :type attr: str
    :param verbose: If True, generalize to "YYYY-MM"; if False, generalize to "YYYY".
    :type verbose: bool, optional
    :return: A copy of the DataFrame with the specified column generalized.
    :rtype: pandas.DataFrame
    :raises TypeError: If the specified column is not of datetime type.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'visit_date': pd.to_datetime(['2023-07-05', '2022-11-20'])})
    >>> dateGeneralization(df, 'visit_date', verbose=True)
      visit_date
    0    2023-07
    1    2022-11

    >>> dateGeneralization(df, 'visit_date', verbose=False)
      visit_date
    0       2023
    1       2022
    """

    if not pd.api.types.is_datetime64_any_dtype(df[attr]):
        raise TypeError("Input must be in datetime format")
    df_copy = df.copy()
    if verbose:
        df_copy[attr] = df_copy[attr].dt.strftime("%Y-%m")
    else:
        df_copy[attr] = df_copy[attr].dt.strftime("%Y")
    return df_copy


# data generalizaton (numerical data)
def meanGeneralization(df, attr, bins):

    """
    Generalize a numerical attribute by binning its values and replacing them with the bin midpoint.

    This function performs data generalization on continuous numeric data by dividing the values
    into a specified number of bins (intervals) and replacing each value with the midpoint
    of its corresponding bin. This helps to reduce data precision while preserving general trends.

    :param df: The input DataFrame containing the numerical attribute.
    :type df: pandas.DataFrame
    :param attr: The name of the column to generalize. Must contain numeric values.
    :type attr: str
    :param bins: The number of bins to group the data into.
    :type bins: int
    :return: A DataFrame with the specified column generalized to bin midpoints.
    :rtype: pandas.DataFrame
    :raises TypeError: If the column contains non-numeric values.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'age': [22, 27, 35, 45, 51]})
    >>> meanGeneralization(df, 'age', bins=3)
       age
    0   24
    1   24
    2   36
    3   48
    4   48
    """

    for val in df[attr]:
        if not isinstance(val, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
            raise TypeError("Input must be a numerical data.")
    cont = []
    val_binned, bins = pd.cut(df[attr], bins=bins, retbins=True)
    for i in val_binned:
        val_mean = (i.left + i.right) // 2
        cont.append(val_mean)
    df[attr] = cont
    return df

# data binning/bucketing
def dataBucketing(df, attr, bins, labels):

    """
    Bucket a numerical attribute into categorical intervals using predefined labels.

    This function groups continuous numeric values into discrete categories (buckets)
    based on specified bin edges and assigns custom labels to each bin. It is useful
    for data generalization or converting numeric values into ordinal categories.

    :param df: The input DataFrame containing the numerical attribute.
    :type df: pandas.DataFrame
    :param attr: The name of the column to bucket. Must contain numeric values.
    :type attr: str
    :param bins: The number of bins or a sequence of bin edges.
    :type bins: int or sequence of scalars
    :param labels: List of labels corresponding to the bins.
    :type labels: list of str
    :return: A DataFrame with the specified column converted into bucket labels.
    :rtype: pandas.DataFrame
    :raises TypeError: If the column contains non-numeric values.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'age': [22, 27, 35, 45, 51]})
    >>> bins = [20, 30, 40, 60]
    >>> labels = ['20s', '30s', '40-50s']
    >>> dataBucketing(df, 'age', bins=bins, labels=labels)
         age
    0   20s
    1   20s
    2   30s
    3  40-50s
    4  40-50s
    """

    for val in df[attr]:
        if not isinstance(val, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
            raise TypeError("Input must be a numerical data.")
    cont = []
    val_binned, bins = pd.cut(df[attr], bins=bins, labels=labels, ordered=True, retbins=True)
    df[attr] = val_binned
    return df