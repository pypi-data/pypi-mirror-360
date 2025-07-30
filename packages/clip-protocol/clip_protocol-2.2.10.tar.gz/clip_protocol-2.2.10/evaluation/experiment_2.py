import optuna
import pandas as pd
import os
import sys
import time
import argparse
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import display_results, get_real_frequency
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

# Escalabilidad: misma distribución distintos tamaños

def filter_dataframe(df):
    df.columns = ["user", "value"]
    return df

def run_command(e, k, m, df, privacy_method):
    if privacy_method == "PCMeS":
        _, _, df_estimated = run_private_cms_client(k, m, e, df)
    elif privacy_method == "PHCMS":
        _, _, df_estimated = run_private_hcms_client(k, m, e, df)
    
    error = compute_error_table(get_real_frequency(df), df_estimated, 2)
    table = display_results(get_real_frequency(df), df_estimated)
    return error, df_estimated, table

def optimize_e(k, m, df, e_r, privacy_level, error_value, tolerance, privacy_method):
    matching_trial = {"trial": None}
    trial_counter = {"count": 0}

    def objective(trial):
        trial_counter["count"] += 1
        e = round(trial.suggest_float('e', 0.1, e_r, step=0.1), 4)
        _, _, table = run_command(e, k, m, df, privacy_method)

        percentage_errors = [float(row[-1].strip('%')) for row in table]
        max_error = max(percentage_errors)

        trial.set_user_attr('table', table)
        trial.set_user_attr('e', e)
        trial.set_user_attr('max_error', max_error)

        if privacy_level == "high":
            objective_high = (error_value + tolerance)*100
            objective_low = (error_value-tolerance)*100
        elif privacy_level == "low":
            objective_high = (error_value-tolerance)*100
            objective_low = 0

        print("Error: ", max_error)
        if objective_high >= max_error > objective_low:
            matching_trial["trial"] = trial
            trial.study.stop()
        
        return round(abs(objective_high - max_error), 4)
        
    study = optuna.create_study(direction='minimize') 
    study.optimize(objective, n_trials=20)

    final_trial = matching_trial["trial"] or study.best_trial
            
    table = final_trial.user_attrs['table']
    max_error = final_trial.user_attrs['max_error']
    e = final_trial.user_attrs['e']
            
    return table, max_error, e, trial_counter["count"]


def run_experiment_2(datasets_by_size, params):
    n_repeats = 10
    error_value = 0.05
    tolerance = 0.01
    privacy_level = "high"

    all_results = []
    
    for repeat in range(n_repeats):
        print(f"🔁 Repetición {repeat + 1}/{n_repeats}...")

        for size, df in datasets_by_size.items():
            df.columns = ["user", "value"]
            df = filter_dataframe(df)

            for method in ["PCMeS", "PHCMS"]:
                print(f"🔍 Ejecutando {method} con tamaño {size}...")

                k = params[method]["k"]
                m = params[method]["m"]
                e_r = params[method]["e_r"]

                start_time = time.time()
                _, _, _, n_iter = optimize_e(k, m, df, e_r, privacy_level, error_value, tolerance, method)
                end_time = time.time()

                all_results.append({
                    "Número de registros": size,
                    "Método": method,
                    "Iteraciones": n_iter,
                    "Tiempo de ejecución": round(end_time - start_time, 4)
                })

    df = pd.DataFrame(all_results)
    df_mean = df.groupby(["Número de registros", "Método"]).mean(numeric_only=True).reset_index()

    df_pivot = df_mean.pivot(index="Número de registros", columns="Método", values=["Iteraciones", "Tiempo de ejecución"])
    df_pivot.columns = [f"{col[0]} {col[1]}" for col in df_pivot.columns]
    df_pivot = df_pivot.reset_index()

    final_cols = ["Número de registros",
                  "Iteraciones PHCMS", "Tiempo de ejecución PHCMS",
                  "Iteraciones PCMeS", "Tiempo de ejecución PCMeS"]
    df_pivot = df_pivot[final_cols]

    df_pivot.to_csv("figures/table_experiment_2.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run scalability experiment")
    parser.add_argument("-f", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()
    data_path = args.f # folder

    params_path = os.path.join(os.path.dirname(__file__), "figures", "experiment_2_params.json")
    with open(params_path, 'r') as f:
        params = json.load(f)

    distribution = input("📌 Enter the distribution 1/2/3/4: ")
    sizes = [3000, 4000, 5000, 6000, 7000]

    datasets = {}
    for size in sizes:
        pattern = f"aoi-hits-d{distribution}-{size}"
        file_path = os.path.join(args.f, pattern + ".xlsx")
        header = 1 if "Unnamed" in pd.read_excel(file_path, nrows=1).columns[0] else 0
        df = pd.read_excel(file_path, header=header)
        datasets[size] = df
        
    
    run_experiment_2(datasets, params)