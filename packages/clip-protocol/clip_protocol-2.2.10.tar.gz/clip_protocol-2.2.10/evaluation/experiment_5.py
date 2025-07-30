import optuna
import pandas as pd
import os
import sys
import time
from tqdm import tqdm
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import get_real_frequency, display_results, load_setup_json
from clip_protocol.utils.errors import compute_error_table

from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client


def filter_dataframe(df):
    event_names = ["Participant", "AOI Name"]
    matching_columns = [col for col in event_names if col in df.columns]
    if not matching_columns:
        print("⚠️ None of the specified event names match the DataFrame columns.")
    
    df = df[matching_columns].copy()
    df.columns = ["user", "value"]

    df['value'] = df['value'].astype(str).apply(lambda x: x.strip())
    df = df[df['value'] != '-']
    df = df[df['value'].str.contains(r'\w', na=False)]
    N = len(df)

    # Filter by percentage >= 0.1%
    real_freq = get_real_frequency(df)
    real_freq_dict = dict(zip(real_freq["Element"], real_freq["Frequency"]))
    real_percent = {k: (v * 100 /N) for k, v in real_freq_dict.items()}
    valid_elements = [k for k, v in real_percent.items() if v >= 0.1]
    df = df[df["value"].isin(valid_elements)]
    
    return df

def run_command(e, k, m, df, privacy_method):
    if privacy_method == "PCMeS":
        _, privatized_data, df_estimated = run_private_cms_client(k, m, e, df)
    elif privacy_method == "PHCMS":
        _, privatized_data, df_estimated = run_private_hcms_client(k, m, e, df)

    error = compute_error_table(get_real_frequency(df), df_estimated, 1.5)
    table = display_results(get_real_frequency(df), df_estimated)
    return table, privatized_data

def optimize_e(k, m, df, e_r, privacy_level, error_value, tolerance, privacy_method, n_trials):
    matching_trial = {"trial": None}
    def objective(trial):
        e = round(trial.suggest_float('e', 0.1, e_r, step=0.1), 4)
        table, privatized_data = run_command(e, k, m, df, privacy_method)

        percentage_errors = [float(row[-1].strip('%')) for row in table]
        max_error = max(percentage_errors)

        trial.set_user_attr('privatized_data', privatized_data)
        trial.set_user_attr('table', table)
        trial.set_user_attr('e', e)
        trial.set_user_attr('max_error', max_error)
        print(f"Trial: e = {e}, max_error = {max_error}")

        if privacy_level == "high":
            objective_high = (error_value + tolerance)*100
            objective_low = (error_value-tolerance)*100
        elif privacy_level == "low":
            objective_high = (error_value-tolerance)*100
            objective_low = 0

        if objective_high >= max_error > objective_low:
            matching_trial["trial"] = trial
            trial.study.stop()
        
        if max_error > objective_high:
            return float("inf")
        
        return round(abs(objective_high - max_error), 4)
        

    study = optuna.create_study(direction='minimize') 
    study.optimize(objective, n_trials=15)

    final_trial = matching_trial["trial"] or study.best_trial
            
    table = final_trial.user_attrs['table']
    max_error = final_trial.user_attrs['max_error']
    e = final_trial.user_attrs['e']
    privatized_data = final_trial.user_attrs['privatized_data']
            
    return table, max_error, e, privatized_data

def measure_size_on_disk(df, prefix):
    temp_path = f"temp_{prefix}.csv"
    df = pd.DataFrame(df)
    df.to_csv(temp_path, index=False)
    size_on_disk = os.path.getsize(temp_path)
    os.remove(temp_path)
    return size_on_disk
    
def run_experiment_5(datasets, privatized_path):
    k, m,  e_r, n_trials, _,  privacy_method,  _,  error_value,  tolerance,  _ = load_setup_json()
    privacy_level = "high"
    privacy_method = "PCMeS"
    k = 841
    m = 41356
    e_r = 16
    error_value = 0.04
    tolerance = 0.01
    
    tables = []
    performance_records = []
    size_comparison_records = []

    for data in datasets:
        data_df = filter_dataframe(data)
        original_size = measure_size_on_disk(data_df, f"original_user")

        start_time = time.time()
        table, max_error, e, privatized_data = optimize_e(k, m, data_df, e_r, privacy_level, error_value, tolerance, privacy_method, n_trials)
        if error_value + tolerance <= max_error:
            end_time = time.time()
            elapsed_time = end_time - start_time
            tables.append(table)

            # Save the privatized data temporarily to check its size
            privatized_size = measure_size_on_disk(privatized_data, f"priv_user")
        
            performance_records.append({
                "User": data_df["user"].iloc[0],
                "Epsilon": e,
                "Maximun Error": max_error,
                "Execution time": round(elapsed_time, 4)
            })

            size_comparison_records.append({
                "User": data_df["user"].iloc[0],
                "Original Size (bytes)": original_size,
                "Privatized Size (bytes)": privatized_size,
                "Compression Ratio": round(privatized_size / original_size, 4)
            })

            user_id = data_df["user"].iloc[0]
            filename = f"{privatized_path}/user_{user_id}_privatized.csv"
            privatized_data = pd.DataFrame(privatized_data)
            privatized_data.to_csv(filename, index=False)
    
    performance_df = pd.DataFrame(performance_records)
    performance_df.to_csv("figures/experiment_5.csv", index=False)

    size_df = pd.DataFrame(size_comparison_records)
    size_df.to_csv("figures/experiment_5_size_comparison.csv", index=False)

def load_excel_with_header_check(filepath):
    try:
        df_temp = pd.read_excel(filepath, nrows=2)
        header = 1 if any(col.startswith("Unnamed") for col in df_temp.columns) else 0
        df = pd.read_excel(filepath, header=header)
        return df
    except Exception as e:
        print(f"Error al leer {filepath}: {e}")
        return None
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment 3")
    parser.add_argument("-d1", type=str, required=True, help="Path to the input excel file")
    parser.add_argument("-d2", type=str, required=True, help="Path save privatized data")
    args = parser.parse_args()

    data_path = args.d1 # folder
    privatized_path = args.d2 # folder

    CACHE_PATH = os.path.join(data_path, "cached_datasets.pkl")
    if os.path.exists(CACHE_PATH):
        print("✅ Cargando datasets desde caché...")
        with open(CACHE_PATH, "rb") as f:
            datasets = pickle.load(f)

    else:
        print("📥 Procesando archivos Excel...")
        datasets = []
        dataset_lengths = []

        excel_files = [f for f in os.listdir(data_path) if f.endswith(".xlsx")]
        full_paths = [os.path.join(data_path, f) for f in excel_files]

        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_file = {executor.submit(load_excel_with_header_check, path): path for path in full_paths}
            for future in tqdm(as_completed(future_to_file), total=len(full_paths), desc="Cargando archivos"):
                df = future.result()
                if df is not None and not df.empty:
                    datasets.append(df)
                    dataset_lengths.append(len(df))
                else:
                    print(f"⚠️ Archivo inválido o vacío: {future_to_file[future]}")
        
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(datasets, f)
            print(f"💾 Datasets guardados en caché: {CACHE_PATH}")
    

    run_experiment_5(datasets, privatized_path)