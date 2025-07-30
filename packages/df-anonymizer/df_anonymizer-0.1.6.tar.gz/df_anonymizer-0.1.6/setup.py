from setuptools import setup, find_packages

setup(
    name="df_anonymizer",
    version="0.1.6",
    description="A Python library for anonymizing and transforming data in pandas DataFrames, including masking, suppression, perturbation, permutation, generalization, and pseudonymization.",
    autho="Tan Shih Jen",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.3.0,<3.0.0",
        "numpy>=2.0.2,<3.0.0"
    ],
)