import jinja2
from typing import List, Dict, Any, Union, Optional
from datetime import datetime

def generate_sql_trend_query(
    snapshot_date: str,
    date_field: str,
    date_unit: str = 'MONTH',
    periods: int = 12,
    table_name: str = None,
    group_by_fields: List[str] = None,
    metrics: List[Dict[str, Any]] = None,
    filters: str = None,
    output_file: str = None
) -> str:
    """
    Generate SQL for trend analysis across time periods.
    
    Parameters:
    -----------
    snapshot_date : str
        Reference date for analysis (e.g., '2025-04-08')
    date_field : str
        Field name in the table that contains the date to analyze
    date_unit : str
        Time unit for analysis: 'DAY', 'WEEK', 'MONTH', 'QUARTER', 'YEAR'
    periods : int
        Number of time periods to analyze
    table_name : str
        Table to query data from
    group_by_fields : list
        Fields to group by (entity identifiers)
    metrics : list
        Metrics to include in analysis with their properties. Each metric is a dict with:
        - name: output column name prefix
        - source: field name in the source table
        - aggregation: function to apply (AVG, SUM, MAX, etc.)
        - condition: optional WHERE condition
        - cumulative: if True, calculate period-over-period differences
        - is_case_expression: if True, the source is already a CASE WHEN expression
        - is_expression: if True, the source is a complex expression
    filters : str
        SQL WHERE clause conditions as a string
    output_file : str, optional
        If provided, save the generated SQL to this file
        
    Returns:
    --------
    str
        The generated SQL query
    """
    # Set defaults
    if table_name is None:
        raise ValueError("table_name is required")
    
    if group_by_fields is None:
        group_by_fields = ['dim_crm_account_id']
    
    if metrics is None or len(metrics) == 0:
        raise ValueError("At least one metric must be provided")

    # Validate date_unit
    valid_date_units = ['DAY', 'WEEK', 'MONTH', 'QUARTER', 'YEAR']
    date_unit = date_unit.upper()
    if date_unit not in valid_date_units:
        raise ValueError(f"date_unit must be one of {valid_date_units}")

    # Prepare metrics
    for metric in metrics:
        if 'name' not in metric:
            raise ValueError("Each metric must have a 'name'")
        if 'source' not in metric:
            raise ValueError("Each metric must have a 'source'")
        if 'aggregation' not in metric:
            metric['aggregation'] = 'AVG'
        if 'condition' not in metric:
            metric['condition'] = None
        if 'cumulative' not in metric:
            metric['cumulative'] = False
        if 'is_case_expression' not in metric:
            metric['is_case_expression'] = False
        if 'is_expression' not in metric:
            metric['is_expression'] = False

    # Generate SQL without using Jinja templates
    sql = _generate_sql(
        snapshot_date=snapshot_date,
        date_field=date_field,
        date_unit=date_unit,
        periods=periods,
        table_name=table_name,
        group_by_fields=group_by_fields,
        metrics=metrics,
        filters=filters,
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(sql)
        print(f"SQL saved to {output_file}")
    
    return 

def _generate_sql(snapshot_date, date_field, date_unit, periods, table_name, 
                 group_by_fields, metrics, filters, generation_time):
    """Generate SQL manually instead of using Jinja templates to avoid nested loop issues."""
    
    column_suffix = date_unit.lower()
    
    # Separate regular and cumulative metrics
    regular_metrics = []
    cumulative_metrics = []
    
    for metric in metrics:
        if metric.get("cumulative", False):
            cumulative_metrics.append(metric)
        else:
            regular_metrics.append(metric)
    
    # Generate base data CTE
    sql = f"""-- Generated SQL Trend Query
-- Generated on: {generation_time}
-- Parameters:
--   snapshot_date: {snapshot_date}
--   date_unit: {date_unit}
--   periods: {periods}

WITH base_data AS (
    -- Get all data for the specified time periods
    SELECT 
        {', '.join(group_by_fields)},
        {date_field},
        -- Calculate {date_unit} number based on difference from snapshot_date
        DATEDIFF({date_unit}, {date_field}, DATE_TRUNC({date_unit}, '{snapshot_date}'::DATE)) AS period_number,
        
        -- Metrics
"""

    # Add metrics - one per line
    metric_lines = []
    for i, metric in enumerate(metrics):
        if metric["is_case_expression"]:
            line = f"{metric['aggregation']}(CASE WHEN {metric['source']} THEN 1 ELSE 0 END) AS {metric['name']}"
        elif metric["is_expression"]:
            line = f"{metric['aggregation']}({metric['source']}) AS {metric['name']}"
        elif metric["condition"]:
            line = f"{metric['aggregation']}(CASE WHEN {metric['condition']} THEN {metric['source']} END) AS {metric['name']}"
        else:
            line = f"{metric['aggregation']}({metric['source']}) AS {metric['name']}"
        
        if i < len(metrics) - 1:
            line += ","
        metric_lines.append(f"        {line}")
    
    sql += "\n".join(metric_lines)

    # Add FROM and WHERE clauses
    sql += f"""
    FROM 
        {table_name}
    WHERE 
        {date_field} BETWEEN 
            DATE_TRUNC({date_unit}, DATEADD({date_unit}, -{periods + 1}, '{snapshot_date}'::DATE)) AND 
            DATE_TRUNC({date_unit}, DATEADD({date_unit}, -1, '{snapshot_date}'::DATE))
"""

    # Add custom filters if provided
    if filters and filters.strip():
        sql += f"        AND {filters}\n"
        
    sql += f"""        -- Only include periods 1-{periods+1}
        AND DATEDIFF({date_unit}, {date_field}, DATE_TRUNC({date_unit}, '{snapshot_date}'::DATE)) BETWEEN 1 AND {periods + 1}
    GROUP BY 
        {', '.join(group_by_fields)}, {date_field}
),

pivoted_data AS (
    SELECT
        {', '.join(group_by_fields)}

"""
    
    # Add pivoted regular metrics first
    if regular_metrics:
        sql += "        -- Regular metrics\n"
        current_group = None
        
        for metric in regular_metrics:
            # Add separator between metric groups
            if current_group and current_group != metric["name"]:
                sql += "\n"  # Extra line between metric groups
            
            current_group = metric["name"]
            
            # Add the pivoted values for this regular metric
            for period in range(1, periods + 1):
                sql += f"        ,MAX(CASE WHEN period_number = {period} THEN {metric['name']} END) AS {metric['name']}_{column_suffix}_{period}_cnt\n"

    # Add cumulative metrics (all-time values only, not the redundant _cnt versions)
    if cumulative_metrics:
        if regular_metrics:  # Add extra space if we had regular metrics
            sql += "\n"
        
        sql += "        -- Cumulative metrics (all-time values)\n"
        current_group = None
        
        for metric in cumulative_metrics:
            # Add separator between metric groups
            if current_group and current_group != metric["name"]:
                sql += "\n"  # Extra line between metric groups
            
            current_group = metric["name"]
            
            # Add all-time values for this cumulative metric (periods+1 for calculations)
            for period in range(1, periods + 2):
                sql += f"        ,MAX(CASE WHEN period_number = {period} THEN {metric['name']} END) AS {metric['name']}_all_time_{column_suffix}_{period}\n"

    # Add usage flags
    sql += "\n        -- Flags for data existence in each period\n"
    for period in range(1, periods + 1):
        sql += f"        ,MAX(CASE WHEN period_number = {period} THEN 1 ELSE 0 END) AS has_data_{column_suffix}_{period}_flag\n"

    # Add final GROUP BY
    sql += f"""    FROM 
        base_data
    GROUP BY 
        {', '.join(group_by_fields)}
),

final_output AS (
    SELECT 
        *,

"""
    
    # Add calculated event metrics for cumulative metrics
    if cumulative_metrics:
        lines = []
        current_group = None
        
        for i, metric in enumerate(cumulative_metrics):
            # Add separator between metric groups
            if current_group and current_group != metric["name"]:
                lines.append("")  # Extra line between metric groups
            
            current_group = metric["name"]
            
            # Add the difference calculations - fixed the range enumeration
            for j in range(periods):
                period = j + 1  # Start from 1, not 0
                line = f"        COALESCE({metric['name']}_all_time_{column_suffix}_{period + 1}, 0) - COALESCE({metric['name']}_all_time_{column_suffix}_{period}, 0) AS {metric['name']}_event_{column_suffix}_{period}_cnt"
                
                # Add comma if not the last line
                if not (i == len(cumulative_metrics) - 1 and j == periods - 1):
                    line += ","
                    
                lines.append(line)
        
        sql += "\n".join(lines)
    
    sql += """
    FROM
        pivoted_data
)

-- Return the final result set
SELECT * FROM final_output
"""
    
    return sql


def trend_analysis(
    df, 
    metric_list=None,
    time_unit='month', 
    periods=6, 
    include_cumulative=True,
    exclude_fields=None,
    verbose=False
):
    """
    Calculate trend metrics for a dataframe produced by the SQL trend generator.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Dataframe containing trend data with time-based columns
    metric_list : list, optional
        List of metric names to analyze. If None, auto-detects metrics from columns
    time_unit : str
        Time unit used in the column names (month, day, week, etc.)
    periods : int
        Number of time periods to analyze
    include_cumulative : bool
        Whether to use cumulative (event) metrics when available
    exclude_fields : list, optional
        List of fields to exclude from auto-detection
    verbose : bool
        Whether to display intermediate output
        
    Returns:
    --------
    pandas.DataFrame
        A dataframe containing trend metrics for each specified metric
    """
    import pandas as pd
    import numpy as np
    import re
    
    trends_df = pd.DataFrame()
        
    # Auto-detect metrics if not provided
    if metric_list is None:
        # Initialize excluded fields
        if exclude_fields is None:
            exclude_fields = []
            
        # Use regular expressions to find metric names from column patterns
        metric_pattern = re.compile(f"(.+?)_(?:event_)?{time_unit}_\\d+_cnt$")
        
        # Extract unique metric names from column names
        detected_metrics = set()
        for col in df.columns:
            match = metric_pattern.match(col)
            if match:
                metric_name = match.group(1)
                # Skip excluded fields and "has_data" flags
                if metric_name not in exclude_fields and not metric_name.startswith("has_data"):
                    detected_metrics.add(metric_name)
        
        metric_list = sorted(list(detected_metrics))
        
        if verbose:
            print(f"Auto-detected {len(metric_list)} metrics: {', '.join(metric_list)}")
    
    for metric in metric_list:
        # Determine whether to use event (cumulative) or regular metric columns
        event_pattern = f"{metric}_event_{time_unit}"
        regular_pattern = f"{metric}_{time_unit}"
        
        event_cols = [col for col in df.columns if event_pattern in col]
        has_event_metrics = len(event_cols) > 0
        
        # Decide which pattern to use
        if include_cumulative and has_event_metrics:
            base_pattern = event_pattern
        else:
            base_pattern = regular_pattern
        
        cols = df.filter(like=base_pattern).columns
        
        if len(cols) == 0:
            if verbose:
                print(f"Warning: No columns found for metric '{metric}' with pattern '{base_pattern}'")
            continue
            
        # Create a working copy of the data
        metric_df = df[cols.to_list()].copy(deep=True)
        metric_df = metric_df.astype("float")
        
        # Extract actual column names for the periods we want to analyze
        period_cols = []
        for i in range(1, periods + 1):
            # Look for columns that end with the pattern _X_cnt where X is the period number
            matching_cols = [col for col in cols if col.endswith(f"_{i}_cnt")]
            if matching_cols:
                period_cols.append(matching_cols[0])
            else:
                # If we can't find period i, break early
                break
        
        # Use actual found period columns (handles missing periods)
        actual_periods = len(period_cols)
        if actual_periods < 2:
            if verbose:
                print(f"Warning: Insufficient periods for metric '{metric}'. Need at least 2, found {actual_periods}.")
            continue
        
        # Calculate differences and percentages between consecutive periods
        for i in range(1, actual_periods):
            prev_col = period_cols[i-1]
            curr_col = period_cols[i]
            
            # Calculate absolute difference
            diff_col = f"diff_{i}_{metric}_{time_unit}_cnt"
            metric_df[diff_col] = metric_df[curr_col] - metric_df[prev_col]
            
            # Calculate percentage change
            pct_col = f"pct_{i}_{metric}_{time_unit}_pct"
            metric_df[pct_col] = np.where(
                metric_df[curr_col] != 0, 
                metric_df[diff_col] / metric_df[curr_col], 
                np.nan
            )
        
        # Get all difference columns
        diff_cols = metric_df.filter(like="diff").columns
        
        if verbose:
            display(diff_cols)
        
        # Count decreases (negative differences)
        df_drop_count = metric_df[metric_df[diff_cols] < 0].notna()
        df_drop_count = pd.DataFrame(
            df_drop_count[diff_cols].sum(axis=1)
        ).rename(columns={0: f'drop_{metric}_period_{actual_periods}_{time_unit}s_cnt'})
        
        # Count increases (positive differences)
        df_increase_count = metric_df[metric_df[diff_cols] > 0].notna()
        df_increase_count = pd.DataFrame(
            df_increase_count[diff_cols].sum(axis=1)
        ).rename(columns={0: f'increase_{metric}_period_{actual_periods}_{time_unit}s_cnt'})
        
        # Check for consecutive patterns
        for i in range(1, actual_periods - 1):
            # Consecutive drops
            metric_df[f"consecutive_drop_{metric}_{i}_flag"] = np.where(
                ((metric_df[f"diff_{i}_{metric}_{time_unit}_cnt"] < 0) & 
                 (metric_df[f"diff_{i+1}_{metric}_{time_unit}_cnt"] < 0)), 
                1, 0
            )
            
            # Consecutive increases
            metric_df[f"consecutive_increase_{metric}_{i}_flag"] = np.where(
                ((metric_df[f"diff_{i}_{metric}_{time_unit}_cnt"] > 0) & 
                 (metric_df[f"diff_{i+1}_{metric}_{time_unit}_cnt"] > 0)), 
                1, 0
            )
        
        # Sum consecutive drops
        consecutive_drop_cols = metric_df.filter(like=f"consecutive_drop_{metric}").columns
        df_consecutive_drop = pd.DataFrame(
            metric_df[consecutive_drop_cols].sum(axis=1)
        ).rename(columns={0: f'consecutive_drop_{metric}_period_{actual_periods}_{time_unit}s_cnt'})
        
        # Sum consecutive increases
        consecutive_increase_cols = metric_df.filter(like=f"consecutive_increase_{metric}").columns
        df_consecutive_increase = pd.DataFrame(
            metric_df[consecutive_increase_cols].sum(axis=1)
        ).rename(columns={0: f'consecutive_increase_{metric}_period_{actual_periods}_{time_unit}s_cnt'})
        
        if verbose:
            print('\ndrop count distribution')
            display(df_drop_count.iloc[:, 0].value_counts(normalize=True, dropna=False))
            
            print('\nconsecutive count within drops')
            display(df_consecutive_drop.iloc[:, 0].value_counts(normalize=True, dropna=False))
            
            print('\nincrease count distribution')
            display(df_increase_count.iloc[:, 0].value_counts(normalize=True, dropna=False))
            
            print('\nconsecutive count within increase')
            display(df_consecutive_increase.iloc[:, 0].value_counts(normalize=True, dropna=False))
        
        # Calculate average percentage change
        pct_cols = metric_df.filter(like="_pct").columns
        if len(pct_cols) > 0:
            df_with_perc = metric_df[pct_cols]
            
            # Calculate mean of percentage changes
            avg_col = f'avg_perc_change_{metric}_period_{actual_periods}_{time_unit}s'
            df_with_perc = df_with_perc.assign(avg=df_with_perc[pct_cols].mean(axis=1, skipna=True))
            df_with_perc.rename(columns={"avg": avg_col}, inplace=True)
            
            df_avg_perc = df_with_perc[avg_col]
        else:
            # Create empty series if no percentage columns
            df_avg_perc = pd.Series(np.nan, index=df.index, name=f'avg_perc_change_{metric}_period_{actual_periods}_{time_unit}s')
        
        # Concat all metrics for this field
        final_metric_df = pd.concat([
            df_drop_count, 
            df_increase_count, 
            df_consecutive_drop, 
            df_consecutive_increase, 
            df_avg_perc
        ], axis=1)
        
        # Add to overall trends dataframe
        trends_df = pd.concat([trends_df, final_metric_df], axis=1, verify_integrity=True)
    
    return trends_df