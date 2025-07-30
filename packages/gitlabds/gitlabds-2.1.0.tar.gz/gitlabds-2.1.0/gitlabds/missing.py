import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union, Set
import warnings
import random


def missing_values(
    df: pd.DataFrame,
    threshold: float = 0.0,
    method: Union[str, Dict[str, str]] = None,
    columns: Union[str, List[str]] = "all",
    constant_value: Any = None,
    verbose: bool = True,
    operation: str = "both"
) -> Union[Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]], Optional[List[str]], None]:
    """
    Detect and optionally fill missing values in a DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input pandas dataframe
    threshold : float, default=0.0
        The percent of missing values at which a column is considered for processing.
        For example, threshold=0.10 will only process columns with more than 10% missing values.
    method : str or dict, optional
        Method to fill missing values or dictionary mapping columns to methods.
        Options for methods:
            - "mean": Fill with column mean (numeric only)
            - "median": Fill with column median (numeric only)
            - "zero": Fill with 0
            - "constant": Fill with the value specified in constant_value
            - "random": Fill with random values sampled from the column's distribution
            - "drop_column": Remove columns with missing values
            - "drop_row": Remove rows with any missing values in specified columns
        If None, only detection is performed without filling.
    columns : str or list, default="all"
        Columns to check and/or fill. If "all", processes all columns with missing values.
    constant_value : any, optional
        Value to use when method="constant" for all columns or when specific columns
        use the constant method in a method dictionary.
    verbose : bool, default=True
        Whether to print detailed information about missing values.
    operation : str, default="both"
        Operation mode:
            - "check": Only check for missing values, don't fill
            - "fill": Fill missing values and return filled dataframe
            - "both": Check and fill missing values
        
    Returns
    -------
    Union[Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]], Optional[List[str]], None]
        - If operation="check": Returns list of column names with missing values or None
        - If operation="fill" or "both": Returns a tuple containing:
            - DataFrame with missing values handled
            - Dictionary with missing value information that can be used with apply_missing_fill()
    
    Examples
    --------
    >>> # Just checking for missing values
    >>> missing_values(df, threshold=0.05, operation="check")
    
    >>> # Fill all columns with missing values using mean
    >>> df_filled, missing_info = missing_values(df, method="mean")
    
    >>> # Fill specific columns with different methods
    >>> df_filled, missing_info = missing_values(
    ...     df, 
    ...     method={"col_A": "median", "col_B": "constant"}, 
    ...     constant_value=0,
    ...     operation="fill"
    ... )
    """
    # Parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
        
    if not isinstance(threshold, (int, float)):
        raise TypeError(f"threshold must be a number, got {type(threshold)}")
    
    if not (0 <= threshold <= 1):
        raise ValueError(f"threshold must be between 0 and 1, got {threshold}")
    
    valid_operations = ["check", "fill", "both"]
    if operation not in valid_operations:
        raise ValueError(f"operation must be one of {valid_operations}, got {operation}")
    
    valid_methods = ["mean", "median", "zero", "constant", "random", "drop_column", "drop_row"]
    
    if method is not None:
        if isinstance(method, str):
            if method not in valid_methods:
                raise ValueError(f"method must be one of {valid_methods} or a dictionary, got {method}")
            if method == "constant" and constant_value is None:
                raise ValueError("constant_value must be provided when method='constant'")
        elif isinstance(method, dict):
            for col, col_method in method.items():
                if col_method not in valid_methods:
                    raise ValueError(f"method for column {col} must be one of {valid_methods}, got {col_method}")
        else:
            raise TypeError(f"method must be a string or dictionary, got {type(method)}")
    
    # Create a deep copy of the dataframe if we're going to modify it
    if operation in ["fill", "both"]:
        work_df = df.copy(deep=True)
    else:
        work_df = df  # No need to copy if we're just checking
    
    # Get missing value statistics for all columns
    missing_stats = pd.DataFrame({
        'column_name': df.columns,
        'missing_count': df.isnull().sum(),
        'missing_percent': df.isnull().sum() / len(df)
    })
    
    # Filter columns based on threshold
    missing_stats = missing_stats[missing_stats['missing_percent'] > threshold]
    
    # Print summary of missing values - only for check and both operations
    if operation in ["check", "both"]:
        print(f"\nMissing Values Summary ({len(df)} rows total):")
        print(f"- Total columns with missing values: {len(missing_stats)}")
        print(f"- Total missing cells: {missing_stats['missing_count'].sum()}")
        print(f"- Percentage of all cells missing: {missing_stats['missing_count'].sum() / (len(df) * len(df.columns)):.2%}")
        
        # Print detailed missing value information if any found
        if len(missing_stats) > 0:
            print("\nColumns with missing values:")
            for _, row in missing_stats.iterrows():
                print(f"- {row['column_name']}: {row['missing_count']} values ({row['missing_percent']:.2%})")
        else:
            print("No columns with missing values found above the threshold.")
    
    # If no missing values found, return early
    if len(missing_stats) == 0:
        if operation == "check":
            return None
        else:
            return work_df, {}
    
    # If only checking, return column names with missing values
    if operation == "check":
        return missing_stats['column_name'].tolist()
    
    # Determine columns to process
    if columns == "all":
        columns_to_process = missing_stats['column_name'].tolist()
    else:
        if isinstance(columns, str):
            columns = [columns]
        
        # Validate columns exist in the dataframe
        invalid_columns = [col for col in columns if col not in df.columns]
        if invalid_columns:
            warnings.warn(f"Columns {invalid_columns} not found in dataframe and will be skipped")
        
        # Filter columns that have missing values
        columns_to_process = [col for col in columns if col in missing_stats['column_name'].tolist()]
    
    if not columns_to_process:
        warnings.warn("No columns with missing values match the specified criteria")
        return work_df, {}
    
    # Initialize missing_info dictionary to store fill information
    missing_info = {}
    
    # Counter for different methods used
    method_counts = {m: 0 for m in valid_methods}
    
    # Process each column
    for col in columns_to_process:
        # Determine method for this column
        col_method = method
        if isinstance(method, dict):
            if col in method:
                col_method = method[col]
            else:
                # Skip columns not in the method dictionary
                continue
        
        # Calculate missing statistics for this column
        missing_count = df[col].isnull().sum()
        missing_percent = missing_count / len(df)
        
        # Skip if column doesn't meet threshold
        if missing_percent <= threshold:
            continue
        
        # Drop column if requested
        if col_method == "drop_column":
            work_df = work_df.drop(columns=[col])
            missing_info[col] = {"method": "drop_column", "fill_value": None}
            method_counts["drop_column"] += 1
            
            if verbose:
                print(f"Dropped column '{col}' with {missing_count} missing values ({missing_percent:.2%})")
            
            continue
        
        # Apply fill method
        fill_value = None
        
        if col_method == "mean":
            if pd.api.types.is_numeric_dtype(df[col]):
                fill_value = df[col].mean()
                work_df[col] = work_df[col].fillna(fill_value)
                method_counts["mean"] += 1
            else:
                warnings.warn(f"Column '{col}' is not numeric, cannot use mean. Skipping.")
                continue
                
        elif col_method == "median":
            if pd.api.types.is_numeric_dtype(df[col]):
                fill_value = df[col].median()
                work_df[col] = work_df[col].fillna(fill_value)
                method_counts["median"] += 1
            else:
                warnings.warn(f"Column '{col}' is not numeric, cannot use median. Skipping.")
                continue
                
        elif col_method == "zero":
            fill_value = 0
            work_df[col] = work_df[col].fillna(fill_value)
            method_counts["zero"] += 1
            
        elif col_method == "constant":
            fill_value = constant_value
            work_df[col] = work_df[col].fillna(fill_value)
            method_counts["constant"] += 1
            
        elif col_method == "random":
            # Sample from non-missing values in the column
            non_missing_values = df[col].dropna().values
            if len(non_missing_values) > 0:
                # Generate random samples for each missing value
                missing_indices = df[col].isna()
                random_samples = np.random.choice(
                    non_missing_values, 
                    size=missing_count, 
                    replace=True
                )
                
                # Fill missing values with random samples
                work_df.loc[missing_indices, col] = random_samples
                method_counts["random"] += 1
            else:
                warnings.warn(f"Column '{col}' has no non-missing values for random sampling. Skipping.")
                continue
        
        # Store fill information
        if col_method != "drop_column":
            missing_info[col] = {"method": col_method, "fill_value": fill_value}
            
            if verbose:
                print(f"Filled column '{col}' using {col_method} method " + 
                     (f"with value {fill_value}" if fill_value is not None else "") +
                     f" ({missing_count} values, {missing_percent:.2%})")
    
    # Handle drop_row if it's the global method
    if method == "drop_row":
        before_count = len(work_df)
        work_df = work_df.dropna(subset=columns_to_process)
        after_count = len(work_df)
        rows_dropped = before_count - after_count
        
        method_counts["drop_row"] = rows_dropped
        
        if verbose:
            print(f"Dropped {rows_dropped} rows with missing values in specified columns " +
                 f"({rows_dropped/before_count:.2%} of data)")
    
    # Print summary of actions taken, regardless of operation mode
    # This is important information for when filling is done
    non_zero_methods = {m: count for m, count in method_counts.items() if count > 0}
    if non_zero_methods:
        print("\nMissing value filling summary:")
        for m, count in non_zero_methods.items():
            if m == "drop_row":
                print(f"- {count} rows dropped")
            elif m == "drop_column":
                print(f"- {count} columns dropped")
            else:
                print(f"- {count} columns filled using {m} method")
    
    return work_df, missing_info


def apply_missing_values(
    df: pd.DataFrame,
    missing_info: Dict[str, Dict[str, Any]]
) -> pd.DataFrame:
    """
    Apply missing value filling to a DataFrame using previously generated missing_info.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to apply missing value filling to
    missing_info : Dict[str, Dict[str, Any]]
        Dictionary with missing value information generated by missing_values()
        
    Returns
    -------
    pd.DataFrame
        DataFrame with missing values filled according to missing_info
        
    Examples
    --------
    >>> # First generate missing_info
    >>> _, missing_info = missing_values(train_df, method="mean")
    >>> 
    >>> # Then apply to test data
    >>> test_df_filled = apply_missing_fill(test_df, missing_info)
    """
    # Parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
        
    if not isinstance(missing_info, dict):
        raise TypeError("missing_info must be a dictionary")
    
    # Create a copy of the dataframe
    work_df = df.copy(deep=True)
    
    # Apply each fill operation
    for col, info in missing_info.items():
        method = info.get("method")
        fill_value = info.get("fill_value")
        
        # Skip if column doesn't exist in the dataframe
        if col not in work_df.columns:
            warnings.warn(f"Column '{col}' not found in dataframe. Skipping.")
            continue
        
        # Apply the appropriate method
        if method == "drop_column":
            work_df = work_df.drop(columns=[col])
        elif method in ["mean", "median", "zero", "constant"]:
            work_df[col] = work_df[col].fillna(fill_value)
        elif method == "random":
            # For random fill, we need to generate new random samples
            missing_count = work_df[col].isna().sum()
            if missing_count > 0:
                # Sample from non-missing values in the column
                non_missing_values = work_df[col].dropna().values
                if len(non_missing_values) > 0:
                    # Generate random samples for each missing value
                    missing_indices = work_df[col].isna()
                    random_samples = np.random.choice(
                        non_missing_values, 
                        size=missing_count, 
                        replace=True
                    )
                    
                    # Fill missing values with random samples
                    work_df.loc[missing_indices, col] = random_samples
    
    return work_df