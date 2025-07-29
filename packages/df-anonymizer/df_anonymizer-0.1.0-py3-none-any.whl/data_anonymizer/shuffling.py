import pandas as pd
import numpy as np

# data shuffling/swapping/permutation
def dataShuffling(df):

    """
    Randomly shuffle the rows of a DataFrame.

    This function returns a new DataFrame with the rows shuffled in random order,
    resetting the index to maintain a clean sequence.

    :param df: The input DataFrame to shuffle.
    :type df: pandas.DataFrame
    :return: A shuffled DataFrame with reset index.
    :rtype: pandas.DataFrame

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
    >>> dataShuffling(df)  # output will vary due to randomness
       A  B
    0  2  y
    1  1  x
    2  3  z
    """

    return df.sample(frac=1).reset_index(drop=True)