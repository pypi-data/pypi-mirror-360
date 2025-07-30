"""
Data processing utilities for AE optimization.

This module handles data loading, preprocessing, and train/test splitting
for the AE optimization system.
"""

import logging
from pathlib import Path
from typing import Tuple, List
import pandas as pd
import polars as pl
from sklearn.model_selection import train_test_split

from .config import AEConfig


class DataProcessor:
    """Handles data loading, preprocessing, and splitting"""
    
    def __init__(self, config: AEConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def load_and_preprocess_data(self) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """Load and preprocess the dataset"""
        try:
            self.logger.info(f"Loading data from {self.config.DATA_PATH}")
            
            # Determine file format and load accordingly
            data_path = Path(self.config.DATA_PATH)
            
            # If path is relative, resolve it relative to current working directory
            if not data_path.is_absolute():
                data_path = Path.cwd() / data_path
            
            if not data_path.exists():
                raise FileNotFoundError(f"Data file not found: {data_path}")
            
            file_extension = data_path.suffix.lower()
            
            if file_extension == '.parquet':
                # Load parquet using Polars for efficiency
                try:
                    lf = pl.scan_parquet(str(data_path))
                    df = lf.select(self.config.FEATURES).collect().to_pandas()
                except Exception as e:
                    self.logger.warning(f"Polars loading failed, falling back to pandas: {e}")
                    df = pd.read_parquet(str(data_path), columns=self.config.FEATURES)
                    
            elif file_extension == '.csv':
                # Load CSV using pandas with optimizations
                df = pd.read_csv(str(data_path), usecols=self.config.FEATURES)
                
            elif file_extension in ['.xlsx', '.xls']:
                # Load Excel files
                df = pd.read_excel(str(data_path), usecols=self.config.FEATURES)
                
            elif file_extension == '.json':
                # Load JSON files
                df = pd.read_json(str(data_path))
                df = df[self.config.FEATURES]
                
            else:
                # Try pandas read_csv as fallback for other formats
                self.logger.warning(f"Unknown file extension {file_extension}, trying CSV format")
                df = pd.read_csv(str(data_path), usecols=self.config.FEATURES)
            
            self.logger.info(f"Loaded {len(df)} samples with {len(df.columns)} features")
            
            # Validate that all required features are present
            missing_features = set(self.config.FEATURES) - set(df.columns)
            if missing_features:
                raise ValueError(f"Missing features in dataset: {missing_features}")
            
            # Validate target column
            if self.config.TARGET_COLUMN not in df.columns:
                raise ValueError(f"Target column '{self.config.TARGET_COLUMN}' not found in dataset")
            
            # Validate target values are binary
            unique_targets = df[self.config.TARGET_COLUMN].dropna().unique()
            if not set(unique_targets).issubset({0, 1, 0.0, 1.0}):
                self.logger.warning(f"Target column contains non-binary values: {unique_targets}")
                self.logger.info("Converting target to binary: >0.5 becomes 1, <=0.5 becomes 0")
                df[self.config.TARGET_COLUMN] = (df[self.config.TARGET_COLUMN] > 0.5).astype(int)
            
            # Handle missing values in target (configurable)
            if df[self.config.TARGET_COLUMN].isna().any():
                missing_target_count = df[self.config.TARGET_COLUMN].isna().sum()
                if self.config.IMPUTE_TARGET_NULLS:
                    self.logger.warning(f"Found {missing_target_count} missing target values, filling with 0")
                    df[self.config.TARGET_COLUMN] = df[self.config.TARGET_COLUMN].fillna(0)
                else:
                    self.logger.warning(f"Found {missing_target_count} missing target values, keeping as null")
                    # Target nulls will cause issues in training, so we still warn but allow it
            
            # Validate categorical features exist
            missing_categorical = set(self.config.CATEGORICAL_FEATURES) - set(df.columns)
            if missing_categorical:
                self.logger.warning(f"Categorical features not found: {missing_categorical}")
                # Filter out missing categorical features
                valid_categorical = [f for f in self.config.CATEGORICAL_FEATURES if f in df.columns]
                self.logger.info(f"Using categorical features: {valid_categorical}")
            else:
                valid_categorical = self.config.CATEGORICAL_FEATURES
            
            # One-hot encode categorical features
            if valid_categorical:
                df = pd.get_dummies(df, columns=valid_categorical, dtype=int)
                self.logger.info(f"One-hot encoded {len(valid_categorical)} categorical features")
            
            # Handle missing values in features (optional imputation)
            if df.drop(columns=[self.config.TARGET_COLUMN]).isna().any().any():
                missing_counts = df.drop(columns=[self.config.TARGET_COLUMN]).isna().sum()
                features_with_missing = missing_counts[missing_counts > 0]
                self.logger.info(f"Features with missing values: {features_with_missing.to_dict()}")
                
                if self.config.ENABLE_DATA_IMPUTATION:
                    self.logger.info("Data imputation enabled - filling missing values")
                    # Fill numeric columns with median, categorical with mode
                    for col in df.columns:
                        if col != self.config.TARGET_COLUMN and df[col].isna().any():
                            if df[col].dtype in ['int64', 'float64']:
                                df[col] = df[col].fillna(df[col].median())
                            else:
                                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 0)
                else:
                    self.logger.info("Data imputation disabled - keeping null values (LightGBM will handle them)")
            
            # Separate features and target
            feature_cols = [col for col in df.columns if col != self.config.TARGET_COLUMN]
            X = df[feature_cols]
            y = df[self.config.TARGET_COLUMN].astype(int)
            
            # Validate sufficient data
            if len(X) < 100:
                self.logger.warning(f"Dataset is very small ({len(X)} samples). Consider using more data for reliable optimization.")
            
            class_counts = y.value_counts().to_dict()
            self.logger.info(f"Class distribution: {class_counts}")
            self.logger.info(f"Final feature set: {len(feature_cols)} features")
            
            # Check for class imbalance
            if len(class_counts) == 2:
                minority_class = min(class_counts.values())
                majority_class = max(class_counts.values())
                imbalance_ratio = majority_class / minority_class
                if imbalance_ratio > 5:
                    self.logger.warning(f"Significant class imbalance detected (ratio: {imbalance_ratio:.1f}). Consider adjusting CLASS_WEIGHT in config.")
            
            return X, y, feature_cols
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def split_data(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split data into train and test sets"""
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=test_size, 
                random_state=self.config.RANDOM_SEED,
                stratify=y
            )
            
            self.logger.info(f"Data split: Train={len(X_train)}, Test={len(X_test)}")
            return X_train, X_test, y_train, y_test
            
        except Exception as e:
            self.logger.error(f"Error splitting data: {e}")
            raise