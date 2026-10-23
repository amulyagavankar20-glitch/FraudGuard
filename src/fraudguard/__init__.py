"""FraudGuard: real-time fraud scoring on a Bayesian Network.

Handles missing data natively (unobserved nodes + explicit missingness
indicators, parameters fitted with EM) and returns calibrated, explainable
scores. Benchmarked honestly against Naive Bayes and LightGBM baselines.
"""

__version__ = "0.1.0"
