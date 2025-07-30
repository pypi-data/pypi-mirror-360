import pandas as pd
import numpy as np
import datetime, uuid, json
from typing import Dict, Any, List, Optional

def calculate_monitoring_metrics(
    run_id: str,
    model_name: str,
    sub_model: str,
    model_version: str,
    scoring_date: datetime,
    feature_df: pd.DataFrame,
    predictions: np.ndarray,
    baseline_metrics: Dict[str, Any],
    importance_threshold_pct: float = 0.05
) -> Dict[str, pd.DataFrame]:
    """
    Calculate all monitoring metrics with proper PSI calculations.
    
    Parameters:
    -----------
    run_id : str
        Unique identifier for this scoring run
    model_name : str
        Model name (e.g., "propensity_model")
    sub_model : str
        Sub model identifier
    model_version : str
        Model version (e.g., "2.1")
    scoring_date : datetime
        Date of scoring
    feature_df : pd.DataFrame
        Feature data used for scoring
    predictions : np.ndarray
        Model predictions (probabilities 0-1)
    baseline_metrics : Dict[str, Any]
        Dictionary containing baseline_features and baseline_calibration JSON data
    importance_threshold_pct : float
        Percentage of total importance required for a feature to be considered "important" (default: 0.05 = 5%)
        
    Returns:
    --------
    Dict[str, pd.DataFrame]: Dictionary containing DataFrames for each table
        - 'scoring_summary': model_scoring_summary table
        - 'feature_drift': model_feature_drift table  
    """
    
    record_count = len(predictions)
    
    # Extract baseline data from the two JSON files
    baseline_features_data = baseline_metrics.get('baseline_features', {})
    baseline_calibration_data = baseline_metrics.get('baseline_calibration', {})
    
    # Get nested data structures
    baseline_features = baseline_features_data.get('baseline_features', {})
    feature_importance_data = baseline_features_data.get('feature_importance', {})
    drift_thresholds = baseline_features_data.get('drift_thresholds', {})
    
    baseline_calibration = baseline_calibration_data.get('calibration_curves', {})
    model_configuration = baseline_calibration_data.get('model_configuration', {})
    prediction_statistics = baseline_calibration_data.get('prediction_statistics', {})
    
    # =================================================================
    # 1. CALCULATE FEATURE DRIFT METRICS - CORRECTED PSI CALCULATIONS
    # =================================================================
    
    feature_drift_rows = []
    drift_statuses = []
    psi_values = []
    
    # Get baseline feature data and importance scores
    baseline_numerical = baseline_features.get('numerical_features', {})
    baseline_categorical = baseline_features.get('categorical_features', {})
    importance_scores = feature_importance_data.get('feature_importance', {})
    psi_thresholds = drift_thresholds.get('psi', {})
    
    # Process each feature in the current data
    for feature_name in feature_df.columns:
        
        # Get feature importance (default to 0 if not found)
        feat_importance = importance_scores.get(feature_name, 0.0)
        
        # Initialize drift metrics
        psi_value = None
        status = 'unknown'
        
        # Check if feature is numerical or categorical
        if feature_name in baseline_numerical:
            # NUMERICAL FEATURE DRIFT CALCULATION
            baseline_feature_df = baseline_numerical[feature_name]
            current_values = feature_df[feature_name].dropna()
            
            if len(current_values) > 0:
                # Extract bin_edges for numerical PSI
                baseline_bin_edges = baseline_feature_df.get('bin_edges', [])
                psi_value = calculate_psi_numerical(current_values.values, baseline_bin_edges)
        
        elif feature_name in baseline_categorical:
            # CATEGORICAL FEATURE DRIFT CALCULATION
            baseline_feature_df = baseline_categorical[feature_name]
            current_values = feature_df[feature_name].dropna()
            
            if len(current_values) > 0:
                # Extract frequencies for categorical PSI
                baseline_frequencies = baseline_feature_df.get('frequencies', {})
                psi_value = calculate_psi_categorical(current_values.values, baseline_frequencies)
        
        # Determine status based on thresholds
        if psi_value is not None:
            psi_critical = psi_thresholds.get('critical', 0.2)
            psi_warning = psi_thresholds.get('warning', 0.1)
            
            if psi_value >= psi_critical:
                status = 'critical'
            elif psi_value >= psi_warning:
                status = 'warning'
            else:
                status = 'healthy'
        
        # Store for summary statistics
        drift_statuses.append(status)
        if psi_value is not None:
            psi_values.append(psi_value)
        
        # Create feature drift row
        feature_drift_rows.append({
            'run_id': run_id,
            'model_name': model_name,
            'sub_model': sub_model,
            'model_version': model_version,
            'feature_name': feature_name,
            'scoring_date': scoring_date.strftime('%Y-%m-%d %H:%M:%S'),
            'psi_value': psi_value,
            'feature_importance': feat_importance,
            'status': status
        })
    
    # =================================================================
    # 2. CALCULATE DRIFT SUMMARY STATISTICS (IMPORTANCE-WEIGHTED)
    # =================================================================
    
    # Calculate total importance for percentage calculations
    total_importance = sum(importance_scores.values()) if importance_scores else 1.0
    
    # Separate features by importance
    important_feature_statuses = []
    important_psi_values = []
    important_feature_names = []
    
    total_features = len(drift_statuses)
    features_healthy = drift_statuses.count('healthy')
    features_warning = drift_statuses.count('warning')
    features_critical = drift_statuses.count('critical')
    
    # Process each feature to determine if it's "important"
    for i, row in enumerate(feature_drift_rows):
        feature_name = row['feature_name']
        feature_importance_score = importance_scores.get(feature_name, 0.0)
        importance_percentage = feature_importance_score / total_importance if total_importance > 0 else 0.0
        
        # Check if feature meets importance threshold
        if importance_percentage > importance_threshold_pct:
            important_feature_statuses.append(row['status'])
            important_feature_names.append(feature_name)
            if row['psi_value'] is not None:
                important_psi_values.append(row['psi_value'])
    
    # Calculate metrics for all features
    all_psi_values = [row['psi_value'] for row in feature_drift_rows if row['psi_value'] is not None]
    
    # Calculate metrics for important features only
    important_features_healthy = important_feature_statuses.count('healthy')
    important_features_warning = important_feature_statuses.count('warning')
    important_features_critical = important_feature_statuses.count('critical')
    
    # Determine overall status based on important features only
    if important_features_critical > 0:
        overall_status = 'critical'
    elif important_features_warning > 0:
        overall_status = 'warning'
    else:
        overall_status = 'healthy'
    
    # Find most drifted important feature
    most_drifted_important_feature = None
    if important_psi_values and important_feature_names:
        max_important_psi_idx = np.argmax(important_psi_values)
        most_drifted_important_feature = important_feature_names[max_important_psi_idx]
    
    drift_summary = {
        'total_features': total_features,
        'important_features': len(important_feature_names),
        'importance_threshold_pct': importance_threshold_pct * 100,  # Convert to percentage for display
        'features_healthy': features_healthy,
        'features_warning': features_warning,
        'features_critical': features_critical,
        'important_features_healthy': important_features_healthy,
        'important_features_warning': important_features_warning,
        'important_features_critical': important_features_critical,
        'avg_psi': float(np.mean(all_psi_values)) if all_psi_values else None,
        'max_psi': float(np.max(all_psi_values)) if all_psi_values else None,
        'avg_important_psi': float(np.mean(important_psi_values)) if important_psi_values else None,
        'max_important_psi': float(np.max(important_psi_values)) if important_psi_values else None,
        'most_drifted_feature': feature_drift_rows[np.argmax([row['psi_value'] or 0 for row in feature_drift_rows])]['feature_name'] if all_psi_values else None,
        'most_drifted_important_feature': most_drifted_important_feature
    }
    
    # =================================================================
    # 3. CALCULATE SCORING SUMMARY WITH ENHANCED PREDICTION ANALYSIS
    # =================================================================
    
    # Calculate current prediction statistics
    current_predictions = {
        'mean_prediction': float(np.mean(predictions)),
        'std_prediction': float(np.std(predictions)),
        'min_prediction': float(np.min(predictions)),
        'max_prediction': float(np.max(predictions)),
        'median_prediction': float(np.median(predictions)),
        'distribution': calculate_prediction_distribution(predictions)
    }
    
    # Calculate baseline prediction statistics and distribution
    baseline_predictions = {}
    prediction_drift = {}
    
    # Get baseline distribution from sample_counts
    baseline_distribution = calculate_baseline_prediction_distribution(baseline_calibration)
    
    if baseline_distribution:
        # Get baseline statistics from stored prediction statistics
        baseline_stats = prediction_statistics.get('test', {})
        
        if baseline_stats:
            # Use pre-calculated baseline statistics
            baseline_predictions = {
                'mean_prediction': baseline_stats.get('mean_prediction'),
                'std_prediction': baseline_stats.get('std_prediction'),
                'min_prediction': baseline_stats.get('min_prediction'),
                'max_prediction': baseline_stats.get('max_prediction'),
                'median_prediction': baseline_stats.get('median_prediction'),
                'distribution': baseline_distribution
            }
        
        # Calculate prediction drift if we have baseline mean
        if baseline_predictions.get('mean_prediction') is not None:
            baseline_mean = baseline_predictions['mean_prediction']
            current_mean = current_predictions['mean_prediction']
            baseline_std = baseline_predictions.get('std_prediction')
            current_std = current_predictions['std_prediction']
            
            prediction_drift = {
                'mean_shift': float(current_mean - baseline_mean),
                'mean_shift_pct': float((current_mean - baseline_mean) / baseline_mean) if baseline_mean > 0 else None,
                'distribution_shift': calculate_distribution_shift(current_predictions['distribution'], baseline_distribution)
            }
            
            # Add std shift if available
            if baseline_std is not None:
                prediction_drift['std_shift'] = float(current_std - baseline_std)
                prediction_drift['std_shift_pct'] = float((current_std - baseline_std) / baseline_std * 100) if baseline_std > 0 else None
            
            # Determine prediction drift status
            mean_shift_pct = abs(prediction_drift.get('mean_shift_pct', 0))
            if mean_shift_pct >= 20:
                prediction_drift['status'] = 'critical'
            elif mean_shift_pct >= 10:
                prediction_drift['status'] = 'warning'
            else:
                prediction_drift['status'] = 'healthy'
    
    # Extract prediction drift status for separate column
    prediction_drift_status = prediction_drift.get('status', 'unknown')
    
    # =================================================================
    # 4. CREATE OUTPUT DATAFRAMES
    # =================================================================
    
    # Scoring Summary DataFrame
    scoring_summary_df = pd.DataFrame([{
        'run_id': run_id,
        'model_name': model_name,
        'sub_model': sub_model,
        'model_version': model_version,
        'scoring_date': scoring_date.strftime('%Y-%m-%d %H:%M:%S'),
        'record_count': record_count,
        'prediction_metrics': json.dumps(current_predictions),
        'prediction_baseline': json.dumps(baseline_predictions),
        'prediction_drift': json.dumps(prediction_drift),
        'prediction_drift_status': prediction_drift_status,
        'feature_drift_summary': json.dumps(drift_summary),
        'feature_drift_status': overall_status,
        'model_configuration': json.dumps(model_configuration)
    }])
    
    # Feature Drift DataFrame
    feature_drift_df = pd.DataFrame(feature_drift_rows)
    
    return {
        'scoring_summary': scoring_summary_df,
        'feature_drift': feature_drift_df
    }

### HELPER FUNCTIONS
def calculate_baseline_prediction_distribution(baseline_calibration):
    """Calculate baseline prediction distribution from sample_counts in calibration data."""
    baseline_test_curve = baseline_calibration.get('test', {})
    sample_counts = baseline_test_curve.get('sample_counts', [])
    
    if not sample_counts or len(sample_counts) != 10:
        return {}
    
    # Convert sample counts to proportions (0.0-1.0)
    total_samples = sum(sample_counts)
    if total_samples == 0:
        return {}
    
    # Create distribution dictionary matching current format
    bin_ranges = ['0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5',
                  '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']
    
    baseline_distribution = {}
    for i, bin_range in enumerate(bin_ranges):
        proportion = float(sample_counts[i] / total_samples)
        baseline_distribution[bin_range] = proportion
    
    return baseline_distribution

def calculate_prediction_distribution(predictions: np.ndarray) -> Dict[str, float]:
    """Calculate prediction distribution across 10 bins."""
    n_bins = 10
    bin_edges = np.linspace(0, 1, n_bins + 1)
    
    # Calculate histogram
    hist, _ = np.histogram(predictions, bins=bin_edges)
    proportions = hist / len(predictions)
    
    # Create distribution dictionary
    distribution = {}
    for i in range(n_bins):
        bin_start = bin_edges[i]
        bin_end = bin_edges[i + 1]
        bin_range = f"{bin_start:.1f}-{bin_end:.1f}"
        distribution[bin_range] = float(proportions[i])
    
    return distribution

def calculate_distribution_shift(current_dist: Dict[str, float], baseline_dist: Dict[str, float]) -> Dict[str, float]:
    """Calculate shift between current and baseline distributions."""
    distribution_shift = {}
    
    for bin_range in current_dist.keys():
        current_pct = current_dist.get(bin_range, 0)
        baseline_pct = baseline_dist.get(bin_range, 0)
        
        shift = current_pct - baseline_pct
        distribution_shift[bin_range] = float(shift)
    
    return distribution_shift

def calculate_psi_numerical(current_values, baseline_bin_edges):
    """
    FINAL PSI calculation handling all edge cases.
    """
    # Use fewer bins for sparse data
    max_bins = 5  
    
    if len(baseline_bin_edges) > max_bins + 1:
        n_total = len(baseline_bin_edges)
        indices = np.linspace(0, n_total-1, max_bins + 1, dtype=int)
        bin_edges = [baseline_bin_edges[i] for i in indices]
    else:
        bin_edges = baseline_bin_edges
    
    bin_edges = sorted(list(set(bin_edges)))
    
    if len(bin_edges) < 2:
        return None
    
    # Calculate current distribution
    current_counts, _ = np.histogram(current_values, bins=bin_edges)
    n_bins = len(current_counts)
    
    current_dist = current_counts / len(current_values)
    
    # Check for sparse data patterns
    non_zero_bins = np.sum(current_dist > 0.01)  # Bins with >1%
    max_proportion = np.max(current_dist)
    
    # CASE 1: Highly sparse (>95% in one bin)
    if max_proportion > 0.95:
        return 0.01  # Minimal PSI for stable sparse data
    
    # CASE 2: Bimodal sparse (only 2-3 bins have significant data)
    elif non_zero_bins <= 3 and max_proportion > 0.6:
        # For bimodal data, only flag major shifts (>5%)
        # Calculate PSI only on non-zero bins
        psi = 0.0
        for i in range(n_bins):
            if current_dist[i] > 0.01:  # Only meaningful bins
                expected = 1.0 / non_zero_bins  # Uniform among active bins
                current = current_dist[i]
                
                # Only contribute if difference > 5%
                if abs(current - expected) > 0.05:
                    psi += (current - expected) * np.log(current / expected)
        
        return max(float(psi), 0.01)  # Minimum 0.01
    
    # CASE 3: Normal distribution
    else:
        expected_dist = np.full(n_bins, 1.0 / n_bins)
        
        smoothing = 1e-5
        current_dist = np.maximum(current_dist, smoothing)
        expected_dist = np.maximum(expected_dist, smoothing)
        
        current_dist = current_dist / current_dist.sum()
        expected_dist = expected_dist / expected_dist.sum()
        
        psi = 0.0
        for i in range(n_bins):
            contribution = (current_dist[i] - expected_dist[i]) * np.log(current_dist[i] / expected_dist[i])
            psi += contribution
        
        return float(psi)

def calculate_psi_categorical(current_values, baseline_frequencies):
    """PSI calculation for categorical features - filters rare categories."""
    # Convert to strings
    current_values_str = [str(val) for val in current_values]
    current_counts = pd.Series(current_values_str).value_counts()
    current_total = len(current_values_str)
    
    # Only include categories with >1% baseline frequency
    main_categories = {k: v for k, v in baseline_frequencies.items() if v >= 0.01}
    
    # Calculate frequencies for main categories
    current_freq = {}
    expected_freq = {}
    current_other = 0
    expected_other = 0
    
    for cat, exp_freq in baseline_frequencies.items():
        if cat in main_categories:
            current_freq[cat] = current_counts.get(cat, 0) / current_total
            expected_freq[cat] = exp_freq
        else:
            expected_other += exp_freq
    
    # Add current categories not in main baseline to "other"
    for cat in current_counts.index:
        if cat not in main_categories:
            current_other += current_counts[cat] / current_total
    
    # Add OTHER category
    current_freq['OTHER'] = current_other
    expected_freq['OTHER'] = expected_other
    
    # Calculate PSI
    psi = 0.0
    for cat in current_freq.keys():
        curr = max(current_freq[cat], 1e-6)
        exp = max(expected_freq[cat], 1e-6)
        psi += (curr - exp) * np.log(curr / exp)
    
    return float(psi)