import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import warnings
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTENC


def split_data(
    df: pd.DataFrame,
    train_pct: float = 0.7,
    dv: Optional[str] = None,
    dv_threshold: float = 0.0,
    random_state: int = 5435,
    stratify: Union[bool, List[str]] = True,
    sampling_strategy: Optional[Union[float, str, Dict]] = None,
    shuffle: bool = True,
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, List[float]]:
    """
    Split data into train and test datasets, with options for stratification and balancing outcome classes.
    
    This function splits data into training and testing sets, with optional resampling for imbalanced
    datasets. It can handle both regression and classification tasks.
    
    Parameters
    ----------
    df : pd.DataFrame
        The input pandas dataframe to split
    train_pct : float, default=0.7
        The percentage of rows randomly assigned to the training dataset (0-1 range)
    dv : str, optional
        The column name of the outcome/target variable. If None, the function will
        return the entire dataframe split without separating features and target
    dv_threshold : float, default=0.0
        The minimum percentage of positive instances (value > 0) in the outcome.
        SMOTE/SMOTE-NC will be used to upsample positive instances to reach this threshold.
        Only accepts values 0 to 0.5. Set to 0 to disable upsampling.
    random_state : int, default=5435
        Random seed for reproducibility in splitting and upsampling
    stratify : Union[bool, List[str]], default=True
        Controls stratified sampling:
        - If True and dv is provided, stratifies by the outcome variable
        - If a list of column names, stratifies by those columns
        - If False, does not use stratified sampling
    sampling_strategy : Union[float, str, Dict], optional
        Sampling strategy for imbalanced data. If None, will use dv_threshold.
        See imblearn documentation for more details on acceptable values.
    shuffle : bool, default=True
        Whether to shuffle the data before splitting
        
    Returns
    -------
    Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, List[float]]
        A tuple containing:
        - x_train: Training features DataFrame
        - y_train: Training target Series (if dv is provided, otherwise empty Series)
        - x_test: Testing features DataFrame
        - y_test: Testing target Series (if dv is provided, otherwise empty Series)
        - model_weights: List of weights to use for modeling [negative_weight, positive_weight]
        
    Raises
    ------
    ValueError
        If input parameters are invalid or incompatible
        
    Examples
    --------
    Basic usage with default parameters:
    >>> X_train, y_train, X_test, y_test, model_weights = split_data(df, dv="target")
    
    With upsampling for imbalanced data:
    >>> X_train, y_train, X_test, y_test, model_weights = split_data(
    ...     df, dv="target", dv_threshold=0.3, random_state=42
    ... )
    
    With advanced stratification:
    >>> X_train, y_train, X_test, y_test, model_weights = split_data(
    ...     df, dv="target", stratify=["target", "age_group", "gender"]
    ... )
    
    Split without target variable:
    >>> train_df, _, test_df, _, _ = split_data(df, train_pct=0.8, dv=None)
    """
    # Parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if not 0 < train_pct < 1:
        raise ValueError(f"train_pct must be between 0 and 1, got {train_pct}")
        
    if not 0 <= dv_threshold <= 0.5:
        raise ValueError(f"dv_threshold must be between 0 and 0.5, got {dv_threshold}")
    
    # Make a copy to avoid modifying the original
    df_copy = df.copy()
    
    # Default model weights
    model_weights = [1.0, 1.0]
    
    # Handle case where no target variable is provided
    if dv is None:
        print(f"No target variable provided. Splitting entire dataframe into {train_pct:.1%} train and {1-train_pct:.1%} test.")
        
        # Stratify parameter is ignored when dv is None
        if isinstance(stratify, list) and stratify:
            stratify_param = df_copy[stratify]
        else:
            stratify_param = None
            
        # Split the data without separating features and target
        train_df, test_df = train_test_split(
            df_copy,
            train_size=train_pct,
            test_size=1-train_pct,
            random_state=random_state,
            shuffle=shuffle,
            stratify=stratify_param
        )
        
        # Return empty Series for y_train and y_test
        return train_df, pd.Series(dtype='float64'), test_df, pd.Series(dtype='float64'), model_weights
    
    # Validate that the target variable exists
    if dv not in df_copy.columns:
        raise ValueError(f"Target variable '{dv}' not found in dataframe columns")
    
    # Separate features and target
    print(f"Splitting dataset with {len(df_copy)} rows into train ({train_pct:.1%}) and test ({1-train_pct:.1%}) sets")
    
    X = df_copy.drop(columns=[dv])
    y = df_copy[dv]
    
    # Determine if this is a binary classification task
    is_binary = False
    if pd.api.types.is_numeric_dtype(y.dtype) or pd.api.types.is_categorical_dtype(y.dtype):
        unique_values = y.nunique()
        is_binary = unique_values == 2
        
    # Determine stratify parameter
    stratify_param = None
    if isinstance(stratify, list):
        # Check if all stratify columns exist
        missing_cols = [col for col in stratify if col not in df_copy.columns]
        if missing_cols:
            raise ValueError(f"Stratify columns not found in dataframe: {missing_cols}")
        
        # Create stratify parameter from multiple columns
        stratify_param = df_copy[stratify].copy()
    elif stratify is True and dv is not None:
        stratify_param = y
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        train_size=train_pct,
        test_size=1-train_pct,
        random_state=random_state,
        shuffle=shuffle,
        stratify=stratify_param
    )
    
    # Apply upsampling if requested and applicable
    if dv_threshold > 0 and is_binary:
        print(f"Checking if upsampling is needed (threshold: {dv_threshold:.1%})")
        
        # Get the proportion of positive instances
        # For binary classification, assume the minority class is the positive class
        value_counts = y_train.value_counts()
        positive_class = value_counts.index[value_counts.argmin()]
        
        # Calculate positive class proportion
        positive_prop = (y_train == positive_class).mean()
        
        print(f"Positive class proportion: {positive_prop:.2%}")
        
        # Apply upsampling if below threshold
        if positive_prop < dv_threshold:
            print(f"Upsampling positive class from {positive_prop:.2%} to {dv_threshold:.2%} using SMOTE-NC")
            
            # Identify categorical features for SMOTE-NC
            # For binary features (with 2 unique values), they are treated as categorical
            numeric_cols = X_train.select_dtypes(include=["number"]).columns
            
            # Create categorical feature indices list
            cats = [i for i, col in enumerate(numeric_cols) 
                   if X_train[col].nunique(dropna=False) == 2]
            
            # Calculate sampling strategy if not provided
            if sampling_strategy is None:
                # Target ratio between positive and negative classes
                target_ratio = dv_threshold / (1 - dv_threshold)
                sampling_strategy = target_ratio
            
            # Apply SMOTE-NC for upsampling
            try:
                smote = SMOTENC(
                    categorical_features=cats,
                    sampling_strategy=sampling_strategy,
                    random_state=random_state
                )
                
                # Fit resample
                X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
                
                # Update training data
                X_train = X_train_resampled
                y_train = y_train_resampled
                
                # Recalculate positive proportion
                new_positive_prop = (y_train == positive_class).mean()
                
                print(f"After upsampling: positive class proportion {new_positive_prop:.2%}")
                print(f"Training set size increased from {len(y_train_resampled)} to {len(y_train)}")
                
                # Calculate model weights to compensate for upsampling
                neg_weight = 1.0 / ((1 - new_positive_prop) / (1 - positive_prop))
                pos_weight = 1.0 / (new_positive_prop / positive_prop)
                
                # Assign model weights
                model_weights = [neg_weight, pos_weight]
                
                print(f"Model weights: negative={neg_weight:.2f}, positive={pos_weight:.2f}")
                
            except Exception as e:
                warnings.warn(f"SMOTE upsampling failed: {str(e)}. Proceeding with original data.")
    
    return X_train, y_train, X_test, y_test, model_weights