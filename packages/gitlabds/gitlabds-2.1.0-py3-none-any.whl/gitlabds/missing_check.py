import pandas as pd

def missing_check(df:pd.DataFrame, threshold:float= 0.1, by:list='column_name', ascending:bool=True, return_missing_cols:bool = False) -> list:
    """
    Check for missing values.
    
    Ex: gitlabds.missing_check(df=None, threshold = 0, by='column_name', ascending=True, return_missing_cols = False):

    Parameters:


    df : your pandas dataframe

    threshold : The percent of missing values at which a column is considered to have missing values. For example, threshold = .10 will only display columns with more than 10% of its values missing. Defaults to 0.

    by : Columns to sort by. Defaults to column_name. Also accepts percent_missing, total_missing, or a list.

    ascending : Sort ascending vs. descending. Defaults to ascending (ascending=True).

    return_missing_cols : Set to True to return a list of column names that meet the threshold criteria for missing.


    Returns

    List of columns with missing values filled or None if return_missing_cols=False.
    """

    missing_value_df = pd.DataFrame({'column_name': df.columns,
                                     'percent_missing': df.isnull().sum() / len(df),
                                     'total_missing': df.isnull().sum()
                                    })
    
    missing_value_df.sort_values(by=by, ascending=ascending, inplace=True)
    columns_with_missing_values = missing_value_df[missing_value_df["percent_missing"] > threshold].reset_index(drop = True)
    print(columns_with_missing_values)

    if return_missing_cols == True:
        
        return columns_with_missing_values['column_name'].tolist()
    
    else:
        return None

