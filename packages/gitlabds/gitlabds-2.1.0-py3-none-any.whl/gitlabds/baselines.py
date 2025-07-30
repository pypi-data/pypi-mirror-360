import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List, Optional

def generate_baseline_features(
    training_data: pd.DataFrame,
    feature_importance_df: pd.DataFrame,
    importance_method: str = "shapley_values",
    n_bins: int = 10,
    # Drift thresholds (integrated)
    psi_warning: float = 0.1,
    psi_critical: float = 0.2,
    ks_warning: float = 0.1,
    ks_critical: float = 0.2,
    js_warning: float = 0.05,
    js_critical: float = 0.1,
    output_path: str = "baseline_features.json"
) -> None:
    """
    Generate baseline feature distributions, importance scores, and drift thresholds 
    in a single comprehensive artifact.
    
    Parameters:
    -----------
    training_data : pd.DataFrame
        Training feature data
    feature_importance_df : pd.DataFrame
        DataFrame with columns: feature, importance
    importance_method : str
        Method used to calculate importance (default: "shapley_values")
    n_bins : int
        Number of bins for numerical features (default: 10)
    psi_warning, psi_critical : float
        PSI thresholds for warning and critical drift detection
    ks_warning, ks_critical : float  
        KS statistic thresholds for warning and critical drift detection
    js_warning, js_critical : float
        JS divergence thresholds for warning and critical drift detection
    output_path : str
        Path to save the JSON file
        
    Returns:
    --------
    None
    """
    
    # === FEATURE DISTRIBUTIONS ===
    baseline_features = {
        "numerical_features": {},
        "categorical_features": {}
    }

    # Extract feature columns from the importance DataFrame
    feature_columns = feature_importance_df['feature'].tolist()
    
    # Filter to only specified feature columns
    columns_to_process = [col for col in feature_columns if col in training_data.columns]
    
    for column in columns_to_process:
        column_data = training_data[column].dropna()
        
        if len(column_data) == 0:
            continue
            
        # Determine if feature is numerical or categorical
        if pd.api.types.is_numeric_dtype(column_data) and len(column_data.unique()) > 20:
            # NUMERICAL FEATURE - Use quantile binning with distribution storage
            
            # Create quantile bins (ensure we don't have more bins than unique values)
            unique_values = len(column_data.unique())
            actual_bins = min(n_bins, unique_values - 1) if unique_values > 1 else 1
            
            if actual_bins <= 1:
                # Handle edge case: feature has only 1-2 unique values
                bin_edges = [column_data.min() - 0.001, column_data.max() + 0.001]
                bin_proportions = [1.0]
            else:
                # Create quantile-based bin edges
                quantiles = np.linspace(0, 1, actual_bins + 1)
                bin_edges = column_data.quantile(quantiles).values
                
                # Handle duplicate quantiles (happens with skewed data)
                bin_edges = np.unique(bin_edges)
                if len(bin_edges) < actual_bins + 1:
                    # Fall back to equal-width binning if quantiles produce duplicates
                    bin_edges = np.linspace(column_data.min(), column_data.max(), actual_bins + 1)
                
                # Calculate actual training distribution across these bins
                hist_counts, _ = np.histogram(column_data, bins=bin_edges)
                bin_proportions = (hist_counts / len(column_data)).tolist()
            
            baseline_features["numerical_features"][column] = {
                "bin_edges": bin_edges.tolist(),
                "bin_proportions": bin_proportions,
                "n_bins": len(bin_proportions),
                "sample_count": len(column_data),
                "min_value": float(column_data.min()),
                "max_value": float(column_data.max()),
                "mean": float(column_data.mean()),
                "std": float(column_data.std())
            }
            
        else:
            # CATEGORICAL FEATURE - Store frequencies with smoothing
            
            value_counts = column_data.value_counts()
            total_count = len(column_data)
            
            # Calculate frequencies with minimum smoothing
            frequencies = {}
            min_frequency = 1 / (total_count * 10)  # Minimum frequency based on sample size
            
            for value, count in value_counts.items():
                frequency = count / total_count
                # Apply minimum frequency smoothing
                frequencies[str(value)] = max(frequency, min_frequency)
            
            # Renormalize to ensure frequencies sum to 1.0
            total_freq = sum(frequencies.values())
            frequencies = {k: v / total_freq for k, v in frequencies.items()}
            
            baseline_features["categorical_features"][column] = {
                "frequencies": frequencies,
                "unique_values": len(value_counts),
                "sample_count": len(column_data),
                "min_frequency": min_frequency
            }
    
    # === FEATURE IMPORTANCE ===
    feature_importance_dict = {}
    importance_ranking = []
    
    # Sort by importance (descending) and create dictionary
    df_sorted = feature_importance_df.sort_values('importance', ascending=False)
    
    for _, row in df_sorted.iterrows():
        feature_name = str(row['feature'])
        importance_score = float(row['importance'])
        
        feature_importance_dict[feature_name] = importance_score
        importance_ranking.append(feature_name)
    
    # Calculate summary statistics
    total_importance = sum(feature_importance_dict.values())
    max_importance = max(feature_importance_dict.values()) if feature_importance_dict else 0
    min_importance = min(feature_importance_dict.values()) if feature_importance_dict else 0
    
    # === DRIFT THRESHOLDS ===
    drift_thresholds = {
        "description": "Fixed industry standard thresholds for drift detection",
        "psi": {
            "warning": psi_warning,
            "critical": psi_critical,
            "description": "Population Stability Index - measures distribution shift"
        },
        "ks_statistic": {
            "warning": ks_warning,
            "critical": ks_critical,
            "description": "Kolmogorov-Smirnov test statistic - measures distribution differences"
        },
        "js_divergence": {
            "warning": js_warning,
            "critical": js_critical,
            "description": "Jensen-Shannon divergence - measures probability distribution similarity"
        }
    }
    
    # === COMBINE INTO SINGLE ARTIFACT ===
    baseline_artifact = {
        "baseline_features": baseline_features,
        "feature_importance": {
            "feature_importance": feature_importance_dict,
            "importance_ranking": importance_ranking,
            "metadata": {
                "importance_method": importance_method,
                "total_features": len(feature_importance_dict),
                "total_importance": float(total_importance),
                "max_importance": float(max_importance),
                "min_importance": float(min_importance),
            }
        },
        "drift_thresholds": drift_thresholds,
        "metadata": {
            "n_bins": n_bins,
            "total_samples": len(training_data),
            "numerical_features_count": len(baseline_features["numerical_features"]),
            "categorical_features_count": len(baseline_features["categorical_features"]),
            "generation_date": pd.Timestamp.now().isoformat(),
            "usage_notes": [
                "Contains feature distributions for PSI drift calculation",
                "Contains importance scores for importance-weighted drift analysis", 
                "Contains drift thresholds for automated health status determination"
            ]
        }
    }
    
    # Save to JSON file
    with open(output_path, 'w') as f:
        json.dump(baseline_artifact, f, indent=2)
    
    numerical_count = len(baseline_features["numerical_features"])
    categorical_count = len(baseline_features["categorical_features"])
    feature_count = len(feature_importance_dict)
    
    print(f"Baseline features saved to {output_path}")
    print(f"Processed {numerical_count} numerical and {categorical_count} categorical features")
    print(f"Included {feature_count} feature importance scores")
    print(f"Drift thresholds: PSI({psi_warning}/{psi_critical}), KS({ks_warning}/{ks_critical}), JS({js_warning}/{js_critical})")
    
    return None


def generate_baseline_calibration(
    train_predictions: np.ndarray,
    train_actuals: np.ndarray,
    test_predictions: np.ndarray,
    test_actuals: np.ndarray,
    model_configuration: Dict[str, Any],
    n_bins: int = 10,
    output_path: str = "baseline_calibration.json"
) -> None:
    """
    Generate baseline calibration data with train + test curves, prediction statistics,
    and model configuration. Eliminates complex calibration metrics (calculated fresh each time).
    
    Parameters:
    -----------
    train_predictions : np.ndarray
        Training set predicted probabilities
    train_actuals : np.ndarray
        Training set actual binary outcomes (0/1)
    test_predictions : np.ndarray
        Test set predicted probabilities  
    test_actuals : np.ndarray
        Test set actual binary outcomes (0/1)
    model_configuration : Dict[str, Any]
        Dictionary of model configuration parameters (e.g., {'f1_threshold': 0.15})
    n_bins : int
        Number of bins for calibration curve (default: 10)
    output_path : str
        Path to save the JSON file
        
    Returns:
    --------
    None
    """
    
    def calculate_calibration_curve(predictions: np.ndarray, actuals: np.ndarray, n_bins: int) -> Dict[str, List]:
        """Calculate calibration curve for given predictions and actuals"""
        
        # Create equal-width bins from 0 to 1
        bin_edges = np.linspace(0, 1, n_bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Digitize predictions into bins
        bin_indices = np.digitize(predictions, bin_edges) - 1
        
        # Handle edge cases (predictions exactly 1.0 go to last bin)
        bin_indices = np.clip(bin_indices, 0, n_bins - 1)
        
        calibration_data = {
            "bin_edges": bin_edges.tolist(),
            "bin_centers": bin_centers.tolist(),
            "predicted_probabilities": [],
            "actual_frequencies": [],
            "sample_counts": []
        }
        
        for i in range(n_bins):
            # Get predictions and actuals in this bin
            mask = (bin_indices == i)
            bin_predictions = predictions[mask]
            bin_actuals = actuals[mask]
            
            if len(bin_predictions) > 0:
                # Average predicted probability in this bin
                avg_predicted = float(np.mean(bin_predictions))
                # Actual frequency of positive outcomes in this bin
                actual_freq = float(np.mean(bin_actuals))
                sample_count = int(len(bin_predictions))
            else:
                # Empty bin
                avg_predicted = float(bin_centers[i])
                actual_freq = 0.0
                sample_count = 0
            
            calibration_data["predicted_probabilities"].append(avg_predicted)
            calibration_data["actual_frequencies"].append(actual_freq)
            calibration_data["sample_counts"].append(sample_count)
        
        return calibration_data
    
    # Calculate calibration curves for train and test sets
    train_calibration = calculate_calibration_curve(train_predictions, train_actuals, n_bins)
    test_calibration = calculate_calibration_curve(test_predictions, test_actuals, n_bins)
    
    # Calculate prediction statistics for drift monitoring
    prediction_statistics = {
        "train": {
            "mean_prediction": float(np.mean(train_predictions)),
            "std_prediction": float(np.std(train_predictions)),
            "min_prediction": float(np.min(train_predictions)),
            "max_prediction": float(np.max(train_predictions)),
            "median_prediction": float(np.median(train_predictions)),
            "sample_size": len(train_predictions)
        },
        "test": {
            "mean_prediction": float(np.mean(test_predictions)),
            "std_prediction": float(np.std(test_predictions)),
            "min_prediction": float(np.min(test_predictions)),
            "max_prediction": float(np.max(test_predictions)),
            "median_prediction": float(np.median(test_predictions)),
            "sample_size": len(test_predictions)
        }
    }
    
    # Build the baseline calibration JSON
    baseline_calibration = {
        "calibration_curves": {
            "train": train_calibration,
            "test": test_calibration
        },
        "prediction_statistics": prediction_statistics,
        "model_configuration": model_configuration,
        "metadata": {
            "n_bins": n_bins,
            "train_sample_size": len(train_predictions),
            "test_sample_size": len(test_predictions),
            "bin_strategy": "equal_width",
            "generation_date": pd.Timestamp.now().isoformat(),
            "usage_notes": [
                "Contains train and test calibration curves for baseline comparison",
                "Contains prediction statistics for distribution drift monitoring",
                "Contains model configuration used during training",
                "Calibration health metrics calculated fresh each time from raw predictions vs actuals"
            ]
        }
    }
    
    # Save to JSON file
    with open(output_path, 'w') as f:
        json.dump(baseline_calibration, f, indent=2)
    
    print(f"Baseline calibration saved to {output_path}")
    print(f"Generated {n_bins}-bin calibration curves for train and test sets")
    print(f"Model configuration included: {model_configuration}")
    print(f"Train sample size: {len(train_predictions):,}, Test sample size: {len(test_predictions):,}")
    
    return None


