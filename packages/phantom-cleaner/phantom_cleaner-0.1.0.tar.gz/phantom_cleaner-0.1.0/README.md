# Phantom Cleaner 🧹

`phantom_cleaner` is a simple and efficient Python library to clean your datasets with minimal effort.

## Features

- Handle missing values (mean, median, mode, drop)
- Remove duplicates
- Remove outliers using IQR
- Label encode categorical variables
- Clean text data (lowercase, remove punctuation and digits)

## Installation

```bash
pip install phantom_cleaner



#USAGE

# import pandas as pd
# from phantom_cleaner import PhantomCleaner

# df = pd.read_csv('yourfile.csv')
# cleaned_df = (PhantomCleaner(df)
#               .fill_missing('mean')
#               .remove_outliers_iqr()
#               .remove_duplicates()
#               .label_encode()
#               .get_data())

# print(cleaned_df.head())
