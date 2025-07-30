import pandas as pd
from scipy import stats
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
import warnings


def mad_outliers(
    df: pd.DataFrame,
    dv: Optional[str] = None,
    min_levels: int = 10,
    columns: Union[str, List[str]] = "all",
    threshold: float = 4.0,
    auto_adjust_skew: bool = False,
    verbose: bool = True,
    windsor_threshold: float = 0.01
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """
    Median Absolute Deviation for outlier detection and correction. By default will windsor all numeric values
    in your dataframe that are more than 4 standard deviations above or below the median.
    
    Parameters
    ----------
    df : pd.DataFrame
        Your pandas dataframe
    dv : str, optional
        The column name of your outcome. Entering your outcome variable will prevent it from being windsored.
    min_levels : int, default=10
        Only include columns that have at least the number of levels specified.
    columns : list or str, default="all"
        Will examine all numeric columns by default. To limit to just a subset of columns, 
        pass a list of column names. Doing so will ignore any constraints from 'dv' and 'min_levels'.
    threshold : float, default=4.0
        Windsor values greater than this number of standard deviations from the median.
    auto_adjust_skew : bool, default=False
        Whether to automatically adjust thresholds based on column skewness:
    verbose : bool, default=True
        Set to True to print outputs of windsoring being done. Set to False to suppress.
    windsor_threshold : float, default=0.01
        Only windsor values that affect less than this percentage of the population (0-1 range).

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]
        A tuple containing:
        - The transformed DataFrame by windsoring outliers
        - Dictionary of outlier limits that can be used with apply_outliers()
    """

    # Enhanced parameter validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
        
    if min_levels < 1:
        raise ValueError(f"min_levels must be at least 1, got {min_levels}")
        
    if threshold <= 0:
        raise ValueError(f"threshold must be positive, got {threshold}")
        
    if windsor_threshold < 0 or windsor_threshold > 1:
        raise ValueError(f"windsor_threshold must be between 0 and 1, got {windsor_threshold}")
    
    if auto_adjust_skew not in [True, False]:
        raise ValueError(f"auto_adjust_skew must be one of ['auto', True, False], got {auto_adjust_skew}")
    
    
    # Create a deep copy of the dataframe
    work_df = df.copy(deep=True)
    
    # Determine columns to process with validation
    if columns == "all":
        var_list = pd.DataFrame(work_df.select_dtypes(include=["number"]).nunique(dropna=True, axis=0))

        # Exclude DV from outliers if one is provided
        if dv is not None:
            if dv not in work_df.columns:
                warnings.warn(f"Specified DV '{dv}' not found in dataframe")
            elif dv in var_list.index.to_list():
                var_list.drop(dv, inplace=True)

        # Exclude Numeric values that are below min_levels threshold
        var_list = var_list[var_list[0] >= min_levels]

        # Set as List
        var_list = var_list.index.to_list()
    else:
        if isinstance(columns, list):
            var_list = columns
        else:
            raise TypeError(f"columns must be a list, got {type(columns)}")
        
        # Validate columns exist in the dataframe
        missing_columns = [col for col in var_list if col not in work_df.columns]
        if missing_columns:
            warnings.warn(f"Columns {missing_columns} not found in dataframe")
            var_list = [col for col in var_list if col in work_df.columns]
    
    # Dictionary to store outlier limits
    outlier_limits = {}
    
    # Process each column
    if verbose:
        print("\nOutliers")
        print(f"Processing {len(var_list)} columns for outliers")
    
    for v in var_list:
        # Skip columns that do not exist or are not numeric
        if v not in work_df.columns:
            if verbose:
                print(f"Warning: Column '{v}' not found in dataframe, skipping")
            continue
            
        if not pd.api.types.is_numeric_dtype(work_df[v]):
            if verbose:
                print(f"Warning: Column '{v}' is not numeric, skipping")
            continue

        # Initialize thresholds to the base threshold
        lower_threshold = threshold
        upper_threshold = threshold
        
        # Determine if we should adjust for skew
        skew = work_df[v].skew()
                        
        # Apply skew adjustment if needed
        if auto_adjust_skew:
           # Logarithmic adjustment for right-skewed data. Taking the log to make it less sensitive to extreme values
            if skew > 0:
                # Adjust upper threshold proportionally to skew, up to 3x for skew of 2.0 or more
                adjustment_factor = 1 + np.log(1 + min(abs(skew), 3)) / 2
                upper_threshold = threshold * adjustment_factor
                if verbose:
                    print(f"Column '{v}' is right-skewed (skew={skew:.2f}), adjusted upper threshold to {upper_threshold:.2f}")
                    
            # Logarithmic adjustment for left-skewed data. Taking the log to make it less sensitive to extreme values
            elif skew < 0:
                # Adjust lower threshold proportionally to absolute skew, up to 3x for skew of -2.0 or less
                adjustment_factor = 1 + np.log(1 + min(abs(skew), 3)) / 2
                lower_threshold = threshold * adjustment_factor     
                if verbose:
                    print(f"Column '{v}' is left-skewed (skew={skew:.2f}), adjusted lower threshold to {lower_threshold:.2f}")           
        
        # Get column statistics
        column_dtype = work_df[v].dtype
        
        # Determine median and MAD
        median = np.nanmedian(work_df[v])

        try:
            mad = stats.median_abs_deviation(work_df[v], axis=0, scale=1, nan_policy='omit')
        except Exception as e:
            if verbose:
                print(f"Warning: Could not compute MAD for '{v}': {str(e)}, skipping")
            continue
        
        # Get original min/max
        old_min = work_df[v].min()
        old_max = work_df[v].max()
        
        # Handle zero MAD
        if np.isnan(mad):
            if verbose:
                print(f"Warning: No variation in column '{v}', skipping")
                continue

        elif mad == 0:
            z_scores = 0.6745 * (work_df[v] - mad)  # 0.6745 to standardize it to 1 SD
            new_min = old_min
            new_max = old_max

        else:
            z_scores = 0.6745 * (work_df[v] - median) / mad
            new_min = median - ((mad * lower_threshold) / 0.6745)
            new_max = median + ((mad * upper_threshold) / 0.6745)
        
        # Maintain integer type if original was integer
        if pd.api.types.is_integer_dtype(column_dtype):
            new_min = np.floor(new_min)
            new_max = np.ceil(new_max)

        # Cast to original dtype
        new_min = np.dtype(column_dtype).type(new_min)
        new_max = np.dtype(column_dtype).type(new_max)


        # Count affected rows
        min_affected = (z_scores < -lower_threshold).sum()
        max_affected = (z_scores > upper_threshold).sum()  
        
        min_pct = min_affected / len(work_df)
        max_pct = max_affected / len(work_df)

        # Track if any winsorization happened for this column
        column_limits = None

        # Windsor lower values if needed
        if (min_pct < windsor_threshold) and (min_affected > 0) and (new_min != old_min):

            work_df[v] = work_df[v].clip(lower=new_min)
            # Cast back to original dtype for integers
            if pd.api.types.is_integer_dtype(column_dtype):
                work_df[v] = work_df[v].astype(column_dtype)
            
            # Create the limits dictionary when first needed
            if column_limits is None:
                column_limits = {'dtype': str(column_dtype)}
            
            column_limits['lower_bound'] = float(new_min)
            
            if verbose:  
                print(f"   {v} - MAD: {mad:.4f}; Lower Windsor Value: {new_min}, Rows affected: {min_affected} ({min_pct:.2%})")

        # Windsor upper values if needed
        if (max_pct < windsor_threshold) and (max_affected > 0) and (new_max != old_max):

            work_df[v] = work_df[v].clip(upper=new_max)
            # Cast back to original dtype for integers
            if pd.api.types.is_integer_dtype(column_dtype):
                work_df[v] = work_df[v].astype(column_dtype)
            
            # Create the limits dictionary when first needed
            if column_limits is None:
                column_limits = {'dtype': str(column_dtype)}
            
            column_limits['upper_bound'] = float(new_max)
            
            if verbose:
                print(f"   {v} - MAD: {mad:.4f}; Upper Windsor Value: {new_max}, Rows affected: {max_affected} ({max_pct:.2%})")

        # Add column to outlier_limits if any winsorization was done
        if column_limits is not None:
            outlier_limits[v] = column_limits

    # Return both the modified dataframe and the outlier limits
    return work_df, outlier_limits


def apply_outliers(df: pd.DataFrame, outlier_limits: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Apply outlier limits to the dataframe, maintaining original data types.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to transform.
    outlier_limits : dict
        Dictionary of outlier limits where keys are column names and values are
        dictionaries containing 'lower_bound' and/or 'upper_bound' and 'dtype'.
    
    Returns
    -------
    pandas.DataFrame
        Transformed dataframe with outliers handled.
    """
    # Validate input
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
        
    if not isinstance(outlier_limits, dict):
        raise TypeError("outlier_limits must be a dictionary")
    
    # Make a copy to avoid modifying the original
    work_df = df.copy()
    
    # Validate column names before processing
    missing_columns = [col for col in outlier_limits if col not in work_df.columns]
    if missing_columns:
        warnings.warn(f"Columns {missing_columns} not found in dataframe and will be skipped")
    
    # Apply limits
    for column, params in outlier_limits.items():
        if column not in work_df.columns:
            continue
            
        if not pd.api.types.is_numeric_dtype(work_df[column]):
            warnings.warn(f"Column '{column}' is not numeric and will be skipped")
            continue
            
        # Keep track of original dtype
        original_dtype = work_df[column].dtype
        
        # Apply lower bound if specified
        if 'lower_bound' in params and params['lower_bound'] is not None:
            work_df[column] = np.where(
                work_df[column] < params['lower_bound'], 
                params['lower_bound'], 
                work_df[column]
            )
            
        # Apply upper bound if specified
        if 'upper_bound' in params and params['upper_bound'] is not None:
            work_df[column] = np.where(
                work_df[column] > params['upper_bound'], 
                params['upper_bound'], 
                work_df[column]
            )
        
        # Cast back to original data type for integers
        if 'dtype' in params and params['dtype'].startswith('int'):
            work_df[column] = work_df[column].astype(original_dtype)
    
    return work_df