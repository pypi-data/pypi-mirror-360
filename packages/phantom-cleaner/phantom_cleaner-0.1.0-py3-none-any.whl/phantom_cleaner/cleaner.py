import pandas as pd
import numpy as np
import string
from sklearn.preprocessing import LabelEncoder

class PhantomCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def fill_missing(self, strategy='mean'):
        """Fill missing numeric values using mean, median, or mode."""
        for col in self.df.select_dtypes(include=np.number).columns:
            if strategy == 'mean':
                self.df[col].fillna(self.df[col].mean(), inplace=True)
            elif strategy == 'median':
                self.df[col].fillna(self.df[col].median(), inplace=True)
            elif strategy == 'mode':
                self.df[col].fillna(self.df[col].mode()[0], inplace=True)
        return self

    def drop_missing(self, axis=0):
        """Drop rows (axis=0) or columns (axis=1) with missing values."""
        self.df.dropna(axis=axis, inplace=True)
        return self

    def remove_duplicates(self):
        """Drop duplicate rows."""
        self.df.drop_duplicates(inplace=True)
        return self

    def remove_outliers_iqr(self):
        """Remove outliers using the IQR method."""
        Q1 = self.df.quantile(0.25)
        Q3 = self.df.quantile(0.75)
        IQR = Q3 - Q1
        condition = ~((self.df < (Q1 - 1.5 * IQR)) | (self.df > (Q3 + 1.5 * IQR))).any(axis=1)
        self.df = self.df[condition]
        return self

    def label_encode(self, columns=None):
        """Label encode categorical variables."""
        le = LabelEncoder()
        if columns is None:
            columns = self.df.select_dtypes(include='object').columns
        for col in columns:
            self.df[col] = le.fit_transform(self.df[col].astype(str))
        return self

    def clean_text(self, column):
        """Clean text column: lowercase, remove punctuation and digits."""
        self.df[column] = self.df[column].astype(str).str.lower()
        self.df[column] = self.df[column].str.translate(str.maketrans('', '', string.punctuation + string.digits))
        return self

    def get_data(self):
        """Return the cleaned DataFrame."""
        return self.df
