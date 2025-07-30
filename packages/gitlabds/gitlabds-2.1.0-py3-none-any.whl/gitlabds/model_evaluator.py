"""
Model evaluation metrics for classification and regression models.

This module provides comprehensive evaluation metrics and visualizations for
machine learning models, supporting both binary and multi-class classification
as well as regression models.

See https://pypi.org/project/gitlabds/ for more information and example calls.

"""

import pandas as pd
import numpy as np
import warnings
import logging
import os
from typing import Dict, List, Tuple, Union, Optional, Callable, Any
from dataclasses import dataclass
import matplotlib.pyplot as plt
from scipy.stats import entropy
import seaborn as sns
from sklearn import metrics
from sklearn.preprocessing import label_binarize
from sklearn.calibration import calibration_curve
import importlib

# Setup logging
logger = logging.getLogger(__name__)

# Check for optional dependencies
SHAP_AVAILABLE = importlib.util.find_spec("shap") is not None



@dataclass
class ModelMetricsResult:
    """Class for storing model evaluation results."""
    metrics_df: pd.DataFrame
    classification_metrics_df: Optional[pd.DataFrame] = None
    lift_df: Optional[pd.DataFrame] = None
    feature_importance: Optional[pd.DataFrame] = None
    model_feature_list: Optional[List[str]] = None 
    decile_breaks: Optional[List[float]] = None
    decile_breaks_class: Optional[Dict[int, List[float]]] = None
    drift_metrics: Optional[pd.DataFrame] = None  

class ModelEvaluator:
    """
    Evaluates machine learning models and provides comprehensive metrics.
    
    This class handles evaluation for both classification (binary and multi-class)
    and regression models, providing metrics, visualizations, and feature importance.
    """

    #--------------------------------------------------------------------------
    # Core Functionality
    #--------------------------------------------------------------------------
    
    
    def __init__(
        self,
        model,
        x_train: pd.DataFrame,
        y_train: Union[pd.Series, pd.DataFrame],
        x_test: pd.DataFrame,
        y_test: Union[pd.Series, pd.DataFrame],
        x_oot: Optional[pd.DataFrame] = None, 
        y_oot: Optional[Union[pd.Series, pd.DataFrame]] = None,  
        classification: bool = True,
        algo: Optional[str] = None,
        f1_threshold: float = 0.50,
        decile_n: int = 10,
        top_features_n: int = 20,
        show_all_classes: bool = True,
        show_plots: bool = True,
        save_plots: bool = True, 
        plot_dir: str = "plots",
        plot_save_format: str = "png", 
        plot_save_dpi: int = 300

    ):
        """
        Initialize the model evaluator.
        
        Parameters
        ----------
        model : object
            The trained model to evaluate. Must have predict and (for classification)
            predict_proba methods.
        x_train : pd.DataFrame
            Training features.
        y_train : Union[pd.Series, pd.DataFrame]
            Training labels.
        x_test : pd.DataFrame
            Test features.
        y_test : Union[pd.Series, pd.DataFrame]
            Test labels.
        x_oot : pd.DataFrame
            Out-of-time validation features.
        y_oot : Union[pd.Series, pd.DataFrame]
            Out-of-time validation labels.
        classification : bool, default=True
            Whether this is a classification model. If False, regression metrics will be used.
        algo : str, optional
            Algorithm type for feature importance calculation. Options: 'xgb', 'rf'
        n_classes : int, optional
            Number of classes for classification. If None, will be inferred from y_train.
        f1_threshold : float, default=0.50
            Threshold for binary classification.
        decile_n : int, default=10
            Number of deciles for lift calculation.
        show_all_classes : bool, default=True
            Whether to show metrics for all classes in multi-class classification.
        show_plots: bool, default=True
            Whether to show plots
        save_plots: bool, default=True
            Whether to save plots locally
        plot_dir: str = "plots"
            Directory to save plots
        plot_save_format: str = "png"
            Plot format
        plot_save_dpi: int = 300
            Plot resolution
        """
        # Store parameters
        self.model = model
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test  
        self.y_test = y_test 
        self.classification = classification
        self.algo = algo
        self.f1_threshold = f1_threshold
        self.decile_n = decile_n
        self.top_features_n = top_features_n
        self.show_all_classes = show_all_classes

        # Store default plotting parameters
        self.show_plots = show_plots
        self.save_plots = save_plots
        self.plot_dir = plot_dir
        self.plot_save_format = plot_save_format
        self.plot_save_dpi = plot_save_dpi

        # Store OOT data if provided
        self.has_oot = x_oot is not None and y_oot is not None
        if self.has_oot:
            self.x_oot = x_oot
            self.y_oot = y_oot
        

        # Create plots directory if plot saving is enabled
        if self.save_plots:
            os.makedirs(self.plot_dir, exist_ok=True)

            
        #Determine number of classes
        if self.classification:
            self.n_classes = len(np.unique(self.y_train))

        # Set up defaults
        pd.set_option("display.float_format", lambda x: "%.5f" % x)

        # Validate all inputs
        self._validate_inputs()
        
        # Compute predictions
        self.train_preds = self._get_predictions(self.x_train, self.y_train)
        self.test_preds = self._get_predictions(self.x_test, self.y_test)

        if self.has_oot:
            self.oot_preds = self._get_predictions(self.x_oot, self.y_oot)
            
    def _validate_inputs(self) -> None:
        """
        Validate input parameters.
        
        Raises
        ------
        ValueError
            If any input parameters are invalid.
        """
        # Check f1_threshold is between 0 and 1
        if not 0 <= self.f1_threshold <= 1:
            raise ValueError(f"f1_threshold must be between 0 and 1, got {self.f1_threshold}")
        
        # Check decile_n is positive
        if self.decile_n <= 0:
            raise ValueError(f"decile_n must be positive, got {self.decile_n}")
                
        # Check model has required methods
        required_methods = ['predict']
        if self.classification:
            required_methods.append('predict_proba')
        
        for method in required_methods:
            if not hasattr(self.model, method):
                raise ValueError(f"Model must have {method} method")
        
        # Check data shapes
        if len(self.x_train) != len(self.y_train):
            raise ValueError(f"x_train and y_train must have same length, got {len(self.x_train)} and {len(self.y_train)}")
        
        if len(self.x_test) != len(self.y_test):
            raise ValueError(f"x_test and y_test must have same length, got {len(self.x_test)} and {len(self.y_test)}")


        # Validate OOT data if provided
        if self.has_oot:
            if len(self.x_oot) != len(self.y_oot):
                raise ValueError(f"x_oot and y_oot must have same length, got {len(self.x_oot)} and {len(self.y_oot)}")
            
            if not self.x_oot.index.equals(self.y_oot.index):
                warnings.warn("x_oot and y_oot indices don't match. This might cause alignment issues.")
            
            # Check OOT data has same columns as training data
            if not set(self.x_train.columns) == set(self.x_oot.columns):
                raise ValueError("OOT data must have the same columns as training data")


    def _get_predictions(self, x_data, y_data) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get model predictions for train and test data.
        
        Returns
        -------
        Tuple[pd.DataFrame, pd.DataFrame]
            DataFrames with predictions for train and test data.
        """
        if self.classification:
            # For classification, get predicted probabilities
            preds = self.model.predict_proba(x_data)
            
            if self.n_classes == 2:
       
                # Binary classification - extract probability for class 1
                df = pd.DataFrame({
                'predicted': [p[1] for p in preds],
                })

                # Add classification based on threshold
                df['classification'] = (df['predicted'] > self.f1_threshold).astype(int)  # If prediction > f-score then 1 (True), Else 0 (False)

            else:
                # Multi-class classification
                df = pd.DataFrame(
                preds,
                columns=[f'{i}' for i in range(self.n_classes)]
                )

                # Add classification based on highest probability class
                df['classification'] = df.iloc[:, :self.n_classes].idxmax(axis=1).astype(int)

        else:
            # For regression, get point predictions
            preds = self.model.predict(x_data)
            
            df = pd.DataFrame({
            'predicted': preds,
            })

        # Set indices to match original data
        df.index = x_data.index

        # Add actual values to both DataFrames (common for all cases)
        df['actual'] = y_data
        
        return df

    def evaluate(self) -> ModelMetricsResult:
        """
        Evaluate the model and return comprehensive metrics.
        
        Returns
        -------
        ModelMetricsResult
            Object containing all evaluation metrics and results.
        """
        # Compute metrics
        metrics_df = self._calculate_metrics()
        
        # Calculate classification metrics if applicable
        classification_metrics_df = None
        if self.classification:
            classification_metrics_df = self._calculate_classification_metrics()
        
        # Calculate lift table if applicable
        lift_df, decile_breaks = None, None
        if self.classification:
            lift_df, decile_breaks = self._calculate_lift()
        
        # Calculate feature importance
        feature_importance = self._calculate_feature_importance()

        # Calculate drift metrics if OOT data is available
        drift_metrics = None
        if self.has_oot:
            drift_metrics = self._calculate_drift_metrics()

        # Get list of features used in the model
        model_feature_list = list(self.x_train.columns)
                        
        return ModelMetricsResult(
            metrics_df=metrics_df,
            classification_metrics_df=classification_metrics_df,
            lift_df=lift_df,
            feature_importance=feature_importance,
            model_feature_list=model_feature_list,
            decile_breaks=decile_breaks,
            decile_breaks_class=getattr(self, 'decile_breaks_class', None),
            drift_metrics=drift_metrics
        )


    def evaluate_custom_metrics(self, custom_metrics: Dict[str, Callable]) -> ModelMetricsResult:
        """
        Evaluate the model with additional custom metrics.
        
        Parameters
        ----------
        custom_metrics : Dict[str, Callable]
            Dictionary of metric name to metric function. Each function should take
            y_true and y_pred as arguments and return a scalar value.
            
        Returns
        -------
        ModelMetricsResult
            Object containing all evaluation metrics and results.
        """
        # Calculate standard metrics
        result = self.evaluate()
        
        # Calculate custom metrics
        custom_metrics_list = []
        for name, metric_fn in custom_metrics.items():
            try:
                if self.classification and self.n_classes == 2:
                    train_value = metric_fn(self.train_preds['actual'], self.train_preds['predicted'])
                    test_value = metric_fn(self.test_preds['actual'], self.test_preds['predicted'])
                else:
                    train_value = metric_fn(self.train_preds['actual'], self.train_preds['classification' if self.classification else 'predicted'])
                    test_value = metric_fn(self.test_preds['actual'], self.test_preds['classification' if self.classification else 'predicted'])
                
                custom_metrics_list.append((name, train_value, test_value))
            except Exception as e:
                logger.warning(f"Error calculating custom metric {name}: {str(e)}")
        
        if custom_metrics_list:
            custom_df = pd.DataFrame(custom_metrics_list, columns=["metric", "train", "test"]).set_index("metric")
            result.metrics_df = pd.concat([result.metrics_df, custom_df])
        
        return result

    def display_metrics(self, results=None):
        """Display evaluation results in a formatted way."""
        if results is None:
            results = self.evaluate()
        
        print("Model Performance Metrics:")
        display(results.metrics_df.style.format({"deviation_pct": "{:.2%}"}))
        
        # Add log-loss threshold info for classification models
        if self.classification:
            # For binary classification, entropy is -sum(p*log(p)) where p is class proportion
            if self.n_classes == 2: 
                p = self.test_preds["actual"].mean()
                chance_log_loss = -(p * np.log(p) + (1-p) * np.log(1-p))
                print(f"Log-loss: values below {chance_log_loss:.4f} are better than chance.\n\n")
            else:
                # For multi-class, calculate entropy of class distribution
                class_props = self.test_preds["actual"].value_counts(normalize=True)
                chance_log_loss = -sum(p * np.log(p) for p in class_props)
                print(f"Log-loss: values below {chance_log_loss:.4f} are better than chance.\n\n")
        
        if results.classification_metrics_df is not None:
            print("\nClassification Metrics:")
            print(f"Using an F-Score of {self.f1_threshold}")
            display(results.classification_metrics_df.style.format({"deviation_pct": "{:.2%}"}))

            print("Accuracy: % of Accurate Predictions. (True Positives + True Negatives) / Total Population")
            print("Precision: % of true positives to all positives. True Positives / (True Positives + False Positives)")
            print("Recall: % of postive cases accurately classified. True Positives / (True Positives + False Negatives)")
            print("F1 Score: The harmonic mean between precision and recall.")
            print('Mean & Median Confidence: Closer to 1 more confident the model is in its predictions')
            print('Mean Entropy: Measures uncertainty . Lower = more confident but more concentrated probabilities')
        
        if results.lift_df is not None and not results.lift_df.empty:
            print("\nLift Table:")
            display(results.lift_df.style.format({
                "accuracy": "{:.1%}",
                "cume_accuracy": "{:.1%}",
                "cume_pct_correct": "{:.1%}"
            }))
            
            # Add class-specific lift tables if available and show_all_classes is True
            if (self.classification and self.n_classes > 2 and self.show_all_classes and 
                hasattr(self, 'class_lift_table') and not self.class_lift_table.empty):
                print("\nClass-Specific Lift Tables:")
                
                for class_idx in range(self.n_classes):
                    print(f"\nClass {class_idx} Lift Table:")
                    
                    # Filter columns for this class
                    class_cols = [col for col in self.class_lift_table.columns if f"class_{class_idx}_" in col]
                    
                    if not class_cols:
                        print(f"No lift data available for Class {class_idx}")
                        continue
                    
                    # Create a new DataFrame with the correctly renamed columns
                    class_df = pd.DataFrame(index=self.class_lift_table.index)
                    
                    # Standard column mapping to exactly match the main lift table
                    column_mapping = {
                        f'class_{class_idx}_total': 'count',
                        f'class_{class_idx}_count': 'correct_predictions',
                        f'class_{class_idx}_accuracy': 'accuracy',
                        f'class_{class_idx}_cume_total': 'cume_count',
                        f'class_{class_idx}_cume_count': 'cume_correct',
                        f'class_{class_idx}_cume_accuracy': 'cume_accuracy',
                        f'class_{class_idx}_lift': 'lift',
                        f'class_{class_idx}_cume_lift': 'cume_lift'
                    }
                    
                    # Copy data with renamed columns
                    for old_name, new_name in column_mapping.items():
                        if old_name in self.class_lift_table.columns:
                            class_df[new_name] = self.class_lift_table[old_name]
                    
                    # Calculate cume_pct_correct if not already present
                    if ('cume_correct' in class_df.columns and 
                        'correct_predictions' in class_df.columns and 
                        'cume_pct_correct' not in class_df.columns):
                        
                        total_correct = class_df['correct_predictions'].sum()
                        if total_correct > 0:
                            class_df['cume_pct_correct'] = class_df['cume_correct'] / total_correct
                    
                    # For confidence metrics, they might have different names in class lift tables
                    confidence_mapping = {
                        f'class_{class_idx}_confidence_mean': 'confidence_mean',
                        f'class_{class_idx}_confidence_min': 'confidence_min', 
                        f'class_{class_idx}_confidence_max': 'confidence_max'
                    }
                    
                    for old_name, new_name in confidence_mapping.items():
                        if old_name in self.class_lift_table.columns:
                            class_df[new_name] = self.class_lift_table[old_name]
                    
                    # Reorder columns to match main lift table layout
                    # Get columns from main lift table
                    main_cols = results.lift_df.columns.tolist()
                    
                    # Try to match same column order
                    ordered_cols = [col for col in main_cols if col in class_df.columns]
                    # Add any additional columns that weren't in the main lift table
                    additional_cols = [col for col in class_df.columns if col not in ordered_cols]
                    
                    if additional_cols:
                        ordered_cols.extend(additional_cols)
                    
                    # Reindex with ordered columns
                    if ordered_cols:
                        class_df = class_df[ordered_cols]
                    
                    # Format and display the class lift table
                    format_dict = {
                        "accuracy": "{:.1%}",
                        "cume_accuracy": "{:.1%}"
                    }
                    
                    if 'cume_pct_correct' in class_df.columns:
                        format_dict['cume_pct_correct'] = "{:.1%}"
                    
                    display(class_df.style.format(format_dict))
        
        return

    
    #--------------------------------------------------------------------------
    # Metric Calculations 
    #--------------------------------------------------------------------------

    def _calculate_metrics(self) -> pd.DataFrame:
        """
        Calculate appropriate metrics based on model type.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with metrics appropriate for the model type.
        """
        metrics_list = []
                
        if self.classification and self.n_classes == 2:
            # Binary classification specific metrics
            metrics_list.extend([
                (
                    "AUC",
                    metrics.roc_auc_score(self.train_preds["actual"], self.train_preds["predicted"]),
                    metrics.roc_auc_score(self.test_preds["actual"], self.test_preds["predicted"]),
                ),
                (
                    "R2",
                    metrics.r2_score(self.train_preds["actual"], self.train_preds["predicted"]),
                    metrics.r2_score(self.test_preds["actual"], self.test_preds["predicted"]),
                ),
                (   "Adj. R2",
                    1 - (1 - metrics.r2_score(self.train_preds["actual"], self.train_preds["predicted"])) * (len(self.train_preds["predicted"]) - 1) / (len(self.train_preds["predicted"]) - self.x_train.shape[1] - 1),
                    1 - (1 - metrics.r2_score(self.test_preds["actual"], self.test_preds["predicted"])) * (len(self.test_preds["predicted"]) - 1) / (len(self.test_preds["predicted"]) - self.x_test.shape[1] - 1),
                ),
                (
                    "LogLoss",
                    metrics.log_loss(self.train_preds["actual"], self.train_preds["predicted"]),
                    metrics.log_loss(self.test_preds["actual"], self.test_preds["predicted"]),
                ),
                (
                    "MSE",
                    metrics.mean_squared_error(
                        self.train_preds["actual"], self.train_preds["predicted"]
                    ),
                    metrics.mean_squared_error(
                        self.test_preds["actual"], self.test_preds["predicted"]
                    ),
                ),
                (
                    "RMSE",
                    metrics.root_mean_squared_error(
                        self.train_preds["actual"], self.train_preds["predicted"]
                    ),
                    metrics.root_mean_squared_error(
                        self.test_preds["actual"], self.test_preds["predicted"]
                    ),
                ),
                (
                    "MSLE",
                    metrics.mean_squared_log_error(
                        self.train_preds["actual"], self.train_preds["predicted"]
                    ),
                    metrics.mean_squared_log_error(
                        self.test_preds["actual"], self.test_preds["predicted"]
                    ),
                ),
            ])

            
        elif self.classification:
            # Multi-class classification specific metrics
            metrics_list.extend([
                (
                    "AUC",
                    metrics.roc_auc_score(
                        self.train_preds["actual"], 
                        self.train_preds.drop(columns=['actual', 'classification']), 
                        multi_class='ovo', 
                        average='weighted'
                    ),
                    metrics.roc_auc_score(
                        self.test_preds["actual"], 
                        self.test_preds.drop(columns=['actual', 'classification']), 
                        multi_class='ovo', 
                        average='weighted'
                    ),
                ),
                (
                    "MLogLoss",
                    metrics.log_loss(
                        self.train_preds["actual"], 
                        self.train_preds.drop(columns=['actual', 'classification'])
                    ),
                    metrics.log_loss(
                        self.test_preds["actual"], 
                        self.test_preds.drop(columns=['actual', 'classification'])
                    ),
                ),
                (
                    "Cohens Kappa",
                    metrics.cohen_kappa_score(
                        self.train_preds["actual"], 
                        self.train_preds['classification'],
                        weights=None
                    ),
                    metrics.cohen_kappa_score(
                        self.test_preds["actual"], 
                        self.test_preds['classification'],
                        weights=None
                    ),
                ),
                (
                    "MCC",
                    metrics.matthews_corrcoef(
                        self.train_preds["actual"], 
                        self.train_preds['classification']
                    ),
                    metrics.matthews_corrcoef(
                        self.test_preds["actual"], 
                        self.test_preds['classification']
                    ),
                ),
            ])
            
            # Calculate and add class distribution metrics for multi-class
            
        else:
            # Regression specific metrics
            metrics_list.extend([
                (
                    "R2",
                    metrics.r2_score(self.train_preds["actual"], self.train_preds["predicted"]),
                    metrics.r2_score(self.test_preds["actual"], self.test_preds["predicted"]),
                ),
                (   "Adj. R2",
                    1 - (1 - metrics.r2_score(self.train_preds["actual"], self.train_preds["predicted"])) * (len(self.train_preds["predicted"]) - 1) / (len(self.train_preds["predicted"]) - self.x_train.shape[1] - 1),
                    1 - (1 - metrics.r2_score(self.test_preds["actual"], self.test_preds["predicted"])) * (len(self.test_preds["predicted"]) - 1) / (len(self.test_preds["predicted"]) - self.x_test.shape[1] - 1),
                ),
                (
                    "MSE",
                    metrics.mean_squared_error(self.train_preds["actual"], self.train_preds["predicted"]),
                    metrics.mean_squared_error(self.test_preds["actual"], self.test_preds["predicted"]),
                ),
                (
                    "RMSE",
                    metrics.mean_squared_error(self.train_preds["actual"], self.train_preds["predicted"], squared=False),
                    metrics.mean_squared_error(self.test_preds["actual"], self.test_preds["predicted"], squared=False),
                ),
                (
                    "MAE",
                    metrics.mean_absolute_error(self.train_preds["actual"], self.train_preds["predicted"]),
                    metrics.mean_absolute_error(self.test_preds["actual"], self.test_preds["predicted"]),
                ),
            ])
            
            # Calculate and add adjusted R2 for regression
        
        # Common metrics for all model types
        metrics_list.append(("Actual Mean", self.train_preds["actual"].mean(), self.test_preds["actual"].mean()))

        # For multiclass use predicted class distribution
        if self.classification and self.n_classes > 2:
            # Add class distribution metrics
            for i in range(self.n_classes):
                train_class_pct = (self.train_preds["classification"] == i).mean()
                test_class_pct = (self.test_preds["classification"] == i).mean()
                metrics_list.append((f"Class {i} Predicted %", train_class_pct, test_class_pct))
        else:
            metrics_list.append(("Predicted Mean", self.train_preds["predicted"].mean(), self.test_preds["predicted"].mean()))
    

        # Create DataFrame from metrics list
        metrics_df = pd.DataFrame(metrics_list, columns=["metric", "train", "test"])
        metrics_df.set_index("metric", inplace=True)
        
        # Calculate deviation percentage
        metrics_df["deviation_pct"] = (metrics_df["test"] - metrics_df["train"]) / metrics_df["train"]
        
        return metrics_df

    def _calculate_classification_metrics(self) -> pd.DataFrame:
        """
        Calculate classification-specific metrics.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with classification metrics.
        """
        metrics_list = []
        
        # Determine which average method to use based on class count
        class_weight = 'binary' if self.n_classes == 2 else 'weighted'


            # Calculate confidence and entropy metrics first
        if self.n_classes == 2:
            # Binary classification - custom confidence calculation
            train_max_probs = np.abs(self.train_preds['predicted'] - 0.5) * 2
            test_max_probs = np.abs(self.test_preds['predicted'] - 0.5) * 2
            
            # Binary entropy calculation
            train_prob_entropy = -(self.train_preds['predicted'] * np.log2(self.train_preds['predicted']) + 
                                (1 - self.train_preds['predicted']) * np.log2(1 - self.train_preds['predicted']))
            test_prob_entropy = -(self.test_preds['predicted'] * np.log2(self.test_preds['predicted']) + 
                                (1 - self.test_preds['predicted']) * np.log2(1 - self.test_preds['predicted']))
        else:
            # Multi-class - use drop to remove non-probability columns
            # Maximum probability (confidence) for each prediction
            train_max_probs = np.max(self.train_preds.drop(columns=['actual', 'classification']), axis=1)
            test_max_probs = np.max(self.test_preds.drop(columns=['actual', 'classification']), axis=1)
            
            # Apply scipy's entropy function along rows
            train_prob_entropy = np.apply_along_axis(entropy, 1, self.train_preds.drop(columns=['actual', 'classification']))
            test_prob_entropy = np.apply_along_axis(entropy, 1, self.test_preds.drop(columns=['actual', 'classification']))

        
        # Calculate standard classification metrics
        metrics_list.extend([
            (
                "accuracy",
                metrics.accuracy_score(
                    self.train_preds["actual"], self.train_preds["classification"]
                ),
                metrics.accuracy_score(
                    self.test_preds["actual"], self.test_preds["classification"]
                ),
            ),
            (
                "precision",
                metrics.precision_score(
                    self.train_preds["actual"], self.train_preds["classification"],
                    average=class_weight
                ),
                metrics.precision_score(
                    self.test_preds["actual"], self.test_preds["classification"],
                    average=class_weight
                ),
            ),
            (
                "recall",
                metrics.recall_score(
                    self.train_preds["actual"], self.train_preds["classification"],
                    average=class_weight
                ),
                metrics.recall_score(
                    self.test_preds["actual"], self.test_preds["classification"],
                    average=class_weight
                ),
            ),
            (
                "F1 Score",
                metrics.f1_score(
                    self.train_preds["actual"], self.train_preds["classification"], 
                    average=class_weight
                ),
                metrics.f1_score(
                    self.test_preds["actual"], self.test_preds["classification"], 
                    average=class_weight
                ),
            ),
            (
                "Mean Confidence",
                np.mean(train_max_probs),
                np.mean(test_max_probs),
            ),
            (
                "Median Confidence",
                np.median(train_max_probs),
                np.median(test_max_probs),
            ),
            (
                "Mean Entropy",
                np.mean(train_prob_entropy),
                np.mean(test_prob_entropy),
            )
        ])
        
        # Create DataFrame and add deviation percentage
        classification_df = pd.DataFrame(metrics_list, columns=["metric", "train", "test"])
        classification_df["deviation_pct"] = (
            classification_df["test"] - classification_df["train"]
        ) / classification_df["train"]
        
        format_dict = {"train": "{0:,.4}", "test": "{0:.4}", "deviation_pct": "{:.2%}"}
        classification_df.set_index("metric", inplace=True)    
        #display(classification_df.style.format(format_dict))

        return classification_df


    def _calculate_lift(self) -> Tuple[pd.DataFrame, List[float]]:
        """
        
        Creates a lift/gains table by dividing predictions into deciles
        and analyzing performance within each decile. It handles both binary and
        multi-class classification.
        
        Returns
        -------
        Tuple[pd.DataFrame, List[float]]
            Lift table and decile breaks.
        """

        if not self.classification:
            # Lift tables only apply to classification
            return pd.DataFrame(), []
            
        try:
            # Calculate global deciles across all predictions based on model type
            if self.n_classes == 2:
                # For binary classification, use the positive class probability directly
                _, decile_breaks = pd.qcut(
                    self.train_preds["predicted"], 
                    self.decile_n, 
                    retbins=True, 
                    duplicates="drop", 
                    precision=10
                )

            else:
                # For multi-class, use max probability across all classes directly for global decile
                prob_cols = [str(i) for i in range(self.n_classes)]
                _, decile_breaks = pd.qcut(
                    self.train_preds[prob_cols].max(axis=1), 
                    self.decile_n, 
                    retbins=True, 
                    duplicates="drop", 
                    precision=10
                )
                # Add 'correct' column to test data for multi-class
                self.test_preds["correct"] = (self.test_preds["actual"] == self.test_preds['classification'])
            
            # Set bounds to 0 and 1 to handle edge cases
            decile_breaks[0] = 0
            decile_breaks[-1] = 1
            
            # Add decile to train and test data
            if self.n_classes == 2:
                # Binary classification
                self.train_preds["decile"] = pd.cut(
                    self.train_preds["predicted"],
                    decile_breaks,
                    labels=np.arange(len(decile_breaks) - 1, 0, step=-1),
                    include_lowest=True
                )
                self.test_preds["decile"] = pd.cut(
                    self.test_preds["predicted"],
                    decile_breaks,
                    labels=np.arange(len(decile_breaks) - 1, 0, step=-1),
                    include_lowest=True
                )

            else:
                # Multi-class classification
                self.train_preds["decile"] = pd.cut(
                    self.train_preds[prob_cols].max(axis=1),
                    decile_breaks,
                    labels=np.arange(len(decile_breaks) - 1, 0, step=-1),
                    include_lowest=True
                )
                self.test_preds["decile"] = pd.cut(
                    self.test_preds[prob_cols].max(axis=1),
                    decile_breaks,
                    labels=np.arange(len(decile_breaks) - 1, 0, step=-1),
                    include_lowest=True
                )
            
            # Convert decile to numeric
            self.train_preds["decile"] = pd.to_numeric(self.train_preds["decile"], downcast="integer")
            self.test_preds["decile"] = pd.to_numeric(self.test_preds["decile"], downcast="integer")
            
            # Create lift table with optimized aggregations
            if self.n_classes == 2:
                # Binary classification lift table
                lift = self.test_preds.groupby(["decile"]).agg({
                    "decile": ["count"],
                    "actual": [lambda x: sum(x == 1), "mean"],
                    "predicted": ["mean", "min", "max"]
                })
                
                lift.columns = [
                    "count",
                    "correct_predictions",
                    "accuracy",
                    "predicted_mean",
                    "predicted_min",
                    "predicted_max"
                ]

            else:
                # Multi-class lift table
                lift = self.test_preds.groupby(["decile"]).agg({
                    "decile": ["count"],
                    "correct": ["sum", "mean"]  # sum and mean of correct predictions
                })
                
                # Add confidence metrics efficiently
                grouped = self.test_preds.groupby("decile")
                
                # Calculate max probabilities for each row and add aggregates to lift table
                # We do this calculation once and use it for all three metrics
                lift["confidence_mean"] = grouped.apply(
                    lambda x: x[prob_cols].max(axis=1).mean(), include_groups=False
                )
                lift["confidence_min"] = grouped.apply(
                    lambda x: x[prob_cols].max(axis=1).min(), include_groups=False
                )
                lift["confidence_max"] = grouped.apply(
                    lambda x: x[prob_cols].max(axis=1).max(), include_groups=False
                )
                
                lift.columns = [
                    "count",
                    "correct_predictions",
                    "accuracy",
                    "confidence_mean",
                    "confidence_min",
                    "confidence_max"
                ]
            
            # Calculate cumulative metrics efficiently
            lift["cume_count"] = lift["count"].cumsum()
            lift["cume_correct"] = lift["correct_predictions"].cumsum()
            lift["cume_accuracy"] = lift["cume_correct"] / lift["cume_count"]
            lift["cume_pct_correct"] = lift["cume_correct"] / lift["correct_predictions"].sum()
            
            # Calculate lift (relative to random accuracy)
            # Lift = Resp Mean for each Decile / Total Cume Responses (i.e. last Row of Cume Resp Mean).
            # This shows how much more likely the outcome is to happe to that decile compared to the average.
            # 300 Lift = 3x (or 300%) more likely to respond/attrite/engage/etc.
            # 40 Lift = 60% (100 - 40)less likely to respond/attrite/engage/etc.
            random_accuracy = lift["correct_predictions"].sum() / lift["count"].sum()
            lift["lift"] = (lift["accuracy"] / random_accuracy * 100).astype(int)
            # Cume Lift = Cume. Resp n for each Decile / Total Cume Responses (i.e. last row of cume resp n)
            # This shows how "deep" you can go in the model while still gettting better results than randomly selecting records for treatment
            # Cume Lift 100 = Would expect to get as many posititve instances of the outcome as chance/random guessing
            lift["cume_lift"] = (lift["cume_accuracy"] / random_accuracy * 100).astype(int)
            
            # For multi-class, calculate class-specific lift tables if needed
            if self.n_classes > 2:
                # Create an empty DataFrame to store class-specific lift metrics
                self.class_lift_table = pd.DataFrame()

                # Create a dictionary to store class-specific decile breaks
                self.decile_breaks_class = {}
                
                for class_label in range(self.n_classes):
                    # Create class deciles directly from probability column
                    _, class_breaks = pd.qcut(
                        self.train_preds[str(class_label)], 
                        self.decile_n, 
                        retbins=True, 
                        duplicates="drop", 
                        precision=10
                    )
                    
                    # Set bounds
                    class_breaks[0] = 0
                    class_breaks[-1] = 1

                    # Store the class-specific breaks in the dictionary
                    self.decile_breaks_class[class_label] = class_breaks
                    
                    # Add class-specific decile column
                    col_name = f"decile_{class_label}"
                    self.train_preds[col_name] = pd.cut(
                        self.train_preds[str(class_label)],
                        class_breaks,
                        labels=np.arange(len(class_breaks) - 1, 0, step=-1),
                        include_lowest=True
                    )
                    self.test_preds[col_name] = pd.cut(
                        self.test_preds[str(class_label)],
                        class_breaks,
                        labels=np.arange(len(class_breaks) - 1, 0, step=-1),
                        include_lowest=True
                    )
                    
                    # Convert to numeric
                    self.train_preds[col_name] = pd.to_numeric(self.train_preds[col_name], downcast="integer")
                    self.test_preds[col_name] = pd.to_numeric(self.test_preds[col_name], downcast="integer")
                    
                    # Create class-specific metrics directly
                    class_lift = pd.DataFrame()
                    grouped = self.test_preds.groupby(col_name)
                    
                    # Calculate metrics efficiently
                    class_lift[f"class_{class_label}_total"] = grouped.size()
                    class_lift[f"class_{class_label}_count"] = grouped.apply(
                        lambda x: sum(x["actual"] == class_label)
                    )
                    class_lift[f"class_{class_label}_accuracy"] = (
                        class_lift[f"class_{class_label}_count"] / 
                        class_lift[f"class_{class_label}_total"]
                    )
                    
                    # Calculate cumulative metrics
                    class_lift[f"class_{class_label}_cume_count"] = class_lift[f"class_{class_label}_count"].cumsum()
                    class_lift[f"class_{class_label}_cume_total"] = class_lift[f"class_{class_label}_total"].cumsum()
                    class_lift[f"class_{class_label}_cume_accuracy"] = (
                        class_lift[f"class_{class_label}_cume_count"] / 
                        class_lift[f"class_{class_label}_cume_total"]
                    )
                    
                    # Calculate lift
                    random_accuracy = (
                        class_lift[f"class_{class_label}_count"].sum() / 
                        class_lift[f"class_{class_label}_total"].sum()
                    )
                    
                    class_lift[f"class_{class_label}_lift"] = (
                        class_lift[f"class_{class_label}_accuracy"] / 
                        random_accuracy * 100
                    ).round(2)
                    
                    class_lift[f"class_{class_label}_cume_lift"] = (
                        class_lift[f"class_{class_label}_cume_accuracy"] / 
                        random_accuracy * 100
                    ).round(2)
                    

                    self.class_lift_table = self.class_lift_table.merge(
                            class_lift, how='outer', left_index=True, right_index=True
                        )

                self.class_lift_table.index.names = ['decile']

            return lift, decile_breaks
        
        except Exception as e:
            # Handle any errors gracefully
            import traceback
            error_msg = f"Error calculating lift: {str(e)}\n{traceback.format_exc()}"
            warnings.warn(error_msg)
        return pd.DataFrame(), []


    def _calculate_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Calculate feature importance with graceful degradation if SHAP is unavailable.
        
        Returns
        -------
        pd.DataFrame or None
            DataFrame with feature importance, or None if not calculable.
        """        
        if self.algo == "rf":
            # Random Forest feature importance
            try:
                features = pd.DataFrame({
                    "feature": self.x_train.columns,
                    "importance": self.model.feature_importances_
                })
                return features.sort_values(by=["importance"], ascending=False)
            except Exception as e:
                logger.warning(f"Could not calculate RF feature importance: {str(e)}")
                return None
        
        elif self.algo == "xgb":
            # XGBoost feature importance
            # Try using SHAP if available
            if SHAP_AVAILABLE:
                import shap
                try:
                    # Create explainer
                    explainer = shap.Explainer(self.model)
                    
                    # Calculate and store SHAP values on training and test data
                    self.shap_train_values = explainer(self.x_train)
                    self.shap_test_values = explainer(self.x_test)
                    
                    if self.n_classes == 2:
                        # Binary classification - process SHAP values directly
                        # Handle different SHAP value formats
                        if hasattr(self.shap_train_values, 'values'):
                            # For newer SHAP versions
                            result = pd.DataFrame({
                                'feature': self.x_train.columns,
                                'importance': np.abs(self.shap_train_values.values).mean(0)
                            })
                        else:
                            # For older SHAP versions
                            result = pd.DataFrame({
                                'feature': self.x_train.columns,
                                'importance': np.abs(np.array(self.shap_train_values)).mean(0)
                            })
                    else:
                        # Multi-class - take mean across all classes
                        # Handle different possible shapes of SHAP values
                        if hasattr(self.shap_train_values, 'values'):
                            values_shape = self.shap_train_values.values.shape
                            if len(values_shape) == 3:
                                # Shape is (samples, features, classes)
                                global_shap_values = np.abs(self.shap_train_values.values).mean(axis=0).mean(axis=1)
                            else:
                                # Handle unexpected shapes with more robust averaging
                                logger.warning(f"Unexpected SHAP values shape: {values_shape}, attempting to average appropriately")
                                # Try flattening the last dimension if it exists
                                global_shap_values = np.abs(self.shap_train_values.values).mean(axis=0)
                                if len(global_shap_values.shape) > 1:
                                    global_shap_values = global_shap_values.mean(axis=1)
                        else:
                            # Direct numpy array handling
                            shap_array = np.array(self.shap_train_values)
                            if len(shap_array.shape) == 3:
                                global_shap_values = np.abs(shap_array).mean(axis=0).mean(axis=1)
                            else:
                                # For unexpected shapes, try best effort averaging
                                global_shap_values = np.abs(shap_array).mean(axis=0)
                                if len(global_shap_values.shape) > 1 and global_shap_values.shape[1] > 1:
                                    global_shap_values = global_shap_values.mean(axis=1)
                        
                        # Create result DataFrame
                        result = pd.DataFrame({
                            'feature': self.x_train.columns, 
                            'importance': global_shap_values
                        })

                    return result.sort_values(by=["importance"], ascending=False)
                        
                except Exception as e:
                    logger.warning(f"Could not calculate XGBoost SHAP feature importance: {str(e)}")
                    
                    # Fallback to built-in feature importance
                    try:
                        features = pd.DataFrame({
                            "feature": self.x_train.columns,
                            "importance": self.model.feature_importances_
                        })
                        return features.sort_values(by=["importance"], ascending=False)
                    except Exception as e2:
                        logger.warning(f"Could not calculate XGBoost built-in feature importance: {str(e2)}")
                        return None
            else:
                # SHAP not available, use built-in feature importance
                try:
                    features = pd.DataFrame({
                        "feature": self.x_train.columns,
                        "importance": self.model.feature_importances_
                    })
                    return features.sort_values(by=["importance"], ascending=False)
                except Exception as e:
                    logger.warning(f"Could not calculate XGBoost built-in feature importance: {str(e)}")
                    return None
        
        else:
            # Generic models - try various approaches
            try:
                # Try using SHAP if available
                if SHAP_AVAILABLE:
                    import shap
                    try:
                        masker = shap.maskers.Independent(data=self.x_test)
                        explainer = shap.Explainer(self.model, masker)
                        
                        # Store SHAP values for later use
                        self.shap_train_values = explainer(self.x_train)
                        self.shap_test_values = explainer(self.x_test)
                        
                        # Calculate feature importance
                        if hasattr(self.shap_train_values, 'values'):
                            # Handle different dimensions
                            if len(self.shap_train_values.values.shape) == 3:
                                # Multi-class case
                                importance_values = np.abs(self.shap_train_values.values).mean(axis=0).mean(axis=1)
                            else:
                                # Binary or regression case
                                importance_values = np.abs(self.shap_train_values.values).mean(axis=0)
                        else:
                            # Direct array handling
                            shap_array = np.array(self.shap_train_values)
                            if len(shap_array.shape) == 3:
                                importance_values = np.abs(shap_array).mean(axis=0).mean(axis=1)
                            else:
                                importance_values = np.abs(shap_array).mean(axis=0)
                        
                        features = pd.DataFrame({
                            "feature": self.x_train.columns,
                            "importance": importance_values
                        })
                        return features.sort_values(by=["importance"], ascending=False)
                    except Exception as e:
                        logger.warning(f"Could not calculate SHAP feature importance: {str(e)}")
                        # Fall back to other methods
                
                # Try model coefficients
                if hasattr(self.model, 'coef_'):
                    coef = self.model.coef_
                    if coef.ndim > 1:
                        coef = np.abs(coef).mean(axis=0)
                    
                    features = pd.DataFrame({
                        "feature": self.x_train.columns,
                        "importance": np.abs(coef)
                    })
                    return features.sort_values(by=["importance"], ascending=False)
                
                # Try feature_importances_ attribute (common in tree-based models)
                elif hasattr(self.model, 'feature_importances_'):
                    features = pd.DataFrame({
                        "feature": self.x_train.columns,
                        "importance": self.model.feature_importances_
                    })
                    return features.sort_values(by=["importance"], ascending=False)
                
                # Try permutation importance as a last resort
                else:
                    try:
                        from sklearn.inspection import permutation_importance
                        
                        perm_importance = permutation_importance(
                            self.model, self.x_test, self.y_test, n_repeats=10, random_state=42
                        )
                        
                        features = pd.DataFrame({
                            "feature": self.x_train.columns,
                            "importance": perm_importance.importances_mean
                        })
                        return features.sort_values(by=["importance"], ascending=False)
                    except Exception as e:
                        logger.warning(f"Could not calculate permutation importance: {str(e)}")
                        return None
            
            except Exception as e:
                logger.warning(f'Feature importance could not be computed: {str(e)}')
                return None


    def _calculate_drift_metrics(self) -> pd.DataFrame:
        """Calculate metrics to measure drift between test and OOT data."""
        from scipy.stats import ks_2samp
        
        # Calculate drift in predictions
        ks_results = []
        
        # Compare test vs OOT predictions
        if self.classification and self.n_classes == 2:
            # Binary classification - compare probability predictions
            test_pred = self.test_preds["predicted"]
            oot_pred = self.oot_preds["predicted"]
            
            statistic, pvalue = ks_2samp(test_pred, oot_pred)
            ks_results.append(("Prediction Drift", statistic, pvalue))
        elif self.classification:
            # Multi-class - compare class distributions
            test_classes = self.test_preds["classification"]
            oot_classes = self.oot_preds["classification"]
            
            # Compare using chi-square test
            from scipy.stats import chi2_contingency
            test_counts = np.bincount(test_classes, minlength=self.n_classes)
            oot_counts = np.bincount(oot_classes, minlength=self.n_classes)
            
            statistic, pvalue, _, _ = chi2_contingency([test_counts, oot_counts])
            ks_results.append(("Class Distribution Drift", statistic, pvalue))
        else:
            # Regression - compare prediction distributions
            test_pred = self.test_preds["predicted"]
            oot_pred = self.oot_preds["predicted"]
            
            statistic, pvalue = ks_2samp(test_pred, oot_pred)
            ks_results.append(("Prediction Drift", statistic, pvalue))
        
        # Calculate feature drift for key features
        for feature in self.x_test.columns:
            test_values = self.x_test[feature]
            oot_values = self.x_oot[feature]
            
            try:
                statistic, pvalue = ks_2samp(test_values, oot_values)
                ks_results.append((f"Feature: {feature}", statistic, pvalue))
            except Exception:
                # Skip features that can't be compared (e.g., categorical features)
                continue
        
        # Create DataFrame
        drift_df = pd.DataFrame(ks_results, columns=["metric", "ks_statistic", "p_value"])
        drift_df.set_index("metric", inplace=True)
        
        # Add significance indicator
        drift_df["significant_drift"] = drift_df["p_value"] < 0.05
        
        return drift_df


    def calibration_assessment(self,      
        show_plot: bool = None,  
        save_plot: bool = None, 
        plot_dir: str = None, 
        plot_name: str = "calibration_assessment", 
        plot_save_format: str = None, 
        plot_save_dpi: int = None) -> pd.DataFrame:
        """
        Assess model calibration for classification models.
        
        This method evaluates how well a model's predicted probabilities
        match the actual observed frequencies of the target variable.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with calibration metrics.
        """
        if not self.classification:
            logger.warning("Calibration assessment only applicable for classification models.")
            return pd.DataFrame()
        
        # Initialize metrics list
        metrics_list = []
        
        if self.n_classes == 2:
            # Binary classification
            
            # Calculate Brier score for train and test
            train_brier = metrics.brier_score_loss(self.train_preds['actual'], self.train_preds['predicted'])
            test_brier = metrics.brier_score_loss(self.test_preds['actual'], self.test_preds['predicted'])
            metrics_list.append(("Brier Score", train_brier, test_brier))
            
            # Calculate log loss (cross-entropy)
            train_log_loss = metrics.log_loss(self.train_preds['actual'], self.train_preds['predicted'])
            test_log_loss = metrics.log_loss(self.test_preds['actual'], self.test_preds['predicted'])
            metrics_list.append(("Log Loss", train_log_loss, test_log_loss))
            
            # Calculate Expected Calibration Error (ECE)
            n_bins = 10
            
            # ECE for train
            prob_true_train, prob_pred_train = calibration_curve(
                self.train_preds['actual'], 
                self.train_preds['predicted'], 
                n_bins=n_bins,
                strategy='uniform'
            )
            train_ece = np.mean(np.abs(prob_true_train - prob_pred_train))
            
            # ECE for test
            prob_true_test, prob_pred_test = calibration_curve(
                self.test_preds['actual'], 
                self.test_preds['predicted'], 
                n_bins=n_bins,
                strategy='uniform'
            )
            test_ece = np.mean(np.abs(prob_true_test - prob_pred_test))
            
            metrics_list.append(("Expected Calibration Error", train_ece, test_ece))
            
            # Create calibration plot
            fig = plt.figure(figsize=(12, 8))
            
            # Main plot for calibration curve
            gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.1)
            ax1 = fig.add_subplot(gs[0])
            ax2 = fig.add_subplot(gs[1], sharex=ax1)
            
            # Plot perfectly calibrated line
            ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
            
            # Plot train calibration curve
            ax1.plot(
                prob_pred_train, prob_true_train, "s-", 
                label=f"Train (Brier: {train_brier:.3f}, ECE: {train_ece:.3f})",
                color='blue'
            )
            
            # Plot test calibration curve
            ax1.plot(
                prob_pred_test, prob_true_test, "s-", 
                label=f"Test (Brier: {test_brier:.3f}, ECE: {test_ece:.3f})",
                color='orange'
            )
            
            # Add histograms of predicted probabilities
            ax2.hist(
                self.train_preds['predicted'], 
                range=(0, 1), bins=n_bins, 
                histtype="step", 
                color='blue', 
                alpha=0.5,
                label="Train"
            )
            
            ax2.hist(
                self.test_preds['predicted'], 
                range=(0, 1), bins=n_bins, 
                histtype="step", 
                color='orange', 
                alpha=0.5,
                label="Test"
            )
            
            # Set labels and title
            ax1.set_ylabel("Fraction of positives")
            ax1.set_xlabel("")
            ax1.set_ylim([-0.05, 1.05])
            ax1.legend(loc="best")
            ax1.set_title("Calibration Curves (Reliability Diagram)")
            ax1.grid(True, alpha=0.3)
            
            ax2.set_xlabel("Mean predicted probability")
            ax2.set_ylabel("Count")
            ax2.legend(loc="best")
            ax2.grid(True, alpha=0.3)
            
            #plt.tight_layout()

            # Use instance defaults if parameters not provided
            show_plot = self.show_plots if show_plot is None else show_plot
            save_plot = self.save_plots if save_plot is None else save_plot
            plot_dir = self.plot_dir if plot_dir is None else plot_dir
            plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
            plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

            if save_plot:
                # Create path using directory and plot name
                os.makedirs(plot_dir, exist_ok=True)
                save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
                plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")

            if show_plot:
                plt.show()
            else:
                plt.close()
            
        else:
            # Multi-class calibration
            
            # For multi-class, calculate metrics for each class
            for class_idx in range(self.n_classes):
                # Extract binary probabilities for this class (one-vs-rest)
                y_train_binary = (self.train_preds['actual'] == class_idx).astype(int)
                y_test_binary = (self.test_preds['actual'] == class_idx).astype(int)
                
                prob_train = self.train_preds[str(class_idx)]
                prob_test = self.test_preds[str(class_idx)]
                
                # Brier score for this class
                train_brier = metrics.brier_score_loss(y_train_binary, prob_train)
                test_brier = metrics.brier_score_loss(y_test_binary, prob_test)
                metrics_list.append((f"Class {class_idx} Brier Score", train_brier, test_brier))
                
                # Log loss for this class
                try:
                    train_log_loss = metrics.log_loss(y_train_binary, prob_train)
                    test_log_loss = metrics.log_loss(y_test_binary, prob_test)
                    metrics_list.append((f"Class {class_idx} Log Loss", train_log_loss, test_log_loss))
                except Exception as e:
                    logger.warning(f"Could not calculate log loss for class {class_idx}: {str(e)}")
                
                # ECE for this class
                try:
                    n_bins = 10
                    
                    # ECE for train
                    prob_true_train, prob_pred_train = calibration_curve(
                        y_train_binary, 
                        prob_train, 
                        n_bins=n_bins,
                        strategy='uniform'
                    )
                    train_ece = np.mean(np.abs(prob_true_train - prob_pred_train))
                    
                    # ECE for test
                    prob_true_test, prob_pred_test = calibration_curve(
                        y_test_binary, 
                        prob_test, 
                        n_bins=n_bins,
                        strategy='uniform'
                    )
                    test_ece = np.mean(np.abs(prob_true_test - prob_pred_test))
                    
                    metrics_list.append((f"Class {class_idx} ECE", train_ece, test_ece))
                    
                    # Create calibration plot for this class
                    fig = plt.figure(figsize=(12, 8))
                    
                    # Main plot for calibration curve
                    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.1)
                    ax1 = fig.add_subplot(gs[0])
                    ax2 = fig.add_subplot(gs[1], sharex=ax1)
                    
                    # Plot perfectly calibrated line
                    ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
                    
                    # Plot train calibration curve
                    ax1.plot(
                        prob_pred_train, prob_true_train, "s-", 
                        label=f"Train (Brier: {train_brier:.3f}, ECE: {train_ece:.3f})",
                        color='blue'
                    )
                    
                    # Plot test calibration curve
                    ax1.plot(
                        prob_pred_test, prob_true_test, "s-", 
                        label=f"Test (Brier: {test_brier:.3f}, ECE: {test_ece:.3f})",
                        color='orange'
                    )
                    
                    # Add histograms of predicted probabilities
                    ax2.hist(
                        prob_train, 
                        range=(0, 1), bins=n_bins, 
                        histtype="step", 
                        color='blue', 
                        alpha=0.5,
                        label="Train"
                    )
                    
                    ax2.hist(
                        prob_test, 
                        range=(0, 1), bins=n_bins, 
                        histtype="step", 
                        color='orange', 
                        alpha=0.5,
                        label="Test"
                    )
                    
                    # Set labels and title
                    ax1.set_ylabel("Fraction of positives")
                    ax1.set_xlabel("")
                    ax1.set_ylim([-0.05, 1.05])
                    ax1.legend(loc="best")
                    ax1.set_title(f"Calibration Curve for Class {class_idx}")
                    ax1.grid(True, alpha=0.3)
                    
                    ax2.set_xlabel("Mean predicted probability")
                    ax2.set_ylabel("Count")
                    ax2.legend(loc="best")
                    ax2.grid(True, alpha=0.3)
                    
                    #plt.tight_layout()

                    # Use instance defaults if parameters not provided
                    show_plot = self.show_plots if show_plot is None else show_plot
                    save_plot = self.save_plots if save_plot is None else save_plot
                    plot_dir = self.plot_dir if plot_dir is None else plot_dir
                    plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
                    plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

                    if save_plot:
                        # Create path using directory and plot name
                        os.makedirs(plot_dir, exist_ok=True)
                        save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
                        plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")

                    if show_plot:
                        plt.show()
                    else:
                        plt.close()
                    
                except Exception as e:
                    logger.warning(f"Could not calculate calibration curve for class {class_idx}: {str(e)}")
        
        # Create DataFrame with metrics
        calibration_df = pd.DataFrame(metrics_list, columns=["metric", "train", "test"])
        calibration_df.set_index("metric", inplace=True)
        
        # Calculate deviation percentage
        calibration_df["deviation_pct"] = (calibration_df["test"] - calibration_df["train"]) / calibration_df["train"]
        
        return calibration_df

    def get_feature_descriptives(
        self, 
        display_results: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate basic descriptive statistics for model features and predictions.
        
        Parameters
        ----------
        display_results : bool, default=True
            Whether to display the results immediately.
            
        Returns
        -------
        Dict[str, pd.DataFrame]
            Dictionary containing DataFrames with descriptive statistics.
        """
        results = {}
        
        # Train data descriptives
        results['train_predictions'] = self.train_preds.describe()
        results['train_features'] = self.x_train.describe()
        
        # Test data descriptives
        results['test_predictions'] = self.test_preds.describe()
        results['test_features'] = self.x_test.describe()
        
        # Display results if requested
        if display_results:
            print("\nTrain Prediction Descriptives:")
            display(results['train_predictions'])
            
            print("\nTrain Feature Descriptives:")
            display(results['train_features'])
            
            print("\nTest Prediction Descriptives:")
            display(results['test_predictions'])
            
            print("\nTest Feature Descriptives:")
            display(results['test_features'])
        
        return results


    #--------------------------------------------------------------------------
    # Visualizations
    #--------------------------------------------------------------------------
        
    def plot_feature_importance(
        self,
        feature_importance: pd.DataFrame,
        n_features: int = 20,
        figsize: Tuple[int, int] = (12, 8),
        title: str = "Feature Importance - Train vs Test",
        style: str = "whitegrid",
        show_test: bool = True,
        show_plot: bool = None,
        save_plot: bool = None, 
        plot_dir: str = None, 
        plot_name: str = "feature_importance", 
        plot_save_format: str = None, 
        plot_save_dpi: int = None
    ):
        """
        Plot feature importance for both training and test datasets.
        
        Parameters
        ----------
        feature_importance : pd.DataFrame
            DataFrame with feature importance.
        n_features : int, default=20
            Number of top features to display.
        figsize : Tuple[int, int], default=(12, 8)
            Figure size.
        title : str, default="Feature Importance - Train vs Test"
            Plot title.
        style : str, default="whitegrid"
            Seaborn style.
        show_test : bool, default=True
            Whether to show test importance alongside train importance.
        """
        if feature_importance is None or feature_importance.empty:
            logger.warning("No feature importance data to plot.")
            return
        
        # Set style
        sns.set_theme(style=style)
        
        # Get top n features for standard plot
        top_features = feature_importance.head(n_features)
        
        # Generate the standard overall feature importance plot first
        # Standard single-plot code follows (unchanged from your current version)
        # If we have SHAP values for both train and test datasets
        if hasattr(self, 'shap_train_values') and hasattr(self, 'shap_test_values') and show_test:
            plt.figure(figsize=figsize)
            
            # Calculate feature importance for test dataset using the same method
            if self.n_classes == 2:
                test_importance = np.abs(self.shap_test_values.values).mean(0)
            else:
                test_importance = np.abs(self.shap_test_values.values).mean(axis=2).mean(axis=0)
            
            # Create DataFrame with both train and test importance
            compare_df = pd.DataFrame({
                'feature': self.x_train.columns,
                'train_importance': np.abs(self.shap_train_values.values).mean(0) if self.n_classes == 2 
                                   else np.abs(self.shap_train_values.values).mean(axis=2).mean(axis=0),
                'test_importance': test_importance
            })
            
            # Sort by train importance
            compare_df = compare_df.sort_values('train_importance', ascending=False).head(n_features)
            
            # Melt for easier plotting
            compare_df_melted = pd.melt(
                compare_df, 
                id_vars=['feature'], 
                value_vars=['train_importance', 'test_importance'],
                var_name='dataset', 
                value_name='importance'
            )
            
            # Plot
            ax = sns.barplot(
                x='importance', 
                y='feature', 
                hue='dataset', 
                data=compare_df_melted,
                palette=['#1f77b4', '#ff7f0e']  # Blue for train, orange for test
            )
            
            plt.title(title)
            plt.xlabel('Mean |SHAP Value|')
            plt.tight_layout()
            plt.legend(title='Dataset')
            
        # If no SHAP values, but we still want to show test importance
        elif show_test and hasattr(self.model, 'feature_importances_') or hasattr(self.model, 'coef_'):
            plt.figure(figsize=figsize)
            
            # For models with feature_importances_ attribute, calculate test importance
            # using a permutation approach
            try:
                from sklearn.inspection import permutation_importance
                
                # Calculate permutation importance on test set
                perm_importance = permutation_importance(
                    self.model, self.x_test, self.y_test, 
                    n_repeats=10, random_state=42
                )
                
                # Create comparison DataFrame
                compare_df = pd.DataFrame({
                    'feature': self.x_train.columns,
                    'train_importance': feature_importance['importance'].values,
                    'test_importance': perm_importance.importances_mean
                })
                
                # Sort by train importance and keep top features
                compare_df = compare_df.sort_values('train_importance', ascending=False).head(n_features)
                
                # Melt for easier plotting
                compare_df_melted = pd.melt(
                    compare_df, 
                    id_vars=['feature'], 
                    value_vars=['train_importance', 'test_importance'],
                    var_name='dataset', 
                    value_name='importance'
                )
                
                # Plot
                ax = sns.barplot(
                    x='importance', 
                    y='feature', 
                    hue='dataset', 
                    data=compare_df_melted,
                    palette=['#1f77b4', '#ff7f0e']  # Blue for train, orange for test
                )
                
                plt.title(title)
                plt.xlabel('Feature Importance')
                plt.tight_layout()
                plt.legend(title='Dataset')
                
            except (ImportError, Exception) as e:
                # Fallback to single feature importance plot
                plt.figure(figsize=figsize)
                ax = sns.barplot(x="importance", y="feature", data=top_features)
                ax.set(title="Feature Importance (Training Data Only)")
                plt.xlabel('Importance')
                plt.tight_layout()
                logger.warning(f"Could not calculate test importance: {str(e)}")
        else:
            # Fallback to single feature importance plot
            plt.figure(figsize=figsize)
            ax = sns.barplot(x="importance", y="feature", data=top_features)
            ax.set(title=title if not show_test else "Feature Importance (Training Data Only)")
            plt.xlabel('Importance')
            plt.tight_layout()
        
        # Handle the overall plot
        show_plot = self.show_plots if show_plot is None else show_plot
        save_plot = self.save_plots if save_plot is None else save_plot
        plot_dir = self.plot_dir if plot_dir is None else plot_dir
        plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
        plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

        if save_plot:
            # Create path using directory and plot name
            os.makedirs(plot_dir, exist_ok=True)
            save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
            plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")

        if show_plot:
            plt.show()
        else:
            plt.close()
        
        # Now add the multi-class visualization if needed
        if self.classification and self.n_classes > 2 and self.show_all_classes:
            try:
                # Create a figure with subplots for each class
                n_plots = self.n_classes
                n_cols = min(2, n_plots)
                n_rows = (n_plots + n_cols - 1) // n_cols
                
                # Make the multi-class plot a bit larger
                multi_figsize = (figsize[0] * 1.2, figsize[1] * n_rows / 2)
                fig, axes = plt.subplots(n_rows, n_cols, figsize=multi_figsize)
                
                # Make axes array for easier indexing
                if n_plots == 1:
                    axes = np.array([axes])
                else:
                    axes = np.reshape(axes, -1)  # Flatten regardless of shape
                
                # Check if we have SHAP values with class dimension
                if hasattr(self, 'shap_train_values') and hasattr(self, 'shap_test_values'):
                    # Extract SHAP values
                    if hasattr(self.shap_train_values, 'values'):
                        train_shap_values = self.shap_train_values.values
                        test_shap_values = self.shap_test_values.values
                    else:
                        train_shap_values = np.array(self.shap_train_values)
                        test_shap_values = np.array(self.shap_test_values)
                    
                    # Check if SHAP values have the expected shape for class-specific plots
                    if (len(train_shap_values.shape) == 3 and 
                        train_shap_values.shape[2] == self.n_classes and
                        len(test_shap_values.shape) == 3 and 
                        test_shap_values.shape[2] == self.n_classes):
                        
                        # Create one subplot per class
                        for class_idx in range(self.n_classes):
                            if class_idx < len(axes):
                                ax = axes[class_idx]
                                
                                # Get class-specific SHAP values
                                train_class_importance = np.abs(train_shap_values[:, :, class_idx]).mean(axis=0)
                                test_class_importance = np.abs(test_shap_values[:, :, class_idx]).mean(axis=0)
                                
                                # Create DataFrame for comparison
                                class_df = pd.DataFrame({
                                    'feature': self.x_train.columns,
                                    'train_importance': train_class_importance,
                                    'test_importance': test_class_importance
                                }).sort_values('train_importance', ascending=False).head(n_features)
                                
                                # Melt for easier plotting
                                class_df_melted = pd.melt(
                                    class_df, 
                                    id_vars=['feature'], 
                                    value_vars=['train_importance', 'test_importance'],
                                    var_name='dataset', 
                                    value_name='importance'
                                )
                                
                                # Plot
                                sns.barplot(
                                    x='importance', 
                                    y='feature', 
                                    hue='dataset', 
                                    data=class_df_melted,
                                    palette=['#1f77b4', '#ff7f0e'],  # Blue for train, orange for test
                                    ax=ax
                                )
                                
                                ax.set_title(f"Class {class_idx} Feature Importance")
                                ax.set_xlabel('Mean |SHAP Value|')
                                
                                # Only show the legend on the first plot to save space
                                if class_idx == 0:
                                    ax.legend(title="Dataset")
                                else:
                                    ax.get_legend().remove()
                    else:
                        # No class dimension in SHAP values, try permutation importance
                        self._plot_class_permutation_subplots(axes, n_features)
                else:
                    # No SHAP values, try permutation importance
                    self._plot_class_permutation_subplots(axes, n_features)
                
                # Hide any unused axes
                for i in range(n_plots, len(axes)):
                    axes[i].set_visible(False)
                
                plt.suptitle("Class-Specific Feature Importance - Train vs Test", fontsize=16)
                plt.tight_layout(rect=[0, 0.03, 1, 0.97])  # Adjust for suptitle
                
                # Handle display/save for multi-class plot
                if save_plot:
                    os.makedirs(plot_dir, exist_ok=True)
                    save_path = os.path.join(plot_dir, f"{plot_name}_by_class.{plot_save_format}")
                    plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")
                    
                if show_plot:
                    plt.show()
                else:
                    plt.close()
                    
            except Exception as e:
                logger.warning(f"Error creating class-specific feature importance plots: {str(e)}")
                
        return

    def _plot_class_permutation_subplots(self, axes, n_features):
        """Helper method to create class-specific subplots using permutation importance."""
        try:
            from sklearn.inspection import permutation_importance
            
            # For each class, create a subplot
            for class_idx in range(self.n_classes):
                if class_idx < len(axes):
                    ax = axes[class_idx]
                    
                    # Create binary classification target for this class (one-vs-rest)
                    y_train_binary = (self.y_train == class_idx).astype(int)
                    y_test_binary = (self.y_test == class_idx).astype(int)
                    
                    # Calculate permutation importance for both train and test
                    train_importance = permutation_importance(
                        self.model, self.x_train, y_train_binary,
                        n_repeats=5, random_state=42
                    )
                    
                    test_importance = permutation_importance(
                        self.model, self.x_test, y_test_binary,
                        n_repeats=5, random_state=42
                    )
                    
                    # Create DataFrame
                    class_df = pd.DataFrame({
                        'feature': self.x_train.columns,
                        'train_importance': train_importance.importances_mean,
                        'test_importance': test_importance.importances_mean
                    }).sort_values('train_importance', ascending=False).head(n_features)
                    
                    # Melt for easier plotting
                    class_df_melted = pd.melt(
                        class_df, 
                        id_vars=['feature'], 
                        value_vars=['train_importance', 'test_importance'],
                        var_name='dataset', 
                        value_name='importance'
                    )
                    
                    # Plot
                    sns.barplot(
                        x='importance', 
                        y='feature', 
                        hue='dataset', 
                        data=class_df_melted,
                        palette=['#1f77b4', '#ff7f0e'],  # Blue for train, orange for test
                        ax=ax
                    )
                    
                    ax.set_title(f"Class {class_idx} Feature Importance (Permutation)")
                    ax.set_xlabel('Importance Score')
                    
                    # Only show the legend on the first plot to save space
                    if class_idx == 0:
                        ax.legend(title="Dataset")
                    else:
                        ax.get_legend().remove()
        
        except Exception as e:
            logger.warning(f"Could not calculate class-specific permutation importance: {str(e)}")
            
            # Display message on plots
            for class_idx in range(self.n_classes):
                if class_idx < len(axes):
                    ax = axes[class_idx]
                    ax.text(0.5, 0.5, 'Class-specific importance not available',
                           horizontalalignment='center',
                           verticalalignment='center',
                           transform=ax.transAxes)
                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.set_title(f"Class {class_idx}")


    def plot_shap_beeswarm(
        self,
        n_features: int = 20,
        plot_type: str = "beeswarm",
        class_index: int = None,
        dataset: str = "test",
        save_plot: bool = None,
        plot_dir: str = None,
        plot_name: str = "shap_beeswarm",
        plot_save_format: str = None,
        plot_save_dpi: str = None,
        show_plot: bool = None
    ) -> None:
        """
        Create a SHAP beeswarm plot for feature importance.
        """
        # Set defaults if not provided
        save_plot = self.save_plots if save_plot is None else save_plot
        plot_dir = self.plot_dir if plot_dir is None else plot_dir
        plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
        plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi
        show_plot = self.show_plots if show_plot is None else show_plot
        
        # Check if SHAP is available
        try:
            import shap
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("SHAP package not installed. Cannot create SHAP beeswarm plot.")
            return
        
        # Get the appropriate data
        if dataset == "train" or dataset == None:
            X = self.x_train
        if dataset == "test":
            X = self.x_test
        
        # Close any existing figures
        plt.close('all')
        
        try:
            # Create an explainer
            explainer = shap.Explainer(self.model)
            
            # Get SHAP values
            shap_values = explainer(X)
            
            # For multi-class classification - create a global view
            if self.classification and self.n_classes > 2:
                # For multi-class, we need to create a 2D representation for beeswarm
                if hasattr(shap_values, 'values') and len(shap_values.values.shape) == 3:
                    # Create global explanation by taking the mean across the class dimension
                    global_values = shap_values.values.mean(axis=2)
                    global_exp = shap.Explanation(
                        values=global_values,
                        data=X.values,
                        feature_names=X.columns.tolist()
                    )
                    
                    # Create a figure first
                    plt.figure(figsize=(12, 8))
                    
                    # Use the global explanation for plotting
                    if plot_type == "beeswarm":
                        shap.plots.beeswarm(global_exp, max_display=n_features, show=False)
                    else:
                        shap.plots.bar(global_exp, max_display=n_features, show=False)
                    
                    plt.title(f"SHAP Values ({dataset.title()} Data)")
                    
                    # Handle saving
                    if save_plot:
                        os.makedirs(plot_dir, exist_ok=True)
                        save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
                        plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")
                    
                    # Show or close
                    if show_plot:
                        plt.show()
                    else:
                        plt.close()
                    
                    return
                else:
                    # If the SHAP values don't have the expected format
                    logger.warning("Multi-class SHAP values don't have expected format. Unable to create beeswarm plot.")
                    return
            
            # Binary classification or regression - use the original behavior
            # Create a figure first
            plt.figure(figsize=(12, 8))
            
            if plot_type == "bar":
                shap.plots.bar(shap_values, max_display=n_features, show=False)
            else:
                shap.plots.beeswarm(shap_values, max_display=n_features, show=False)
            
            plt.title(f"SHAP Values ({dataset.title()} Data)")
            
            # Handle saving
            if save_plot:
                os.makedirs(plot_dir, exist_ok=True)
                save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
                plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")
            
            # Show or close
            if show_plot:
                plt.show()
            else:
                plt.close()
        
        except Exception as e:
            plt.close('all')  # Close any open figures
            logger.error(f"Error creating SHAP plot: {str(e)}")
            print(f"Error: {str(e)}")


    def plot_score_distribution(
        self,
        bins=None,
        figsize=(12, 8),
        train_label="Train",
        test_label="Test",
        alpha=0.8,
        range_=None,
        show_plot=None,
        save_plot=None, 
        plot_dir=None, 
        plot_name="distribution", 
        plot_save_format=None, 
        plot_save_dpi=None
    ):
        """
        Plot the distribution of predicted values with separate histograms for training and test sets.
        Modified to handle multiclass models properly.
        """
        import matplotlib.pyplot as plt
        import numpy as np
        
        if bins is None:
            bins = self.decile_n
        
        # Create a figure with subplots based on model type
        if self.classification and self.n_classes > 2:
            # For multiclass, create one subplot per class
            n_cols = min(3, self.n_classes)
            n_rows = (self.n_classes + n_cols - 1) // n_cols
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(figsize[0] * n_cols / 2, figsize[1] * n_rows / 2))
            axes = axes.flatten() if n_rows * n_cols > 1 else [axes]
            
            # Get class probability columns
            prob_columns = [str(i) for i in range(self.n_classes)]
            
            # Plot histogram for each class
            for i, col in enumerate(prob_columns):
                if i < len(axes):
                    ax = axes[i]
                    
                    # Get data for this class
                    train_data = self.train_preds[col]
                    test_data = self.test_preds[col]
                    
                    # Determine range if not provided
                    if range_ is None:
                        min_val = min(train_data.min(), test_data.min())
                        max_val = max(train_data.max(), test_data.max())
                        padding = (max_val - min_val) * 0.05
                        local_range = (min_val - padding, max_val + padding)
                    else:
                        local_range = range_
                    
                    # Create bin edges
                    bin_edges = np.linspace(local_range[0], local_range[1], bins + 1)
                    
                    # Plot histograms
                    ax.hist(train_data, bins=bin_edges, alpha=alpha, color='blue', density=True, label=train_label)
                    ax.hist(test_data, bins=bin_edges, alpha=alpha, color='orange', density=True, label=test_label)
                    
                    ax.set_title(f"Class {col} Probability")
                    ax.set_xlabel("Predicted Probability")
                    ax.set_ylabel("Density")
                    ax.legend()
                    ax.grid(False)
            
            # Hide any unused subplots
            for i in range(self.n_classes, len(axes)):
                axes[i].set_visible(False)
                
            # Add a main title
            fig.suptitle(f"Multiclass Probability Distributions (n_classes={self.n_classes})", 
                        fontsize=14, y=1.05)
        else:
            # Binary classification or regression - original implementation
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, sharey=True)
            
            # Get data
            train_data = self.train_preds["predicted"]
            test_data = self.test_preds["predicted"]
            
            # Determine range if not provided
            if range_ is None:
                min_val = min(train_data.min(), test_data.min())
                max_val = max(train_data.max(), test_data.max())
                padding = (max_val - min_val) * 0.05
                range_ = (min_val - padding, max_val + padding)
            
            # Create bin edges
            bin_edges = np.linspace(range_[0], range_[1], bins + 1)
            
            # Left subplot: Train data
            ax1.hist(train_data, bins=bin_edges, alpha=alpha, color='blue', density=True)
            ax1.set_title(f"{train_label} Distribution")
            ax1.set_xlabel("Predicted Probability" if self.classification else "Predicted Value")
            ax1.set_ylabel("Density")
            ax1.grid(False)
            
            # Right subplot: Test data
            ax2.hist(test_data, bins=bin_edges, alpha=alpha, color='orange', density=True)
            ax2.set_title(f"{test_label} Distribution")
            ax2.set_xlabel("Predicted Probability" if self.classification else "Predicted Value")
            ax2.grid(False)
            
            # Add a main title
            fig.suptitle("Predicted Probability Distribution" if self.classification else "Predicted Value Distribution", 
                        fontsize=14, y=1.05)
        
        plt.tight_layout()

        # Use instance defaults if parameters not provided
        show_plot = self.show_plots if show_plot is None else show_plot
        save_plot = self.save_plots if save_plot is None else save_plot
        plot_dir = self.plot_dir if plot_dir is None else plot_dir
        plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
        plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

        if save_plot:
            # Create path using directory and plot name
            os.makedirs(plot_dir, exist_ok=True)
            save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
            plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")

        if show_plot:
            plt.show()
        else:
            plt.close()
 
    def plot_feature_interactions(
        self,
        feature_pairs: List[Tuple[str, str]] = None,
        n_top_pairs: int = 5,
        figsize: Tuple[int, int] = (12, 10),
        plot_type: str = "scatter",  # Changed default to "scatter" as it's more reliable
        cmap: str = "viridis",
        show_plot: bool = None,
        save_plot: bool = None, 
        plot_dir: str = None, 
        plot_name: str = "feature_interactions", 
        plot_save_format: str = None, 
        plot_save_dpi: int = None
    ) -> None:
        """
        Plot feature interactions to visualize how pairs of features jointly affect predictions.
        
        Parameters
        ----------
        feature_pairs : List[Tuple[str, str]], optional
            Specific pairs of features to plot. If None, uses top interacting pairs.
        n_top_pairs : int, default=5
            Number of top interaction pairs to plot if feature_pairs is None.
        figsize : Tuple[int, int], default=(12, 10)
            Figure size.
        plot_type : str, default="scatter"
            Type of interaction plot: "pdp" (partial dependence) or "scatter" (colored scatter plot).
            Note: "shap" type is disabled due to compatibility issues.
        cmap : str, default="viridis"
            Colormap for the plots.
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import seaborn as sns
        
        # Check if SHAP is available for correlation calculation
        try:
            import shap
            shap_available = True
        except ImportError:
            shap_available = False
        
        # If user tries to use SHAP, warn and default to PDP
        if plot_type.lower() == "shap":
            logger.warning("SHAP interaction plots are not supported with this explainer type. Using PDP instead.")
            plot_type = "pdp"  # Fallback
        
        # Define approach based on plot type
        if plot_type.lower() == "pdp":
            # Partial Dependence Plot
            try:
                from sklearn.inspection import PartialDependenceDisplay
                
                # If specific pairs not provided, use top feature importance
                if feature_pairs is None:
                    # Get top features from feature importance
                    if hasattr(self, '_calculate_feature_importance'):
                        feature_importance = self._calculate_feature_importance()
                        if feature_importance is not None:
                            top_features = feature_importance.head(int(np.sqrt(n_top_pairs) + 1))['feature'].tolist()
                        else:
                            # If feature importance not available, use first few features
                            top_features = self.x_train.columns[:int(np.sqrt(n_top_pairs) + 1)].tolist()
                            
                        # Create pairs from top features
                        feature_pairs = []
                        for i in range(len(top_features)):
                            for j in range(i+1, len(top_features)):
                                feature_pairs.append((top_features[i], top_features[j]))
                                if len(feature_pairs) >= n_top_pairs:
                                    break
                            if len(feature_pairs) >= n_top_pairs:
                                break
                    else:
                        # If feature importance not available, use first few features
                        top_features = self.x_train.columns[:int(np.sqrt(n_top_pairs) + 1)].tolist()
                        feature_pairs = []
                        for i in range(len(top_features)):
                            for j in range(i+1, len(top_features)):
                                feature_pairs.append((top_features[i], top_features[j]))
                                if len(feature_pairs) >= n_top_pairs:
                                    break
                            if len(feature_pairs) >= n_top_pairs:
                                break
                
                # Convert feature names to column indices
                feature_indices = []
                for feature1, feature2 in feature_pairs:
                    idx1 = list(self.x_train.columns).index(feature1)
                    idx2 = list(self.x_train.columns).index(feature2)
                    feature_indices.append((idx1, idx2))
                
                # Create PDP interaction plots
                # Calculate grid size based on number of pairs
                n_pairs = len(feature_pairs)
                n_cols = min(2, n_pairs)
                n_rows = (n_pairs + n_cols - 1) // n_cols
                figsize = (figsize[0] * n_cols / 2, figsize[1] * n_rows / 2)
                
                fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
                axes = np.array(axes).reshape(-1) if n_pairs > 1 else np.array([axes])
                
                # Create PDP for each pair
                for i, (pair_idx, pair_name) in enumerate(zip(feature_indices, feature_pairs)):
                    if i < len(axes):
                        # sklearn's PDP expects indices, not feature names
                        PartialDependenceDisplay.from_estimator(
                            self.model,
                            self.x_train,
                            features=[pair_idx],
                            feature_names=[f"{pair_name[0]} vs {pair_name[1]}"],
                            ax=axes[i],
                            kind="both",
                            random_state=42,
                            contour_kw={"cmap": cmap},
                            line_kw={"alpha": 0.5}
                        )
                
                # Hide any unused subplots
                for i in range(n_pairs, len(axes)):
                    axes[i].axis('off')


                plt.tight_layout()

                # Use instance defaults if parameters not provided
                show_plot = self.show_plots if show_plot is None else show_plot
                save_plot = self.save_plots if save_plot is None else save_plot
                plot_dir = self.plot_dir if plot_dir is None else plot_dir
                plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
                plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

                if save_plot:
                    # Create path using directory and plot name
                    os.makedirs(plot_dir, exist_ok=True)
                    save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
                    plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")
                
                if show_plot:
                    plt.show()
                else:
                    plt.close()    
                
            except ImportError:
                logger.warning("sklearn.inspection not available. Cannot create PDP interaction plot.")
                logger.warning("Using scatter plot instead.")
                plot_type = "scatter"  # Fallback
            except Exception as e:
                logger.warning(f"Error creating PDP interaction plot: {str(e)}")
                logger.warning("Falling back to scatter plot.")
                plot_type = "scatter"
        
        if plot_type.lower() == "scatter":
            # Colored scatter plot
            # If specific pairs not provided, use top correlation pairs
            if feature_pairs is None:
                # Calculate correlation matrix
                corr_matrix = self.x_train.corr().abs()
                
                # Set diagonal to 0
                np.fill_diagonal(corr_matrix.values, 0)
                
                # Get indices of top correlated pairs
                top_pairs = []
                for _ in range(n_top_pairs):
                    # Find max correlation
                    i, j = np.unravel_index(corr_matrix.values.argmax(), corr_matrix.shape)
                    feature1, feature2 = corr_matrix.index[i], corr_matrix.columns[j]
                    
                    # Add to list and set to 0 to find next highest
                    top_pairs.append((feature1, feature2))
                    corr_matrix.loc[feature1, feature2] = 0
                    corr_matrix.loc[feature2, feature1] = 0
                
                feature_pairs = top_pairs
            
            # Calculate grid size based on number of pairs
            n_pairs = len(feature_pairs)
            n_cols = min(3, n_pairs)
            n_rows = (n_pairs + n_cols - 1) // n_cols
            figsize = (figsize[0] * n_cols / 3, figsize[1] * n_rows / 2)
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
            axes = np.array(axes).reshape(-1) if n_pairs > 1 else np.array([axes])
            
            # For binary classification or regression, use predicted values as color
            # For multi-class, use the predicted class
            if self.classification:
                if self.n_classes == 2:
                    color_values = self.test_preds['predicted']
                    cbar_label = "Predicted Probability"
                else:
                    color_values = self.test_preds['classification']
                    cbar_label = "Predicted Class"
            else:
                color_values = self.test_preds['predicted']
                cbar_label = "Predicted Value"
            
            # Create scatter plot for each pair
            for i, (feature1, feature2) in enumerate(feature_pairs):
                if i < len(axes):
                    ax = axes[i]
                    
                    # Create scatter plot
                    scatter = ax.scatter(
                        self.x_test[feature1],
                        self.x_test[feature2],
                        c=color_values,
                        cmap=cmap,
                        alpha=0.7,
                        edgecolors='none'
                    )
                    
                    # Add colorbar
                    cbar = plt.colorbar(scatter, ax=ax)
                    cbar.set_label(cbar_label)
                    
                    # Set labels and title
                    ax.set_xlabel(feature1)
                    ax.set_ylabel(feature2)
                    ax.set_title(f"{feature1} vs {feature2}")
                    
                    # Add grid
                    ax.grid(True, alpha=0.3)
            
            # Hide any unused subplots
            for i in range(n_pairs, len(axes)):
                axes[i].axis('off')
            
            plt.tight_layout()


            # Use instance defaults if parameters not provided
            show_plot = self.show_plots if show_plot is None else show_plot
            save_plot = self.save_plots if save_plot is None else save_plot
            plot_dir = self.plot_dir if plot_dir is None else plot_dir
            plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
            plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

            if save_plot:
                # Create path using directory and plot name
                os.makedirs(plot_dir, exist_ok=True)
                save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
                plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")

            if show_plot:
                plt.show()
            else:
                plt.close()

    
    def plot_confusion_matrix(
        self,
        figsize=None,
        title="Confusion Matrix",
        cmap="Blues",
        annot=True,
        fmt="g",
        normalize=False,
        show_train=False,
        show_test=True,
        show_plot: bool = None,
        save_plot: bool = None, 
        plot_dir: str = None, 
        plot_name: str = "confusion_matrix", 
        plot_save_format: str = None, 
        plot_save_dpi: int = None
    ) -> None:
        """
        Plot confusion matrix for classification models.
        """
        if not self.classification:
            logger.warning("Confusion matrix only applicable for classification models.")
            return
        
        # Determine class names
        class_names = list(range(self.n_classes))
        
        # Auto-calculate figsize if not provided
        if figsize is None:
            base_size = max(6, self.n_classes + 2)
            figsize = (base_size, base_size) if show_train and show_test else (base_size, base_size)
        
        # Prepare figure
        if show_train and show_test:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(figsize[0]*2, figsize[1]))
            fig.suptitle(title, fontsize=16)
        else:
            fig, ax = plt.subplots(figsize=figsize)
            plt.title(title)
        
        # Function to plot a single confusion matrix
        def plot_single_cm(ax, y_true, y_pred, title_suffix, local_fmt=fmt, local_annot=annot, 
                           local_cmap=cmap, local_normalize=normalize):
            cm = metrics.confusion_matrix(y_true, y_pred)
            
            # Normalize if requested
            if local_normalize:
                cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
                local_fmt = '.2%'
            
            # Create DataFrame for better visualization
            cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)
            
            # Plot confusion matrix
            sns.heatmap(
                cm_df, 
                annot=local_annot, 
                cmap=local_cmap, 
                fmt=local_fmt,
                xticklabels=class_names,
                yticklabels=class_names,
                ax=ax
            )
            
            # Add labels
            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            ax.set_title(f"{title_suffix}")
            
            # Add accuracy, precision, recall and F1 text
            accuracy = metrics.accuracy_score(y_true, y_pred)
            
            if self.n_classes == 2:
                precision = metrics.precision_score(y_true, y_pred)
                recall = metrics.recall_score(y_true, y_pred)
                f1 = metrics.f1_score(y_true, y_pred)
                stats_text = f"Accuracy: {accuracy:.3f}\nPrecision: {precision:.3f}\nRecall: {recall:.3f}\nF1: {f1:.3f}"
            else:
                # For multi-class, show macro averages
                precision = metrics.precision_score(y_true, y_pred, average='macro')
                recall = metrics.recall_score(y_true, y_pred, average='macro')
                f1 = metrics.f1_score(y_true, y_pred, average='macro')
                stats_text = f"Accuracy: {accuracy:.3f}\nMacro Precision: {precision:.3f}\nMacro Recall: {recall:.3f}\nMacro F1: {f1:.3f}"
            
        
        # Plot train confusion matrix if requested
        if show_train:
            if show_train and show_test:
                plot_single_cm(ax1, self.train_preds["actual"], self.train_preds["classification"], "Training Data")
            else:
                plot_single_cm(ax, self.train_preds["actual"], self.train_preds["classification"], "Training Data")
        
        # Plot test confusion matrix if requested
        if show_test:
            if show_train and show_test:
                plot_single_cm(ax2, self.test_preds["actual"], self.test_preds["classification"], "Testing Data")
            else:
                plot_single_cm(ax, self.test_preds["actual"], self.test_preds["classification"], "Testing Data")
        
        plt.tight_layout()


        # Use instance defaults if parameters not provided
        show_plot = self.show_plots if show_plot is None else show_plot
        save_plot = self.save_plots if save_plot is None else save_plot
        plot_dir = self.plot_dir if plot_dir is None else plot_dir
        plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
        plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

        if save_plot:
            # Create path using directory and plot name
            os.makedirs(plot_dir, exist_ok=True)
            save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
            plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")

        if show_plot:
            plt.show()
        else:
            plt.close()

           
    def plot_lift_analysis(
        self,
        figsize: Tuple[int, int] = (12, 20),
        show_decile_distribution: bool = False,
        show_actual_vs_predicted: bool = False,
        show_lift: bool = True,
        show_cumulative_lift: bool = True,
        show_cumulative_pct: bool = False,
        show_plot: bool = None,
        save_plot: bool = None, 
        plot_dir: str = None, 
        plot_name: str = "lift_analysis", 
        plot_save_format: str = None, 
        plot_save_dpi: int = None
    ):
        """
        Plot a comprehensive lift analysis with multiple visualizations.
        
        Parameters
        ----------
        figsize : Tuple[int, int], default=(12, 20)
            Figure size for the plots.
        show_decile_distribution : bool, default=False
            Whether to show the distribution of deciles.
        show_actual_vs_predicted : bool, default=False
            Whether to show actual vs predicted values by decile.
        show_lift : bool, default=True
            Whether to show lift by decile.
        show_cumulative_lift : bool, default=True
            Whether to show cumulative lift by decile.
        show_cumulative_pct : bool, default=False
            Whether to show cumulative percentage of total outcomes.
        """

        from matplotlib.ticker import FuncFormatter
        import matplotlib.pyplot as plt

        if not self.classification:
            logger.warning("Lift analysis is only applicable for classification models.")
            return
        
        # Set default colors
        colors = plt.cm.tab10.colors
        
        # Get the lift table data
        lift_df = self._calculate_lift()[0]
        if lift_df.empty:
            logger.warning("No lift data available to plot.")
            return
        
        # Determine number of plots to show for main lift analysis
        main_plots = sum([show_decile_distribution, show_actual_vs_predicted, 
                         show_lift, show_cumulative_lift, show_cumulative_pct])
        
        # For multi-class models with show_all_classes, add two more plots for class-specific lift and cumulative lift
        additional_plots = 0
        if self.classification and self.n_classes > 2 and self.show_all_classes and hasattr(self, 'class_lift_table'):
            if show_lift:
                additional_plots += 1
            if show_cumulative_lift:
                additional_plots += 1
        
        # Total number of plots
        total_plots = main_plots + additional_plots
        
        if total_plots == 0:
            logger.warning("No plots selected to display.")
            return
        
        # Set plotting defaults
        show_plot = self.show_plots if show_plot is None else show_plot
        save_plot = self.save_plots if save_plot is None else save_plot
        plot_dir = self.plot_dir if plot_dir is None else plot_dir
        plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
        plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi
        
        # Calculate appropriate figure size
        fig_height = 4 * total_plots  # 4 inches per plot
        main_figsize = (figsize[0], fig_height)
        
        # Create a figure with subplots
        fig, axes = plt.subplots(total_plots, 1, figsize=main_figsize)
        
        # Make axes iterable even if there's only one plot
        if total_plots == 1:
            axes = [axes]
        
        plot_idx = 0
        
        # 1. Decile Distribution
        if show_decile_distribution:
            ax = axes[plot_idx]
            # Get decile counts for train and test
            self.train_preds["decile"].value_counts().sort_index().plot(
                kind='bar', ax=ax, alpha=0.7, color='blue', label='Train'
            )
            self.test_preds["decile"].value_counts().sort_index().plot(
                kind='bar', ax=ax, alpha=0.7, color='orange', label='Test'
            )
            ax.set_xlabel("Decile")
            ax.set_ylabel("Count")
            ax.set_title("Decile Distribution", fontsize=14)
            ax.legend()
            # Explicitly turn off the grid
            ax.grid(False)
            plot_idx += 1
        
        # 2. Actual vs Predicted
        if show_actual_vs_predicted and "accuracy" in lift_df.columns and "predicted_mean" in lift_df.columns:
            ax = axes[plot_idx]
            lift_df["accuracy"].plot(kind="line", marker='o', linewidth=2, markersize=8, ax=ax, color='blue', label='Actual')
            lift_df["predicted_mean"].plot(kind="line", marker='x', linewidth=2, markersize=8, ax=ax, color='orange', label='Predicted')
            ax.set_title("Actual vs Predicted by Decile", fontsize=14)
            ax.set_ylabel("Outcome %")
            ax.set_xlabel("Decile")
            plt.sca(ax)
            plt.xticks(np.arange(1, len(lift_df)+1), [str(int(i)) for i in np.arange(1, len(lift_df)+1)])
            ax.legend()
            # Explicitly turn off the grid
            ax.grid(False)
            plot_idx += 1
        
        # 3. Lift (renamed from "lift" to make it clearer)
        if show_lift and "lift" in lift_df.columns:
            ax = axes[plot_idx]
            lift_df["lift"].plot(kind="line", marker='o', linewidth=2, markersize=8, ax=ax, color='purple')
            # Add a reference line at 100 (no lift)
            ax.axhline(y=100, color='red', linestyle='--')
            ax.set_title("Lift by Decile", fontsize=14)  # Renamed title for clarity
            ax.set_ylabel("Lift")
            ax.set_xlabel("Decile")
            plt.sca(ax)
            plt.xticks(np.arange(1, len(lift_df)+1), [str(int(i)) for i in np.arange(1, len(lift_df)+1)])
            # Explicitly turn off the grid
            ax.grid(False)
            plot_idx += 1
        
        # 4. Cumulative Lift
        if show_cumulative_lift and "cume_lift" in lift_df.columns:
            ax = axes[plot_idx]
            lift_df["cume_lift"].plot(kind="line", marker='o', linewidth=2, markersize=8, ax=ax, color='green')
            # Add a reference line at 100 (no lift)
            ax.axhline(y=100, color='red', linestyle='--')
            ax.set_title("Cumulative Lift by Decile", fontsize=14)  # Renamed title for clarity
            ax.set_ylabel("Cumulative Lift")
            ax.set_xlabel("Decile")
            plt.sca(ax)
            plt.xticks(np.arange(1, len(lift_df)+1), [str(int(i)) for i in np.arange(1, len(lift_df)+1)])
            # Explicitly turn off the grid
            ax.grid(False)
            plot_idx += 1
        
        # 5. Cumulative Percentage
        if show_cumulative_pct and "cume_pct_correct" in lift_df.columns:
            ax = axes[plot_idx]
            lift_df["cume_pct_correct"].plot(kind="line", marker='o', linewidth=2, markersize=8, ax=ax, color='purple')
            ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
            ax.set_title("Cumulative % of Total Outcomes", fontsize=14)
            ax.set_ylabel("% of Total Outcomes")
            ax.set_xlabel("Decile")
            plt.sca(ax)
            plt.xticks(np.arange(1, len(lift_df)+1), [str(int(i)) for i in np.arange(1, len(lift_df)+1)])
            # Explicitly turn off the grid
            ax.grid(False)
            plot_idx += 1
        
        # Add class-specific lift plots for multi-class models with show_all_classes
        if (self.classification and self.n_classes > 2 and self.show_all_classes and
           hasattr(self, 'class_lift_table') and not self.class_lift_table.empty):
            
            # 6. Class-specific Lift
            if show_lift:
                ax = axes[plot_idx]
                ax.set_title("Lift by Class", fontsize=14)
                ax.set_ylabel("Lift")
                ax.set_xlabel("Decile")
                
                # Plot lift for each class on the same plot
                for class_idx in range(self.n_classes):
                    lift_col = f"class_{class_idx}_lift"
                    if lift_col in self.class_lift_table.columns:
                        self.class_lift_table[lift_col].plot(
                            kind="line", marker='o', linewidth=2, markersize=8, 
                            ax=ax, color=colors[class_idx % len(colors)],
                            label=f"Class {class_idx}"
                        )
                
                # Add reference line
                ax.axhline(y=100, color='red', linestyle='--', label="Baseline")
                
                # Set x-ticks
                plt.sca(ax)
                plt.xticks(np.arange(1, len(self.class_lift_table)+1), 
                           [str(int(i)) for i in np.arange(1, len(self.class_lift_table)+1)])
                
                # Add legend
                ax.legend()
                
                # Turn off grid
                ax.grid(False)
                plot_idx += 1
            
            # 7. Class-specific Cumulative Lift
            if show_cumulative_lift:
                ax = axes[plot_idx]
                ax.set_title("Cumulative Lift by Class - Class-Specific Deciles", fontsize=14)
                ax.set_ylabel("Cumulative Lift - Class-Specific Deciles")
                ax.set_xlabel("Decile")
                
                # Plot cumulative lift for each class on the same plot
                for class_idx in range(self.n_classes):
                    cume_lift_col = f"class_{class_idx}_cume_lift"
                    if cume_lift_col in self.class_lift_table.columns:
                        self.class_lift_table[cume_lift_col].plot(
                            kind="line", marker='o', linewidth=2, markersize=8, 
                            ax=ax, color=colors[class_idx % len(colors)],
                            label=f"Class {class_idx}"
                        )
                
                # Add reference line
                ax.axhline(y=100, color='red', linestyle='--', label="Baseline")
                
                # Set x-ticks
                plt.sca(ax)
                plt.xticks(np.arange(1, len(self.class_lift_table)+1), 
                           [str(int(i)) for i in np.arange(1, len(self.class_lift_table)+1)])
                
                # Add legend
                ax.legend()
                
                # Turn off grid
                ax.grid(False)
        
        # Use figure-level spacing adjustment
        plt.subplots_adjust(hspace=0.5)
        
        # Save and show all plots
        if save_plot:
            os.makedirs(plot_dir, exist_ok=True)
            save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
            plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")
        
        if show_plot:
            plt.show()
        else:
            plt.close()

        return


    def plot_performance_curves(
        self,
        figsize: Tuple[int, int] = (16, 8),  # Increased width for longer plots
        title: str = "Model Performance Curves",
        colors: Optional[List[str]] = None,
        show_train: bool = True,
        show_test: bool = True,
        show_plot: bool = None,
        save_plot: bool = None, 
        plot_dir: str = None, 
        plot_name: str = "performance_curves", 
        plot_save_format: str = None, 
        plot_save_dpi: int = None
    ) -> None:
        """
        Plot ROC curves and precision-recall curves side-by-side for both training and test data.
        
        Parameters
        ----------
        figsize : Tuple[int, int], default=(20, 7)
            Figure size for the combined plot. Width increased for better visualization.
        title : str, default="Model Performance Curves"
            Main title for the plot.
        colors : List[str], optional
            Colors for each class. If None, uses default colors.
        show_train : bool, default=True
            Whether to show training data curves.
        show_test : bool, default=True
            Whether to show test data curves.
        """
        if not self.classification:
            logger.warning("Performance curves only applicable for classification models.")
            return
        
        # Create a figure with two subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle(title, fontsize=16)
        
        # Set default colors if not provided
        if colors is None:
            colors = plt.cm.tab10.colors
        
        # ROC Curves (Left subplot)
        if self.n_classes == 2:
            # Binary classification ROC curve
            if show_train:
                fpr_train, tpr_train, _ = metrics.roc_curve(
                    self.train_preds['actual'], self.train_preds['predicted']
                )
                train_auc = metrics.roc_auc_score(
                    self.train_preds['actual'], self.train_preds['predicted']
                )
                ax1.plot(
                    fpr_train, tpr_train, lw=2,
                    label=f"Train ROC (AUC = {train_auc:.3f})",
                    color=colors[0],
                    linestyle='-'
                )
            
            if show_test:
                fpr_test, tpr_test, _ = metrics.roc_curve(
                    self.test_preds['actual'], self.test_preds['predicted']
                )
                test_auc = metrics.roc_auc_score(
                    self.test_preds['actual'], self.test_preds['predicted']
                )
                ax1.plot(
                    fpr_test, tpr_test, lw=2,
                    label=f"Test ROC (AUC = {test_auc:.3f})",
                    color=colors[1],
                    linestyle='--'
                )
            
            # Add diagonal reference line (random classifier) - Make sure it's included in legend
            ax1.plot([0, 1], [0, 1], 'k--', lw=1, label="Random Classifier (AUC = 0.5)")
        else:
            # Multi-class ROC curve
            from sklearn.preprocessing import label_binarize
            
            # Create one-vs-rest binary labels
            y_train_bin = label_binarize(self.train_preds['actual'], classes=range(self.n_classes))
            y_test_bin = label_binarize(self.test_preds['actual'], classes=range(self.n_classes))
            
            for i in range(self.n_classes):
                class_color = colors[i % len(colors)]
                
                if show_train:
                    # Train ROC
                    fpr_train, tpr_train, _ = metrics.roc_curve(
                        y_train_bin[:, i], self.train_preds[str(i)]
                    )
                    train_auc = metrics.roc_auc_score(
                        y_train_bin[:, i], self.train_preds[str(i)]
                    )
                    ax1.plot(
                        fpr_train, tpr_train, lw=2,
                        label=f"Train Class {i} (AUC = {train_auc:.3f})",
                        color=class_color,
                        linestyle='-'
                    )
                
                if show_test:
                    # Test ROC
                    fpr_test, tpr_test, _ = metrics.roc_curve(
                        y_test_bin[:, i], self.test_preds[str(i)]
                    )
                    test_auc = metrics.roc_auc_score(
                        y_test_bin[:, i], self.test_preds[str(i)]
                    )
                    ax1.plot(
                        fpr_test, tpr_test, lw=2,
                        label=f"Test Class {i} (AUC = {test_auc:.3f})",
                        color=class_color,
                        linestyle='--'
                    )
            
            # Add diagonal reference line (random classifier) - Always include in legend
            ax1.plot([0, 1], [0, 1], 'k--', lw=1, label="Random Classifier (AUC = 0.5)")
        
        # Format ROC plot
        ax1.set_xlim([0.0, 1.0])
        ax1.set_ylim([0.0, 1.05])
        ax1.set_xlabel("False Positive Rate", fontsize=12)
        ax1.set_ylabel("True Positive Rate", fontsize=12)
        ax1.set_title("ROC Curves", fontsize=14)
        ax1.legend(loc="lower right")
        ax1.grid(True, alpha=0.3)
        
        # Precision-Recall Curves (Right subplot)
        if self.n_classes == 2:
            # Binary classification
            if show_train:
                precision_train, recall_train, _ = metrics.precision_recall_curve(
                    self.train_preds['actual'], self.train_preds['predicted']
                )
                train_ap = metrics.average_precision_score(
                    self.train_preds['actual'], self.train_preds['predicted']
                )
                ax2.plot(
                    recall_train, precision_train, lw=2,
                    label=f"Train PR (AP = {train_ap:.3f})",
                    color=colors[0],
                    linestyle='-'
                )
            
            if show_test:
                precision_test, recall_test, _ = metrics.precision_recall_curve(
                    self.test_preds['actual'], self.test_preds['predicted']
                )
                test_ap = metrics.average_precision_score(
                    self.test_preds['actual'], self.test_preds['predicted']
                )
                ax2.plot(
                    recall_test, precision_test, lw=2,
                    label=f"Test PR (AP = {test_ap:.3f})",
                    color=colors[1],
                    linestyle='--'
                )
                
            # Add no-skill baseline (prevalence of positive class)
            baseline = np.sum(self.test_preds['actual'] == 1) / len(self.test_preds['actual'])
            ax2.axhline(y=baseline, color='r', linestyle=':', 
                       label=f'No Skill Baseline ({baseline:.3f})')
            
            # Add text annotation explaining the no-skill baseline
            no_skill_text = (
                "No Skill Baseline: A classifier that randomly predicts\n"
                "the positive class with a frequency equal to the class\n"
                "distribution. For PR curves, this is equal to the ratio\n"
                f"of positive samples ({baseline:.3f} or {baseline*100:.1f}%)."
            )
            ax2.text(0.05, 0.05, no_skill_text, transform=ax2.transAxes, 
                    bbox=dict(facecolor='white', alpha=0.8), fontsize=9)
            
        else:
            # Multi-class classification
            for i in range(self.n_classes):
                class_color = colors[i % len(colors)]
                
                if show_train:
                    # Train precision-recall
                    precision_train, recall_train, _ = metrics.precision_recall_curve(
                        y_train_bin[:, i], self.train_preds[str(i)]
                    )
                    train_ap = metrics.average_precision_score(
                        y_train_bin[:, i], self.train_preds[str(i)]
                    )
                    ax2.plot(
                        recall_train, precision_train, lw=2,
                        label=f"Train Class {i} (AP = {train_ap:.3f})",
                        color=class_color,
                        linestyle='-'
                    )
                
                if show_test:
                    # Test precision-recall
                    precision_test, recall_test, _ = metrics.precision_recall_curve(
                        y_test_bin[:, i], self.test_preds[str(i)]
                    )
                    test_ap = metrics.average_precision_score(
                        y_test_bin[:, i], self.test_preds[str(i)]
                    )
                    ax2.plot(
                        recall_test, precision_test, lw=2,
                        label=f"Test Class {i} (AP = {test_ap:.3f})",
                        color=class_color,
                        linestyle='--'
                    )
                
                # Add no-skill baseline for each class
                class_ratio = np.sum(self.test_preds['actual'] == i) / len(self.test_preds['actual'])
                ax2.axhline(y=class_ratio, color=class_color, linestyle=':', alpha=0.5,
                           label=f'No Skill Class {i} ({class_ratio:.3f})')
            
            # Add text explaining multi-class no-skill baselines
            no_skill_text = (
                "No Skill Baselines: For each class, represents the precision\n"
                "achieved by a model that randomly predicts that class with a\n"
                "frequency equal to the class distribution in the dataset."
            )
            ax2.text(0.05, 0.05, no_skill_text, transform=ax2.transAxes,
                    bbox=dict(facecolor='white', alpha=0.8), fontsize=9)
        
        # Format Precision-Recall plot
        ax2.set_xlim([0.0, 1.0])
        ax2.set_ylim([0.0, 1.05])
        ax2.set_xlabel("Recall", fontsize=12)
        ax2.set_ylabel("Precision", fontsize=12)
        ax2.set_title("Precision-Recall Curves", fontsize=14)
        ax2.legend(loc="lower right")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Adjust for suptitle and bottom text


        # Use instance defaults if parameters not provided
        show_plot = self.show_plots if show_plot is None else show_plot
        save_plot = self.save_plots if save_plot is None else save_plot
        plot_dir = self.plot_dir if plot_dir is None else plot_dir
        plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
        plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

        if save_plot:
            # Create path using directory and plot name
            os.makedirs(plot_dir, exist_ok=True)
            save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
            plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")

        if show_plot:
            plt.show()
        else:
            plt.close()

        
    def plot_learning_history(
        self,
        history: Dict[str, List[float]] = None,
        figsize: Tuple[int, int] = (12, 6),
        metrics: List[str] = None,
        start_epoch: int = 0,
        smooth_factor: float = 0,
        include_lr: bool = False,
        show_plot: bool = None,
        save_plot: bool = None, 
        plot_dir: str = None, 
        plot_name: str = "learning_history", 
        plot_save_format: str = None, 
        plot_save_dpi: int = None
    ) -> None:
        """
        Plot learning history from iterative models like neural networks.
        
        This function visualizes training metrics over epochs from models that track
        training history (like Keras, LightGBM, or XGBoost with callbacks).
        
        Parameters
        ----------
        history : Dict[str, List[float]], optional
            Training history dictionary. If None, tries to extract from model.
        figsize : Tuple[int, int], default=(12, 6)
            Figure size.
        metrics : List[str], optional
            List of metrics to plot. If None, plots all available metrics.
        start_epoch : int, default=0
            Starting epoch for plotting (to skip initial volatile values).
        smooth_factor : float, default=0
            Exponential moving average factor for smoothing (0 = no smoothing, 0.9 = high smoothing).
        include_lr : bool, default=False
            Whether to include learning rate plot if available.
        """
        import matplotlib.pyplot as plt
        import numpy as np
        import re
        
        # Try to extract history from model if not provided
        if history is None:
            # Try common attributes/methods for various libraries
            if hasattr(self.model, 'history') and hasattr(self.model.history, 'history'):
                # Keras model
                history = self.model.history.history
            elif hasattr(self.model, 'evals_result'):
                # XGBoost model
                history = self._format_xgboost_history(self.model.evals_result())
            elif hasattr(self.model, 'best_score'):
                # LightGBM model
                if hasattr(self.model, '_Booster') and hasattr(self.model._Booster, 'eval_valid'):
                    history = self._format_lightgbm_history(self.model._Booster.eval_valid)
            else:
                logger.warning("Could not extract training history from model.")
                return
        
        if not history:
            logger.warning("No training history available.")
            return
        
        # Function to apply smoothing
        def smooth_curve(points, factor=0.9):
            smoothed_points = []
            for point in points:
                if smoothed_points:
                    previous = smoothed_points[-1]
                    smoothed_points.append(previous * factor + point * (1 - factor))
                else:
                    smoothed_points.append(point)
            return smoothed_points
        
        # Extract metrics from history
        available_metrics = []
        for key in history.keys():
            # Skip learning rate if not requested
            if 'lr' in key.lower() and not include_lr:
                continue
            available_metrics.append(key)
        
        # Filter metrics if specified
        if metrics is not None:
            metrics_to_plot = [m for m in metrics if m in available_metrics]
            if len(metrics_to_plot) == 0:
                logger.warning(f"None of the specified metrics {metrics} found in history. Available metrics: {available_metrics}")
                metrics_to_plot = available_metrics
        else:
            metrics_to_plot = available_metrics
        
        # Group related metrics (training and validation)
        metric_groups = {}
        for metric in metrics_to_plot:
            # Strip val_ prefix if present
            base_metric = re.sub(r'^(val_|validation_|train_|training_)', '', metric)
            if base_metric not in metric_groups:
                metric_groups[base_metric] = []
            metric_groups[base_metric].append(metric)
        
        # Determine subplot layout
        n_metrics = len(metric_groups)
        n_cols = min(3, n_metrics)
        n_rows = (n_metrics + n_cols - 1) // n_cols
        
        # Create figure and axes
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        
        # Add a main title to the figure
        fig.suptitle('Training History by Metric', fontsize=16, y=1.02)
        
        # Ensure axes is always a 2D array for consistent indexing
        if n_metrics == 1:
            axes = np.array([[axes]])
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        # Create plots
        metric_index = 0
        for base_metric, metrics_list in metric_groups.items():
            if metric_index >= n_rows * n_cols:
                break
                
            row, col = metric_index // n_cols, metric_index % n_cols
            ax = axes[row, col]
            
            # Plot each variant of this metric (train/val)
            for metric in metrics_list:
                values = history[metric][start_epoch:]
                epochs = range(start_epoch + 1, start_epoch + len(values) + 1)
                
                if smooth_factor > 0:
                    values = smooth_curve(values, smooth_factor)
                
                # Determine if this is training or validation
                if metric.startswith(('val_', 'validation_')):
                    label = 'Validation'
                    color = 'orange'
                elif metric.startswith(('train_', 'training_')):
                    label = 'Training'
                    color = 'blue'
                elif 'lr' in metric.lower():
                    label = 'Learning Rate'
                    color = 'green'
                else:
                    label = 'Training'  # Default assumption
                    color = 'blue'
                
                # Plot the metric
                ax.plot(epochs, values, label=f'{label}', color=color)
            
            # Format title and axis labels 
            # More descriptive titles that clearly identify the metric
            metric_name = base_metric.replace('_', ' ').title()
            if 'Lr' in metric_name:
                metric_name = metric_name.replace('Lr', 'Learning Rate')
            
            # Add metric type to title
            metric_type = self._identify_metric_type(base_metric)
            if metric_type:
                title = f"Metric: {metric_name} ({metric_type})"
            else:
                title = f"Metric: {metric_name}"
            
            ax.set_title(title)
            ax.set_xlabel('Epochs/Iterations')
            
            # More descriptive y-label based on the metric type
            if 'loss' in base_metric.lower() or 'error' in base_metric.lower():
                ax.set_ylabel('Loss Value (lower is better)')
            elif 'accuracy' in base_metric.lower() or 'auc' in base_metric.lower() or 'f1' in base_metric.lower():
                ax.set_ylabel('Score (higher is better)')
            elif 'lr' in base_metric.lower():
                ax.set_ylabel('Learning Rate')
            else:
                ax.set_ylabel('Value')
            
            # Add legend if there are multiple variants
            if len(metrics_list) > 1:
                ax.legend()
            
            # Add grid
            ax.grid(True, alpha=0.3)
            
            metric_index += 1
        
        # Hide any unused subplots
        for i in range(n_metrics, n_rows * n_cols):
            row, col = i // n_cols, i % n_cols
            axes[row, col].axis('off')
        
        plt.tight_layout()

        # Use instance defaults if parameters not provided
        show_plot = self.show_plots if show_plot is None else show_plot
        save_plot = self.save_plots if save_plot is None else save_plot
        plot_dir = self.plot_dir if plot_dir is None else plot_dir
        plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
        plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi

        if save_plot:
            # Create path using directory and plot name
            os.makedirs(plot_dir, exist_ok=True)
            save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
            plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")

        if show_plot:
            plt.show()
        else:
            plt.close()

    def plot_performance_comparison(self, figsize=(12, 8), save_plot=None, plot_dir=None, 
                                   plot_name="performance_comparison", plot_save_format=None, 
                                   plot_save_dpi=None, show_plot=None):
        """Plot performance metrics comparison between test and OOT datasets."""
        if not self.has_oot:
            logger.warning("No out-of-time data available for comparison.")
            return
            
        # Set defaults
        save_plot = self.save_plots if save_plot is None else save_plot
        plot_dir = self.plot_dir if plot_dir is None else plot_dir
        plot_save_format = self.plot_save_format if plot_save_format is None else plot_save_format
        plot_save_dpi = self.plot_save_dpi if plot_save_dpi is None else plot_save_dpi
        show_plot = self.show_plots if show_plot is None else show_plot

        # Calculate metrics directly for each dataset
        test_metrics = []
        oot_metrics = []
        
        if self.classification and self.n_classes == 2:
            # Binary classification metrics
            test_metrics.extend([
                ("AUC", metrics.roc_auc_score(self.test_preds["actual"], self.test_preds["predicted"])),
                ("Accuracy", metrics.accuracy_score(self.test_preds["actual"], self.test_preds["classification"])),
                ("Precision", metrics.precision_score(self.test_preds["actual"], self.test_preds["classification"])),
                ("Recall", metrics.recall_score(self.test_preds["actual"], self.test_preds["classification"])),
                ("F1", metrics.f1_score(self.test_preds["actual"], self.test_preds["classification"])),
                ("LogLoss", metrics.log_loss(self.test_preds["actual"], self.test_preds["predicted"]))
            ])
            
            oot_metrics.extend([
                ("AUC", metrics.roc_auc_score(self.oot_preds["actual"], self.oot_preds["predicted"])),
                ("Accuracy", metrics.accuracy_score(self.oot_preds["actual"], self.oot_preds["classification"])),
                ("Precision", metrics.precision_score(self.oot_preds["actual"], self.oot_preds["classification"])),
                ("Recall", metrics.recall_score(self.oot_preds["actual"], self.oot_preds["classification"])),
                ("F1", metrics.f1_score(self.oot_preds["actual"], self.oot_preds["classification"])),
                ("LogLoss", metrics.log_loss(self.oot_preds["actual"], self.oot_preds["predicted"]))
            ])
        elif self.classification:
            # Multi-class metrics
            test_metrics.extend([
                ("Accuracy", metrics.accuracy_score(self.test_preds["actual"], self.test_preds["classification"])),
                ("Weighted F1", metrics.f1_score(self.test_preds["actual"], self.test_preds["classification"], average='weighted')),
                ("MLogLoss", metrics.log_loss(self.test_preds["actual"], self.test_preds.drop(columns=['actual', 'classification'])))
            ])
            
            oot_metrics.extend([
                ("Accuracy", metrics.accuracy_score(self.oot_preds["actual"], self.oot_preds["classification"])),
                ("Weighted F1", metrics.f1_score(self.oot_preds["actual"], self.oot_preds["classification"], average='weighted')),
                ("MLogLoss", metrics.log_loss(self.oot_preds["actual"], self.oot_preds.drop(columns=['actual', 'classification'])))
            ])
        else:
            # Regression metrics
            test_metrics.extend([
                ("R2", metrics.r2_score(self.test_preds["actual"], self.test_preds["predicted"])),
                ("RMSE", metrics.mean_squared_error(self.test_preds["actual"], self.test_preds["predicted"], squared=False)),
                ("MAE", metrics.mean_absolute_error(self.test_preds["actual"], self.test_preds["predicted"]))
            ])
            
            oot_metrics.extend([
                ("R2", metrics.r2_score(self.oot_preds["actual"], self.oot_preds["predicted"])),
                ("RMSE", metrics.mean_squared_error(self.oot_preds["actual"], self.oot_preds["predicted"], squared=False)),
                ("MAE", metrics.mean_absolute_error(self.oot_preds["actual"], self.oot_preds["predicted"]))
            ])
        
        # Create DataFrames from metrics
        test_df = pd.DataFrame(test_metrics, columns=["metric", "value"]).set_index("metric")
        oot_df = pd.DataFrame(oot_metrics, columns=["metric", "value"]).set_index("metric")
        
        # Combine into comparison DataFrame
        comparison = pd.DataFrame({
            'Test': test_df["value"],
            'OOT': oot_df["value"]
        })
        
        # Calculate percentage change
        comparison['change_pct'] = (comparison['OOT'] - comparison['Test']) / comparison['Test']
        
        # Create visualization
        plt.figure(figsize=figsize)
        
        # Create bar chart
        comparison[['Test', 'OOT']].plot(kind='bar', ax=plt.gca())
        plt.title('Model Performance: Test vs Out-of-Time', fontsize=14)
        plt.ylabel('Metric Value')
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        
        for i, metric in enumerate(comparison.index):
            change = comparison.loc[metric, 'change_pct']
            color = 'red' if change < 0 else 'green'
            plt.annotate(f"{change:.1%}", 
                        xy=(i, max(comparison.loc[metric, ['Test', 'OOT']])), 
                        ha='center', va='bottom',
                        color=color, fontweight='bold')
        
        # Save if requested
        if save_plot:
            import os
            os.makedirs(plot_dir, exist_ok=True)
            save_path = os.path.join(plot_dir, f"{plot_name}.{plot_save_format}")
            plt.savefig(save_path, format=plot_save_format, dpi=plot_save_dpi, bbox_inches="tight")
        
        # Show or close
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def _identify_metric_type(self, metric_name):
        """
        Identify the type of metric to provide more context in plot titles.
        """
        metric_lower = metric_name.lower()
        
        if 'loss' in metric_lower:
            return 'Loss Metric'
        elif 'accuracy' in metric_lower or 'acc' == metric_lower:
            return 'Accuracy Metric'
        elif 'auc' in metric_lower:
            return 'Area Under Curve'
        elif 'f1' in metric_lower:
            return 'F1 Score'
        elif 'precision' in metric_lower:
            return 'Precision Metric'
        elif 'recall' in metric_lower:
            return 'Recall Metric'
        elif 'error' in metric_lower:
            return 'Error Metric'
        elif 'lr' in metric_lower:
            return 'Learning Rate'
        
        return None

    #--------------------------------------------------------------------------
    # Utility Functions
    #--------------------------------------------------------------------------
    

    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """
        Check if all optional dependencies are available.
        
        Returns
        -------
        Dict[str, bool]
            Dictionary of dependency name to availability.
        """
        dependencies = {
            'pandas': True,  # Required
            'numpy': True,   # Required
            'sklearn': True, # Required
            'matplotlib': importlib.util.find_spec("matplotlib") is not None,
            'seaborn': importlib.util.find_spec("seaborn") is not None,
            'shap': importlib.util.find_spec("shap") is not None,
        }
        
        return dependencies

    def _format_xgboost_history(self, evals_result):
        """
        Format XGBoost evals_result() output into a consistent history dictionary.
        """
        history = {}
        for data_name, metrics in evals_result.items():
            for metric_name, values in metrics.items():
                key = f"{data_name}_{metric_name}"
                history[key] = values
        return history


    def _format_lightgbm_history(self, eval_results):
        """
        Format LightGBM evaluation history into a consistent dictionary.
        """
        history = {}
        if not eval_results:
            return history
            
        # LightGBM history is a list of tuples: (iteration, metric_name, value, is_higher_better)
        for data_name, metric_values in eval_results.items():
            for metric_name, values in metric_values.items():
                key = f"{data_name}_{metric_name}"
                history[key] = values
        return history

    def _safe_division(self, numerator, denominator, default=0.0):
        """
        Safely divide two numbers, returning default if denominator is zero.
        
        Parameters
        ----------
        numerator : number
            Numerator for division.
        denominator : number
            Denominator for division.
        default : number, default=0.0
            Default value to return if denominator is zero.
            
        Returns
        -------
        number
            Result of division or default.
        """
        return numerator / denominator if denominator != 0 else default
    
    def _handle_missing_shap(self) -> pd.DataFrame:
        """
        Handle case where SHAP is not available.
        
        Returns
        -------
        pd.DataFrame
            DataFrame with feature importance based on model coefficients or other methods.
        """
        importance = None
        
        try:
            # Try to get feature importance from model attributes
            if hasattr(self.model, 'feature_importances_'):
                importance = pd.DataFrame({
                    'feature': self.x_train.columns,
                    'importance': self.model.feature_importances_
                })
            elif hasattr(self.model, 'coef_'):
                coef = self.model.coef_
                if coef.ndim > 1:
                    coef = np.abs(coef).mean(axis=0)
                importance = pd.DataFrame({
                    'feature': self.x_train.columns,
                    'importance': np.abs(coef)
                })
            
            if importance is not None:
                return importance.sort_values('importance', ascending=False)
            
            logger.warning("Could not determine feature importance without SHAP.")
            return pd.DataFrame(columns=['feature', 'importance'])
            
        except Exception as e:
            logger.error(f"Error calculating feature importance: {str(e)}")
            return pd.DataFrame(columns=['feature', 'importance'])
    

