import os
import sys
import optuna
import numpy as np
import pandas as pd
from tabulate import tabulate
import argparse
import hashlib
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from clip_protocol.utils.utils import load_setup_json, get_real_frequency, save_mask_json, display_results
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

class Mask:
    def __init__(self, privacy_level, df):
        self.k, self.m, self.e_ref, self.n_trials, self.events_names, self.privacy_method, self.error_metric, self.error_value, self.tolerance, self.p = load_setup_json()
        self.privacy_level = privacy_level
        self.df = df
        self.matching_trial = None
        self.N = len(self.df)

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

        # Filter by percentage >= 0.1%
        real_freq = get_real_frequency(self.df)
        real_freq_dict = dict(zip(real_freq["Element"], real_freq["Frequency"]))
        real_percent = {k: (v * 100 /self.N) for k, v in real_freq_dict.items()}
        valid_elements = [k for k, v in real_percent.items() if v >= 0.1]
        self.df = self.df[self.df["value"].isin(valid_elements)]
        
        # Pseudonimize the user column
        self.df['user'] = self.df['user'].apply(self.pseudonimize)
    
    def pseudonimize(self, user_name):
        return hashlib.sha256(user_name.encode()).hexdigest()[:10] 
    
    def run_command(self, e):
        if self.privacy_method == "PCMeS":
            coeffs, privatized_data, df_estimated = run_private_cms_client(self.k, self.m, e, self.df)
        elif self.privacy_method == "PHCMS":
            coeffs, privatized_data, df_estimated = run_private_hcms_client(self.k, self.m, e, self.df)
        
        return coeffs, privatized_data, df_estimated

    def optimize_e(self):
        def objective(trial):
            e = round(trial.suggest_float('e', 0.1, self.e_ref, step=0.1), 4)
            coeffs, privatized_data, df_estimated = self.run_command(e)

            headers=[
                "Element", "Real Frequency", "Real Percentage", 
                "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
                "Percentage Error"
            ]

            table = display_results(get_real_frequency(self.df), df_estimated)
            print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

            max_error = max([float(row[-1].strip('%')) for row in table])

            trial.set_user_attr('e', e)
            trial.set_user_attr('hash', coeffs)
            trial.set_user_attr('privatized_data', privatized_data)

            bounds = self._get_error_bounds()
            if bounds[0] < max_error <= bounds[1]:
                self.matching_trial = trial
                trial.study.stop()
            
            if max_error > bounds[1]:
                return float("inf")
            
            return round(abs(bounds[1] - max_error), 4)

        study = optuna.create_study(direction='minimize') 
        study.optimize(objective, n_trials=self.n_trials)

        if self.matching_trial is not None:
            trial = self.matching_trial
        else:
            trial = study.best_trial
               
        best_e = trial.user_attrs['e']
        coeffs = trial.user_attrs['hash']
        privatized_data = trial.user_attrs['privatized_data']
                
        return best_e, privatized_data, coeffs
    
    def _get_error_bounds(self):
        if self.privacy_level == "high":
            return (self.error_value-self.tolerance)*100, (self.error_value + self.tolerance)*100
        elif self.privacy_level == "low":
            return 0, (self.error_value-self.tolerance)*100
    
def run_mask(df):
    privacy_level = input("Enter the privacy level (high/low): ").strip().lower()
    if privacy_level not in ["high", "low"]:
        print("Invalid privacy level. Please enter 'high' or 'low'.")
        return
    mask_instance = Mask(privacy_level, df)
    mask_instance.filter_dataframe()
    best_e, privatized_data, coeffs = mask_instance.optimize_e()
    save_mask_json(mask_instance, best_e, coeffs, privatized_data, mask_instance.privacy_method)
    return privatized_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run privatization mask with input CSV")
    parser.add_argument("-i", type=str, required=True, help="Path to the input CSV file")
    args = parser.parse_args()
    if not os.path.isfile(args.i):
        print(f"❌ File not found: {args.i}")
        sys.exit(1)

    df_temp = pd.read_excel(args.i)

    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.i, header=1)  
    else:
        df = df_temp

    start = time.time()
    run_mask(df)
    end = time.time()
    elapsed_time = end - start
    print(f"Execution time: {elapsed_time:.2f} seconds")