# logging
LOGGING_LEVEL = "INFO"  # logging level

# common
BLOCKS_BATCH_SIZE = 10000  # number of blocks from which to fetch historical events in a single batch
SPOT_BATCH_SIZE = 10000  # number of historical spot values to fetch in a single batch
SEED_SHIFT = 1000000000  # seed shift to instantiate random generators of a simulation

# uniswap constants
UNISWAPV3_RANDOM_AGENT_TICK_SPACING = 1000  # tick spacing used to generate Uniswap V3 random agent mints
MAX_SLIPPAGE: float | None = None
ADJUST_MINT_AMOUNTS = True
BUFFER_BLOCK_SAMPLING = 25
BUFFER_LAMBDA_COEF = 0.94

# arbitrage
PROFIT_MULTIPLICATOR = 1  # multiplicator for the uniswapv3 arbitrageur threshold

# observer
DEFAULT_N_METRIC_OBSERVATIONS = (
    100  # if constant.block_step_metrics is not set, this is the default number of observations
)
CAP_FEES_TO_LVR = 10000.0  # highest value displayed for total_fees_relative_to_lvr metric

# strategies
BENCHMARK_AGENT_NAME = "benchmark"  # name to append to agent's name when creating benchmark agents for that agent
OVERFLOW = 2**256 - 1

AVERAGE_NB_OF_BLOCKS_PER_YEAR = 365 * 24 * 60 * 60 / 12  # average number of blocks per year
