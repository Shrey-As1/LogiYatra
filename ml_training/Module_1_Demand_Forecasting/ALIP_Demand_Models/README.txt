
============================================================
ALIP — MODULE 1
RESEARCH-GRADE DEMAND FORECASTING
============================================================

DATASET
-------
Walmart Recruiting - Store Sales Forecasting


MODELS
------
1. Lag-1 Naive Baseline
2. Seasonal Lag-12 Baseline
3. Tuned XGBoost
4. Multivariate LSTM
   - Store Embeddings
   - Department Embeddings
5. Hybrid XGBoost + LSTM


DATA SPLIT
----------
Chronological split

Train:
70%

Validation:
15%

Test:
15%


LSTM
----
Window:
12 weeks

Store embedding:
8 dimensions

Department embedding:
16 dimensions


HYBRID
------
XGBoost weight:
1.00

LSTM weight:
0.00

Weight selected using:
Validation RMSE


IMPORTANT RESEARCH PRINCIPLE
----------------------------
The test set is not used for model selection.

Validation is used for:
- XGBoost configuration
- LSTM architecture
- LSTM epoch selection
- Hybrid ensemble weight

After selection, models are retrained on
Train + Validation.

The final performance is reported on
the untouched Test set.


MAIN MODEL FILES
----------------
demand_xgb.json

demand_lstm.keras

demand_lstm_preprocessing.pkl


CONFIGURATION
-------------
xgb_features.json
lstm_config.json
hybrid_config.json
demand_model_metrics.json


RESEARCH OUTPUTS
----------------
model_comparison.csv
demand_predictions.csv
xgb_feature_importance.csv
xgboost_hyperparameter_search.csv
lstm_architecture_search.csv
hybrid_weight_search.csv


PLOTS
-----
plots/actual_vs_hybrid.png
plots/forecast_model_comparison.png
plots/rmse_comparison.png
plots/hybrid_weight_optimization.png
plots/hybrid_residual_distribution.png
plots/xgboost_feature_importance.png


BEST TEST MODEL
---------------
XGBoost


BEST TEST RMSE
--------------
2611.7979


============================================================
