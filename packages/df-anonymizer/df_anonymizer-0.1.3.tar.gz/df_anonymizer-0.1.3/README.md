# df-anonymizer

A lightweight Python library designed to apply privacy-preserving transformations on datasets in `pandas.DataFrame` format.  
It is ideal for preparing data for research, analysis, reporting or machine learning while protecting sensitive personal information.

## ✨ Key Features

- **Masking**: Mask email addresses and identification numbers
- **Pseudonymization**: Generate unique pseudonyms with key mapping table
- **Data perturbation**: Add privacy noise to age, weight, height, etc.
- **Data generalization**: Bucket or reduce granularity for numeric and date values
- **Suppression**: Remove sensitive columns or filter out specific records
- **Shuffling**: Randomly reorder rows
- **Evaluation**: Compute the k-anonymity score for your dataset

> All functions are optimized to work with `pandas.DataFrame` structures.

## 📦 Installation

```bash
pip install df-anonymizer
```


## 👉 Example

### 📌 Pseudonymization

```python
import pandas as pd
from df_anonymizer import pseudonymization

df = pd.DataFrame({'NRIC': ['S1234567A', 'S2345678B', 'S3456789C']})
anon_df = pseudonymization(df, 'NRIC')
print(anon_df)

# Example output:
#        NRIC
# 0  abcd123456
# 1  efgh234567
# 2  ijkl345678
```

### 📌 Masking

```python
from df_anonymizer import maskID, maskEmail

df_mask = pd.DataFrame({
    'ID': ['123456789', '987654321'],
    'Email': ['alice@example.com', 'bob@example.com']
})
df_mask = maskID(df_mask, 'ID')
df_mask = maskEmail(df_mask, 'Email')
print(df_mask)

# Output:
#          ID              Email
# 0     ******789     a****@example.com
# 1     ******321     b**@example.com
```



## Reference

1. [Guide To Basic Anonymization](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.pdpc.gov.sg/-/media/files/pdpc/pdf-files/advisory-guidelines/guide-to-basic-anonymisation-(updated-24-july-2024).pdf) 