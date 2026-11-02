# Data

This project uses the [Rossmann Store Sales](https://www.kaggle.com/c/rossmann-store-sales/data) dataset from Kaggle. It is not included in the repo: it's large, and Kaggle's competition terms limit sharing it.

1. Download the data from the Kaggle page (you need a free Kaggle account and must accept the competition rules).
2. Put `train.csv`, `test.csv` and `store.csv` in `data/raw/`.

`pytest` checks that all three files are there, with the expected columns and row counts.
