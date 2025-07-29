import pandas as pd
import numpy as np

# masking the ID and keep the last 3 digits
def maskID(df, attr):

    """
    Mask the characters of an ID in a DataFrame column, showing only the last three characters.

    This function replaces all but the last three characters of each ID with asterisks ('*'),
    helping to anonymize sensitive identifiers while retaining a partial visible suffix.

    :param df: The input DataFrame containing the ID column.
    :type df: pandas.DataFrame
    :param attr: The name of the column with IDs to mask.
    :type attr: str
    :return: A DataFrame with the specified column masked.
    :rtype: pandas.DataFrame
    :raises TypeError: If any ID is not None, int, or string.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'NRIC': ['S1234567A', 'T9876543B', None, 123456789]})
    >>> maskID(df, 'NRIC')
           NRIC
    0  *****67A
    1  *****43B
    2      None
    3  ******789
    """

    cont = []
    for id in df[attr]:
        if id is None:
            cont.append(id)
        elif not isinstance(id, (int, str, np.int8, np.int16, np.int32, np.int64)):
            raise TypeError("Input must ne a string or integer number.")
        else:
            id_str = str(id)
            cont.append((len(list(id_str)[0:-3]) * "*") + ''.join(list(id_str)[-3:]))
    df[attr] = cont
    return df

# masking the email
def maskEmail(df, attr):

    """
    Mask an email address in a DataFrame column by replacing all characters
    in the username except the first character with asterisks (*).

    This helps anonymize email addresses while retaining the domain and
    the first character of the username for partial identification.

    :param df: The input DataFrame containing the email column.
    :type df: pandas.DataFrame
    :param attr: The name of the column with email addresses to mask.
    :type attr: str
    :return: A DataFrame with the specified column masked.
    :rtype: pandas.DataFrame
    :raises TypeError: If any email is not None or a string.

    :example:

    >>> import pandas as pd
    >>> df = pd.DataFrame({'email': ['alice@example.com', 'bob.smith@test.org', None]})
    >>> maskEmail(df, 'email')
                email
    0    a****@example.com
    1    b*******@test.org
    2                 None
    """

    cont = []
    for email in df[attr]:
        if email is None:
            cont.append(email)
        elif not isinstance(email, str):
            raise TypeError("Email must be a string.")
        else:
            name, domain = email.split("@")
            cont.append(list(name)[0] + len(list(name)[1:]) * "*" + "@" + domain)
    df[attr] = cont
    return df