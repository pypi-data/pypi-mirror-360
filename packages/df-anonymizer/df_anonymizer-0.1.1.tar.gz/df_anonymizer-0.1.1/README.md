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

import pandas as pd
from df_anonymizer import (
    pseudonymization, maskID, maskEmail, agePerturbation, weightPerturbation,
    heightPerturbation, dataPerturbation, datePerturbation, dateGeneralization,
    meanGeneralization, dataBucketing, attributeSuppression, recordSuppression,
    dataShuffling, calculateKAnonymity
)

# Pseudonymization
df = pd.DataFrame({'NRIC': ['S1234567A', 'S2345678B', 'S3456789C']})
anon_df = pseudonymization(df, 'NRIC')
print(anon_df)

# Masking
df_mask = pd.DataFrame({
    'ID': ['123456789', '987654321'],
    'Email': ['alice@example.com', 'bob@example.com']
})
df_mask = maskID(df_mask, 'ID')
df_mask = maskEmail(df_mask, 'Email')
print(df_mask)

# Perturbation
df_perturb = pd.DataFrame({
    'Age': [25, 34, 57],
    'Weight': [58.4, 72.1, 80.5],
    'Height': [163.2, 177.5, 170.0],
    'Score': [81, 92, 87],
    'Date': pd.to_datetime(['2023-01-01', '2023-01-15', '2023-02-01'])
})
df_perturb = agePerturbation(df_perturb, 'Age')
df_perturb = weightPerturbation(df_perturb, 'Weight')
df_perturb = heightPerturbation(df_perturb, 'Height')
df_perturb = dataPerturbation(df_perturb, 'Score', base_number=10)
df_perturb = datePerturbation(df_perturb, 'Date', max_days=7)
print(df_perturb)

# Generalization
df_gen = pd.DataFrame({
    'DOB': pd.to_datetime(['1990-01-01', '1995-05-15']),
    'Income': [2000, 4500, 7800],
    'Age': [22, 35, 47]
})
df_gen = dateGeneralization(df_gen, 'DOB', verbose=False)
df_gen = meanGeneralization(df_gen, 'Income', bins=3)
df_gen = dataBucketing(df_gen, 'Age', bins=[0, 30, 60], labels=['Young', 'Adult'])
print(df_gen)

# Suppression
df_sup = pd.DataFrame({
    'Name': ['Alice', 'Bob'],
    'Age': [25, 40],
    'City': ['SG', 'NY']
})
df_sup = attributeSuppression(df_sup, ['Name'])
df_sup = recordSuppression(df_sup, ['City'], [['NY']])
print(df_sup)

# Shuffling
df_shuffle = pd.DataFrame({'Name': ['A', 'B', 'C'], 'Age': [20, 30, 40]})
df_shuffle = dataShuffling(df_shuffle)
print(df_shuffle)

# k-Anonymity Evaluation
df_kanon = pd.DataFrame({
    'Age': [25, 25, 30, 30],
    'Zip': ['12345', '12345', '67890', '67890']
})
k_score = calculateKAnonymity(df_kanon, ['Age', 'Zip'])
print(f"k-anonymity score: {k_score}")