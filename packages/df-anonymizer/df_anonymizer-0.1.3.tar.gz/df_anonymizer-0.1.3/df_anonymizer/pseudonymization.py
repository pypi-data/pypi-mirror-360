import pandas as pd
import numpy as np
import random, string

# data pseudonymization
def randomword():

    """
    Generate a random lowercase string of length 5.

    This function creates a random sequence of 5 lowercase alphabetic characters,
    useful for generating random IDs or pseudonyms.

    :return: A random 5-character lowercase string.
    :rtype: str

    :example:

    >>> randomword()
    'xqjrt'
    """

    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(5))

def generatePseudonym(srs):

    """
    Generate a list of pseudonym codes for unique values in a pandas Series.

    Each pseudonym consists of a random 5-letter lowercase string followed by a 
    random 9-digit number, providing unique and anonymized identifiers.

    :param srs: A pandas Series containing values to be pseudonymized.
    :type srs: pandas.Series
    :return: A list of pseudonym strings, one for each unique value in the input Series.
    :rtype: list of str

    :example:

    >>> import pandas as pd
    >>> s = pd.Series(['ID1', 'ID2', 'ID1', 'ID3'])
    >>> generatePseudonym(s)
    ['abcde123456789', 'fghij987654321', 'klmno135792468']
    """

    code_lst = []
    srs_str = srs.astype(str)
    total_unique = srs_str.nunique()
    random_num = np.random.randint(low=100000000, high=999999999, size=total_unique)
    random_char = [randomword() for i in range(total_unique)]
    for m, n in zip(random_num, random_char):
        code = n + str(m)
        code_lst.append(code)
    return code_lst


def pseudonymization(df, attr):

    """
    Replace values in a DataFrame column with unique pseudonyms and save the mapping key.

    This function generates unique pseudonyms for each distinct value in the specified column,
    replaces the original values with these pseudonyms, and saves a key table mapping original 
    values to pseudonyms in an Excel file named "key_table.xlsx".

    :param df: The input DataFrame containing the attribute to pseudonymize.
    :type df: pandas.DataFrame
    :param attr: The name of the column to pseudonymize.
    :type attr: str
    :return: A DataFrame with the specified column replaced by pseudonyms.
    :rtype: pandas.DataFrame

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'NRIC': ['S1234567A', 'T9876543B', 'S1234567A']})
    >>> pseudonymized_df = pseudonymization(df, 'NRIC')
    >>> pseudonymized_df
          NRIC
    0  abcde123456789
    1  fghij987654321
    2  abcde123456789
    """

    df_copy = df.copy()
    while True:
        pseduonyms = generatePseudonym(df_copy[attr])
        if not pd.Series(pseduonyms).duplicated().any():
            break
    key = pd.Series(df[attr].unique()).sample(frac=1.0, replace=False, random_state=122, ignore_index=True)
    key_table = pd.DataFrame([key, pd.Series(pseduonyms)]).T
    key_table.columns = ["NRIC", "PseudoID"]
    key_table.to_excel("key_table.xlsx", index=False)
    mapping_dict = dict(zip(key_table["NRIC"], key_table["PseudoID"]))
    cont = df_copy[attr].map(mapping_dict)
    df_copy[attr] = cont
    return df_copy