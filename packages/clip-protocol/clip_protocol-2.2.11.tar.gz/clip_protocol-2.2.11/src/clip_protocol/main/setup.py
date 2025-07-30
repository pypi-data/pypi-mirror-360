import optuna
import pandas as pd
import numpy as np
import os
import sys
from tabulate import tabulate
import argparse
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from clip_protocol.utils.utils import save_setup_json, get_real_frequency, display_results
from clip_protocol.utils.errors import compute_error_table, display_error_table

from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client
class Setup:
    def __init__(self, df):
        self.df = df
        self.e_ref = 20
        self.n_trials = 30
        self.failure_prob = 0.001
        self.events_names, self.privacy_method, self.error_metric, self.error_value, self.tolerance = self.ask_values()
        self.found_best_values = False
        self.N = len(self.df)
        self.matching_trial = None

    def ask_values(self):
        """
        Prompt the user to input configuration parameters.
        Returns:
            tuple: Contains events_names (list), privacy_method (str), 
                   error_metric (str), error (float), tolerance (float)
        """
        print("Please enter the values for the parameters:")
        print(", ".join(f"'{col}'" for col in self.df.columns))
        print("\n")
        events_inputs = input("🔹 Event columns names (comma-separated): ")
        events_names = [e.strip() for e in events_inputs.split(",") if e.strip()]

        privacy_options = {"1": "PCMeS", "2": "PHCMS"}
        privacy_method = self._ask_option("🔹 Privacy method", privacy_options)
        
        error_metric_options = { "1": "MAE", "2": "MSE", "3": "RMSE",  "4": "Lρ Norm"}
        error_metric = self._ask_option("🔹 Error metric", error_metric_options)
        if error_metric == "Lρ Norm":
            self.p = float(input("🔹 ρ value: "))
        else:
            self.p = 1.5
        
        error_value = float(input("🔹 Error value: "))
        tolerance = float(input("🔹 Tolerance: "))
        default_parameters = input("🔹 Do you want to change the default parameters (y/n): ")
        if default_parameters.lower() == "y":
            self.e_ref = float(input("🔹 Epsilon reference value: "))
            self.n_trials = int(input("🔹 Number of trials: "))
            self.failure_prob = float(input("🔹 Failure probability value: "))


        return events_names, privacy_method, error_metric, error_value, tolerance
    
    def _ask_option(self, prompt, options):
        print(f"{prompt}:\n" + "\n".join([f"\t {k}. {v}" for k, v in options.items()]))
        choice = input(f"\t Enter option ({'/'.join(options)}): ").strip()
        while choice not in options:
            choice = input("Invalid option. Try again: ").strip()
        return options[choice]
    
    def filter_dataframe(self):
        matching_columns = [col for col in self.events_names if col in self.df.columns]
        if not matching_columns:
            print("⚠️ None of the specified event names match the DataFrame columns.")
        
        self.df = self.df[matching_columns].copy()
        self.df.columns = ["user", "value"]

        self.df['value'] = self.df['value'].astype(str).apply(lambda x: x.strip())
        self.df = self.df[self.df['value'] != '-']
        self.df = self.df[self.df['value'].str.contains(r'\w', na=False)]
        self.N = len(self.df)
    
    def run_command(self, e, k, m):
        if self.privacy_method == "PCMeS":
            _, _, df_estimated = run_private_cms_client(k, m, e, self.df)
        elif self.privacy_method == "PHCMS":
            _, _, df_estimated = run_private_hcms_client(k, m, e, self.df)
    
        error_table = compute_error_table(self.real_freq, df_estimated, self.p)
        return error_table, df_estimated
    
    def optimize_k_m(self):
       
        def objective(trial):
            # Choose the event with less frequency
            self.real_freq = get_real_frequency(self.df)
            min_freq_value = self.real_freq['Frequency'].min()
            
            # Calculate the value of the range of m
            sobreestimation = float(min_freq_value * self.error_value) / self.N
            m_range = 2.718/sobreestimation

            if self.privacy_method == "PHCMS":
                k_range = 1/self.failure_prob
                k = trial.suggest_int("k", 100, k_range)
                exp_max = int(math.floor(math.log2(m_range)))
                m = 2 ** exp_max
                print(f"m must be a power of 2, so m = {m}")

            else:
                k = trial.suggest_int("k", 10, 1000)
                m = trial.suggest_int("m", m_range/2, m_range)

            trial.set_user_attr('k', k)
            trial.set_user_attr('m', m)
                     
            error_table, _ = self.run_command(self.e_ref, k, m)  
            error = float([v for k, v in error_table if k == self.error_metric][0])

            print(f"Error: {error}, Error value: {self.error_value * min_freq_value}")
            if error <= (self.error_value * min_freq_value):
                self.found_best_values = True
                self.matching_trial = trial
                trial.study.stop()
            
            return m
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.n_trials)

        if self.matching_trial is not None:
            trial = self.matching_trial
        else:
            trial = study.best_trial
        
        return trial.user_attrs["k"], trial.user_attrs["m"]
    
    def minimize_epsilon(self, k, m):
        matching_trial = {"trial": None}
        def objective(trial):
            e = trial.suggest_int("e", 1, self.e_ref)

            _, df_estimated = self.run_command(self.e_ref, k, m)

            trial.set_user_attr('real', get_real_frequency(self.df))
            trial.set_user_attr('estimated', df_estimated)
            trial.set_user_attr('e', e)
            table = display_results(get_real_frequency(self.df), df_estimated)
            percentage_errors = [float(row[-1].strip('%')) for row in table]
            max_error = max(percentage_errors)

            print(f"Max error: {max_error}")
            print(f"Error value: {self.error_value * 100}")

            if max_error <= (self.error_value * 100):
                matching_trial["trial"] = trial
                trial.study.stop()
            
            return e
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.n_trials)

        final_trial = matching_trial["trial"] or study.best_trial

        real = final_trial.user_attrs['real']
        estimated = final_trial.user_attrs['estimated']

        display_error_table(real, estimated, self.p)

        return final_trial.user_attrs["e"]

def run_setup(df):
    """
    Main function to run the setup process.
    """
    df_temp = df.copy()
    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.i, header=1)  
    else:
        df = df_temp

    setup_instance = Setup(df)
    setup_instance.filter_dataframe()

    while not setup_instance.found_best_values:
        setup_instance.k, setup_instance.m = setup_instance.optimize_k_m()
        if not setup_instance.found_best_values:
            setup_instance.e_ref += (setup_instance.e_ref*0.2)
    
    setup_instance.e_ref = setup_instance.minimize_epsilon(setup_instance.k, setup_instance.m)
    
    print(f"Optimal parameters found: k={setup_instance.k}, m={setup_instance.m}, e={setup_instance.e_ref}")
    print(f"Events: {setup_instance.events_names}")
    print(f"Privacy method: {setup_instance.privacy_method}")
    print(f"Error metric: {setup_instance.error_metric}")
    
    save_setup_json(setup_instance)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run setup process")
    parser.add_argument("-i", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()
    if not os.path.isfile(args.i):
        print(f"❌ File not found: {args.i}")
        sys.exit(1)

    df_temp = pd.read_excel(args.i)

    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.i, header=1)  
    else:
        df = df_temp

    run_setup(df)