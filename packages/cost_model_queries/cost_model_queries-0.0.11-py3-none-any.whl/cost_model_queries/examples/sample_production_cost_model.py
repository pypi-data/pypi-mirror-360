import pandas as pd

from cost_model_queries.sampling.sampling_functions import (
    problem_spec,
    convert_factor_types,
    sample_production_cost,
)

# Filename for saved samples
samples_save_fn = "production_cost_samples.csv"

# Path to cost model
wb_file_path = "C:\\Users\\rcrocker\\Documents\\Github\\Cost Models\\3.7.0 CA Production Model.xlsx"

# Generate sample
N = 2**2

# Generate problem spec, factor names and list of categorical factors to create factor sample
sp, factor_specs = problem_spec("production", config_filepath="./examples/config.csv")
# Sample factors using sobal sampling
sp.sample_sobol(N, calc_second_order=True)

factors_df = pd.DataFrame(data=sp.samples, columns=factor_specs.factor_names)

# Convert categorical factors to categories
factors_df = convert_factor_types(factors_df, factor_specs.is_cat)

# Sample cost using factors sampled
factors_df = sample_production_cost(wb_file_path, factors_df, factor_specs, N)
breakpoint()
factors_df.to_csv(samples_save_fn, index=False)  # Save to CSV
