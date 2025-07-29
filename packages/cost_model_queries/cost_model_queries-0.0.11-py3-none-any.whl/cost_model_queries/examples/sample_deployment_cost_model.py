import pandas as pd

from cost_model_queries.sampling.sampling_functions import (
    problem_spec,
    convert_factor_types,
    sample_deployment_cost,
)

# Filename for saved samples
samples_save_fn = "deployment_cost_samples_cape_ferg_ship.csv"

# Path to cost model
#file_name = "\\Cost Models\\3.5.3 CA Deployment Model.xlsx"
wb_file_path = "C:\\Users\\rcrocker\\Documents\\Github\\cost-eco-model-linker\\src\\cost_models\\3.5.5 CA Deployment Model.xlsx"
#os.path.abspath(os.getcwd()) + file_name

# Generate sample
N = 2**2

# Generate problem spec, factor names and list of categorical factors to create factor sample
sp, factor_specs = problem_spec("deployment", config_filepath="config.csv")
# Sample factors using sobal sampling
sp.sample_sobol(N, calc_second_order=True)

factors_df = pd.DataFrame(data=sp.samples, columns=factor_specs.factor_names)

# Convert categorical factors to categories
factors_df = convert_factor_types(factors_df, factor_specs.is_cat)

# Sample cost using factors sampled
factors_df = sample_deployment_cost(wb_file_path, factors_df, factor_specs, N)
breakpoint()
factors_df["setup_cost_per_km"] = factors_df["setupCost"]/(factors_df["distance_from_port"]*1.852)
factors_df["setup_cost_per_km_per_device"] = factors_df["setup_cost_per_km"]/factors_df["num_devices"]
factors_df.to_csv(samples_save_fn, index=False)  # Save to CSV


exp_ship_df = pd.read_csv("deployment_cost_samples_cape_ferg_ship.csv")
default_ship_df = pd.read_csv("deployment_cost_samples_default_ship.csv")
