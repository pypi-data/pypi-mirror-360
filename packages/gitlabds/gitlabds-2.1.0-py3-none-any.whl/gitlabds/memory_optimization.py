import pandas as pd
import numpy as np
from typing import Union, List, Optional
import warnings
from tqdm import tqdm


def reduce_memory_usage(
    df: Union[pd.DataFrame, pd.Series, List[pd.DataFrame]],
    categorical_threshold: int = 50,
    convert_categorical: bool = False,
    convert_datetime: bool = True,
    verbose: bool = True,
    show_progress: bool = True,
    exclude_columns: Optional[List[str]] = None
) -> Union[pd.DataFrame, pd.Series, List[pd.DataFrame]]:
    """
    Reduce the memory usage of pandas DataFrame(s) by optimizing data types.
    
    This function reduces memory usage by:
    1. Converting numeric columns to the smallest possible type that can represent the data
    2. Optionally converting string columns to categorical type if they have few unique values
    3. Optionally optimizing datetime columns to more efficient formats
    
    Parameters
    ----------
    df : Union[pd.DataFrame, pd.Series, List[pd.DataFrame]]
        Input dataframe(s) to optimize
    categorical_threshold : int, default=50
        Maximum number of unique values for a string column to be converted to categorical
    convert_categorical : bool, default=False
        Whether to convert string columns with low cardinality to categorical type
    convert_datetime : bool, default=True
        Whether to optimize datetime columns
    verbose : bool, default=True
        Whether to print memory usage statistics
    show_progress : bool, default=True
        Whether to show progress bar for optimization
    exclude_columns : List[str], optional
        List of column names to exclude from optimization
    
    Returns
    -------
    Union[pd.DataFrame, pd.Series, List[pd.DataFrame]]
        Optimized dataframe(s)
    """
    # Define reusable functions to avoid code duplication
    def get_memory_usage(df_obj):
        if isinstance(df_obj, pd.Series):
            return df_obj.memory_usage(deep=True) / 1024**2
        else:
            return df_obj.memory_usage(deep=True).sum() / 1024**2
    
    def optimize_single_df(df_input, exclude_list=None):
        """Inner function to optimize a single dataframe"""
        # Input validation
        if not isinstance(df_input, (pd.DataFrame, pd.Series)):
            raise TypeError("Input must be a pandas DataFrame or Series")
        
        # Make a copy to avoid modifying the original
        df_result = df_input.copy()
        
        if exclude_list is None:
            exclude_list = []
        
        start_mem = get_memory_usage(df_result)
        column_changes = {}
        
        all_cols = df_result.columns if isinstance(df_result, pd.DataFrame) else [df_result.name]
        process_cols = [col for col in all_cols if col not in exclude_list]
        
        # Use tqdm for progress tracking
        iterator = tqdm(process_cols, desc="Optimizing columns") if show_progress else process_cols
        
        for col in iterator:
            # Handle Series case
            if isinstance(df_result, pd.Series):
                series = df_result
            else:
                series = df_result[col]
            
            col_dtype = series.dtype
            
            # Process numerics
            if pd.api.types.is_numeric_dtype(col_dtype):
                # Get min and max safely accounting for NaN values
                c_min = series.min() if not series.isna().all() else 0
                c_max = series.max() if not series.isna().all() else 0
                
                # Check if column has NaN values
                has_null = series.isna().any()
                
                # For integers
                if pd.api.types.is_integer_dtype(col_dtype):
                    # Can only convert to nullable integer dtype if there are nulls
                    if has_null:
                        # Choose appropriate nullable integer dtype
                        if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                            new_dtype = pd.Int8Dtype()
                        elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                            new_dtype = pd.Int16Dtype()
                        elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                            new_dtype = pd.Int32Dtype()
                        else:
                            new_dtype = pd.Int64Dtype()
                    else:
                        # Regular integer dtype for non-null columns
                        if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                            new_dtype = np.int8
                        elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                            new_dtype = np.int16
                        elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                            new_dtype = np.int32
                        else:
                            new_dtype = np.int64
                # For floats
                else:
                    # If column has NaN, must use at least float16
                    if has_null:
                        if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                            # Check if we can use float16 based on precision requirements
                            if abs(c_min) < 65500 and abs(c_max) < 65500:
                                new_dtype = np.float16
                            else:
                                new_dtype = np.float32
                        else:
                            new_dtype = np.float64
                    else:
                        if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max and abs(c_min) < 65500 and abs(c_max) < 65500:
                            new_dtype = np.float16
                        elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                            new_dtype = np.float32
                        else:
                            new_dtype = np.float64
                
                # Apply the new dtype
                try:
                    if isinstance(df_result, pd.Series):
                        df_result = df_result.astype(new_dtype)
                    else:
                        df_result[col] = df_result[col].astype(new_dtype)
                    
                    column_changes[col] = (str(col_dtype), str(new_dtype))
                except (ValueError, TypeError) as e:
                    warnings.warn(f"Could not convert column {col} to {new_dtype}: {str(e)}")
            
            # Process string columns for categorical conversion
            elif convert_categorical and pd.api.types.is_string_dtype(col_dtype):
                n_unique = series.nunique()
                
                if n_unique <= categorical_threshold:
                    try:
                        if isinstance(df_result, pd.Series):
                            df_result = df_result.astype('category')
                        else:
                            df_result[col] = df_result[col].astype('category')
                        
                        column_changes[col] = (str(col_dtype), 'category')
                    except Exception as e:
                        warnings.warn(f"Could not convert string column {col} to category: {str(e)}")
            
            # Process datetime columns
            elif convert_datetime and pd.api.types.is_datetime64_dtype(col_dtype):
                # Check date range to see if we can use a more efficient format
                min_date = series.min()
                max_date = series.max()
                
                if pd.notna(min_date) and pd.notna(max_date):
                    # Check if dates fall within pandas.Timestamp COMPAT_DAYS
                    min_year = min_date.year if not pd.isna(min_date) else 1970
                    max_year = max_date.year if not pd.isna(max_date) else 2030
                    
                    if 1900 <= min_year and max_year <= 2100:
                        # Use more compact datetime representation
                        try:
                            series_new = pd.to_datetime(series)
                            if isinstance(df_result, pd.Series):
                                df_result = series_new
                            else:
                                df_result[col] = series_new
                            
                            column_changes[col] = (str(col_dtype), 'datetime64[ns]')
                        except Exception as e:
                            warnings.warn(f"Could not optimize datetime column {col}: {str(e)}")
        
        # Calculate memory usage after optimization
        end_mem = get_memory_usage(df_result)
        reduction_mb = start_mem - end_mem
        reduction_pct = 100 * reduction_mb / start_mem if start_mem > 0 else 0

        print(f"Memory usage decreased from {start_mem:.2f} MB to {end_mem:.2f} MB ({reduction_pct:.1f}% reduction)")
        
        if verbose:
            if column_changes:
                print("\nColumn dtype changes:")
                for col, (before, after) in column_changes.items():
                    if before != after:
                        print(f"  {col}: {before} → {after}")
        
        return df_result
    
    # Process single DataFrame/Series or list of DataFrames
    exclude_cols = exclude_columns if exclude_columns is not None else []
    
    if isinstance(df, list):
        # Handle list of dataframes
        result_dfs = []
        total_before = 0
        total_after = 0
        
        for i, single_df in enumerate(df):
            if verbose:
                print(f"\nOptimizing DataFrame {i+1}/{len(df)}")
            
            before_mem = get_memory_usage(single_df)
            total_before += before_mem
            
            opt_df = optimize_single_df(single_df, exclude_cols)
            result_dfs.append(opt_df)
            
            after_mem = get_memory_usage(opt_df)
            total_after += after_mem
        
        if verbose and len(df) > 1:
            reduction_pct = 100 * (total_before - total_after) / total_before if total_before > 0 else 0
            print(f"\nTotal memory usage decreased from {total_before:.2f} MB to {total_after:.2f} MB ({reduction_pct:.1f}% reduction)")
        
        return result_dfs
    else:
        # Handle single dataframe
        result = optimize_single_df(df, exclude_cols)
        return result


def sparse_encode_df(
    df: pd.DataFrame, 
    fill_value: Union[int, float, str] = 0, 
    sparse_columns: Optional[List[str]] = None,
    sparsity_threshold: float = 0.5,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Convert appropriate columns to Pandas SparseArray format for memory savings.
    
    Particularly effective for dataframes with many constant or repeated values.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe to optimize
    fill_value : Union[int, float, str], default=0
        The value to treat as fill value for the sparse encoding
    sparse_columns : Optional[List[str]], default=None
        List of columns to convert to sparse. If None, will check all columns.
    sparsity_threshold : float, default=0.5
        Minimum ratio of fill_value occurrences required to apply sparse encoding
    verbose : bool, default=True
        Whether to print memory usage statistics
        
    Returns
    -------
    pd.DataFrame
        DataFrame with applicable columns converted to sparse format
    """
    result_df = df.copy()
    
    # Determine which columns to convert
    if sparse_columns is None:
        # Default to numeric columns
        process_columns = [
            col for col in df.columns 
            if pd.api.types.is_numeric_dtype(df[col].dtype)
        ]
    else:
        process_columns = [col for col in sparse_columns if col in df.columns]
    
    if verbose:
        print(f"Examining {len(process_columns)} columns for sparse encoding...")
        original_mem = df.memory_usage(deep=True).sum() / 1024**2
    
    # Track columns and memory savings
    converted_columns = []
    total_savings_mb = 0
    
    # Process columns
    for col in process_columns:
        sparsity = (df[col] == fill_value).mean()
        
        # Only convert if there's a reasonable sparsity level
        if sparsity > sparsity_threshold:
            try:
                # Measure memory before conversion
                if verbose:
                    before_mem = df[col].memory_usage(deep=True) / 1024**2
                
                # Convert to sparse
                result_df[col] = pd.arrays.SparseArray(df[col], fill_value=fill_value)
                converted_columns.append(col)
                
                # Calculate savings if verbose
                if verbose:
                    after_mem = result_df[col].memory_usage(deep=True) / 1024**2
                    savings_mb = before_mem - after_mem
                    total_savings_mb += savings_mb
                    print(f"  {col}: {sparsity:.1%} {fill_value}s, saved {savings_mb:.2f} MB")
            except Exception as e:
                warnings.warn(f"Could not convert column {col} to sparse: {str(e)}")
    
    if verbose:
        final_mem = result_df.memory_usage(deep=True).sum() / 1024**2
        print(f"\nConverted {len(converted_columns)} columns to sparse format")
        print(f"Total memory usage: {original_mem:.2f} MB → {final_mem:.2f} MB")
        print(f"Sparse encoding saved {total_savings_mb:.2f} MB ({100*total_savings_mb/original_mem:.1f}% of original)")
    
    return result_df


def identify_categorical_candidates(df: pd.DataFrame, string_only: bool = False, verbose: bool = True) -> pd.DataFrame:
    """
    Identify columns that would benefit from conversion to categorical type.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    string_only : bool, default=False
        Whether to only analyze string columns
    verbose : bool, default=True
        Whether to print summary information
        
    Returns
    -------
    pd.DataFrame
        DataFrame with analysis of potential memory savings
    """
    stats = []
    
    for col in df.columns:
        # Skip non-string columns if string_only is True
        if string_only and not pd.api.types.is_string_dtype(df[col].dtype):
            continue
        
        # Skip already categorical columns
        if pd.api.types.is_categorical_dtype(df[col].dtype):
            continue
        
        current_size = df[col].memory_usage(deep=True)
        nunique = df[col].nunique()
        
        # Estimate memory usage if converted to categorical
        if nunique > 0:  # Avoid division by zero
            # Estimate size of the categories themselves
            if pd.api.types.is_string_dtype(df[col].dtype):
                # For strings, estimate average string length + overhead
                sample = df[col].dropna().sample(min(1000, len(df)))
                avg_len = sample.str.len().mean() if len(sample) > 0 else 0
                cat_size = avg_len * nunique  # Size of category labels
            else:
                # For other types, use the size of the original dtype
                cat_size = nunique * df[col].dtype.itemsize
            
            # Size of the integer codes (1, 2, 4, or 8 bytes per value)
            if nunique <= 2**8:
                codes_size = len(df) * 1  # uint8
            elif nunique <= 2**16:
                codes_size = len(df) * 2  # uint16
            elif nunique <= 2**32:
                codes_size = len(df) * 4  # uint32
            else:
                codes_size = len(df) * 8  # uint64
            
            # Total estimated categorical size
            estimated_cat_size = cat_size + codes_size
            
            # Calculate savings
            savings = current_size - estimated_cat_size
            savings_pct = (savings / current_size) * 100 if current_size > 0 else 0
            
            stats.append({
                'column': col,
                'dtype': str(df[col].dtype),
                'unique_values': nunique,
                'unique_pct': (nunique / len(df)) * 100,
                'current_size_kb': current_size / 1024,
                'estimated_cat_size_kb': estimated_cat_size / 1024,
                'savings_kb': savings / 1024,
                'savings_pct': savings_pct,
                'recommended': savings_pct > 20 and nunique < len(df) * 0.5  # Arbitrary threshold
            })
    
    results = pd.DataFrame(stats).sort_values('savings_kb', ascending=False)
    
    if verbose and not results.empty:
        recommended = results[results['recommended']]
        total_savings = recommended['savings_kb'].sum() / 1024  # Convert to MB
        
        print(f"Found {len(results)} columns that could be converted to categorical type")
        print(f"Recommended converting {len(recommended)} columns for highest memory savings")
        
        if len(recommended) > 0:
            print(f"Potential memory savings: {total_savings:.2f} MB")
            print("\nTop 5 recommended columns:")
            for _, row in recommended.head(5).iterrows():
                print(f"  {row['column']}: {row['unique_values']} unique values, would save {row['savings_kb']/1024:.2f} MB ({row['savings_pct']:.1f}%)")
    
    return results


def compact_categorical(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Optimize categorical columns by ensuring they use the minimum memory footprint.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with categorical columns
    verbose : bool, default=True
        Whether to print memory usage statistics
        
    Returns
    -------
    pd.DataFrame
        Dataframe with optimized categorical columns
    """
    result_df = df.copy()
    cat_columns = [col for col in df.columns if pd.api.types.is_categorical_dtype(df[col])]
    
    if not cat_columns:
        if verbose:
            print("No categorical columns found in the dataframe.")
        return result_df
    
    if verbose:
        print(f"Optimizing {len(cat_columns)} categorical columns...")
        before_mem = sum(df[col].memory_usage(deep=True) for col in cat_columns) / 1024**2
    
    # Keep track of dtype changes
    dtype_changes = {}
    
    for col in cat_columns:
        # Get the category codes to determine the range
        codes = result_df[col].cat.codes
        code_min, code_max = codes.min(), codes.max()
        
        # Record original dtype
        original_dtype = result_df[col].dtype
        
        # Determine the smallest integer dtype that can represent the categories
        if code_min >= 0:
            if code_max < 2**8:
                dtype = 'uint8'
            elif code_max < 2**16:
                dtype = 'uint16'
            elif code_max < 2**32:
                dtype = 'uint32'
            else:
                dtype = 'uint64'
        else:
            if code_min >= -2**7 and code_max < 2**7:
                dtype = 'int8'
            elif code_min >= -2**15 and code_max < 2**15:
                dtype = 'int16'
            elif code_min >= -2**31 and code_max < 2**31:
                dtype = 'int32'
            else:
                dtype = 'int64'
        
        # Set the categorical dtype
        result_df[col] = pd.Categorical(
            result_df[col],
            categories=result_df[col].cat.categories,
            ordered=result_df[col].cat.ordered
        )
        
        # Update the categorical codes dtype
        result_df[col] = result_df[col].astype(f'category:{dtype}')
        
        # Record the change
        dtype_changes[col] = (str(original_dtype), f'category:{dtype}')
    
    if verbose:
        after_mem = sum(result_df[col].memory_usage(deep=True) for col in cat_columns) / 1024**2
        savings = before_mem - after_mem
        
        print(f"Memory usage for categorical columns: {before_mem:.2f} MB → {after_mem:.2f} MB")
        print(f"Saved {savings:.2f} MB ({100*savings/before_mem:.1f}% of categorical columns)")
        
        print("\nCategory dtype changes:")
        for col, (before, after) in dtype_changes.items():
            if before != after:
                print(f"  {col}: {before} → {after}")
    
    return result_df


def memory_profile_df(df: pd.DataFrame, detailed: bool = False) -> pd.DataFrame:
    """
    Generate a detailed memory usage profile of a DataFrame.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to profile
    detailed : bool, default=False
        Whether to include additional details like unique values
        
    Returns
    -------
    pd.DataFrame
        DataFrame with memory usage statistics by column
    """
    # Get memory usage by column
    usage_bytes = df.memory_usage(deep=True)
    
    # Create a DataFrame with the results
    result = pd.DataFrame({
        'memory_usage_bytes': usage_bytes,
        'memory_usage_mb': usage_bytes / 1024**2,
        'dtype': [df[col].dtype if col in df else 'index' for col in usage_bytes.index],
        'percent': 100 * usage_bytes / usage_bytes.sum()
    })
    
    if detailed and isinstance(df, pd.DataFrame):
        # Add more detailed information
        nunique = []
        has_nulls = []
        null_percent = []
        
        for col in result.index:
            if col != 'index':
                try:
                    nunique.append(df[col].nunique())
                    nulls = df[col].isna().sum()
                    has_nulls.append(True if nulls > 0 else False)
                    null_percent.append(100 * nulls / len(df))
                except:
                    nunique.append(None)
                    has_nulls.append(None)
                    null_percent.append(None)
            else:
                nunique.append(None)
                has_nulls.append(None)
                null_percent.append(None)
        
        result['nunique'] = nunique
        result['has_nulls'] = has_nulls
        result['null_percent'] = null_percent
        
        # For string columns, get average length
        avg_length = []
        for col in result.index:
            if col != 'index' and pd.api.types.is_string_dtype(df[col].dtype):
                try:
                    avg_length.append(df[col].str.len().mean())
                except:
                    avg_length.append(None)
            else:
                avg_length.append(None)
        
        result['avg_string_length'] = avg_length
    
    # Sort by memory usage
    result = result.sort_values('memory_usage_bytes', ascending=False)
    
    return result


def memory_optimization(
    df: Union[pd.DataFrame, pd.Series, List[pd.DataFrame]],
    apply_sparse: bool = True,
    apply_categorical: bool = True,
    apply_numeric_downcasting: bool = True,
    precision_mode: str = "balanced",  # Options: "aggressive", "balanced", "safe"
    verbose: bool = True,
    exclude_columns: Optional[List[str]] = None,
    show_progress: bool = True,
    **kwargs
) -> Union[pd.DataFrame, pd.Series, List[pd.DataFrame]]:
    """
    Apply multiple memory optimization techniques to reduce DataFrame memory usage.
    
    Parameters
    ----------
    df : Union[pd.DataFrame, pd.Series, List[pd.DataFrame]]
        Input dataframe(s) to optimize
    apply_sparse : bool, default=True
        Apply sparse encoding for appropriate columns
    apply_categorical : bool, default=True
        Convert string columns to categorical when beneficial
    apply_numeric_downcasting : bool, default=True
        Downcast numeric columns to smaller dtypes
    precision_mode : str, default="balanced"
        Controls aggressiveness of numeric downcasting:
        - "aggressive": Maximum memory savings, may affect precision
        - "balanced": Good memory savings while preserving most precision
        - "safe": Conservative downcasting to preserve numeric precision
    verbose : bool, default=True
        Print progress and statistics
    exclude_columns : Optional[List[str]], default=None
        Columns to exclude from optimization
    show_progress : bool, default=True
        Whether to show progress bar for optimization
    **kwargs
        Additional arguments for optimization techniques
        
    Returns
    -------
    Union[pd.DataFrame, pd.Series, List[pd.DataFrame]]
        Optimized dataframe(s)
    """
    # Define reusable functions to avoid code duplication
    def get_memory_usage(df_obj):
        if isinstance(df_obj, pd.Series):
            return df_obj.memory_usage(deep=True) / 1024**2
        else:
            return df_obj.memory_usage(deep=True).sum() / 1024**2
    
    # Validate precision_mode
    valid_modes = ["aggressive", "balanced", "safe"]
    if precision_mode not in valid_modes:
        raise ValueError(f"precision_mode must be one of {valid_modes}, got {precision_mode}")
    
    def optimize_single_df(df_input, exclude_list=None):
        """Inner function to optimize a single dataframe"""
        # Input validation
        if not isinstance(df_input, (pd.DataFrame, pd.Series)):
            raise TypeError("Input must be a pandas DataFrame or Series")
        
        # Make a copy to avoid modifying the original
        df_result = df_input.copy()
        
        if exclude_list is None:
            exclude_list = []
        
        start_mem = get_memory_usage(df_result)
        column_changes = {}
        
        all_cols = df_result.columns if isinstance(df_result, pd.DataFrame) else [df_result.name]
        process_cols = [col for col in all_cols if col not in exclude_list]
        
        # Use tqdm for progress tracking
        iterator = tqdm(process_cols, desc="Optimizing columns") if show_progress else process_cols
        
        for col in iterator:
            # Handle Series case
            if isinstance(df_result, pd.Series):
                series = df_result
            else:
                series = df_result[col]
            
            col_dtype = series.dtype
            
            # Process numerics
            if pd.api.types.is_numeric_dtype(col_dtype) and apply_numeric_downcasting:
                # Get min and max safely accounting for NaN values
                c_min = series.min() if not series.isna().all() else 0
                c_max = series.max() if not series.isna().all() else 0
                
                # Check if column has NaN values
                has_null = series.isna().any()
                
                # Skip columns with NaN values if in safe mode
                if precision_mode == "safe" and has_null:
                    continue
                
                # For integers
                if pd.api.types.is_integer_dtype(col_dtype):
                    if has_null:
                        # Choose appropriate nullable integer dtype based on precision mode
                        if precision_mode == "aggressive":
                            if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                                new_dtype = pd.Int8Dtype()
                            elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                                new_dtype = pd.Int16Dtype()
                            elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                                new_dtype = pd.Int32Dtype()
                            else:
                                new_dtype = pd.Int64Dtype()
                        elif precision_mode == "balanced":
                            if c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                                new_dtype = pd.Int16Dtype()
                            elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                                new_dtype = pd.Int32Dtype()
                            else:
                                new_dtype = pd.Int64Dtype()
                        else:  # safe mode
                            # Only use Int32 or Int64 for nullable integers in safe mode
                            if c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                                new_dtype = pd.Int32Dtype()
                            else:
                                new_dtype = pd.Int64Dtype()
                    else:
                        # Regular integer dtype for non-null columns
                        if precision_mode == "aggressive":
                            if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                                new_dtype = np.int8
                            elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                                new_dtype = np.int16
                            elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                                new_dtype = np.int32
                            else:
                                new_dtype = np.int64
                        elif precision_mode == "balanced":
                            if c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                                new_dtype = np.int16
                            elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                                new_dtype = np.int32
                            else:
                                new_dtype = np.int64
                        else:  # safe mode
                            # Only use int32 or int64 in safe mode
                            if c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                                new_dtype = np.int32
                            else:
                                new_dtype = np.int64
                # For floats
                else:
                    # Float column downcasting logic
                    # Never use float16 in safe mode or with nulls
                    if precision_mode == "aggressive" and not has_null:
                        # Check if we can use float16 (this is the most aggressive)
                        if (c_min > np.finfo(np.float16).min and 
                            c_max < np.finfo(np.float16).max and 
                            abs(c_min) < 65500 and abs(c_max) < 65500):
                            new_dtype = np.float16
                        elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                            new_dtype = np.float32
                        else:
                            new_dtype = np.float64
                    elif precision_mode == "balanced" or has_null:
                        # Use float32 when possible, otherwise float64
                        if c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                            new_dtype = np.float32
                        else:
                            new_dtype = np.float64
                    else:  # safe mode
                        # Always use float64 in safe mode
                        new_dtype = np.float64
                
                # Apply the new dtype
                try:
                    if isinstance(df_result, pd.Series):
                        df_result = df_result.astype(new_dtype)
                    else:
                        df_result[col] = df_result[col].astype(new_dtype)
                    
                    column_changes[col] = (str(col_dtype), str(new_dtype))
                except (ValueError, TypeError) as e:
                    warnings.warn(f"Could not convert column {col} to {new_dtype}: {str(e)}")
            
            # Process string columns for categorical conversion
            elif apply_categorical and pd.api.types.is_string_dtype(col_dtype):
                n_unique = series.nunique()
                categorical_threshold = kwargs.get('categorical_threshold', 50)
                
                if n_unique <= categorical_threshold or (n_unique / len(series) < 0.5):
                    try:
                        if isinstance(df_result, pd.Series):
                            df_result = df_result.astype('category')
                        else:
                            df_result[col] = df_result[col].astype('category')
                        
                        column_changes[col] = (str(col_dtype), 'category')
                    except Exception as e:
                        warnings.warn(f"Could not convert string column {col} to category: {str(e)}")
            
            # Process datetime columns
            elif convert_datetime := kwargs.get('convert_datetime', True):
                if pd.api.types.is_datetime64_dtype(col_dtype):
                    # Check date range to see if we can use a more efficient format
                    min_date = series.min()
                    max_date = series.max()
                    
                    if pd.notna(min_date) and pd.notna(max_date):
                        # Check if dates fall within pandas.Timestamp COMPAT_DAYS
                        min_year = min_date.year if not pd.isna(min_date) else 1970
                        max_year = max_date.year if not pd.isna(max_date) else 2030
                        
                        if 1900 <= min_year and max_year <= 2100:
                            # Use more compact datetime representation
                            try:
                                series_new = pd.to_datetime(series)
                                if isinstance(df_result, pd.Series):
                                    df_result = series_new
                                else:
                                    df_result[col] = series_new
                                
                                column_changes[col] = (str(col_dtype), 'datetime64[ns]')
                            except Exception as e:
                                warnings.warn(f"Could not optimize datetime column {col}: {str(e)}")
        
        # Apply sparse encoding if requested
        if apply_sparse:
            # Determine which columns to convert to sparse
            fill_value = kwargs.get('sparse_fill_value', 0)
            sparse_threshold = kwargs.get('sparsity_threshold', 0.5)
            
            for col in process_cols:
                if isinstance(df_result, pd.Series):
                    series = df_result
                else:
                    series = df_result[col]
                
                # Only apply to numeric columns
                if pd.api.types.is_numeric_dtype(series.dtype):
                    # Calculate sparsity (ratio of fill_value)
                    sparsity = (series == fill_value).mean()
                    
                    if sparsity > sparse_threshold:
                        try:
                            if isinstance(df_result, pd.Series):
                                df_result = pd.Series.sparse.from_dense(
                                    df_result, fill_value=fill_value
                                )
                            else:
                                df_result[col] = pd.Series.sparse.from_dense(
                                    df_result[col], fill_value=fill_value
                                )
                            
                            col_dtype = df_result[col].dtype if not isinstance(df_result, pd.Series) else df_result.dtype
                            column_changes[col] = (str(series.dtype), str(col_dtype))
                        except Exception as e:
                            warnings.warn(f"Could not convert column {col} to sparse: {str(e)}")
        
        # Calculate memory usage after optimization
        end_mem = get_memory_usage(df_result)
        reduction_mb = start_mem - end_mem
        reduction_pct = 100 * reduction_mb / start_mem if start_mem > 0 else 0
        
        if verbose:
            print(f"Memory usage decreased from {start_mem:.2f} MB to {end_mem:.2f} MB ({reduction_pct:.1f}% reduction)")
            
            if column_changes:
                print("\nColumn dtype changes:")
                for col, (before, after) in column_changes.items():
                    if before != after:
                        print(f"  {col}: {before} → {after}")
        
        return df_result
    
    # Process single DataFrame/Series or list of DataFrames
    exclude_cols = exclude_columns if exclude_columns is not None else []
    
    if isinstance(df, list):
        # Handle list of dataframes
        result_dfs = []
        total_before = 0
        total_after = 0
        
        for i, single_df in enumerate(df):
            if verbose:
                print(f"\nOptimizing DataFrame {i+1}/{len(df)} with '{precision_mode}' precision mode")
            
            before_mem = get_memory_usage(single_df)
            total_before += before_mem
            
            opt_df = optimize_single_df(single_df, exclude_cols)
            result_dfs.append(opt_df)
            
            after_mem = get_memory_usage(opt_df)
            total_after += after_mem
        
        if verbose and len(df) > 1:
            reduction_pct = 100 * (total_before - total_after) / total_before if total_before > 0 else 0
            print(f"\nTotal memory usage decreased from {total_before:.2f} MB to {total_after:.2f} MB ({reduction_pct:.1f}% reduction)")
        
        return result_dfs
    else:
        # Handle single dataframe
        if verbose:
            print(f"Optimizing DataFrame with '{precision_mode}' precision mode")
            
        result = optimize_single_df(df, exclude_cols)
        return result

