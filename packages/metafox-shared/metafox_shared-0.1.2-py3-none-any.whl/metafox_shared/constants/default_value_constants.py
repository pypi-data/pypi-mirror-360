from metafox_shared.config import Config

_ORIGINAL_DEFAULTS: dict = {
    "generations": None,
    "population_size": 100,
    "offspring_size": None,
    "mutation_rate": 0.9,
    "crossover_rate": 0.1,
    "scoring": None,
    "cv": 5,
    "subsample": 1.0,
    "max_time_mins": 10,
    "max_eval_time_mins": 5,
    "random_state": None,
    "config_dict": None,
    "template": None,
    "early_stop": None,
    "scoring_classification": "accuracy",
    "scoring_regression": "neg_mean_squared_error"
}

# Dynamically create constants by fetching from Config or using original defaults
# The section 'tpot_job' corresponds to a top-level key in your custom_defaults.yml
DEFAULT_GENERATIONS = Config.get_custom_default("tpot_job", "generations", _ORIGINAL_DEFAULTS["generations"])
DEFAULT_POPULATION_SIZE = Config.get_custom_default("tpot_job", "population_size", _ORIGINAL_DEFAULTS["population_size"])
DEFAULT_OFFSPRING_SIZE = Config.get_custom_default("tpot_job", "offspring_size", _ORIGINAL_DEFAULTS["offspring_size"])
DEFAULT_MUTATION_RATE = Config.get_custom_default("tpot_job", "mutation_rate", _ORIGINAL_DEFAULTS["mutation_rate"])
DEFAULT_CROSSOVER_RATE = Config.get_custom_default("tpot_job", "crossover_rate", _ORIGINAL_DEFAULTS["crossover_rate"])
DEFAULT_SCORING = Config.get_custom_default("tpot_job", "scoring", _ORIGINAL_DEFAULTS["scoring"])
DEFAULT_CV = Config.get_custom_default("tpot_job", "cv", _ORIGINAL_DEFAULTS["cv"])
DEFAULT_SUBSAMPLE = Config.get_custom_default("tpot_job", "subsample", _ORIGINAL_DEFAULTS["subsample"])
DEFAULT_MAX_TIME_MINS = Config.get_custom_default("tpot_job", "max_time_mins", _ORIGINAL_DEFAULTS["max_time_mins"])
DEFAULT_MAX_EVAL_TIME_MINS = Config.get_custom_default("tpot_job", "max_eval_time_mins", _ORIGINAL_DEFAULTS["max_eval_time_mins"])
DEFAULT_RANDOM_STATE = Config.get_custom_default("tpot_job", "random_state", _ORIGINAL_DEFAULTS["random_state"])
DEFAULT_CONFIG_DICT = Config.get_custom_default("tpot_job", "config_dict", _ORIGINAL_DEFAULTS["config_dict"])
DEFAULT_TEMPLATE = Config.get_custom_default("tpot_job", "template", _ORIGINAL_DEFAULTS["template"])
DEFAULT_EARLY_STOP = Config.get_custom_default("tpot_job", "early_stop", _ORIGINAL_DEFAULTS["early_stop"])
DEFAULT_SCORING_CLASSIFICATION = Config.get_custom_default("tpot_job", "scoring_classification", _ORIGINAL_DEFAULTS["scoring_classification"])
DEFAULT_SCORING_REGRESSION = Config.get_custom_default("tpot_job", "scoring_regression", _ORIGINAL_DEFAULTS["scoring_regression"])