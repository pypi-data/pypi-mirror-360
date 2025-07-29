import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

class DataLoader:
    def __init__(
        self,
        df: pd.DataFrame,
        feature_cols: list,
        label_col: str,
        val_size: float = 0.2,
        test_size: float = 0.1,
        random_state: int = 42,
        scale: bool = True
    ):
        self.df = df.copy()
        self.feature_cols = feature_cols
        self.label_col = label_col
        self.val_size = val_size
        self.test_size = test_size
        self.random_state = random_state
        self.scale = scale
        self.scaler = StandardScaler() if scale else None

    def _split(self):
        X = self.df[self.feature_cols]
        y = self.df[self.label_col]
        X_train_val, X_test, y_train_val, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y
        )
        val_relative = self.val_size / (1 - self.test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_val,
            y_train_val,
            test_size=val_relative,
            random_state=self.random_state,
            stratify=y_train_val
        )
        return X_train, X_val, X_test, y_train, y_val, y_test

    def load_data(self):
        X_train, X_val, X_test, y_train, y_val, y_test = self._split()

        imputer = SimpleImputer(strategy="mean")
        X_train = pd.DataFrame(imputer.fit_transform(X_train), columns=self.feature_cols, index=X_train.index)
        X_val = pd.DataFrame(imputer.transform(X_val), columns=self.feature_cols, index=X_val.index)
        X_test = pd.DataFrame(imputer.transform(X_test), columns=self.feature_cols, index=X_test.index)

        if self.scale:
            X_train = pd.DataFrame(
                self.scaler.fit_transform(X_train),
                columns=self.feature_cols,
                index=X_train.index
            )
            X_val = pd.DataFrame(
                self.scaler.transform(X_val),
                columns=self.feature_cols,
                index=X_val.index
            )
            X_test = pd.DataFrame(
                self.scaler.transform(X_test),
                columns=self.feature_cols,
                index=X_test.index
            )

        return X_train, X_val, X_test, y_train, y_val, y_test