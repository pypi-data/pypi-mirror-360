import pandas as pd
def missing_fill(df:pd.DataFrame=None, columns="all", method:str="zero", inplace:bool=False, verbose:bool=True, output_file = None, output_method = 'a') -> pd.DataFrame:

    """
    Fill missing values using a range of different options.
    
    Ex: gitlabds.missing_fill(df=None, columns='all', method='zero', inplace=False):

    Parameters:


    df : your pandas dataframe

    columns : Columns which to miss fill. Defaults to all which will miss fill all columns with missing values.

    method : Options are zero, median, mean, drop_column, and drop_row. Defaults to zero.

    inplace : Set to True to replace existing dataframe. Set to False to create a new one and suppress.


    Returns

    DataFrame with missing values filled or None if inplace=True.
    """
    
    if output_file != None:
        f = open(output_file, output_method)
        
        if method == "zero":
            f.write("\n\ndef zero_miss_fill(df):")
            f.write("\n    import pandas as pd")
            f.write("\n    import numpy as np")

        elif method == "mean":
            f.write("\n\ndef mean_miss_fill(df):")
            f.write("\n    import pandas as pd")
            f.write("\n    import numpy as np")

        elif method == "median":
            f.write("\n\ndef median_miss_fill(df):")
            f.write("\n    import pandas as pd")
            f.write("\n    import numpy as np")
            
    if inplace == True:
        df2 = df

    else:
        df2 = df.copy(deep=True)

    # Get all columns with missing values
    missing_cols = set(df.columns[df.isnull().any()].tolist())

    if columns == "all":
        # Pull all numeric columns to miss fill
        all_numeric = set(df.select_dtypes(include=["number"]).columns.tolist())
        # print(all_numeric)

        # Remove columns that have no missing values
        var_list = list(all_numeric & missing_cols)

    else:
        var_list = columns

    print("\nMissing Fill")
    print(f"Columns selected for {method} filling: {columns}\n")
    print(f"Actual columns with missing values that will be {method} filled: {var_list}\n")

    for v in var_list:

        if method == "zero":
            fill_value = 0
            df2[v] = df[v].fillna(fill_value)

        elif method == "mean":
            fill_value = df[v].mean()
            df2[v] = df[v].fillna(fill_value)

        elif method == "median":
            fill_value = df[v].median()
            df2[v] = df[v].fillna(fill_value)
            
        elif method == "drop_column":
            df2.drop(columns=[v], inplace=True)
            
        if verbose == True:
            if method in ("zero", "mean", "median"):
                print(f"Field: {v}; Fill Value: {fill_value}")
            elif method in ("drop_column"):
                print(f"Dropping column: {v}")
                
        if (output_file != None) & (method in ("zero", "median", "mean")):
            f.write(f"\n    df['{v}'] = df['{v}'].fillna({fill_value})")

    if method == "drop_row":
        before = len(df2)
        df2.dropna(axis=0, how='any', subset=var_list, inplace=True)
        after = len(df2)
        
        print(f"{before-after} rows dropped due to missing values")
         
    if output_file != None: 
            f.write('\n\n    return')
            f.close()
                
    return df2
