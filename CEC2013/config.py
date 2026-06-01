
POP_SIZE = 50
MAX_FES = 250_000
# Upper-bound estimate of generation count. Actual generations may be fewer
# if the FES budget is exhausted mid-generation.
MAX_GENERATIONS = MAX_FES // POP_SIZE
RUNS = 30

LOWER_BOUND = -100
UPPER_BOUND = 100

# --- Raw Population Data Export Config ---
EXPORT_RAW_DATA = True          # Enable/disable raw population data export at each iteration
RAW_DATA_FORMAT = 'csv'         # Export format: 'csv', 'excel', or 'both'
RAW_DATA_SAMPLE_INTERVAL = 1    # Snapshot every N generations (1 = every generation)
