TPOT = "tpot"
VERBOSITY_TPOT = 2
USE_DASK_TPOT = False
MEMORY_TPOT = None
WARM_START_TPOT = False
N_JOBS_TPOT = -1

OBSERVER_LOGS_SLEEP = 10 # How many seconds to wait before checking the logs again
AVAILABLE_CONFIG_DICTS = [None, 'TPOT light', 'TPOT MDR', 'TPOT sparse']
AVAILABLE_CLASSIFICATION_METRICS = [
    'accuracy', 'adjusted_rand_score', 'average_precision', 'balanced_accuracy',
    'f1', 'f1_macro', 'f1_micro', 'f1_samples', 'f1_weighted', 'neg_log_loss',
    'precision', 'precision_macro', 'precision_micro', 'precision_samples',
    'precision_weighted', 'recall', 'recall_macro', 'recall_micro', 'recall_samples',
    'recall_weighted', 'jaccard', 'jaccard_macro', 'jaccard_micro', 'jaccard_samples',
    'jaccard_weighted', 'roc_auc', 'roc_auc_ovr', 'roc_auc_ovo', 'roc_auc_ovr_weighted',
    'roc_auc_ovo_weighted'
]
AVAILABLE_REGRESSION_METRICS = [
    'neg_median_absolute_error', 'neg_mean_absolute_error', 'neg_mean_squared_error', 'r2'
]