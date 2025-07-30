import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union, Set
import warnings
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif


def drop_categorical(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Drop all categorical columns from the dataframe.
    
    A useful step before regression modeling, when categorical variables are not supported by
    the algorithm being used.
    
    Parameters
    ----------
    df : pd.DataFrame
        Your pandas dataframe
    
    Returns
    -------
    pd.DataFrame
        The transformed DataFrame with categorical columns dropped
    
    Examples
    --------
    >>> new_df = drop_categorical(my_df)
    >>> print(f"Dropped categorical columns")
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    # Create a deep copy of the dataframe
    work_df = df.copy(deep=True)
    
    # Get categorical columns
    categorical_columns = list(work_df.select_dtypes(exclude="number").columns)
    
    # Drop categorical columns if any exist
    if categorical_columns:
        work_df = work_df.drop(columns=categorical_columns)
        print(f'The following categorical columns were dropped: {categorical_columns}')
    else:
        print('No categorical columns to drop')
    
    return work_df


def remove_low_variation(
    df: pd.DataFrame,
    dv: Optional[str] = None,
    columns: Union[str, List[str]] = "all",
    threshold: float = 0.98,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Remove columns from a dataset that do not meet the variation threshold.
    
    Columns will be dropped if they contain a high percentage of one value, as they
    provide minimal information for modeling.
    
    Parameters
    ----------
    df : pd.DataFrame
        Your pandas dataframe
    dv : str, optional
        The column name of your outcome. Entering your outcome variable will prevent 
        it from being removed due to low variation.
    columns : list or str, default="all"
        Will examine all columns by default. To limit to just a subset of columns, 
        pass a list of column names.
    threshold : float, default=0.98
        The maximum percentage one value in a column can represent. Columns that 
        exceed this threshold will be dropped. For example, the default value of 0.98 
        will drop any column where one value is present in more than 98% of rows.
    verbose : bool, default=True
        Set to True to print outputs of columns being dropped. Set to False to suppress.
    
    Returns
    -------
    pd.DataFrame
        The transformed DataFrame with low variation columns dropped
    
    Examples
    --------
    >>> new_df = remove_low_variation(df=my_df, dv='target', threshold=0.95)
    >>> print(f"Removed columns due to low variation")
    """
    # Enhanced parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
        
    if not (0 < threshold < 1):
        raise ValueError(f"threshold must be between 0 and 1, got {threshold}")
    
    if dv is not None and dv not in df.columns:
        warnings.warn(f"Specified DV '{dv}' not found in dataframe")
    
    # Create a deep copy of the dataframe
    work_df = df.copy(deep=True)
    
    # Determine columns to process
    if columns == "all":
        var_list = work_df.columns.tolist()
        if verbose:
            print("\nExamining all columns as candidates for removal")
    else:
        if isinstance(columns, list):
            var_list = columns
            if verbose:
                print(f"\nExamining the following columns as candidates for removal: {var_list}")
        else:
            raise TypeError(f"columns must be 'all' or a list, got {type(columns)}")
        
        # Validate columns exist in the dataframe
        missing_columns = [col for col in var_list if col not in work_df.columns]
        if missing_columns:
            warnings.warn(f"Columns {missing_columns} not found in dataframe")
            var_list = [col for col in var_list if col in work_df.columns]
    
    # Remove target variable from consideration if specified
    if dv is not None and dv in var_list:
        var_list.remove(dv)
        if verbose:
            print(f"Target variable '{dv}' excluded from low variation check")
    
    # List to store columns to remove
    removal_list = []
    
    # Process all columns
    for v in var_list:
        try:
            # Skip non-finite columns
            if work_df[v].isna().all():
                continue
                
            # Get value counts for the column
            counts = work_df[v].value_counts(normalize=True, dropna=False)
            max_freq = counts.iloc[0]
            max_value = counts.index[0]
            
            # Check if the column should be dropped
            if max_freq > threshold:
                removal_list.append(v)
                
                if verbose:
                    print(f"In column '{v}', the value {max_value} accounts for {max_freq:.2%} of the values (threshold: {threshold:.2%})")
        except Exception as e:
            warnings.warn(f"Error processing column '{v}': {str(e)}")
    
    print(f"\nRemoved {len(removal_list)} columns due to low variation")
    
    # Drop columns if any were identified for removal
    if removal_list:
        work_df = work_df.drop(columns=removal_list)
    
    return work_df


def remove_outcome_proxies(
    df: pd.DataFrame,
    dv: str,
    threshold: float = 0.8,
    method: str = "pearson",
    verbose: bool = True
) -> pd.DataFrame:
    """
    Remove columns that are highly correlated with the outcome (target) column.
    
    This helps prevent data leakage by removing features that are essentially just
    noisy copies of the target variable.
    
    Parameters
    ----------
    df : pd.DataFrame
        Your pandas dataframe
    dv : str
        The column name of your outcome.
    threshold : float, default=0.8
        The correlation value to the outcome above which columns will be dropped.
        For example, the default value of 0.8 will identify and drop columns that
        have correlations greater than 80% to the outcome.
    method : str, default="pearson"
        The correlation method to use. Options are:
        - "pearson": Standard correlation coefficient (linear relationships)
        - "spearman": Spearman rank correlation (monotonic relationships)
        - "mutual_info": Mutual information (any statistical dependency)
    verbose : bool, default=True
        Set to True to print outputs of columns being dropped. Set to False to suppress.
    
    Returns
    -------
    pd.DataFrame
        The transformed DataFrame with outcome proxy columns dropped
    
    Examples
    --------
    >>> new_df = find_outcome_proxies(df=my_df, dv='target', threshold=0.7, method="spearman")
    >>> print(f"Removed columns as outcome proxies")
    """
    # Parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if not isinstance(dv, str):
        raise TypeError(f"dv must be a string, got {type(dv)}")
    
    if dv not in df.columns:
        raise ValueError(f"Target variable '{dv}' not found in dataframe")
    
    if not isinstance(threshold, (int, float)):
        raise TypeError(f"threshold must be a number, got {type(threshold)}")
    
    if not (0 <= threshold <= 1):
        raise ValueError(f"threshold must be between 0 and 1, got {threshold}")
    
    valid_methods = ["pearson", "spearman", "mutual_info"]
    if method not in valid_methods:
        raise ValueError(f"method must be one of {valid_methods}, got {method}")
    
    # Create a deep copy of the dataframe
    work_df = df.copy(deep=True)
    
    # Identify numeric columns for correlation
    numeric_cols = work_df.select_dtypes(include=["number"]).columns.tolist()
    if dv not in numeric_cols:
        raise ValueError(f"Target variable '{dv}' must be numeric for correlation analysis")
    
    # Remove the target variable from the list of features
    feature_cols = [col for col in numeric_cols if col != dv]
    
    # Calculate correlations based on the specified method
    if method in ["pearson", "spearman"]:
        # Calculate correlations using pandas
        correlations = work_df[numeric_cols].corr(method=method)[dv].drop(dv)
        corr_values = {col: abs(corr) for col, corr in correlations.items() if abs(corr) > threshold}
    
    elif method == "mutual_info":
        # For mutual information, we need to handle the target type differently
        # Create X and y for mutual information calculation
        X = work_df[feature_cols]
        y = work_df[dv]
        
        # Determine if this is a classification or regression problem
        if pd.api.types.is_categorical_dtype(y) or y.nunique() < 10:
            # Classification problem
            mi_values = mutual_info_classif(X, y)
        else:
            # Regression problem
            mi_values = mutual_info_regression(X, y)
        
        # Normalize MI values to 0-1 range for comparison with threshold
        if len(mi_values) > 0:
            mi_max = max(mi_values) if max(mi_values) > 0 else 1
            mi_normalized = mi_values / mi_max
            
            # Create dictionary of feature: mi_value
            corr_values = {col: mi for col, mi in zip(feature_cols, mi_normalized) if mi > threshold}
        else:
            corr_values = {}
    
    # Create the list of columns to drop
    dropped_columns = list(corr_values.keys())
    
    
    if dropped_columns:
        print(f"\nIdentified {len(dropped_columns)} columns as outcome proxies (threshold: {threshold:.2f}, method: {method}):")
        if verbose:
            for col, val in corr_values.items():
                print(f"  - '{col}': {val:.4f}")
    else:
        print(f"\nNo outcome proxies found (threshold: {threshold:.2f}, method: {method})")
    
    # Drop columns if any were identified for removal
    if dropped_columns:
        work_df = work_df.drop(columns=dropped_columns)
    
    return work_df


def correlation_reduction(
    df: pd.DataFrame,
    dv: Optional[str] = None,
    threshold: float = 0.9,
    method: str = "pearson",
    verbose: bool = True
) -> pd.DataFrame:
    """
    Reduce the number of columns by dropping features that are highly correlated with each other.
    
    For each pair of highly correlated features, one will be dropped to reduce multicollinearity.
    If a target variable is specified, the feature with the lower correlation to the target will
    be dropped.
    
    Parameters
    ----------
    df : pd.DataFrame
        Your pandas dataframe
    dv : str, optional
        The column name of your outcome. If provided, when choosing between 
        correlated features, the one with higher correlation to the target will be kept.
    threshold : float, default=0.9
        The correlation threshold above which columns will be considered redundant.
        For example, the default value of 0.9 will identify columns that have
        correlations greater than 90% to each other.
    method : str, default="pearson"
        The correlation method to use. Options are:
        - "pearson": Standard correlation coefficient (linear relationships)
        - "spearman": Spearman rank correlation (monotonic relationships)
        - "mutual_info": Mutual information (any statistical dependency)
    verbose : bool, default=True
        Set to True to print outputs of columns being dropped. Set to False to suppress.
    
    Returns
    -------
    pd.DataFrame
        The transformed DataFrame with redundant correlated columns dropped
    
    Examples
    --------
    >>> new_df = reduce_correlation(df=my_df, dv='target', threshold=0.85, method="spearman")
    >>> print(f"Removed correlated columns")
    """
    # Parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if dv is not None and dv not in df.columns:
        warnings.warn(f"Specified DV '{dv}' not found in dataframe")
        dv = None
    
    if not isinstance(threshold, (int, float)):
        raise TypeError(f"threshold must be a number, got {type(threshold)}")
    
    if not (0 <= threshold <= 1):
        raise ValueError(f"threshold must be between 0 and 1, got {threshold}")
    
    valid_methods = ["pearson", "spearman", "mutual_info"]
    if method not in valid_methods:
        raise ValueError(f"method must be one of {valid_methods}, got {method}")
    
    # Create a deep copy of the dataframe
    work_df = df.copy(deep=True)
    
    # Identify numeric columns for correlation, excluding the target variable if specified
    feature_cols = work_df.select_dtypes(include=["number"]).columns.tolist()
    
    if dv is not None and dv in feature_cols:
        # Remove the target variable from the list of features to consider for removal
        feature_cols.remove(dv)
    
    # Ensure we have the target in numeric_cols for correlation calculations if it's numeric
    numeric_cols = feature_cols.copy()
    if dv is not None and dv in work_df.columns and pd.api.types.is_numeric_dtype(work_df[dv]):
        numeric_cols.append(dv)
    
    # Check if we have enough numeric columns to proceed
    if len(feature_cols) < 2:
        if verbose:
            print("Not enough numeric columns for correlation analysis")
        return work_df
    
    # Calculate correlations based on the chosen method
    if method in ["pearson", "spearman"]:
        # Standard correlation methods
        correlation_matrix = work_df[numeric_cols].corr(method=method).abs()
        
        # Create a list of feature pairs and their correlation
        corr_pairs = []
        for i in range(len(feature_cols)):
            for j in range(i+1, len(feature_cols)):
                # Get the column names
                col1 = feature_cols[i]
                col2 = feature_cols[j]
                
                # Find their positions in the correlation matrix
                idx1 = numeric_cols.index(col1)
                idx2 = numeric_cols.index(col2)
                
                # Check if correlation exceeds threshold
                if correlation_matrix.iloc[idx1, idx2] > threshold:
                    corr_pairs.append({
                        "feature1": col1,
                        "feature2": col2,
                        "correlation": correlation_matrix.iloc[idx1, idx2]
                    })
    
    elif method == "mutual_info":
        # For mutual information between features
        corr_pairs = []
        X = work_df[feature_cols]
        
        # Calculate pairwise mutual information
        for i in range(len(feature_cols)):
            for j in range(i+1, len(feature_cols)):
                feature1 = feature_cols[i]
                feature2 = feature_cols[j]
                
                # Skip if either column has all identical values
                if X[feature1].nunique() <= 1 or X[feature2].nunique() <= 1:
                    continue
                
                # Calculate mutual information between the two features
                mi = mutual_info_regression(
                    X[[feature1]], X[feature2].values.reshape(-1, 1)
                )[0]
                
                # Normalize by entropy for a 0-1 scale
                entropy1 = mutual_info_regression(
                    X[[feature1]], X[feature1].values.reshape(-1, 1)
                )[0]
                entropy2 = mutual_info_regression(
                    X[[feature2]], X[feature2].values.reshape(-1, 1)
                )[0]
                
                # Avoid division by zero
                if entropy1 > 0 and entropy2 > 0:
                    normalized_mi = mi / min(entropy1, entropy2)
                    
                    if normalized_mi > threshold:
                        corr_pairs.append({
                            "feature1": feature1,
                            "feature2": feature2,
                            "correlation": normalized_mi
                        })
    
    # Sort the correlated pairs by correlation value (descending)
    corr_pairs.sort(key=lambda x: x["correlation"], reverse=True)
    
    # Determine which features to drop
    to_drop = set()
    corr_details = {}
    
    if dv is not None and dv in work_df.columns:
        # If we have a target variable, calculate correlations to the target
        if method in ["pearson", "spearman"]:
            target_corr = work_df[numeric_cols].corr(method=method)[dv].abs()
            target_corr = target_corr.drop(dv) if dv in target_corr.index else target_corr
        else:  # mutual_info
            X = work_df[feature_cols]  # Only use feature columns, not target
            y = work_df[dv]
            
            # Determine if classification or regression
            if pd.api.types.is_categorical_dtype(y) or y.nunique() < 10:
                mi_values = mutual_info_classif(X, y)
            else:
                mi_values = mutual_info_regression(X, y)
            
            # Create a Series for target correlations
            target_corr = pd.Series(mi_values, index=feature_cols)
        
        # Process each correlated pair
        for pair in corr_pairs:
            # Skip if either feature is already marked for dropping
            if pair["feature1"] in to_drop or pair["feature2"] in to_drop:
                continue
            
            # Keep the feature with higher correlation to the target
            feature1_corr = target_corr.get(pair["feature1"], 0)
            feature2_corr = target_corr.get(pair["feature2"], 0)
            
            if feature1_corr >= feature2_corr:
                to_drop.add(pair["feature2"])
                corr_details[pair["feature2"]] = {
                    "correlated_with": pair["feature1"],
                    "correlation_value": pair["correlation"],
                    "target_correlation": feature2_corr,
                    "kept_feature_target_correlation": feature1_corr
                }
            else:
                to_drop.add(pair["feature1"])
                corr_details[pair["feature1"]] = {
                    "correlated_with": pair["feature2"],
                    "correlation_value": pair["correlation"],
                    "target_correlation": feature1_corr,
                    "kept_feature_target_correlation": feature2_corr
                }
    else:
        # If no target, just keep the first feature in each correlated pair
        for pair in corr_pairs:
            # Skip if either feature is already marked for dropping
            if pair["feature1"] in to_drop or pair["feature2"] in to_drop:
                continue
            
            # Default to keeping the first feature
            to_drop.add(pair["feature2"])
            corr_details[pair["feature2"]] = {
                "correlated_with": pair["feature1"],
                "correlation_value": pair["correlation"]
            }
    
    # Convert to list for consistent return type
    dropped_columns = list(to_drop)
    
    if verbose:
        if dropped_columns:
            print(f"\nDropping {len(dropped_columns)} columns due to high correlation (threshold: {threshold:.2f}, method: {method}):")
            for col in dropped_columns:
                details = corr_details[col]
                corr_msg = f"correlation: {details['correlation_value']:.4f}"
                if "target_correlation" in details:
                    corr_msg += f", target correlation: {details['target_correlation']:.4f}"
                print(f"  - '{col}' (correlated with '{details['correlated_with']}', {corr_msg})")
        else:
            print(f"\nNo highly correlated columns found (threshold: {threshold:.2f}, method: {method})")
    
    # Drop columns if any were identified for removal
    if dropped_columns:
        work_df = work_df.drop(columns=dropped_columns)
    
    return work_df
    
    return work_df