import pandas as pd
import numpy as np
import random, string
from datetime import timedelta

# base-3 rounding for age (in years)
def agePerturbation(df, attr):

    """
    Perturb age values by rounding them down to the nearest multiple of 3.

    This function reduces the precision of age data by grouping ages into intervals 
    of size 3, which helps protect individual privacy while retaining approximate age information.

    :param df: The input DataFrame containing the age attribute.
    :type df: pandas.DataFrame
    :param attr: The name of the age column to perturb. Must contain numeric values.
    :type attr: str
    :return: A DataFrame with the specified age column perturbed.
    :rtype: pandas.DataFrame
    :raises TypeError: If any value in the age column is not numeric.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'age': [22, 27, 35, 40, 51]})
    >>> agePerturbation(df, 'age')
       age
    0   21
    1   27
    2   33
    3   39
    4   51
    """

    cont = []
    df_copy = df.copy()
    for age in df_copy[attr]:
        if not isinstance(age, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
            raise TypeError("Input must be a numerical data.")
        else:
            cont.append((age // 3) * 3)
    df_copy[attr] = cont
    return df_copy

# base-3 rounding for weight (in kg)
def weightPerturbation(df, attr):

    """
    Perturb weight values by rounding them down to the nearest multiple of 3.

    This function reduces the precision of weight data by grouping weights into intervals 
    of size 3, helping to anonymize the data while preserving approximate weight information.

    :param df: The input DataFrame containing the weight attribute.
    :type df: pandas.DataFrame
    :param attr: The name of the weight column to perturb. Must contain numeric values.
    :type attr: str
    :return: A DataFrame with the specified weight column perturbed.
    :rtype: pandas.DataFrame
    :raises TypeError: If any value in the weight column is not numeric.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'weight': [55.5, 62.3, 70, 81.7]})
    >>> weightPerturbation(df, 'weight')
       weight
    0      54
    1      60
    2      69
    3      81
    """

    cont = []
    df_copy = df.copy()
    for weight in df_copy[attr]:
        if not isinstance(weight, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
            raise TypeError("Input must be a numerical data.")
        else:
            cont.append((weight // 3) * 3)
    df_copy[attr] = cont
    return df_copy  

# base-5 rounding for height (in cm)
def heightPerturbation(df, attr):

    """
    Perturb height values by rounding them down to the nearest multiple of 5.

    This function reduces the precision of height data by grouping heights into intervals 
    of size 5, helping to anonymize the data while preserving approximate height information.

    :param df: The input DataFrame containing the height attribute.
    :type df: pandas.DataFrame
    :param attr: The name of the height column to perturb. Must contain numeric values.
    :type attr: str
    :return: A DataFrame with the specified height column perturbed.
    :rtype: pandas.DataFrame
    :raises TypeError: If any value in the height column is not numeric.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'height': [161, 167, 175, 182]})
    >>> heightPerturbation(df, 'height')
       height
    0     160
    1     165
    2     175
    3     180
    """

    cont = []
    df_copy = df.copy()
    for height in df_copy[attr]:
        if not isinstance(height, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
            raise TypeError("Input must be a numerical data.")
        else:
            cont.append((height // 5) * 5)
    df_copy[attr] = cont
    return df_copy  

# base-x roudning
def dataPerturbation(df, attr, base_number):

    """
    Perturb numerical values by rounding them down to the nearest multiple of a base number.

    This function reduces the precision of numeric data by grouping values into intervals
    defined by the base number, helping to anonymize the data while preserving approximate information.

    :param df: The input DataFrame containing the numerical attribute.
    :type df: pandas.DataFrame
    :param attr: The name of the column to perturb. Must contain numeric values.
    :type attr: str
    :param base_number: The base number to define the perturbation interval.
    :type base_number: int or float
    :return: A DataFrame with the specified column perturbed.
    :rtype: pandas.DataFrame
    :raises TypeError: If any value in the specified column is not numeric.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'value': [12, 25, 37, 44, 58]})
    >>> dataPerturbation(df, 'value', base_number=10)
       value
    0     10
    1     20
    2     30
    3     40
    4     50
    """

    cont = []
    df_copy = df.copy()
    for val in df_copy[attr]:
        if not isinstance(val, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
            raise TypeError("Input must be a numerical data.")
        else:
            cont.append((val // base_number) * base_number)
    df_copy[attr] = cont
    return df_copy  

# date shifting
def datePerturbation(df, attr, max_days=30):

    """
    Perturb datetime values by randomly shifting dates within a specified range.

    This function adds or subtracts a random number of days (up to max_days) to each date,
    helping to anonymize temporal data while preserving approximate timeframes.

    :param df: The input DataFrame containing the datetime attribute.
    :type df: pandas.DataFrame
    :param attr: The name of the datetime column to perturb.
    :type attr: str
    :param max_days: Maximum number of days to shift the date forward or backward. Default is 30.
    :type max_days: int, optional
    :return: A DataFrame with the specified datetime column perturbed.
    :rtype: pandas.DataFrame
    :raises TypeError: If the specified column is not of datetime type.

    :example:

    >>> import pandas as pd
    >>> from datetime import datetime
    >>> df = pd.DataFrame({'visit_date': pd.to_datetime(['2023-07-05', '2023-07-10'])})
    >>> perturbed_df = datePerturbation(df, 'visit_date', max_days=5)
    >>> perturbed_df['visit_date']  # Dates shifted by up to ±5 days (output will vary)
    0   2023-07-02
    1   2023-07-13
    Name: visit_date, dtype: datetime64[ns]
    """

    if not pd.api.types.is_datetime64_any_dtype(df[attr]):
        raise TypeError("Input must be in datetime format.")
    cont = []
    for date in df[attr]:
        days_to_shift = np.random.randint(-max_days, max_days + 1)
        shifted_date = date + timedelta(days = days_to_shift)
        cont.append(shifted_date)
    df[attr] = cont
    return df


    





    